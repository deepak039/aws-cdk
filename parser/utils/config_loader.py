import yaml
import os

class ConfigLoader:
    # DEFAULTS = {
    #     "lambda_config": {
    #         "runtime": "python3.8",
    #         "handler": "handler.handler",
    #         "memory_size": 128,
    #         "code_path": "lambda" ,
    #         "timeout": 3,
    #     },
    #     "api_endpoints": []
    # }

    @staticmethod
    def load_config(config_path: str = "/config.yaml"):
        """Load and validate the configuration file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}.")

        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        return config

    @staticmethod
    def merge_defaults(user_config):
        """Merge user-provided config with defaults."""
        def recursive_merge(defaults, user):
            if isinstance(defaults, dict):
                return {
                    key: recursive_merge(value, user.get(key, value)) for key, value in defaults.items()
                }
            return user
        return recursive_merge(ConfigLoader.DEFAULTS, user_config)