from aws_cdk.aws_ec2 import CfnRouteTable, CfnRoute, CfnSubnetRouteTableAssociation
from aws_cdk import (
    Stack,
   
)
from constructs import Construct
class PublicRoute(Stack):
    def __init__(self, scope: Construct,vpc,config:dict, **kwargs):
        super().__init__(scope, f"{config['name']}PublicTableId", **kwargs)
        self.public_route_table = CfnRouteTable(
        self,
        f"{config['name']}PublicTable",
        vpc_id=vpc.vpc_id,
        )

    # Add a default route to the Internet Gateway
        CfnRoute(
        self,
        f"{config['name']}PublicDefaultRoute",
        route_table_id=self.public_route_table.ref,
        destination_cidr_block="0.0.0.0/0",  # Internet-bound traffic
        gateway_id=vpc.internet_gateway_id,  # Attach Internet Gateway
        )

    # Associate Public Subnets with the Public Route Table
        for i, public_subnet in enumerate(vpc.public_subnets):
            CfnSubnetRouteTableAssociation(
            self,
            f"{config['name']}PublicSubnetRouteAssoc{i}",
            subnet_id=public_subnet.subnet_id,
            route_table_id=self.public_route_table.ref,
            )

