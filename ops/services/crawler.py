from .base import FunctionService
from pulumi import Output
from pydantic import Field


# lambda
class CrawlerService(FunctionService):
    service_name: str = "crawler"
    image_name: str = "crawler" + ":latest"
    docker_file: str = "../data-crawling/Dockerfile.crawler"
    context: str = "../data-crawling"
    target_service: str = "lambda"

    container_port: int = 3333
    host_port: int = 3333

    boundary_sgs: list[Output[str]] = Field(..., description="List of boundary signal groups")

    class Config:
        arbitrary_types_allowed = True