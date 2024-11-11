from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from crawlers import GithubCrawler, LinkedinCrawler, MediumCrawler
from db.documents import UserDoc
from dispatcher import CrawlerDispatcher
from utils import user_to_names

logger = Logger(service="selfai/crawler")

_dispatcher = CrawlerDispatcher()
_dispatcher.register_crawler("github", GithubCrawler)
_dispatcher.register_crawler("linkedin", LinkedinCrawler)
_dispatcher.register_crawler("medium", MediumCrawler)


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> None:
    logger.info("starting crawler")
    first_name, last_name = user_to_names(event.get("user"))

    user = UserDoc.get_or_create(first_name=first_name, last_name=last_name)
    link = event.get("link")
    crawler = _dispatcher.get_crawler(link)

    try:
        crawler.extract(link=link, user=user)
        return {"statusCode": 200, "body": "Link processed Succesfully"}
    except Exception as e:
        return {"statusCode": 500, "body": f"Error occured: {str(e)}"}


# if __name__ == "__main__":
#     event = {"user": "Dewa Sahu", "link": "https://www.linkedin.com/in/dewasahu/"}
#     handler(event, None)
