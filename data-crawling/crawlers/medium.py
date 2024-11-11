from typing import Dict, List

from aws_lambda_powertools import Logger
from .base import BaseAbstractCrawler
from bs4 import BeautifulSoup
from bs4.element import Tag
from config import settings
from db.documents import PostDoc
from errors import ImproperlyConfigured
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

logger = Logger(service="selfai/crawler/medium")


class MediumCrawler(BaseAbstractCrawler):
    model = PostDoc

    def set_extra_driver_options(self, options: Options) -> None:
        options.add_experimental_option("detach", True)

    def extract(self, link: str, **kwargs):
        logger.info(f"Extracting data from medium {link}")
        self.driver.get(link)
        self.scroll_page()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        title = soup.find_all("h1", class_="pw-post-title")
        subtitle = soup.find_all("h2", class_="pw-subtitle-paragraph")

        data = {
            "Title": title[0].string if title else None,
            "Subtitle": subtitle[0].string if subtitle else None,
            "Content": soup.get_text(),
        }
        logger.info(f"Extracted article and saved: {data}")
        self.driver.close()
        instance = self.model(
            platform="medium",
            content=data,
            author_id=kwargs.get("user"),
        )
        instance.save()

    def login(self) -> None:
        self.driver.get("https://medium.com/m/signin")
        self.driver.find_element(By.TAG_NAME, "a").click()
