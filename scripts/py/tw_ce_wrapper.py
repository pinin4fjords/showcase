#!/usr/bin/env python3

"""
Wrapper script to automate creation of CEs and export of CEs from/to JSON files. 
"""
import argparse
from computeenvs import ComputeEnvs as ce
import utils
from pathlib import Path


def parse_args(args=None):
    # TODO: description and usage

    parser = argparse.ArgumentParser()
    parser.add_argument("json_files", type=str, help="List of JSON config files")
    parser.add_argument("credentials", type=str, help="Credentials for Tower")
    parser.add_argument("workspace", type=str, help="Workspace name")
    parser.add_argument("outdir", type=Path, help="Output directory")

    def get_ce_list(workspace):
        ce_list = []
        for ce in ce.list():
            ce_list.append(ce["name"])
        return ce_list

    def export_ce_list(workspace):
        for name in get_ce_list(workspace):
            ce(name).export_ce()
