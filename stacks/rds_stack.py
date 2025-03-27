# from aws_cdk import Stack
# from aws_cdk.aws_rds import DatabaseInstance, DatabaseInstanceEngine, Credentials, StorageType
# from aws_cdk.aws_ec2 import SubnetType
# from constructs import Construct


# class RDSStack(Stack):
#     def __init__(self, scope: Construct, vpc, security_group, config: dict, **kwargs):
#         super().__init__(scope, config['name'], **kwargs)

#         self.db_instance = DatabaseInstance(
#             self,
#             f"{config['name']}RDSInstance",
#             database_name=config['database_name'],
#             engine=DatabaseInstanceEngine.mysql(version=config['engine_version']),
#             instance_type=config['instance_type'],
#             vpc=vpc,
#             security_groups=[security_group],
#             vpc_subnets={"subnet_type": SubnetType[config["subnet_type"].upper()]},
#             credentials=Credentials.from_username(config['username'], password=config['password']),
#             storage_type=StorageType[config.get("storage_type", "GP2").upper()],
#             allocated_storage=config.get("allocated_storage", 20),
#             multi_az=config.get("multi_az", False),
#             backup_retention=config.get("backup_retention", 7)  # Retain backup for 7 days by default
#         )