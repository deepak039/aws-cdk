import os
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    Stack
)
from constructs import Construct
from aws_cdk.aws_iam import PolicyStatement

class Ec2Stack(Construct):
    def __init__(self, scope: Construct, config: dict, vpc=None, security_group=None, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.name = config['name']

        # Load user data from a .sh file located in the same directory
        current_directory = os.path.dirname(__file__)
        user_data_path = os.path.join(current_directory, config.get('user_data_path', ''))
        ec2_role = iam.Role(
            self, 
            "Ec2Instance",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        user_data_content = ""
        
        if user_data_path:
            try:
                # Open the file and read user data content
                with open(user_data_path, 'r') as f:
                    user_data_content = f.read()
            except FileNotFoundError:
                print(f"Error: '{user_data_path}' file not found.")

        # Create the UserData object and add content
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(user_data_content)

        # Define the EC2 instance
        self.instance = ec2.Instance(
            self, 
            config['name'],
            instance_type=ec2.InstanceType(config.get('instance_type', 't2.micro')),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_group=security_group,
            user_data=user_data,
            role=ec2_role,
            instance_monitoring=ec2.Monitoring.DETAILED
        )

    def addPolicy(self, config):
        ec2_role = self.instance.role
        
        if 'policies' in config:
            for policy in config['policies']:
                ec2_role.add_to_policy(
                    PolicyStatement(
                        actions=policy['action'],
                        resources=["*"]
                    )
                )
