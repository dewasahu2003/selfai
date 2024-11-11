import pulumi_aws as aws


class VPC:

    vpc = aws.ec2.Vpc(
        "my_vpc",
        cidr_block="10.0.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags={"Name": "selfai-vpc"},
    )

    public_subnet = aws.ec2.Subnet(
        "public_subnet",
        vpc_id=vpc.id,
        cidr_block="10.0.1.0/24",
        map_public_ip_on_launch=True,
        tags={"Name": "selfai-public-subnet"},
    )

    private_subnet = aws.ec2.Subnet(
        "private_subnet",
        vpc_id=vpc.id,
        cidr_block="10.0.2.0/24",
        tags={"Name": "selfai-private-subnet"},
    )

    # 4. Create an Internet Gateway
    internet_gateway = aws.ec2.InternetGateway(
        "selfai-internet-gateway", vpc_id=vpc.id, tags={"Name": "main"}
    )

    # Route table for public subnet
    public_route_table = aws.ec2.RouteTable(
        "public_route_table",
        vpc_id=vpc.id,
        routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": internet_gateway.id}],
        tags={"Name": "public_route_table"},
    )

    # Associate the public subnet with the route table
    public_route_table_assoc = aws.ec2.RouteTableAssociation(
        "public_route_table_assoc",
        subnet_id=public_subnet.id,
        route_table_id=public_route_table.id,
    )

    # 5. Create a NAT Gateway
    # Allocate an Elastic IP for the NAT Gateway
    elastic_ip = aws.ec2.Eip("selfai-ip", vpc=True)

    nat_gateway = aws.ec2.NatGateway(
        "selfai-nat-gateway",
        subnet_id=public_subnet.id,
        allocation_id=elastic_ip.id,
        tags={"Name": "selfai"},
    )

    # Route table for private subnet
    private_route_table = aws.ec2.RouteTable(
        "private_route_table",
        vpc_id=vpc.id,
        routes=[{"cidr_block": "0.0.0.0/0", "nat_gateway_id": nat_gateway.id}],
        tags={"Name": "private_route_table"},
    )

    # Associate the private subnet with the route table
    private_route_table_assoc = aws.ec2.RouteTableAssociation(
        "private_route_table_assoc",
        subnet_id=private_subnet.id,
        route_table_id=private_route_table.id,
    )
