"""
Python wrapper for tw compute-envs command  
"""

from utils import tw_run


class ComputeEnvs:
    """
    Python wrapper for tw compute-envs command
    """

    def __init__(self, ce_name):
        self.name = ce_name
        self.cmd = "compute-envs"

    def tw(self, command):
        return tw_run(command)

    def list(self):
        """
        List compute environments
        """
        return self.tw([self.cmd, "list"])

    def view(self):
        """
        View a compute environment
        """
        return self.tw([self.cmd, "view", "--name", self.name])

    def delete(self):
        """
        Delete a compute environment
        """
        self.tw([self.cmd, "delete", "--name", self.name])

    def export_ce(self):
        """
        Export a compute environment
        """
        return self.tw([self.cmd, "export", "--name", self.name, self.name + ".json"])

    def import_ce(self, config, credentials):
        """
        Import a compute environment
        """
        self.tw(
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
        self.tw([self.cmd, "primary", "set", "--name", self.name])
