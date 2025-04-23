from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
)
import os
from constructs import Construct

class ASGStack(Construct):
    def __init__(self, scope: Construct, config: dict, permissions: dict, rds=None, vpc=None, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.name = config['name']

        current_directory = os.path.dirname(__file__)
        user_data_path = os.path.join(current_directory, config.get('user_data_path', 'user_data.sh'))

        # Load User Data script
        user_data_content = ""
        try:
            with open(user_data_path, 'r') as f:
                user_data_content = f.read()
        except FileNotFoundError:
            print(f"Error: '{user_data_path}' file not found.")

        # Inject dynamic RDS database parameters
        if rds:
            rds_instance = rds
            print(f"[DEBUG] RDS instance found: {rds_instance.db_endpoint}, port: {rds_instance.db_port}")

            endpoint = {
                "db_host": rds_instance.db_endpoint,
                "db_port": str(rds_instance.db_port),
            }

            # Replace placeholders in the user data content
            user_data_content = user_data_content.replace("${db_host}", endpoint["db_host"])
            user_data_content = user_data_content.replace("${db_port}", endpoint["db_port"])

        # Create UserData object and populate it with commands
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(user_data_content)

        # IAM Role for the Auto Scaling instances
        asg_role = iam.Role(
            self,
            "ASGInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ],
        )

        # Attach additional policies if specified
        if 'policy' in config:
            for policy_name in config['policy']:
                for policy in permissions[policy_name].policies:
                    asg_role.add_to_policy(policy)

        # Create the Auto Scaling Group
        self.asg = autoscaling.AutoScalingGroup(
            self,
            config['name'],
            vpc=vpc,  # Specify the VPC
            instance_type=ec2.InstanceType(config.get("instance_type", "t2.micro")),  # Default: "t2.micro"
            machine_image=ec2.MachineImage.latest_amazon_linux2(),  # Use Amazon Linux 2
            min_capacity=config.get("min", 1),  # Minimum capacity
            max_capacity=config.get("max", 3),  # Maximum capacity
            desired_capacity=config.get("desired", 2),  # Desired capacity
            role=asg_role,  # IAM Role
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC  # Use public subnets
            ),
            user_data=user_data,  # Add user data to instances
            instance_monitoring=autoscaling.Monitoring.DETAILED,  # Enable detailed monitoring
        )