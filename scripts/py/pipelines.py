"""
Python wrapper for tw pipelines command
"""
from utils import tw_run
from pathlib import Path


class Pipelines:
    """
    Python wrapper for tw pipelines command
    """

    cmd = "pipelines"

    def __init__(self, workspace_name):
        self.workspace = workspace_name

    def _tw_run(self, command, to_json=False):
        return tw_run(command, to_json)

    def list(self):
        """
        List pipelines
        """
        return self._tw_run(
            [self.cmd, "list", "--workspace", self.workspace], to_json=True
        )

    def view(self, name):
        """
        View a pipeline
        """
        return self._tw_run([self.cmd, "view", "--name", name], to_json=True)

    def delete(self, name):
        """
        Delete a pipeline
        """
        self._tw_run([self.cmd, "delete", "--name", name])

    def export_pipeline(self, name):
        """
        Export a pipeline
        """
        # create a Path object for the workspace directory
        workspace_dir = Path(self.workspace)

        # create the directory if it doesn't exist
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # define the output file path
        outfile = workspace_dir / f"{name}.json"

        return self._tw_run(
            [
                self.cmd,
                "export",
                "--workspace",
                self.workspace,
                "--name",
                name,
                outfile,
            ],
            to_json=True,
        )

    def import_pipeline(self, name, config):
        """
        Import a pipeline
        """
        self._tw_run(
            [self.cmd, "import", "--name", name, config, "--workspace", self.workspace]
        )

    def add(self, name, config, repository):
        """
        Add a pipeline to the workspace
        """
        self._tw_run(
            [
                self.cmd,
                "add",
                "--name",
                name,
                "--params-file",
                config,
                repository,
                "--workspace",
                self.workspace,
            ]
        )

    def launch(self, name, config=None):
        """
        Launch a pipeline
        """
        command = [
            "launch",
            name,
            "--workspace",
            self.workspace,
        ]
        if config:
            return command + " --params-file " + config
        return self._tw_run(command)

    # TODO: add labels method
