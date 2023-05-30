"""
Python wrapper for tw compute-envs command  
"""

from utils import tw_run
from pathlib import Path


class ComputeEnvs:
    """
    Python wrapper for tw compute-envs command
    """

    cmd = "compute-envs"

    def __init__(self, workspace_name):
        self.workspace = workspace_name

    def _tw_run(self, command, to_json=False):
        return tw_run(command, to_json)

    def list(self):
        """
        List compute environments
        """
        return self._tw_run([self.cmd, "list"], to_json=True)

    def view(self):
        """
        View a compute environment
        """
        return self._tw_run([self.cmd, "view", "--name", self.name], to_json=True)

    def delete(self):
        """
        Delete a compute environment
        """
        self._tw_run([self.cmd, "delete", "--name", self.name])

    def export_ce(self, name):
        """
        Export a compute environment
        """
        # create a Path object for the workspace directory
        workspace_dir = Path(self.workspace)

        # create the directory if it doesn't exist
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # define the output file path
        outfile = workspace_dir / f"{name}.json"

        return self._tw_run([self.cmd, "export", "--name", name, outfile], to_json=True)

    def import_ce(self, name, config, credentials):
        """
        Import a compute environment
        """
        self._tw_run(
            [
                self.cmd,
                "import",
                "--name",
                name,
                config,
                "--credentials",
                credentials,
            ]
        )

    def set_default(self):
        """
        Set a compute environment as default
        """
        self._tw_run([self.cmd, "primary", "set", "--name", self.name])
