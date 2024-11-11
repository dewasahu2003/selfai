from .base import ContainerService
from pulumi import Output
from pydantic import Field


class CDCService(ContainerService):
    service_name: str = "cdc"
    image_name: str = "cdc" + ":latest"
    docker_file: str = "../data-ingestion/Dockerfile.cdc"
    context: str = "../data-ingestion"
    target_service: str = "fargate"

    container_port: int = 3434
    host_port: int = 3434

   # boundary_sgs: list[str] = [SG.cdc.id, SG.mq.id]
   

    boundary_sgs: list[Output[str]] = Field(..., description="List of boundary signal groups")

    class Config:
        arbitrary_types_allowed = True