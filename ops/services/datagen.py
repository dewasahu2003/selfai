from .base import FunctionService
from pulumi import Output
from pydantic import Field



class Datagen(FunctionService):
    service_name: str = "datagen" 
    image_name: str = "datagen" + ":latest"
    docker_file: str = "../feature-processing/Dockerfile.datagen"
    context: str = "../feature-processing"
    target_service: str = "lambda"

    container_port: int = 8888
    host_port: int = 8888

   # boundary_sgs: list[str] = [SG.datagen.id]
    

    boundary_sgs: list[Output[str]] = Field(..., description="List of boundary signal groups")

    class Config:
        arbitrary_types_allowed = True