import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

class Crawler:
    def __init__(self, start_url="http://quotes.toscrape.com/"):
        """
        Initialises the crawler with the target website and a session. 
        """
        self.start_url = start_url
        self.session = requests.Session()
        self.politeness_delay = 6.0 # 6-second politness window.

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
        Parses the HTML and extracts all visible text (quotes) for the inverted index.
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        quotes = soup.find_all('div', class_='quote')

        extracted = []
        for q in quotes:
            text = q.find('span', class_='text').get_text(strip=True)
            author = q.find('small', class_='author').get_text(strip=True)
            extracted.append(f"{text} - {author}")

        return " ".join(extracted)
    
    def get_next_page(self, html_content, current_url):
        """
        Finds the 'Next' button on the page to handle pagination.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        next_list_item = soup.find('li', class_='next')

        if next_list_item:
            next_link = next_list_item.find('a')['href']
            # urljoin safely handles relative paths
            return urljoin(current_url, next_link)
        
        return None
    
    def crawl(self):
        """
        Main crawling loop that handles fetching, text extraction,
        pagination, and the politeness window.
        """
        current_url = self.start_url
        crawled_data = []

        while current_url:
            html = self.fetch_page(current_url)

            if not html:
                break # Stop if we encounter a fetch error.

            # Extract text to eventually pass to the indexer.
            page_text = self.extract_text(html)
            crawled_data.append({
                'url': current_url,
                'text': page_text
            })

            # Check for the next page.
            current_url = self.get_next_page(html, current_url)

            # If there's another page, wait before making the next request.
            if current_url:
                print(f"Politeness window: waiting {self.politeness_delay} seconds...")
                time.sleep(self.politeness_delay)

        print(f"Crawl complete. Successfully scraped {len(crawled_data)} pages.")
        return crawled_data
    
if __name__ == "__main__":
    crawler = Crawler()
    data = crawler.crawl()
    # Print the text from the first page.
    if data:
        print("\nPreview of first page text:\n")
        print(data[0]['text'][:500] + "...")
