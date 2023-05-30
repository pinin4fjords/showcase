"""
Python wrapper for tw compute-envs command  
"""

from utils import tw_run


class ComputeEnvs:
    """
    Python wrapper for tw compute-envs command
    """

    cmd = "compute-envs"

    def __init__(self, env_name):
        self.name = env_name

    def _tw_run(self, command):
        return tw_run(command)

    def list(self):
        """
        List compute environments
        """
        return self._tw_run([self.cmd, "list"])

    def view(self):
        """
        View a compute environment
        """
        return self._tw_run([self.cmd, "view", "--name", self.name])

    def delete(self):
        """
        Delete a compute environment
        """
        self._tw_run([self.cmd, "delete", "--name", self.name])

    def export_ce(self):
        """
        Export a compute environment
        """
        return self._tw_run(
            [self.cmd, "export", "--name", self.name, self.name + ".json"]
        )

    def import_ce(self, config, credentials):
        """
        Import a compute environment
        """
        self._tw_run(
            [
                self.cmd,
                "import",
                "--name",
                self.name,
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
