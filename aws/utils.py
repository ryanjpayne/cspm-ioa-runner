"""
Utils module for AWS IOA scripts
"""

import configparser
import os


def get_config_options():
    """Read configuration from config.ini"""
    config = configparser.ConfigParser()
    # Look for config.ini in parent directory
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")
    config.read(config_path)
    return config


def get_aws_tags():
    """
    Get AWS resource tags from config.ini
    Returns a list of tag dictionaries in AWS format: [{"Key": "name", "Value": "value"}, ...]
    """
    aws_resource_tags = []

    try:
        config = get_config_options()
        if "tags" in config:
            tags = config["tags"]
            for key, value in tags.items():
                aws_resource_tags.append({"Key": key, "Value": value})
    except Exception as e:
        print(f"Warning: Could not load tags from config.ini: {e}")
        # Return default tags if config fails
        aws_resource_tags = [{"Key": "app", "Value": "crowdstrike-ioa-generator"}]

    return aws_resource_tags


# Export standardized AWS resource tags
AWS_RESOURCE_TAGS = get_aws_tags()
