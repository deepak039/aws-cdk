from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
)
from constructs import Construct

class ASGStack(Stack):
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
        asg_role = iam.Role(
            self, 
            "ASGInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ],
        )

        user_data_path = config.get("path")
        user_data_script = self._load_user_data(user_data_path)

        # Auto Scaling Group
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
            
        )
        if user_data_script:
            asg.add_user_data(user_data_script)

        # User data (optional): Install Node.js app on instance start
        # asg.add_user_data("""
        #     #!/bin/bash
        #     yum update -y
        #     curl -sL https://rpm.nodesource.com/setup_16.x | bash -
        #     yum install nodejs -y
        #     echo 'const http = require("http"); const server = http.createServer((req, res) => { res.writeHead(200, {"Content-Type": "text/plain"}); res.end("Hello from Node.js"); }); server.listen(3000);' > /home/ec2-user/app.js
        #     node /home/ec2-user/app.js &
        # """)

        # Create an ALB
    
    def _load_user_data(self, path: str) -> str:
        """Load the user data script from the given file path."""
        if not path or not os.path.exists(path):
            raise FileNotFoundError(f"User data script not found at path: {path}")
        with open(path, 'r') as file:
            return file.read()    
       

       