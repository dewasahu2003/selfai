from .base import ContainerService
from pulumi import Output
from pydantic import Field



class Bytewax(ContainerService):
    service_name: str = "bytewax"
    image_name: str = "bytewax" + ":latest"
    docker_file: str = "../feature-processing/Dockerfile.bytewax"
    context: str = "../feature-processing"
    target_service: str = "fargate"

    container_port: int = 5555
    host_port: int = 5555

   # boundary_sgs: list[str] = [SG.bytewax.id, SG.mq.id]

    boundary_sgs: list[Output[str]] = Field(..., description="List of boundary signal groups")

    class Config:
        arbitrary_types_allowed = True