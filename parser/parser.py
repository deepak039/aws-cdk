import os
from collections import defaultdict
from .utils.config_loader import ConfigLoader
from .utils.merge_config import MergeConfig
from constructs_cus.policy_stack import PolicyStack
from constructs_cus.api_gateway_stack import ApiGatewayStack
from constructs_cus.lambda_stack import LambdaStack
from constructs_cus.vpc import VpcStack
from constructs_cus.security_groups import SecurityGroupStack
from constructs_cus.vpc_endpoints import  VpcEndpoint
from constructs_cus.dynamodb_stack import DynamoDBStack
from constructs_cus.rds_stack import RDSStack
from constructs_cus.ec2_stack import Ec2Stack
from constructs_cus.asg_stack import ASGStack
from constructs_cus.alb_stack import ALBStack
from constructs_cus.s3bucket_stack import S3BucketStack
from constructs_cus.eks_stack import EksStack

from constructs import Construct
import yaml
from aws_cdk import (
    Stack,
    Tags,
)

class Parser(Stack):

    def __init__(self,app : Construct,configName : str, defaultConfigPath: str):
         super().__init__(app, "ParserStack")
         print(f"[DEBUG] Received configName: {configName}")
         self.resources = defaultdict(dict)
         self.configName = configName
         self.defaultConfigPath = defaultConfigPath
         self.app = app
         self.function = {
            'lambdas' : self.createLambda,
            'api_gateways' : self.createApiGateway,
            'vpcs' : self.createVpc,
            'security_groups' : self.createSecurityGroups,
            'vpc_endpoints' : self.createVpcEndpoints,
            'dynamodb': self.createDynamoDBTable,
            'rds': self.createRDSInstance,
            'ec2':self.createEc2,
            'asg':self.createAsg,
            'alb':self.createAlb,
            's3_buckets': self.createS3Bucket,
            'iam_permissions': self.addPolicy,
            'eks': self.createEksCluster
         }
         self.run()
         
    
        
    
    def addPolicy(self,config):
          print(f"[DEBUG] Creating policies : {config['name']}")
          policy_stack = PolicyStack(scope=self, config=config)
          return policy_stack

    def createVpcEndpoints(self,config):
        print(f"[DEBUG] Creating VPC Endpoint with config: {config}")
        vpc_endpoint = VpcEndpoint(scope = self,vpc=self.resources['vpcs'][config['vpc']].vpc,config=config)
        return vpc_endpoint

    def createSecurityGroups(self,config):
        print(f"[DEBUG] Creating Security Group with config: {config}")
        sec_group = SecurityGroupStack(scope = self,vpc = self.resources['vpcs'][config['service']].vpc,config = config)
        return sec_group

    def createVpc(self,config):
        print(f"[DEBUG] Creating VPC with config: {config}")
        vpc_obj = VpcStack(scope = self,config = config)
        return vpc_obj

    def createEc2(self,config):
        print(f"[DEBUG] Creating EC2 instance with config: {config}")
        ec2Instance = Ec2Stack(scope = self,vpc = self.resources['vpcs'][config['vpc']].vpc,security_group = self.resources['security_groups'][config['security_group']].sg,config = config,permissions = self.resources['iam_permissions'])
        return ec2Instance   
    
    def createAsg(self,config):
        print(f"[DEBUG] Creating Auto Scaling Group with config: {config}")
        asgg = ASGStack(scope = self,vpc = self.resources['vpcs'][config['vpc']].vpc,config = config,permissions = self.resources['iam_permissions'])
        return asgg   
    
    def createEksCluster(self, config):
        print(f"[DEBUG] Creating EKS cluster with config: {config}")
        eks = EksStack(scope = self, vpc = self.resources['vpcs'][config['vpc']].vpc, config = config)
        return eks
    
    def createAlb(self,config):
        print(f"[DEBUG] Creating Application Load Balancer with config: {config}")
        alb=ALBStack(scope = self,vpc = self.resources['vpcs'][config['vpc']].vpc, asg=self.resources['asg'][config['asg']].asg,config = config)
        return alb
    
    def createLambda(self,config):
        print(f"[DEBUG] Creating Lambda function with config: {config}")
        lambda_func = LambdaStack(scope = self,vpc = self.resources['vpcs'][config['vpc']].vpc,security_group = self.resources['security_groups'][config['security_group']].sg,config = config,permissions = self.resources['iam_permissions'])
        return lambda_func
        
    
    def createApiGateway(self,config : dict):
        print(f"[DEBUG] Creating/Updating API Gateway with config: {config}")
        if config['name'] not in self.resources:
            gateway = ApiGatewayStack(scope = self,lambda_stack = self.resources[config['lambdaname']],config = config)
            gateway.createEndpoints(self.resources['lambdas'][config['lambdaname']],config['routes'],config['key'])
            return gateway
        else:
            self.resources['api_gateways'][config['name']].createEndpoints(self.resources['lambdas'][config['lambdaname']],config['routes'],config['key'])
            return self.resources[config['name']]

    def createDynamoDBTable(self, config):
        print(f"[DEBUG] Creating DynamoDB table with config: {config}")
        dynamo_db_stack = DynamoDBStack(scope=self, config=config)
        return dynamo_db_stack

    def createRDSInstance(self, config):
        print(f"[DEBUG] Creating RDS instance with config: {config}")
        rds_stack = RDSStack(
            scope=self, 
            resources=self.resources, 
            config=config
        )
        return rds_stack

    def createS3Bucket(self, config):
        print(f"[DEBUG] Creating S3 bucket with config: {config}")
        required_keys = ["name", "bucket_name", "file_upload"]
        # for key in required_keys:
        #     if key not in config:
        #         raise KeyError(f"Missing required key '{key}' in S3 bucket configuration. Check your config.yaml: {config}")

        # Validate if file_upload.local_path exists
        # local_path = config["file_upload"]["local_path"]
        # if not os.path.exists(local_path):
        #     raise FileNotFoundError(f"Local path '{local_path}' not found for S3 bucket deployment")

        # Create and return the bucket stack
        s3_bucket_stack = S3BucketStack(
            scope=self,
            id=config["name"],
            config=config
        )
        return s3_bucket_stack

    def run(self):
        print("[DEBUG] Starting Parser.run()")
        base_dir = os.path.dirname(os.path.abspath(__file__))

        user_config_path = self.configName if os.path.isabs(self.configName) else os.path.join(base_dir, "configs", self.configName)
        default_config_path = self.defaultConfigPath if os.path.isabs(self.defaultConfigPath) else os.path.join(base_dir, "configs", self.defaultConfigPath)
        iam_config_path =  os.path.join(base_dir, "configs", "iam_config.yaml")
        if not os.path.exists(user_config_path):
            raise FileNotFoundError(f"User configuration file not found: {user_config_path}")
        if not os.path.exists(default_config_path):
            raise FileNotFoundError(f"Default configuration file not found: {default_config_path}")

        # Load and merge configurations
        merged_config = MergeConfig.load_and_merge(user_config_path, default_config_path)
        iam_config = ConfigLoader.load_config(iam_config_path)
        print(f"[DEBUG] Processing configuration with keys: {list(merged_config.keys())}")
        
        # adding permissions in iam file
        for key, val in iam_config.items():
            for instance in val:
                inst_obj = self.function[key](config=instance)
                self.resources[key][instance['name']] = inst_obj

        for key, val in merged_config.items():
            if key not in self.function:
                raise KeyError(f"Unsupported resource type '{key}' in config file")
            for instance in val:
                inst_obj = self.function[key](config=instance)
                self.resources[key][instance['name']] = inst_obj

        print("[DEBUG] Parser.run() completed")

