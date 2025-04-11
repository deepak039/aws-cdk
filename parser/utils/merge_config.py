from parser.utils.config_loader import ConfigLoader
from parser.utils.dependency_resolver import DependencyResolver

class MergeConfig:
    @staticmethod
    def merge_resource_type(resource_type, user_instances, default_defaults):
        """
        Merge a single resource type. Combines user instances with missing default template values.

        Args:
            resource_type (str): The resource type being merged.
            user_instances (list): List of user-provided instances for the resource type.
            default_defaults (list): List of default templates for the resource type.

        Returns:
            list: Merged list of instances for the resource type.
        """
        # Default template is the first dictionary in the defaults list (assuming one default per resource type)
        # If the default defaults list is more complex, additional logic can be added
        if not default_defaults or not isinstance(default_defaults, list):
            raise TypeError(f"Default template for resource type '{resource_type}' must be a list of dictionaries.")
        default_template = default_defaults[0]

        merged_instances = []
        for user_instance in user_instances:
            # Start with user-provided instance
            merged_instance = user_instance.copy()

            # Add missing keys from the default template
            for key, value in default_template.items():
                if key not in merged_instance:
                    merged_instance[key] = value

            # Append the fully merged instance
            merged_instances.append(merged_instance)

        return merged_instances

    @staticmethod
    def merge_config(config_default, config):
        """
        Merges the user configuration with the default configuration.

        Args:
            config_default (dict): Default configuration dictionary.
            config (dict): User-provided configuration dictionary.

        Returns:
            dict: Merged configuration dictionary.
        """
        # Initialize the merged_config dictionary
        merged_config = {}

        # Iterate through all resource types in user_config
        for resource_type, user_instances in config.items():
            # If the resource type exists in the default config
            if resource_type in config_default:
                default_defaults = config_default[resource_type]  # List of default templates for the resource type
                # Merge resource type with the default configuration
                merged_config[resource_type] = MergeConfig.merge_resource_type(
                    resource_type, user_instances, default_defaults
                )
            else:
                # No default configuration exists for this resource type; use user-provided instances
                merged_config[resource_type] = user_instances

        return merged_config

    @staticmethod
    def load_and_merge(user_config_path: str, default_config_path: str) -> dict:
        """
        Loads the user configuration and default configuration from their respective YAML files.
        Returns the merged configuration.

        Args:
            user_config_path (str): Path to the user configuration YAML file.
            default_config_path (str): Path to the default configuration YAML file.

        Returns:
            dict: Merged configuration.
        """
        # Load YAML files using ConfigLoader
        user_config = ConfigLoader.load_config(user_config_path)
        default_config = ConfigLoader.load_config(default_config_path)

        # Log detailed configurations
        # print("\n=== Detailed Configuration of user_config ===")
        # MergeConfig.print_config_details(user_config, "user_config")
        # print("\n=== Detailed Configuration of default_config ===")
        # MergeConfig.print_config_details(default_config, "default_config")

        # Sort the dictionary based on dependency order
        resolver = DependencyResolver(user_config)
        sorted_services = resolver.resolve_dependencies()
        sorted_config = resolver.sort_configuration(user_config, sorted_services)
        print(sorted_config)
        user_config = sorted_config

        # Log detailed configurations after dependency resolution
        print("\n=== Detailed Configuration of user_config after dependency resolution ===")
        MergeConfig.print_config_details(user_config, "user_config")

        # Perform merging
        merged_config = MergeConfig.merge_config(default_config, user_config)

        # Log merged configuration
        # print("\n=== Detailed Configuration of merged_config ===")
        # MergeConfig.print_config_details(merged_config, "merged_config")

        return merged_config

    @staticmethod
    def print_config_details(config, config_name):
        """
        Prints detailed configuration details in a clean format.

        Args:
            config (dict): Configuration dictionary to print.
            config_name (str): Name of the configuration (e.g., "user_config").
        """
        print(f"Available resource types in {config_name}:")
        for key in config.keys():
            print(f"\nResource Type: {key}")
            for instance in config[key]:
                print("\nInstance configuration:")
                if isinstance(instance, dict):
                    for k, v in instance.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"  Value: {instance}")
        print("===========================\n")