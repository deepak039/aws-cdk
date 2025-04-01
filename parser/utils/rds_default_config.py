class RDSDefaultConfig:
    """
    Default configuration for RDS instances.
    """

    DEFAULTS = {
        "vpc": "main-vpc",
        "instance_type": "t3.micro",
        "allocated_storage": 20,    # Storage in GB
        "multi_az": True,           # Enable multi-AZ deployment
        "deletion_protection": False,
        "publicly_accessible": False,
        "storage_encrypted": True,
        "backup_retention_days": 7, # Backup retention duration in days
        "removal_policy": "DESTROY",  # Options: DESTROY, SNAPSHOT, RETAIN
        "cloudwatch_logs_exports": [
            "error",
            "general",
            "slowquery"
        ]  # CloudWatch logs to export
    }

    @classmethod
    def get(cls, key):
        """
        Get the default value for the given key.
        """
        return cls.DEFAULTS.get(key)