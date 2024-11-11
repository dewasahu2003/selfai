from typing import List
import pulumi
import pulumi_aws as aws
from security.vpc import VPC
from services.base import BaseService
import json
from .api_gateway import APIGateway
from utils.logging import get_logger

logger = get_logger(__name__)


class LambdaService:
    def __init__(self) -> None:
        self.lambda_functions: List[BaseService] = []

    def add_lambda(self, function: BaseService):
        logger.info(f"Adding Lambda function: {function.service_name}")
        self.lambda_functions.append(function)

    def remove_lambda(self, function: BaseService):
        logger.info(f"Removing Lambda function: {function.service_name}")
        self.lambda_functions.remove(function)

    # def dock_and_push(self, service: BaseService):
    #     try:
    #         logger.info(f"Creating ECR repository for service: {service.service_name}")
    #         ecr_repo = aws.ecr.Repository(service.service_name)

    #         logger.info("Retrieving ECR authorization token")
    #         token = aws.ecr.get_authorization_token()

    #         docker_image = docker.Image(
    #             skip_push=False,
    #             resource_name=service.service_name,
    #             build=docker.DockerBuildArgs(
    #                 context=service.context,
    #                 dockerfile=service.docker_file,
    #                 platform="linux/amd64",
    #             ),
    #             image_name=ecr_repo.repository_url.apply(lambda url: f"{url}:latest"),
    #             registry={
    #                 "username": token.user_name,
    #                 "password": token.password,
    #                 "server": ecr_repo.repository_url,
    #             },
    #         )
    #         logger.info(f"ECR repository URL: {ecr_repo.repository_url}")
    #         return docker_image.image_name

    #     except Exception as e:
    #         logger.error(
    #             f"Failed to dock and push image for {service.service_name}: {e}"
    #         )
    #         raise
    def __get_image_url(self, service_name) -> str:
        logger.info("Getting repository URL")
        ecr_repo = aws.ecr.get_repository(name=service_name)
        return ecr_repo.repository_url + ":latest"

    def deploy_single_lambda(self, service: BaseService):
        try:
            logger.info(f"Deploying {service.service_name} to AWS Lambda")
            image_uri = self.__get_image_url(service.service_name)

            # Create a Lambda role with necessary permissions
            logger.info(
                f"Creating IAM role for Lambda function: {service.service_name}"
            )
            lambda_role = aws.iam.Role(
                f"selfai-lambda-role-{service.service_name}",
                assume_role_policy=pulumi.Output.all().apply(
                    lambda _: json.dumps(
                        {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Action": "sts:AssumeRole",
                                    "Principal": {"Service": "lambda.amazonaws.com"},
                                    "Effect": "Allow",
                                    "Sid": "",
                                }
                            ],
                        }
                    )
                ),
            )
            lambda_policy = aws.iam.RolePolicyAttachment(
                f"selfai-lambda-policy-{service.service_name}",
                role=lambda_role.name,
                policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            )

            function_name = f"{service.service_name}Function"

            # Deploy the Lambda function using the ECR image
            logger.info(f"Creating Lambda function: {function_name}")
            lambda_function = aws.lambda_.Function(
                function_name,
                opts=pulumi.ResourceOptions(depends_on=[lambda_policy]),
                package_type="Image",
                role=lambda_role.arn,
                image_uri=image_uri,
                timeout=300,
                vpc_config=aws.lambda_.FunctionVpcConfigArgs(
                    subnet_ids=[VPC.private_subnet.id],
                    security_group_ids=service.boundary_sgs,
                ),
            )
            # pulumi.export(f"{service.service_name}-lambda-name", function_name)
            # pulumi.export(f"{service.service_name}-lambda-arn", lambda_function.arn)

            return (
                service.service_name,
                function_name,
                lambda_function.invoke_arn,
            )

        except Exception as e:
            logger.error(
                f"Failed to deploy Lambda function {service.service_name}: {e}"
            )
            raise

    def deploy_all_lambda_with_as_api(self):
        apigateway = APIGateway()
        for fun in self.lambda_functions:
            try:
                service_name, name, arn = self.deploy_single_lambda(service=fun)
                logger.info(
                    f"Successfully deployed {service_name} with ARN {arn.apply(lambda x: x)}"
                )

                apigateway.add_lambdas((name, arn))

            except Exception as e:
                logger.error(
                    f"Failed to deploy Lambda function {fun.service_name}: {e}"
                )

        logger.info("Deploying API Gateway")
        apigateway.deploy_apigateway()
