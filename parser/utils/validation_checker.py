from parser.exceptions import MissingKeyException


class ValidationChecker:
    SERVICE_MANDATORY_KEYS = {
        "alb": ["name", "asg"],
        "api_gateways": ["name", "lambdaname", "routes"],
        "asg": ["name", "vpc", "user_data_path", "max", "min"],
        "dynamodb": ["name", "partition_key"],
        "ec2": ["name"],
        "eks": ["name", "vpc", "admin_roles", "node_groups"],
        "elasticache": [],
        "iam_permissions": [],
        "lambdas": ["name", "runtime", "handler", "memory_size", "timeout"],
        "nat_gateways": [],
        "rds": ["name", "vpc", "security_group"],
        "s3_buckets": ["name"],
        "security_groups": ["name", "service", "description", "ingress_rules", "allow_all_outbound"],
        "subnet_groups": ["vpcs"],
        "vpcs": ["name", "cidr", "max_azs", "subnets"],
        "vpc_endpoints": ["name", "service", "vpc", "subnets"],
    }

    @staticmethod
    def validate_service_keys(service_name, service_instances):
        """
        Validate if all mandatory keys are present for the specified service.

        Args:
            service_name (str): Name of the service.
            service_instances (list): List of service instances in the configuration.

        Raises:
            MissingKeyException: If mandatory keys are missing.
        """
        mandatory_keys = ValidationChecker.SERVICE_MANDATORY_KEYS.get(service_name, [])

        for instance in service_instances:
            # Check for missing keys
            missing_keys = [key for key in mandatory_keys if key not in instance]
            if missing_keys:
                raise MissingKeyException(
                    service_name=service_name,
                    missing_keys=missing_keys,
                )

    @staticmethod
    def validate_config(config):
        """
        Validate the entire merged configuration by checking each service.

        Args:
            merged_config (dict): Merged configuration dictionary.

        Raises:
            MissingKeyException: If any services in the configuration are missing mandatory keys.
        """
        for service_name, service_instances in config.items():
            ValidationChecker.validate_service_keys(service_name, service_instances)