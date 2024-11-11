from .base import FunctionService
from pulumi import Output
from pydantic import Field



class Inference(FunctionService):
    service_name: str = "inference"
    image_name: str = "inference" + ":latest"
    docker_file: str = "../inference/Dockerfile.inference"
    context: str = "../inference/"
    target_service: str = "lambda"

    container_port: int = 4444
    host_port: int = 4444

#    boundary_sgs: list[str] = [SG.inference.id]

    boundary_sgs: list[Output[str]] = Field(..., description="List of boundary signal groups")

    class Config:
        arbitrary_types_allowed = True