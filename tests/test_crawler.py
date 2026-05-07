import pytest
from unittest.mock import patch, MagicMock
from src.crawler import Crawler
import requests

# --- Fixtures ---

@pytest.fixture
def crawler():
    """Provides a fresh Crawler instance for each test."""
    return Crawler()

@pytest.fixture
def sample_html():
    """Provides mock HTML with quotes and a 'Next' button."""
    return """
    <html>
        <body>
            <div class="quote">
                <span class="text">"The world as we have created it is a process of our thinking."</span>
                <small class="author">Albert Einstein</small>
            </div>
            <div class="quote">
                <span class="text">"It is our choices, Harry, that show what we truly are."</span>
                <small class="author">J.K. Rowling</small>
            </div>
            <li class="next"><a href="/page/2/">Next <span aria-hidden="true">&rarr;</span></a></li>
        </body>
    </html>
    """

@pytest.fixture
def last_page_html():
    """Provides mock HTML for a page with no 'Next' button."""
    return """
    <html>
        <body>
            <div class="quote">
                <span class="text">"A day without sunshine is like, you know, night."</span>
                <small class="author">Steve Martin</small>
            </div>
        </body>
    </html>
    """

# --- Tests ---

def test_extract_text(crawler, sample_html):
    """Test that the custom BeautifulSoup logic correctly formats quotes and authors."""
    result = crawler.extract_text(sample_html)
    expected_result = ('"The world as we have created it is a process of our thinking." - Albert Einstein '
                       '"It is our choices, Harry, that show what we truly are." - J.K. Rowling')
    
    assert result == expected_result

def test_extract_links_exists(crawler):
    """Tests that the crawler successfully finds and formats valid internal links."""
    html = '<html><body><a href="/page/2/">Next</a><a href="/author/Einstein/">Bio</a></body></html>'
    
    # Action: Extract links based on a current URL
    links = crawler.extract_links(html, "http://quotes.toscrape.com/")
    
    # Assert: It should find both internal links and format them as absolute URLs
    assert len(links) == 2
    assert "http://quotes.toscrape.com/page/2/" in links
    assert "http://quotes.toscrape.com/author/Einstein/" in links

def test_extract_links_missing_or_external(crawler):
    """Tests that the crawler safely returns an empty list if there are no valid internal links."""
    # This HTML has plain text and one external link (which must be ignored)
    html = '<html><body><p>No internal links here!</p><a href="https://wikipedia.org">External</a></body></html>'
    
    # Action: Extract links
    links = crawler.extract_links(html, "http://quotes.toscrape.com/")
    
    # Assert: The list should be completely empty
    assert links == []

@patch('src.crawler.requests.Session.get')
def test_fetch_page_success(mock_get, crawler, sample_html):
    """Test that fetch_page successfully returns HTML on a 200 OK response."""
    # Setup the mock to simulate a successful HTTP response
    mock_response = MagicMock()
    mock_response.text = sample_html
    mock_response.raise_for_status.return_value = None 
    mock_get.return_value = mock_response

    html = crawler.fetch_page("http://quotes.toscrape.com/")
    
    assert html == sample_html

@patch('src.crawler.time.sleep') 
@patch('src.crawler.requests.Session.get') 
def test_crawl_integration(mock_get, mock_sleep, crawler, sample_html, last_page_html):
    """Test the full crawl loop without hitting the live site or waiting 6 seconds."""
    # Setup mock network responses for two pages
    mock_resp_page_1 = MagicMock()
    mock_resp_page_1.text = sample_html
    
    mock_resp_page_2 = MagicMock()
    mock_resp_page_2.text = last_page_html
    
    # side_effect allows the mock to return different responses on consecutive calls
    mock_get.side_effect = [mock_resp_page_1, mock_resp_page_2]

    results = crawler.crawl()

    # Assertions
    assert len(results) == 2, "Crawler should have scraped exactly two pages."
    assert "Albert Einstein" in results[0]['text']
    assert "Steve Martin" in results[1]['text']
    
    # Ensure the 6-second politeness window was triggered exactly once
    mock_sleep.assert_called_once_with(6.0)

# Network Failure Test:
import requests

@patch('src.crawler.requests.Session.get')
def test_fetch_page_network_error(mock_get, crawler):
    """Tests that the crawler handles network errors gracefully without crashing."""
    # Force the mock to simulate a network crash (e.g., timeout or 500 error)
    mock_get.side_effect = requests.RequestException("Simulated connection timeout")
    
    # Action: Try to fetch a page
    result = crawler.fetch_page("http://quotes.toscrape.com/")
    
    # Assert: It should catch the error, print a message, and safely return None
    assert result is None

# Test limit_pages=False
@patch('src.crawler.time.sleep')
@patch('src.crawler.requests.Session.get')
def test_crawl_limit_pages_false(mock_get, mock_sleep):
    """Tests that with limit_pages=False, it crawls until the queue is naturally empty."""
    # Setup a crawler with NO hard limit
    unlimited_crawler = Crawler(limit_pages=False)
    
    # Mock a tiny 2-page website: 
    # Page A links to Page B. 
    # Page B has a quote, but NO further links.
    mock_html_a = '<html><body><a href="/page-b/">Next</a></body></html>'
    mock_html_b = '<html><body><div class="quote"><span class="text">"Done"</span><small class="author">Me</small></div></body></html>'
    
    mock_resp_a = MagicMock()
    mock_resp_a.text = mock_html_a
    mock_resp_a.raise_for_status.return_value = None
    
    mock_resp_b = MagicMock()
    mock_resp_b.text = mock_html_b
    mock_resp_b.raise_for_status.return_value = None
    
    # Tell the mock to return Page A on the first request, and Page B on the second
    mock_get.side_effect = [mock_resp_a, mock_resp_b]
    
    # Action: Run the unlimited crawl
    results = unlimited_crawler.crawl()
    
    # Assert: It stopped naturally after 2 requests because the queue ran out
    assert mock_get.call_count == 2
    # Only Page B had text to extract, so only 1 item should be in the results
    assert len(results) == 1

# Test Fragment Stripping (Preventing Infinite Loops)
def test_extract_links_strips_fragments(crawler):
    """Tests that URL fragments (#) are stripped to prevent duplicate queueing."""
    # A link with an anchor tag pointing to a specific part of a page
    html = '<a href="/page/2/#author-bio">Go to bio</a>'
    
    links = crawler.extract_links(html, "http://quotes.toscrape.com/")
    
    # It should resolve the URL but completely strip the #author-bio part
    assert "http://quotes.toscrape.com/page/2/" in links
    assert "#author-bio" not in links[0]