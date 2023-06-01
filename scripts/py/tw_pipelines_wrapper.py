#!/usr/bin/env python3

"""
Wrapper script to automate pipeline export, import, adding using JSON files.
"""
import argparse
from pipelines import Pipelines as PipelineWrapper
import utils
from pathlib import Path
import sys
import json
import logging

logger = logging.getLogger(__name__)


def log_and_continue(e):
    logger.error(e)
    return


def parse_args():
    # TODO: description and usage
    parser = argparse.ArgumentParser()
    parser.add_argument("--params_file", type=Path, help="JSON pipeline config files")
    parser.add_argument(
        "--json_files", type=Path, nargs="+", help="List of JSON config files"
    )
    parser.add_argument("-w", "--workspace", type=str, help="Workspace name")
    parser.add_argument(
        "-e",
        "--export",
        action="store_true",
        help="Export pipelines from Tower to JSON",
    )
    parser.add_argument(
        "-i",
        "--import",
        action="store_true",
        help="Import pipelines to Tower from JSON",
        dest="import_arg",
    )
    parser.add_argument(
        "--pipeline_name", type=str, help="Name of pipeline to be added"
    )
    parser.add_argument(
        "--add_new", action="store_true", help="Add new pipelines to Tower from JSON"
    )
    parser.add_argument(
        "--repository",
        type=str,
        help="Repository to be used to add pipeline (i.e. https://github.com/nf-core/rnaseq.git)",
    )
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="The desired log level (default: WARNING).",
    )
    parser.add_argument(
        "--launch",
        action="store_true",
        help="Launch pipeline after using import or add_new, or launch an existing pipeline",
    )

    return parser.parse_args()


def get_pipelines(pipeline_list):
    """
    Get a list of pipeline names available in a workspace
    """
    pipelines = json.loads(pipeline_list)

    names = [item["name"] for item in pipelines["pipelines"]]
    return names


def validate_params_file(file_path):
    extension = file_path.suffix
    if extension.lower() == ".json":
        if not utils.is_valid_json(file_path):
            raise ValueError(f"{file_path} is not a valid JSON file.")
    elif extension.lower() == ".yaml":
        if not utils.is_valid_yaml(file_path):
            raise ValueError(f"{file_path} is not a valid YAML file.")
    else:
        raise ValueError(
            f"Unsupported file type: {extension}. Please provide a .json or .yaml file."
        )


def handle_export(tw_pipelines, pipeline_list):
    pipeline_names = get_pipelines(pipeline_list)
    for pipeline in pipeline_names:
        tw_pipelines.export_pipeline(pipeline)


def handle_import(tw_pipelines, json_files):
    json_in, json_names = utils.get_json_files(json_files)
    for config, pipeline_name in zip(json_in, json_names):
        try:
            # Check if pipeline already exists
            utils.check_if_exists(tw_pipelines.list(), pipeline_name)
            # TODO: override option?
            tw_pipelines.import_pipeline(pipeline_name, config)
            utils.validate_id(tw_pipelines.list(), pipeline_name)
        except ValueError as e:
            log_and_continue(e)
        else:
            logger.info(f"Pipeline '{pipeline_name}' imported successfully.")
    return pipeline_name


def handle_add(tw_pipelines, pipeline_name, params_file, repository):
    try:
        validate_params_file(params_file)
    except ValueError as e:
        logger.error(f"{e}")
    else:
        tw_pipelines.add(pipeline_name, params_file, repository)


def handle_launch(tw_pipelines, pipeline_name, workspace, config=None):
    """Launch a pipeline that either already exists in launchpad
    or was just imported or added via the wrapper. Can be appended
     at the end of a command using this wrapper.
    """
    try:
        utils.validate_id(tw_pipelines.list(), pipeline_name)
    except ValueError as e:
        log_and_continue(e)
    else:
        if config is not None:
            tw_pipelines.launch(pipeline_name, config)
        else:
            tw_pipelines.launch(pipeline_name)


def main():
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
        else:
            args.workspace = utils.tw_env_var("TOWER_WORKSPACE_ID")

    # Create instance of CE Wrapper
    tw_pipelines = PipelineWrapper(args.workspace)

    if args.export:
        handle_export(tw_pipelines, tw_pipelines.list())

    # Return pipeline name
    if args.import_arg and args.json_files:
        args.pipeline_name = handle_import(tw_pipelines, args.json_files)

    # Handle adding new pipelines
    if args.add_new and args.repository and args.pipeline_name:
        handle_add(tw_pipelines, args.pipeline_name, args.params_file, args.repository)

    # If --launch is specified
    if args.launch and args.pipeline_name:
        logger.info(f"Launching pipeline {args.pipeline_name}")
        handle_launch(
            tw_pipelines, args.pipeline_name, args.workspace, args.params_file
        )

    # TODO: add update method
    # TODO: error handling for argument parsing


if __name__ == "__main__":
    sys.exit(main())
