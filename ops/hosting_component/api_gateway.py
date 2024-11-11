import pulumi_aws as aws
from utils.logging import get_logger

logger = get_logger(__name__)


# Create the API Gateway REST API
class APIGateway:
    def __init__(self) -> None:

        self.rest_api = aws.apigateway.RestApi(
            "inferenceApi", description="API Gateway for Inference Service"
        )
        self.lambdas = []

    # Create the deployment and stage
    def add_lambdas(self, single_lambda_fn: tuple):
        self.lambdas.append(single_lambda_fn)

    def define_api_gateway(self):
        if not self.lambdas:
            logger.info("No lambdas to deploy.")
            return
        for lambda_name, lambda_invoke_arn in self.lambdas:
            resource = aws.apigateway.Resource(
                lambda_name,
                rest_api=self.rest_api.id,
                parent_id=self.rest_api.root_resource_id,
                path_part=lambda_name,  # e.g., /function1, /function2, etc.
            )
            # Create the POST method for the resource
            method = aws.apigateway.Method(
                f"apiMethod-{lambda_name}",
                rest_api=self.rest_api.id,
                resource_id=resource.id,
                http_method="POST",
                authorization="NONE",
            )

            # Create the Lambda integration
            lambda_integration = aws.apigateway.Integration(
                f"lambdaIntegration-{lambda_name}",
                rest_api=self.rest_api.id,
                resource_id=resource.id,
                http_method=method.http_method,
                # integration_http_method="POST",
                type="AWS_PROXY",
                uri=lambda_invoke_arn,
            )

    def deploy_apigateway(self):
        self.define_api_gateway()
        deployment = aws.apigateway.Deployment(
            "deployment",
            rest_api=self.rest_api.id,
            description="Deployment for the inference service",
        )

        stage = aws.apigateway.Stage(
            "stage",
            rest_api=self.rest_api.id,
            deployment=deployment.id,
            stage_name="prod",
        )

        # Export the API Gateway URL
        # pulumi.export(
        #     "api_gateway_url", pulumi.Output.concat(deployment.invoke_url, "prod")
        # )
