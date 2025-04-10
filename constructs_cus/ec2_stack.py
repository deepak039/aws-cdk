import os
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    Stack
)
from constructs import Construct
from aws_cdk.aws_iam import PolicyStatement

# Example YAML configuration:
"""
ec2:
  name: my-ec2-instance                    # Required: Name for the EC2 instance
  instance_type: t2.micro                  # Optional: EC2 instance type (default: t2.micro)
  volume_size: 20                          # Optional: EBS volume size in GB (default: 8)
  volume_type: gp3                         # Optional: EBS volume type (default: gp3)
  iops: 3000                              # Optional: IOPS for io1/io2 volumes
  key_name: my-key-pair                   # Optional: SSH key pair name
  availability_zone: us-east-1a           # Optional: AZ to launch instance in
  termination_protection: false           # Optional: Enable/disable termination protection
  instance_name: my-custom-name           # Optional: Custom name tag for instance
  user_data_path: scripts/startup.sh      # Optional: Path to user data script
  policy:                                 # Optional: List of IAM policies to attach
    - s3_read_only
    - cloudwatch_full_access
"""

class Ec2Stack(Construct):
    def __init__(self, scope: Construct, config: dict,permissions : dict, vpc=None, security_group=None, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.name = config['name']

        
        current_directory = os.path.dirname(__file__)
        user_data_path = os.path.join(current_directory, config.get('user_data_path', ''))
        self.ec2_role = iam.Role(
            self, 
            "Ec2Instance",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        print(permissions)
        if 'policy' in config:
            for policy_name in config['policy']:
                for policy in permissions[policy_name].policies:

                    self.ec2_role.add_to_policy(
                        policy
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
            instance_type=ec2.InstanceType(config.get('instance_type', 't2.micro')), # Example: 't2.micro', 't2.small', 't3.medium'
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_group=security_group,
            user_data=user_data,
            role=self.ec2_role,
            instance_monitoring=ec2.Monitoring.DETAILED,
            key_name=config.get('key_name', None),  # Example: 'my-key-pair'
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=config.get('volume_size', 8),  # Example: 20 for 20GB
                        volume_type=ec2.EbsDeviceVolumeType(config.get('volume_type', 'gp3')),  # Example: 'gp2', 'gp3', 'io1'
                        iops=config.get('iops', None),  # Example: 3000 for io1/io2 volumes
                    )
                )
            ],
            availability_zone=config.get('availability_zone', None),  # Example: 'us-east-1a'
            disable_api_termination=config.get('termination_protection', False),  # Example: True to enable termination protection
            instance_name=config.get('instance_name', config['name'])  # Example: 'my-instance'
        )

    
