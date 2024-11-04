import os
import yaml
import json
from typing import Any, Dict, Optional

class ConfigLoader:
    """
    Configuration loader that supports YAML and JSON configuration files with
    environment-specific overrides.
    """

    def __init__(self, config_dir: str, env: str = "dev"):
        """
        Initialize the ConfigLoader with the directory containing config files and the environment.

        Args:
            config_dir (str): Directory containing config files.
            env (str): Current environment (dev, prod).
        """
        self.config_dir = config_dir
        self.env = env
        self.config = {}

    def load_config(self, config_name: str) -> Dict[str, Any]:
        """
        Load the configuration from the specified YAML or JSON file.

        Args:
            config_name (str): Base name of the config file (without extension).

        Returns:
            dict: Loaded configuration as a dictionary.
        """
        base_config = self._load_file(config_name)
        env_config = self._load_file(f"{config_name}.{self.env}")
        self.config = self._merge_configs(base_config, env_config)
        return self.config

    def _load_file(self, config_name: str) -> Dict[str, Any]:
        """
        Load a configuration file from YAML or JSON.

        Args:
            config_name (str): The name of the config file.

        Returns:
            dict: Parsed configuration as a dictionary.
        """
        yaml_file = os.path.join(self.config_dir, f"{config_name}.yaml")
        json_file = os.path.join(self.config_dir, f"{config_name}.json")

        if os.path.exists(yaml_file):
            return self._load_yaml(yaml_file)
        elif os.path.exists(json_file):
            return self._load_json(json_file)
        else:
            raise FileNotFoundError(f"Configuration file {config_name} not found.")

    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Load a YAML file.

        Args:
            file_path (str): Path to the YAML file.

        Returns:
            dict: Parsed YAML file.
        """
        with open(file_path, "r") as file:
            return yaml.safe_load(file) or {}

    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """
        Load a JSON file.

        Args:
            file_path (str): Path to the JSON file.

        Returns:
            dict: Parsed JSON file.
        """
        with open(file_path, "r") as file:
            return json.load(file)

    def _merge_configs(self, base_config: Dict[str, Any], env_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge the base configuration with environment-specific overrides.

        Args:
            base_config (dict): Base configuration.
            env_config (dict): Environment-specific configuration.

        Returns:
            dict: Merged configuration.
        """
        if not env_config:
            return base_config

        merged_config = base_config.copy()
        for key, value in env_config.items():
            if isinstance(value, dict) and key in merged_config and isinstance(merged_config[key], dict):
                merged_config[key] = self._merge_configs(merged_config[key], value)
            else:
                merged_config[key] = value
        return merged_config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key (str): The key of the configuration value.
            default (any): Default value if the key is not found.

        Returns:
            any: Configuration value.
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def validate(self, schema: Dict[str, Any]) -> None:
        """
        Validate the loaded configuration against a schema.

        Args:
            schema (dict): The validation schema.

        Raises:
            ValueError: If validation fails.
        """
        self._validate_schema(self.config, schema)

    def _validate_schema(self, config: Dict[str, Any], schema: Dict[str, Any], path: str = "") -> None:
        """
        Recursive schema validation.

        Args:
            config (dict): The configuration to validate.
            schema (dict): The schema to validate against.
            path (str): Current path in the configuration (for error messages).

        Raises:
            ValueError: If validation fails.
        """
        for key, key_type in schema.items():
            full_path = f"{path}.{key}" if path else key
            if key not in config:
                raise ValueError(f"Missing configuration key: {full_path}")
            if not isinstance(config[key], key_type):
                raise ValueError(f"Invalid type for key {full_path}: expected {key_type}, got {type(config[key])}")

    def reload(self) -> None:
        """
        Reload the configuration.
        """
        self.config = self.load_config()

    def save_config(self, config_name: str, format: str = "yaml") -> None:
        """
        Save the current configuration to a file in either YAML or JSON format.

        Args:
            config_name (str): The name of the config file (without extension).
            format (str): Format to save the configuration in (yaml or json).
        """
        if format not in ["yaml", "json"]:
            raise ValueError("Format must be 'yaml' or 'json'.")

        file_path = os.path.join(self.config_dir, f"{config_name}.{format}")

        if format == "yaml":
            self._save_yaml(file_path, self.config)
        elif format == "json":
            self._save_json(file_path, self.config)

    def _save_yaml(self, file_path: str, config: Dict[str, Any]) -> None:
        """
        Save a configuration to a YAML file.

        Args:
            file_path (str): Path to the YAML file.
            config (dict): Configuration data to save.
        """
        with open(file_path, "w") as file:
            yaml.safe_dump(config, file)

    def _save_json(self, file_path: str, config: Dict[str, Any]) -> None:
        """
        Save a configuration to a JSON file.

        Args:
            file_path (str): Path to the JSON file.
            config (dict): Configuration data to save.
        """
        with open(file_path, "w") as file:
            json.dump(config, file, indent=4)

    def _get_config_path(self, config_name: str, format: str) -> str:
        """
        Get the full file path of a configuration file.

        Args:
            config_name (str): The name of the config file (without extension).
            format (str): The format of the config file (yaml or json).

        Returns:
            str: Full file path.
        """
        return os.path.join(self.config_dir, f"{config_name}.{format}")

# Usage
if __name__ == "__main__":
    loader = ConfigLoader(config_dir="/configs", env="prod")
    config = loader.load_config("config")
    loader.validate({
        "app_name": str,
        "version": str,
        "logging": dict,
        "database": dict,
    })
    print(loader.get("database.host"))