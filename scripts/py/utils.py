import subprocess
import sys
import os


def tw_run(cmd):
    """
    Run a tw command with supplied commands
    """
    cmd = ["tw"] + cmd
    process = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    output_lines = process.stdout.splitlines()

    # Print and return the captured output line by line
    for line in output_lines:
        print(line)

    return output_lines


def tw_env_var(tw_variable):
    """
    Check if a tw environment variable exists
    """
    if not tw_variable in os.environ:
        print("Tower environment variable {} is not set".format(tw_variable))
        sys.exit(1)
