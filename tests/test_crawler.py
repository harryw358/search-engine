import pytest
from unittest.mock import patch, MagicMock
from src.crawler import Crawler

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

def test_get_next_page_exists(crawler, sample_html):
    """Test that pagination correctly identifies the next URL."""
    next_url = crawler.get_next_page(sample_html, "http://quotes.toscrape.com/")
    
    assert next_url == "http://quotes.toscrape.com/page/2/"

def test_get_next_page_missing(crawler, last_page_html):
    """Test that pagination returns None when there is no next page."""
    next_url = crawler.get_next_page(last_page_html, "http://quotes.toscrape.com/page/10/")
    
    assert next_url is None

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