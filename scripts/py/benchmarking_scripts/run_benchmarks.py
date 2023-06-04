#!/usr/bin/env python3

"""
Wrapper script to automate pipeline running for a set of nf-core/pipelines
provided in a config.yaml
"""
import argparse
from wrappers.pipelines import Pipelines as PipelineWrapper
import wrappers.utils as utils
from pathlib import Path
import sys
import logging
import yaml
import tempfile

logger = logging.getLogger(__name__)


def log_and_continue(e):
    logger.error(e)
    return


def parse_args():
    # TODO: description and usage
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, help="Config file with pipelines to run")
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="The desired log level (default: WARNING).",
    )
    return parser.parse_known_args()


def get_pipeline_keys_values(config):
    """
    Parser to get keys and values from config.yaml
    """
    pipelines = config.get("pipelines", {})
    keys = []
    values = []
    for key, value in pipelines.items():
        keys.append(key)
        values.append(value)
    return keys, values


def append_string_to_outdir_base(outdir_base, pipeline, profile):
    """
    Create a temporary params.yaml file for the pipeline tests
    which will take `outdir_base` defined in the your config.yaml
    and append the pipeline name to it and date to be used
    as your params.outdir.
    """
    # Create a dictionary with the outdir_base key and its value
    data = {"outdir": outdir_base}

    # Remove the trailing "/" if it exists
    if outdir_base.endswith("/"):
        outdir_base = outdir_base[:-1]

    # Append the string to the outdir_base value
    if outdir_base:
        formatted_date = utils.get_date()
        params_string = f"{outdir_base}/{pipeline}/profile_{profile}/{formatted_date}"
        data["outdir"] = params_string

    # Create a temporary file to write the modified data
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        params_yaml = temp_file.name

        # Write the modified data to the temporary file
        with open(params_yaml, "w") as file:
            yaml.dump(data, file)

    return params_yaml


def handle_launch(
    tw_wrapper,
    pipeline,
    profile,
    revision=None,
    compute_env=None,
    params_file=None,
    config_file=None,
):
    """
    Handle the launch of an nf-core pipeline with the given parameters
    """
    pipeline_repo = "https://github.com/nf-core/" + pipeline
    profile = "--profile=" + profile
    version = "--revision=" + revision
    ce = "--compute-env=" + compute_env
    try:
        tw_wrapper.launch(
            pipeline_repo,
            version,
            profile,
            ce,
            params_file=params_file,
            config=config_file,
        )
        logging.info(
            f"Launched pipeline {pipeline_repo} with revision {version} and profile {profile}"
        )

    except Exception as e:
        log_and_continue(e)


def parse_config(config_file):
    config = utils.load_yaml(config_file)
    return config


def main():
    args, unknown_args = parse_args()
    logging.basicConfig(level=args.log_level)

    # Check environment variables first
    try:
        utils.tw_env_var("TOWER_ACCESS_KEY")
    except EnvironmentError as e:
        logger.error(e)

    # Make sure config is provided
    if not args.config:
        logger.error(
            "Please provide a path to the YAML configuration file using --config."
        )
        return

    # Validate YAML file
    if not utils.is_valid_yaml(args.config):
        logging.error("Invalid YAML configuration file")
        return

    # Load YAML configuration
    try:
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError) as e:
        logging.error(f"Error loading the YAML configuration file: {e}")
        return

    # Parse config file fields
    workspace = config.get("workspace")
    compute_env = config.get("compute-env")
    profile = config.get("profile")
    pipelines = config.get("pipelines")
    outdir = config.get("outdir_base")
    config_file = config.get("config_file")  # Nextflow config file

    if not workspace:
        try:
            utils.tw_env_var("TOWER_WORKSPACE_ID")
        except EnvironmentError as e:
            logger.error(e)
            logger.error("Please set a workspace name")
        else:
            workspace = utils.tw_env_var("TOWER_WORKSPACE_ID")

    # Create an instance of the PipelineWrapper class
    tw_wrapper = PipelineWrapper(workspace)

    # Launch the pipeline
    pipelines, revisions = get_pipeline_keys_values(config)
    for repo, version in zip(pipelines, revisions):
        params_file = append_string_to_outdir_base(outdir, repo, profile)
        handle_launch(
            tw_wrapper, repo, profile, version, compute_env, params_file, config_file
        )


if __name__ == "__main__":
    sys.exit(main())
