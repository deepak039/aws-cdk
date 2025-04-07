import os
from .utils.config_loader import ConfigLoader


from constructs_cus.api_gateway_stack import ApiGatewayStack
from constructs_cus.lambda_stack import LambdaStack
from constructs_cus.vpc import VpcStack
from constructs_cus.security_groups import SecurityGroupStack
from constructs_cus.vpc_endpoints import VpcEndpoint

from constructs_cus.dynamodb_stack import DynamoDBStack
from constructs_cus.rds_stack import RDSStack
from constructs_cus.ec2_stack import Ec2Stack
from constructs_cus.asg_stack import ASGStack
from constructs_cus.alb_stack import ALBStack
from constructs_cus.s3bucket_stack import S3BucketStack
from constructs import Construct
import yaml
from aws_cdk import (
    Stack,
    Tags,
)

class Parser(Stack):

    def __init__(self,app : Construct,configName : str):
         super().__init__(app, "ParserStack")
         print(f"[DEBUG] Received configName: {configName}")
         self.resources = {}
         self.configName = configName
         self.app = app
         self.function = {
            'lambdas' : self.createLambda,
            'api_gateways' : self.createApiGateway,
            'vpcs' : self.createVpc,
            'security_groups' : self.createSecurityGroups,
            'vpc_endpoints' : self.createVpcEndpoints,
            'dynamodb': self.createDynamoDBTable,
            'rds_instances': self.createRDSInstance,
            'ec2':self.createEc2,
            'asg':self.createAsg,
            'alb':self.createAlb,
            's3_buckets': self.createS3Bucket, # Added missing mapping for S3 buckets
            'iam_permissions': self.addPermission
         }
         self.run()
         
    
        

    def addPermission(self,config):
          print(f"[DEBUG] Adding permissions for service: {config['service']}")
          self.resources[config['service']].addPolicy(config['policies'])

    def createVpcEndpoints(self,config):
        print(f"[DEBUG] Creating VPC Endpoint with config: {config}")
        vpc_endpoint = VpcEndpoint(scope = self,vpc=self.resources[config['vpc']].vpc,config=config)
        return vpc_endpoint

    def createSecurityGroups(self,config):
        print(f"[DEBUG] Creating Security Group with config: {config}")
        sec_group = SecurityGroupStack(scope = self,vpc = self.resources[config['service']].vpc,config = config)
        return sec_group

    def createVpc(self,config):
        print(f"[DEBUG] Creating VPC with config: {config}")
        vpc_obj = VpcStack(scope = self,config = config)
        return vpc_obj

    def createEc2(self,config):
        print(f"[DEBUG] Creating EC2 instance with config: {config}")
        ec2Instance = Ec2Stack(scope = self,vpc = self.resources[config['vpc']].vpc,security_group = self.resources[config['security_group']].sg,config = config)
        return ec2Instance   
    
    def createAsg(self,config):
        print(f"[DEBUG] Creating Auto Scaling Group with config: {config}")
        asgg = ASGStack(scope = self,vpc = self.resources[config['vpc']].vpc,config = config)
        return asgg   
    
    def createAlb(self,config):
        print(f"[DEBUG] Creating Application Load Balancer with config: {config}")
        alb=ALBStack(scope = self,vpc = self.resources[config['vpc']].vpc, asg=self.resources[config['asg']].asg,config = config)
        return alb
    
    def createLambda(self,config):
        print(f"[DEBUG] Creating Lambda function with config: {config}")
        lambda_func = LambdaStack(scope = self,vpc = self.resources[config['vpc']].vpc,security_group = self.resources[config['security_group']].sg,config = config)
        return lambda_func
        
    
    def createApiGateway(self,config : dict):
        print(f"[DEBUG] Creating/Updating API Gateway with config: {config}")
        if config['name'] not in self.resources:
            gateway = ApiGatewayStack(scope = self,lambda_stack = self.resources[config['lambdaname']],config = config)
            gateway.createEndpoints(self.resources[config['lambdaname']],config['routes'],config['key'])
            return gateway
        else:
            self.resources[config['name']].createEndpoints(self.resources[config['lambdaname']],config['routes'],config['key'])
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

        # # Validate if file_upload.local_path exists
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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)
        
        if not os.path.isabs(self.configName):
            file_path = os.path.join(base_path, "parser", "utils", self.configName)
        else:
            file_path = self.configName

        print(f"[DEBUG] Resolved Config Path: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found at: {file_path}")
        
        print("[DEBUG] Loading configuration file")
        config = ConfigLoader.load_config(file_path)
        
        print(f"[DEBUG] Processing configuration with keys: {list(config.keys())}")
        for key, val in config.items():
            if key not in self.function:
                raise KeyError(f"Unsupported resource type '{key}' in config file")

            print(f"[DEBUG] Processing resource type: {key}")
            for instance in config[key]:
                print(f"[DEBUG] Creating instance: {instance.get('name', 'unnamed')}")
                inst_obj = self.function[key](config = instance)
                if 'name' in instance:
                    self.resources[instance['name']] = inst_obj
                    
                
        
        print("[DEBUG] Parser.run() completed")








