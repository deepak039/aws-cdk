from aws_cdk.aws_ec2 import CfnEIP, CfnNatGateway
from constructs import Construct
def create_nat_gateways(scope, vpc, nat_config):
    nat_gateways = []
    for i in range(min(nat_config.get("number_of_nat_gateways", 1), len(vpc.public_subnets))):
        nat_eip = CfnEIP(scope, f"NatEIP{i+1}")
        nat_gateway = CfnNatGateway(
            scope,
            f"NatGateway{i+1}",
            allocation_id=nat_eip.attr_allocation_id,
            subnet_id=vpc.public_subnets[i].subnet_id
        )
        nat_gateways.append(nat_gateway)
    return nat_gateways