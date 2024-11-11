from typing import List
import pulumi
import pulumi_aws as aws
from services.base import BaseService
from security.vpc import VPC
from security.sg import SecurityGroup as SG
from utils.logging import get_logger

logger = get_logger(__name__)

class FargateService:
    def __init__(self) -> None:
        logger.info("Initializing FargateService")
        self.ecs_cluster = aws.ecs.Cluster(resource_name="selfai-cluster")
        self.services: List[BaseService] = []

    @property
    def get_task_execution_role(self):
        logger.info("Creating task execution role")
        task_execution_role = aws.iam.Role(
            f"selfai-fargate-execution-role",
            assume_role_policy="""{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ecs-tasks.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }""",
        )
        return task_execution_role

    @property
    def execution_role_policy(self):
        logger.info("Attaching execution role policy")
        ecs_task_execution_role_policy = aws.iam.RolePolicyAttachment(
            "selfai-fargate-execution-role-policy",
            role=self.get_task_execution_role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
        )
        return ecs_task_execution_role_policy

    def add_service(self, service: BaseService):
        logger.info(f"Adding service: {service.service_name}")
        self.services.append(service)

    def remove_service(self, service: BaseService):
        logger.info(f"Removing service: {service.service_name}")
        self.services.remove(service)

    def __get_image_url(self, service_name) -> str:
        logger.info("Getting repository URL")
        ecr_repo = aws.ecr.get_repository(name=service_name)
        logger.info(f"ECR repository URL: {ecr_repo.repository_url}")
        return ecr_repo.repository_url + ":latest"

    def create_task_definitions(self):
        logger.info("Creating task definitions")
        _container_definitions = [
            {
                "name": service.service_name,
                "image": self.__get_image_url(service.service_name),
                "essential": True,
                "portMappings": [
                    {
                        "containerPort": service.container_port,
                        "hostPort": service.host_port,
                    }
                ],
            }
            for service in self.services
        ]

        _task_definition = aws.ecs.TaskDefinition(
            "selfai-task-def",
            family="selfai-task-family",
            cpu="256",
            memory="512",
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            execution_role_arn=self.get_task_execution_role.arn,
            container_definitions=pulumi.Output.json_dumps(_container_definitions),
        )
        return _task_definition

    # def dock_and_push(self, service: BaseService):
    #     try:
    #         logger.info(
    #             f"Docking and pushing image for service: {service.service_name}"
    #         )
    #         _repo = aws.ecr.Repository(resource_name=service.service_name)
    #         _token = aws.ecr.get_authorization_token()

    #         _img = docker.Image(
    #             resource_name=service.service_name,
    #             build=docker.DockerBuildArgs(
    #                 context=service.context,
    #                 dockerfile=service.docker_file,
    #                 platform="linux/amd64",
    #             ),
    #             skip_push=False,
    #             image_name=_repo.repository_url.apply(lambda url: f"{url}:latest"),
    #             registry={
    #                 "username": _token.user_name,
    #                 "password": _token.password,
    #                 "server": _repo.repository_url,
    #             },
    #         )
    #         logger.info(f"Image pushed: {_img.image_name}")
    #         return _img.image_name

    #     except Exception as e:
    #         logger.error(
    #             f"Failed to dock and push image for {service.service_name}: {e}"
    #         )
    #         raise

    def create_fargate_services(self, task_def: aws.ecs.TaskDefinition):
        logger.info("Creating Fargate service")
        sg=[]
        for s in self.services:
            sg.extend(s.boundary_sgs)
        fargate_service = aws.ecs.Service(
            "selfai_ecs_service",
            cluster=self.ecs_cluster.arn,
            task_definition=task_def.arn,
            desired_count=1,
            network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
                assign_public_ip=True,
                subnets=[VPC.private_subnet.id],
                security_groups=sg,
            ),
            launch_type="FARGATE",
        )
        logger.info(f"Fargate service created: {fargate_service.id}")
        return fargate_service

    def deploy_all(self):
        logger.info("Deploying all services")
        for service in self.services:
            try:
                service.image_name = service.image_name
            except Exception as e:
                logger.error(
                    f"Failed to dock and push for service {service.service_name}: {e}"
                )

        _task_def = self.create_task_definitions()
        _fargate_service = self.create_fargate_services(task_def=_task_def)

        # pulumi.export("cluster_arn", self.ecs_cluster.arn)
        # pulumi.export("task_definition_arn", _task_def.arn)
        # pulumi.export("services", [s.service_name for s in self.services])
        # pulumi.export("fargate_service_arn", _fargate_service.arn)
