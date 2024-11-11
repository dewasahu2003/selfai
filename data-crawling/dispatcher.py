import re
from crawlers.base import BaseCrawler


class CrawlerDispatcher:
    def __init__(self) -> None:
        self._crawlers = {}

    def register_crawler(self, domain: str, crawler: type[BaseCrawler]) -> None:
        pattern = r"https://(www\.)?{}.com".format(re.escape(domain))
        self._crawlers[pattern] = crawler

    def get_crawler(self, url: str) -> BaseCrawler:
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler()
        else:
            raise ValueError("No crawler found for the given URL.")
