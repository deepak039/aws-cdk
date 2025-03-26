from aws_cdk import Stack
from aws_cdk.aws_dynamodb import Table, AttributeType, BillingMode
from constructs import Construct


class DynamoDBStack(Stack):
    def __init__(self, scope: Construct, config: dict, **kwargs):
        super().__init__(scope, config['name'], **kwargs)

        self.table = Table(
            self,
            f"{config['name']}Table",
            table_name=config['name'],
            partition_key={
                "name": config['partition_key']['name'], 
                "type": AttributeType[config['partition_key']['type'].upper()]
            },
            sort_key={
                "name": config['sort_key']['name'], 
                "type": AttributeType[config['sort_key']['type'].upper()]
            } if 'sort_key' in config else None,
            billing_mode=BillingMode.PAY_PER_REQUEST if config["billing_mode"] == "PAY_PER_REQUEST" else BillingMode.PROVISIONED,
            read_capacity=config.get("read_capacity", 5) if config["billing_mode"] == "PROVISIONED" else None,
            write_capacity=config.get("write_capacity", 5) if config["billing_mode"] == "PROVISIONED" else None,
            point_in_time_recovery=config.get("enable_point_in_time_recovery", False)  # Enable Point-in-Time Recovery if specified
        )