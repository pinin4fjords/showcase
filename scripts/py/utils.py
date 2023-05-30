import subprocess
import sys
import os
import json


def tw_run(cmd, to_json=False):
    """
    Run a tw command with supplied commands
    """
    if to_json:
        cmd = ["tw", "-o", "json"] + cmd
    else:
        cmd = ["tw"] + cmd
    process = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    output_lines = process.stdout
    # # Print and return the captured output line by line
    print(output_lines)
    return output_lines


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
