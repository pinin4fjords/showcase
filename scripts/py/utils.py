import subprocess
import os
import json
from pathlib import Path
import yaml


def tw_run(cmd, *args, **kwargs):
    """
    Run a tw command with supplied commands
    """
    full_cmd = ["tw"]
    if kwargs.get("to_json"):
        full_cmd.extend(["-o", "json"])
    full_cmd.extend(cmd)
    full_cmd.extend(args)
    # Run the command and return the stdout
    process = subprocess.run(full_cmd, stdout=subprocess.PIPE)
    stdout = process.stdout.decode("utf-8")
    return stdout


def tw_env_var(tw_variable):
    """
    Check if a tw environment variable exists
    """
    if not tw_variable in os.environ:
        raise EnvironmentError(
            f"Tower environment variable '{tw_variable}' is not set."
        )
    else:
        return os.environ[tw_variable]


def validate_credentials(credentials, workspace):
    """
    Validate credentials for a workspace using the name of the credentials
    """
    credentials_avail = tw_run(
        ["credentials", "list", "--workspace", workspace], to_json=True
    )
    credentials_avail = json.loads(credentials_avail)

    # Check if provided credentials exist in the workspace
    if credentials not in [item["name"] for item in credentials_avail["credentials"]]:
        raise ValueError(
            f"Credentials '{credentials}' not found in workspace '{workspace}'"
        )


def get_json_files(json_files):
    """
    Convert a list of PosixPath objects for the provided JSON files
    into a comma-separated list of strings and parse the name of JSONs out
    to use as the name for the CE being created.

    If a single path is provided, return the string representation of the path..
    Returns both lists in a tuple.
    """
    if not isinstance(json_files, list):
        json_files = [json_files]

    json_str = [str(json_in) for json_in in json_files]
    basenames = [Path(x).stem for x in json_files]

    return json_str, basenames


def find_key_value_in_dict(data, target_key, target_value):
    """
    Generic method to find a key-value pair in a nested dictionary and within
    lists of dictionaries.
    Can use the input of json.loads() converting JSON string to dict.
    #TODO: huge candidate for refactoring
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key and value == target_value:
                return True
            if isinstance(value, dict) and find_key_value_in_dict(
                value, target_key, target_value
            ):
                return True
            if isinstance(value, list):
                for item in value:
                    if find_key_value_in_dict(item, target_key, target_value):
                        return True
    elif isinstance(data, list):
        for item in data:
            if find_key_value_in_dict(item, target_key, target_value):
                return True
    return False


def validate_id(json_data, name):
    """
    Wrapper around find_key_value_in_dict() to validate that a resource was
    created successfully in Tower by looking for the name.
    """
    data = json.loads(json_data)
    if not find_key_value_in_dict(data, "name", name):
        raise ValueError(f"Could not find '{name}' in Tower. Something went wrong.")


def check_if_exists(json_data, name):
    data = json.loads(json_data)
    if find_key_value_in_dict(data, "name", name):
        raise ValueError(f"Resource '{name}' already exists in Tower.")


def is_valid_json(file_path):
    try:
        with open(file_path, "r") as f:
            json.load(f)
        return True
    except json.JSONDecodeError:
        return False


def is_valid_yaml(file_path):
    try:
        with open(file_path, "r") as f:
            yaml.safe_load(f)
        return True
    except yaml.YAMLError:
        return False
