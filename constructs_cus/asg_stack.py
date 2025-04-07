from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
)
import os
from constructs import Construct

class ASGStack(Construct):
    def __init__(self, scope: Construct,config:dict,vpc = None, **kwargs) :
        super().__init__(scope,config['name'],  **kwargs)
        self.name = config['name']

        # Lookup VPC
       

        # IAM Role for EC2 instances
        # role = iam.Role(
        #     self, "ASGInstanceRole",
        #     assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        #     managed_policies=[
        #         iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
        #     ]
        # )

             # IAM Role for EC2 instances
        current_directory = os.path.dirname(__file__)
        user_data_path = os.path.join(current_directory, config.get('user_data_path', ''))

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
        asg_role = iam.Role(
            self, 
            "ASGInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ],
        )

        
        self.asg = autoscaling.AutoScalingGroup(
            self, config['name'],
              vpc=vpc,  # Specify the VPC where instances should be launched
            instance_type=ec2.InstanceType("t2.micro"),  # Instance type
            machine_image=ec2.MachineImage.latest_amazon_linux2(),  # Latest Amazon Linux 2
            min_capacity=config.get("min", 1),  # Use minimum capacity
            max_capacity=config.get("max", 3),  # Use maximum capacity
            desired_capacity=config.get("desired", 2),  # Use desired capacity
            role=asg_role,  # IAM Role is attached to instances
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS  # Restrict to private subnets
            ),
            user_data=user_data,
            
        )
       
    
  
       

       