import pulumi_aws as aws
from security.vpc import VPC


class SecurityGroup:
    # Crawler Lambda (Private Subnet)
    crawler = aws.ec2.SecurityGroup(
        resource_name="selfai-crawler-sg",
        description="Security group for Crawler Lambda",
        vpc_id=VPC.vpc.id,
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["10.0.1.0/24"],  # Adjust this to your VPC CIDR
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
    )

    # CDC Fargate Container (Private Subnet)
    cdc = aws.ec2.SecurityGroup(
        resource_name="selfai-cdc-sg",
        description="Security group for CDC Fargate container",
        vpc_id=VPC.vpc.id,
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=0,
                to_port=65535,
                cidr_blocks=["10.0.2.0/24"],  # Adjust to your private subnet CIDR
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="tcp",
                from_port=27017,
                to_port=27017,
                cidr_blocks=["0.0.0.0/0"],  # Allow outbound to MongoDB Atlas
            ),
            aws.ec2.SecurityGroupEgressArgs(
                protocol="tcp",
                from_port=5672,
                to_port=5672,
                cidr_blocks=["10.0.2.0/24"],  # Allow outbound to RabbitMQ
            ),
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],  # Allow all other outbound traffic
            ),
        ],
    )

    # RabbitMQ Fargate Container (Private Subnet)
    mq = aws.ec2.SecurityGroup(
        resource_name="selfai-mq-sg",
        description="Security group for RabbitMQ Fargate container",
        vpc_id=VPC.vpc.id,
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=5672,
                to_port=5672,
                cidr_blocks=["10.0.2.0/24"],  # Adjust to your private subnet CIDR
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
    )

    # Bytewax Fargate Container (Private Subnet)
    bytewax = aws.ec2.SecurityGroup(
        resource_name="selfai-bytewax-sg",
        description="Security group for Bytewax Fargate container",
        vpc_id=VPC.vpc.id,
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=0,
                to_port=65535,
                cidr_blocks=["10.0.2.0/24"],  # Adjust to your private subnet CIDR
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
    )

    # Datagen Lambda (Private Subnet)
    datagen = aws.ec2.SecurityGroup(
        resource_name="selfai-datagen-sg",
        description="Security group for Datagen Lambda",
        vpc_id=VPC.vpc.id,
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["10.0.1.0/24"],  # Adjust this to your VPC CIDR
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
    )

    # Inference Lambda (Private Subnet)
    inference = aws.ec2.SecurityGroup(
        resource_name="selfai-inference-sg",
        description="Security group for Inference Lambda",
        vpc_id=VPC.vpc.id,
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["10.0.1.0/24"],  # Adjust this to your VPC CIDR
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
    )

    # API Gateway (Public Subnet)
    apigateway = aws.ec2.SecurityGroup(
        resource_name="selfai-apigateway-sg",
        description="Security group for API Gateway",
        vpc_id=VPC.vpc.id,
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["0.0.0.0/0"],  # Allow HTTPS from anywhere
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],  # Allow all outbound traffic
            ),
        ],
    )
