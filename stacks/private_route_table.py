from aws_cdk.aws_ec2 import CfnRouteTable, CfnRoute, CfnSubnetRouteTableAssociation
from aws_cdk.aws_ec2 import CfnRouteTable, CfnRoute, CfnSubnetRouteTableAssociation
from aws_cdk import (
    Stack,
   Tags,
)
from constructs import Construct
class PrivateRoute(Stack):
    def __init__(self, scope: Construct,vpc,config:dict, **kwargs):
        super().__init__(scope, f"{config['name']}-PrivateTableId", **kwargs)
        self.private_route_table = CfnRouteTable(
        self,
        f"{config['name']}-PrivateTable",
        vpc_id=vpc.vpc_id,
        )
        Tags.of(self.private_route_table).add("Name", f"{config['name']}-PrivateTable")

        # Add a default route to the NAT Gateway
        # default_cidr = config.get("route_tables", {}).get("private", {}).get("destination_cidr_block", "0.0.0.0/0")
        # CfnRoute(
        # scope,
        # "PrivateDefaultRoute",
        # route_table_id=private_route_table.ref,
        # destination_cidr_block=default_cidr,  # Use CIDR from the configuration or default to 0.0.0.0/0
        # nat_gateway_id=nat_gateway.ref,  # Attach to the specified NAT Gateway
        # )

    # Associate Private Subnets with the Private Route Table
        for i, private_subnet in enumerate(vpc.private_subnets):
            CfnSubnetRouteTableAssociation(
            self,
            f"{config['name']}-PrivateSubnetRouteAssoc{i}",
            subnet_id=private_subnet.subnet_id,
            route_table_id=self.private_route_table.ref,
            )

