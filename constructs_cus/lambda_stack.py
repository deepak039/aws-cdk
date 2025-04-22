"""
LambdaStack Class
----------------
A CDK construct that creates an AWS Lambda function with associated IAM role and permissions.

Parameters:
    scope (Construct): The parent construct
    config (dict): Configuration for the Lambda function with structure:
        {
            "name": "function-name",
            "runtime": "python_3_9", # See supported runtimes below
            "handler": "index.handler",
            "code": "./path/to/code",
            "file_type": "zip",
            "policy": ["policy1", "policy2"] # Optional policies to attach
        }
    permissions (dict): IAM permissions to attach to Lambda role
    vpc (ec2.Vpc): Optional VPC to deploy Lambda into 
    security_group (ec2.SecurityGroup): Optional security group for Lambda
    **kwargs: Additional arguments passed to parent construct

Example YAML Configuration:
--------------------------
lambda_function:
  name: my-lambda-function
  runtime: python_3_9  
  handler: index.handler
  code: ./src/lambda
  file_type: zip
  policy:
    - dynamodb_access
    - s3_access

permissions:
  dynamodb_access:
    policies:
      - Effect: Allow
        Action:
          - dynamodb:GetItem
          - dynamodb:PutItem
        Resource: "*"
  s3_access: 
    policies:
      - Effect: Allow
        Action:
          - s3:GetObject
          - s3:PutObject
        Resource: "*"

vpc:
  name: my-vpc
  cidr: 10.0.0.0/16

security_groups:
  - name: lambda-sg
    description: Security group for Lambda function
    vpc: my-vpc
    
Supported Runtimes:
------------------
- nodejs_20, nodejs_18, nodejs_16, nodejs_14, nodejs_12
- python_3_9, python_3_8, python_3_7
- java_11, java_8
- dotnet_6, dotnet_5
- ruby_3_2, ruby_2_7
- go_1_x
"""

from aws_cdk import (
    Stack,
   
)
from aws_cdk import aws_ec2 as ec2, Duration
from constructs import Construct
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy,PolicyStatement
from dependencies.lambda_functions import addDynamoDBRole 
class LambdaStack(Construct):
    def __init__(self, scope: Construct,config:dict,permissions : dict,vpc = None,security_group = None, resources: dict = None, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.name = config['name']

        print(vpc,security_group)
        self.lambda_role = Role(
            self,
            "LambdaExecutionRole",  
            assumed_by=ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole")
            ]
        )

        
      
        self.lambda_role = Role(
            self,
            "AWSLambdaExecutionRole",
            assumed_by=ServicePrincipal("lambda.amazonaws.com"),
        )

        self.lambda_role.add_to_policy(
            PolicyStatement(
                actions=[
                    "ec2:CreateNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface",
                    "ec2:DescribeInstances",
                    "ec2:AttachNetworkInterface"
                ],
                resources=["*"]  
            )
        )
        print(permissions)
        if 'policy' in config:
            for policy_name in config['policy']:
                for policy in permissions[policy_name].policies:

                    self.lambda_role.add_to_policy(
                        policy
                    )


        code = ''

        if config['file_type'] == 'zip':
            code = Code.from_asset(f'parser/configs/external-repo/{config["code"]}') 
        else:
            # logic of container code
            raise NotImplementedError("Container-based Lambda deployment is not yet supported.")
        
        # Prepare environment variables
        environment = config.get('environment', {})


        # Add RDS connection details to environment variables if RDS is specified
        if "rds_instance" in config and config["rds_instance"] in resources.get("rds", {}):
            rds_instance = resources["rds"][config["rds_instance"]]
            print(f"[DEBUG] RDS instance found: {rds_instance.db_endpoint}, port: {rds_instance.db_port}")
            
            environment.update({
                "db_host": rds_instance.db_endpoint,
                "db_port": str(rds_instance.db_port),
            })
        else:
            print("[DEBUG] No RDS instance specified in config, skipping RDS environment variables.")
        
        self.my_lambda = Function(
            self,
            id = config['name'],
            runtime=self._resolve_runtime(config["runtime"]),  
            handler=config["handler"],
            code=code,  
            vpc = vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups = [security_group],
            role=self.lambda_role,
            environment=environment,  # Pass environment variables
            memory_size=config.get("memory_size", 128),
            timeout=Duration.seconds(config.get("timeout", 10)),
        )
        #  # Add logs for debugging
        # print(f"[DEBUG] LambdaStack environment variables:")
        # print(f"[DEBUG] Environment Variables: {environment}")
        # if "db_host" in environment:
        #     print(f"[DEBUG] DB_HOST: {environment['db_host']}")
        # if "db_port" in environment:
        #     print(f"[DEBUG] DB_PORT: {environment['db_port']}")
        # if "db_name" in environment:
        #     print(f"[DEBUG] DB_NAME: {environment['db_name']}")
        # if "db_username" in environment:
        #     print(f"[DEBUG] DB_USERNAME: {environment['db_username']}")
        # if "db_password" in environment:
        #     print(f"[DEBUG] DB_PASSWORD: {environment['db_password']}")
           
    def _resolve_runtime(self, runtime: str):
        runtime_options = {
                "nodejs_18": Runtime.NODEJS_18_X,
                "nodejs_16": Runtime.NODEJS_16_X,
                "nodejs_14": Runtime.NODEJS_14_X,
                "nodejs_12": Runtime.NODEJS_12_X,  
                "nodejs_20": Runtime.NODEJS_20_X,

                "python_3_9": Runtime.PYTHON_3_9,
                "python_3_8": Runtime.PYTHON_3_8,
                "python_3_7": Runtime.PYTHON_3_7,  
                "java_11": Runtime.JAVA_11,
                "java_8": Runtime.JAVA_8,

                "dotnet_6": Runtime.DOTNET_6,
                "dotnet_5": Runtime.DOTNET_CORE_3_1,  
                "ruby_3_2": Runtime.RUBY_3_2,
                "ruby_2_7": Runtime.RUBY_2_7,
                "go_1_x": Runtime.GO_1_X,         
        }
        try:
            return runtime_options[runtime.lower()]
        except KeyError:
            raise ValueError(f"Unsupported runtime: {runtime}. Supported runtimes are: {list(runtime_options.keys())}")

