import yaml
import os

class ConfigLoader:
    @staticmethod
    def load_config(config_path: str) -> dict:
        """
        Load and validate the configuration file.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}.")

        with open(config_path, "r") as file:
            yaml_data=yaml.safe_load(file)

        return ConfigLoader.normalize_keys(yaml_data)
    

    @staticmethod
    def normalize_keys(data):
        """
        Convert all dictionary keys in a nested structure to lowercase.

        Args:
            data (dict or list): YAML data loaded as dictionary or list.

        Returns:
            dict or list: Normalized data with lowercase keys.
        """
        if isinstance(data, dict):
            return {key.lower(): ConfigLoader.normalize_keys(value) for key, value in data.items()}
        elif isinstance(data, list):
            # Recursively normalize each item if it's a list
            return [ConfigLoader.normalize_keys(item) for item in data]
        else:
            # For primitive types (strings, numbers, etc.), return unchanged
            return data