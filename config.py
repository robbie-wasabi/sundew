import json
import jsonschema
from pathlib import Path

def load_config(config_path):
    """
    Load and validate the configuration file.
    
    Args:
    config_path (str): Path to the configuration file.
    
    Returns:
    dict: Validated configuration.
    
    Raises:
    jsonschema.exceptions.ValidationError: If the configuration is invalid.
    FileNotFoundError: If the configuration file is not found.
    json.JSONDecodeError: If the configuration file is not valid JSON.
    """
    config_path = Path(config_path)
    schema_path = config_path.parent / "schema.json"
    
    try:
        with open(schema_path, "r") as schema_file:
            schema = json.load(schema_file)
        
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        
        jsonschema.validate(instance=config, schema=schema)
        return config
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Configuration file not found: {e.filename}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in configuration file: {e.msg}", e.doc, e.pos)
    except jsonschema.exceptions.ValidationError as e:
        raise jsonschema.exceptions.ValidationError(f"Invalid configuration: {e.message}")

def get_account_groups(config):
    """
    Get the account groups from the configuration.
    
    Args:
    config (dict): The loaded configuration.
    
    Returns:
    dict: Account groups.
    """
    return config["account_groups"]

def get_llm_instructions(config):
    """
    Get the LLM instructions from the configuration.
    
    Args:
    config (dict): The loaded configuration.
    
    Returns:
    dict: LLM instructions.
    """
    return config["llm_instructions"]

def get_output_format(config):
    """
    Get the output format from the configuration.
    
    Args:
    config (dict): The loaded configuration.
    
    Returns:
    str: Output format.
    """
    return config["output_format"]

def get_output_destination(config):
    """
    Get the output destination from the configuration.
    
    Args:
    config (dict): The loaded configuration.
    
    Returns:
    str: Output destination.
    """
    return config["output_destination"]

def get_update_interval(config):
    """
    Get the update interval from the configuration.
    
    Args:
    config (dict): The loaded configuration.
    
    Returns:
    int: Update interval in seconds.
    """
    return config["update_interval"]