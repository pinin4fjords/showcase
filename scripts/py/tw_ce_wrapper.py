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
import logging

logger = logging.getLogger(__name__)


def log_and_continue(e):
    logger.error(e)
    return


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
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="The desired log level (default: WARNING).",
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


def validate_input_files(json_files):
    # Check if JSON input files exist
    for filepath in json_files:
        if not Path(filepath).is_file():
            raise ValueError(f"JSON file {filepath} provided does not exist!")


def handle_export(tw_ce):
    # Export compute environments to JSON files
    compute_env_names = get_compute_envs(tw_ce.list())
    for name in compute_env_names:
        # Export all CEs in workspace by name
        tw_ce.export_ce(name)
        logger.info(f"Successfully exported CE {name}")


def handle_import(tw_ce, json_files, credentials):
    # Import compute environments from JSON files
    # TODO: add argument to supply a prefix/name

    # Get JSON file list and their basenames to name the CEs
    json_in, json_names = utils.get_json_files(json_files)
    for config, ce_name in zip(json_in, json_names):
        try:
            # Check if CE already exists
            utils.check_if_exists(tw_ce.list(), ce_name)

            # Import the CE into Tower workspace
            # TODO: overwrite option?
            tw_ce.import_ce(ce_name, config, credentials)

            # Check if CE resource was created by its name
            utils.validate_id(tw_ce.list(), ce_name)
        except ValueError as e:
            log_and_continue(e)
        else:
            logger.info(f"Successfully imported CE {ce_name}")


def main(args=None):
    args = parse_args()
    logging.basicConfig(level=args.log_level)

    # Check environment variables first
    try:
        utils.tw_env_var("TOWER_ACCESS_KEY")
    except EnvironmentError as e:
        logger.error(e)

    # If workspace is not provided, check if env var is set
    if not args.workspace:
        try:
            utils.tw_env_var("TOWER_WORKSPACE_ID")
        except EnvironmentError as e:
            logger.error(e)
            logger.error("Please set or provide a workspace name with --workspace.")
            sys.exit(1)
        else:
            args.workspace = utils.tw_env_var("TOWER_WORKSPACE_ID")

    # Create instance of CE Wrapper
    tw_ce = CeWrapper(args.workspace)

    if args.export:
        handle_export(tw_ce)

    elif args.import_arg:
        # Import compute environments from JSON files
        try:
            utils.validate_credentials(args.credentials, args.workspace)
            validate_input_files(args.json_files)
        except ValueError as e:
            logger.exception(e)

        handle_import(tw_ce, args.json_files, args.credentials)

    else:
        # If neither --import or --export is provided, exit
        logger.error("Please provide either the --import or --export option")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
