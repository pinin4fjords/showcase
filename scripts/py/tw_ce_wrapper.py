#!/usr/bin/env python3

"""
Wrapper script to automate creation of CEs and export of CEs from/to JSON files. 
"""
import argparse
from computeenvs import ComputeEnvs as CeWrapper
import utils
from pathlib import Path
import sys
import json


def parse_args(args=None):
    # TODO: description and usage
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json_files", type=Path, nargs="+", help="List of JSON config files"
    )
    parser.add_argument("--credentials", type=str, help="Credentials for Tower")
    parser.add_argument("--workspace", type=str, help="Workspace name")
    parser.add_argument("--export", action="store_true", help="Export CEs to JSON")
    parser.add_argument(
        "--import", action="store_true", help="Import CEs from JSON", dest="import_arg"
    )
    args = parser.parse_args()
    return args


def get_compute_envs(ce_list):
    """
    Get a list of compute environment names available in a workspace
    """
    compute_envs = json.loads(ce_list)

    names = [item["name"] for item in compute_envs["computeEnvs"]]
    return names


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


def main(args=None):
    args = parse_args(args)

    # Check environment variables first
    try:
        utils.tw_env_var("TOWER_ACCESS_KEY")
    except EnvironmentError as e:
        print(e)
        sys.exit(1)

    # If workspace is not provided, check if env var is set
    if not args.workspace:
        try:
            utils.tw_env_var("TOWER_WORKSPACE_ID")
        except EnvironmentError as e:
            print(e)
            print("Please set or provide a workspace name with --workspace.")
            sys.exit(1)
        else:
            args.workspace = utils.tw_env_var("TOWER_WORKSPACE_ID")

    # Create instance of CE Wrapper
    cli = CeWrapper(args.workspace)

    if args.export:
        # Export compute environments to JSON files
        compute_env_names = get_compute_envs(cli.list())

        for name in compute_env_names:
            cli.export_ce(name)

    elif args.import_arg:
        # Import compute environments from JSON files
        try:
            utils.validate_credentials(args.credentials, args.workspace)
        except ValueError as e:
            print(e)
            sys.exit(1)

        # Check if the json_files provided exist
        for filepath in args.json_files:
            if not Path(filepath).is_file():
                print(f"JSON file {filepath} provided does not exist!")
                sys.exit(1)

        # Get JSON file list and their basenames to name the CEs
        json_in, json_names = get_json_files(args.json_files)
        for config, ce_name in zip(json_in, json_names):
            print(config, ce_name)
            cli.import_ce(ce_name, config, args.credentials)

    else:
        # If neither --import or --export is provided, exit
        print("Please provide either the --import or --export option")
        sys.exit(1)


if __name__ == "__main__":
    main()
