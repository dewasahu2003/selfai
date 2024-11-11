import time
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

logger = Logger(service="selfai/crawler/linkedin")


class LinkedinCrawler(BaseAbstractCrawler):
    model = PostDoc

    def set_extra_driver_options(self, options: Options) -> None:
        options.add_experimental_option("detach", True)

    def extract(self, link: str, **kwargs):
        logger.info(f"Extracting data from {link}")
        self.login()

        soup = self._get_page_content(link)
        data = {
            "Name": self._scrape_section(soup, "h1", class_="text-heading-xlarge"),
            "About": self._scrape_section(soup, "div", class_="display-flex ph5 pv3"),
            "Main Page": self._scrape_section(soup, "div", {"id": "main-content"}),
            "Experience": self._extract_experience(link),
            "Education": self._extract_education(link),
        }
        self.driver.get(link)
        time.sleep(5)
        button = self.driver.find_element(
            By.CSS_SELECTOR,
            ".app-aware-link.profile-creator-shared-content-view__footer-action",
        )
        button.click()

        self.scroll_page()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        post_elements = soup.find_all(
            "div",
            class_="update-components-text relative update-components-update-v2__commentary",
        )
        buttons = soup.find_all(
            "div",
            class_="update-components-image__image-link",
        )
        posts_images = self._extract_image_urls(buttons)

        posts = self._extract_posts(post_elements, posts_images)
        logger.info(f"Extracted {len(posts)} posts for {link}")

        self.driver.close()

        self.model.bulk_insert(
            [
                PostDoc(platform="linkedin", content=post, author_id=kwargs.get("user"))
                for post in posts
            ]
        )
        logger.info(f"Inserted {len(posts)} posts for {link}")

    def _scrape_section(self, soup: BeautifulSoup, *args, **kwargs):
        parent_div = soup.find(*args, **kwargs)
        return parent_div.get_text(strip=True) if parent_div else ""

    def _extract_image_urls(self, buttons: List[Tag]) -> Dict[str, str]:
        """ "extract img url for each button"""
        post_images = {}
        for i, button in enumerate(buttons):
            img_tag = button.find("img")
            if img_tag and "src" in img_tag.attrs:
                post_images[f"Post_{i}"] = img_tag["src"]
            else:
                logger.warning("no image found for this button")
        return post_images

    def _get_page_content(self, url: str) -> BeautifulSoup:
        self.driver.get(url)
        time.sleep(5)
        return BeautifulSoup(self.driver.page_source, "html.parser")

    def _extract_posts(
        self, post_elements: List[Tag], post_images: Dict[str, str]
    ) -> Dict[str, Dict[str, str]]:
        posts_data = {}
        for i, post_element in enumerate(post_elements):
            post_text = post_element.get_text(strip=True, separator="\n")
            post_data = {"text": post_text}

            if f"Post_{i}" in post_images:
                post_data["image"] = post_images[f"Post_{i}"]
            posts_data[f"Post_{i}"] = post_data
        return posts_data

    def _extract_experience(self, profile_url: str) -> str:
        self.driver.get(profile_url + "/details/experience/")
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        experience_section = soup.find("section", {"id": "experience-section"})
        return experience_section.get_text(strip=True) if experience_section else ""

    def _scrape_education(self, profile_url: str) -> str:
        self.driver.get(profile_url + "/details/education/")
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        education_section = soup.find("section", {"id": "education-section"})
        return education_section.get_text(strip=True) if education_section else ""

    def login(self) -> None:
        self.driver.get("https://www.linkedin.com/login")
        if not settings.LINKEDIN_USERNAME and not settings.LINKEDIN_PASSWORD:
            raise ImproperlyConfigured(
                "LINKEDIN_USERNAME and LINKEDIN_PASSWORD must be set"
            )

        self.driver.find_element(By.ID, "username").send_keys(
            settings.LINKEDIN_USERNAME
        )
        self.driver.find_element(By.ID, "password").send_keys(
            settings.LINKEDIN_PASSWORD
        )
        self.driver.find_element(
            By.CSS_SELECTOR, ".login__form_action_container button"
        ).click()
