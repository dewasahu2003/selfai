from .base import ContainerService
from pulumi import Output
from pydantic import Field


class MQ(ContainerService):

    service_name: str = "mq"
    image_name: str = "mq" + ":latest"
    docker_file: str = "../data-ingestion/Dockerfile.mq"
    context: str = "../data-ingestion"
    target_service: str = "fargate"

    container_port: int = 5732
    host_port: int = 5732

    #boundary_sgs: list[Output[str]] = [SG.mq.id, SG.bytewax.id, SG.cdc.id]

    boundary_sgs: list[Output[str]] = Field(..., description="List of boundary signal groups")

    class Config:
        arbitrary_types_allowed = True