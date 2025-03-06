"""
Web crawler utility for finding URLs on a website.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging
import time


class WebsiteCrawler:
    """Crawls a website to find all URLs."""

    def __init__(self, max_pages=10, same_domain_only=True, delay=0.5):
        """Initialize the crawler.

        Args:
            max_pages (int): Maximum number of pages to crawl
            same_domain_only (bool): Only crawl URLs from the same domain
            delay (float): Delay between requests in seconds
        """
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.delay = delay
        self.visited = set()
        self.queue = []
        self.found_urls = set()
        self.logger = logging.getLogger(self.__class__.__name__)

    def crawl(self, start_url):
        """Crawl the website starting from the given URL.

        Args:
            start_url (str): URL to start crawling from

        Returns:
            list: List of found URLs
        """
        self.visited = set()
        self.queue = [start_url]
        self.found_urls = set([start_url])
        base_domain = urlparse(start_url).netloc

        self.logger.info(f"Starting crawl from {start_url}")
        self.logger.info(f"Maximum pages: {self.max_pages}")

        while self.queue and len(self.visited) < self.max_pages:
            # Get the next URL from the queue
            current_url = self.queue.pop(0)

            # Skip if already visited
            if current_url in self.visited:
                continue

            # Add to visited set
            self.visited.add(current_url)

            try:
                self.logger.info(f"Crawling {current_url}")

                # Request the URL
                response = requests.get(current_url, timeout=10)

                # Skip if not HTML
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type.lower():
                    self.logger.info(f"Skipping non-HTML content: {content_type}")
                    continue

                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all links
                links = soup.find_all('a', href=True)

                for link in links:
                    href = link['href']

                    # Skip empty, fragment, mailto, and javascript links
                    if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
                        continue

                    # Convert to absolute URL
                    full_url = urljoin(current_url, href)

                    # Remove fragments
                    full_url = full_url.split('#')[0]

                    # Skip if already found
                    if full_url in self.found_urls:
                        continue

                    # Check domain if same_domain_only is True
                    if self.same_domain_only:
                        link_domain = urlparse(full_url).netloc
                        if link_domain != base_domain:
                            continue

                    # Add to found URLs
                    self.found_urls.add(full_url)

                    # Add to queue for further crawling
                    self.queue.append(full_url)

                    self.logger.debug(f"Found URL: {full_url}")

                # Respect robots.txt by adding a delay
                time.sleep(self.delay)

            except Exception as e:
                self.logger.error(f"Error crawling {current_url}: {str(e)}")

        self.logger.info(f"Crawl complete. Found {len(self.found_urls)} URLs")
        return list(self.found_urls)