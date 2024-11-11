from pydantic import BaseModel
from abc import ABC
from pulumi import Output


class BaseService(ABC, BaseModel):
    service_name: str
    docker_file: str
    context: str
    target_service: str

    container_port: int
    host_port: int

    boundary_sgs: list[str]

    class Config:
        arbitrary_types_allowed = True


class ContainerService(BaseService):
    image_name: str
    pass


class FunctionService(BaseService):
    image_name: str
    pass


# BaseService.model_rebuild()
# ContainerService.model_rebuild()
# FuntionService.model_rebuild()
