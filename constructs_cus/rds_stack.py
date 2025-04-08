from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    RemovalPolicy,
    Duration,
    SecretValue,
)
from constructs import Construct

class RDSStack(Construct):
    def __init__(self, scope: Construct, resources, config: dict, **kwargs):
        super().__init__(scope, config["name"], **kwargs)

        self.name = config["name"]
        # Retrieve the default VPC from resources
        vpc = resources[config["vpc"]].vpc

        # Map removal policies for lifecycle
        removal_policy_map = {
            "DESTROY": RemovalPolicy.DESTROY,
            "RETAIN": RemovalPolicy.RETAIN,
            "SNAPSHOT": RemovalPolicy.SNAPSHOT,
        }

        # Create a DB Subnet Group covering private subnets in at least 2 AZs
        self.subnet_group = rds.SubnetGroup(
            self,
            f"{config['name']}DBSubnetGroup",
            description="Private Subnets for RDS",
            vpc=vpc,
            removal_policy=removal_policy_map.get(config["removal_policy"].upper(), RemovalPolicy.DESTROY),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        self.db_instance = rds.DatabaseInstance(
            self,
            f"{config['name']}DBInstance",
            engine=self._resolve_db_engine(config["engine"]),
            instance_type=ec2.InstanceType(config["instance_type"]),
            allocated_storage=config["allocated_storage"],
            vpc=vpc,
            security_groups=[resources[config["security_group"]].sg],
            database_name=config.get("database_name"),
            backup_retention=Duration.days(config["backup_retention_days"]),
            deletion_protection=config["deletion_protection"],
            multi_az=config["multi_az"],
            publicly_accessible=config["publicly_accessible"],
            storage_encrypted=config["storage_encrypted"],
            credentials=rds.Credentials.from_username(
                config["master_username"],
                password=SecretValue.unsafe_plain_text(config["master_password"]),
            ),
            subnet_group=self.subnet_group,
            removal_policy=removal_policy_map.get(config["removal_policy"].upper(), RemovalPolicy.DESTROY),
            cloudwatch_logs_exports=config["cloudwatch_logs_exports"],
        )

    def _resolve_db_engine(self, engine: str):
        """
        Automatically use the latest supported version for each database engine.
        """
        engine_map = {
            "mysql": rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0
            ),
            "postgres": rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_13
            ),
            "maria_db": rds.DatabaseInstanceEngine.maria_db(
                version=rds.MariaDbEngineVersion.VER_10_11
            ),
            "oracle-se2": rds.DatabaseInstanceEngine.oracle_se2(
                version=rds.OracleEngineVersion.VER_19_0_0_0_2023_10_R1
            ),
        }
        try:
            return engine_map[engine.lower()]
        except KeyError:
            raise ValueError(
                f"Unsupported database engine: {engine}. Supported engines are: {list(engine_map.keys())}."
            )