
# import the necessary classes
from aws_cdk import (
    aws_ec2 as ec2,
     Stack
)
from constructs import Construct
import aws_cdk.aws_ec2 as ec2

# class/function/main code definition 
class Ec2Stack(Stack):
    def __init__(self, scope: Construct,config:dict,vpc = None,security_group = None, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.name = config['name']




       
        
        self.instance = ec2.Instance(
            self, "MyEC2Instance",
            instance_type=ec2.InstanceType("t2.micro"),  # Choose your instance type
            machine_image=ec2.MachineImage.latest_amazon_linux(),  # Choose your Amazon Machine Image (AMI)
            vpc=vpc,  # Associate with the VPC
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),  # Specify the subnet
            security_group=security_group,
            
        )
        



