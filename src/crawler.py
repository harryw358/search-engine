import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
from collections import deque

class Crawler:
    def __init__(self, start_url="http://quotes.toscrape.com/", max_pages=50, limit_pages=True):
        """
        Initialises the recursive crawler with the target website, 
        a session, and a limit for maximum pages to crawl.
        """
        self.start_url = start_url
        self.base_domain = urlparse(start_url).netloc
        self.session = requests.Session()
        self.politeness_delay = 6.0 # 6-second politness window.
        self.max_pages = max_pages
        self.limit_pages = limit_pages

    def fetch_page(self, url):
        """
        Makes the HTTP GET request to fetch the HTML content of the page.
        """
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
        
    def extract_text(self, html_content):
        """
        Parses the HTML and extracts all visible text (quotes and authors) for the inverted index.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted = []

        # 1. Extract quotes (from index and tag pages)
        quotes = soup.find_all('div', class_='quote')
        for q in quotes:
            text = q.find('span', class_='text').get_text(strip=True)
            author = q.find('small', class_='author').get_text(strip=True)
            extracted.append(f"{text} - {author}")

        # 2. Extract author bios (from /author/ pages)
        author_title = soup.find('h3', class_='author-title')
        author_desc = soup.find('div', class_='author-description')
        if author_title and author_desc:
            extracted.append(f"{author_title.get_text(strip=True)}: {author_desc.get_text(strip=True)}")

        return " ".join(extracted)
    
    def extract_links(self, html_content, current_url):
            """
            Finds all valid internal links on the page to add to the crawl queue.
            """
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(current_url, href)
                
                # Strip URL fragments (e.g., #top) so we don't treat them as new pages
                full_url = full_url.split('#')[0]

                # Only keep the link if it belongs to our target domain
                if urlparse(full_url).netloc == self.base_domain:
                    links.append(full_url)
                    
            return links

    def crawl(self):
        """
        Main recursive crawling loop using Breadth-First Search (BFS).
        """
        # deque is highly optimized for popping items from the front of the list
        queue = deque([self.start_url])
        visited = set([self.start_url])
        crawled_data = []


        while queue and (not self.limit_pages or len(crawled_data) < self.max_pages):
            current_url = queue.popleft()
            html = self.fetch_page(current_url)

            if not html:
                continue

            page_text = self.extract_text(html)
            
            # Only save the page if we actually found quotes or bios
            if page_text: 
                crawled_data.append({
                    'url': current_url,
                    'text': page_text
                })

            # Find new links and add them to the queue if we haven't seen them
            new_links = self.extract_links(html, current_url)
            for link in new_links:
                if link not in visited:
                    visited.add(link)
                    queue.append(link)

            # Politeness delay (only sleep if we have more pages to process)
            if queue and (not self.limit_pages or len(crawled_data) < self.max_pages):
                print(f"Politeness window: waiting {self.politeness_delay} seconds...")
                time.sleep(self.politeness_delay)

        print(f"Crawl complete. Successfully scraped {len(crawled_data)} pages.")
        return crawled_data