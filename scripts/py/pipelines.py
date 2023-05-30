"""
Python wrapper for tw pipelines command  
"""
from utils import tw_run


class Pipelines:
    """
    Python wrapper for tw pipelines command
    """

    def __init__(self):
        self.cmd = "pipelines"

    def tw(self, command):
        return tw_run(command)

    def list(self):
        """
        List pipelines
        """
        return self.tw([self.cmd, "list"])

    def view(self, name):
        """
        View a pipeline
        """
        return self.tw([self.cmd, "view", "--name", name])

    def delete(self, name):
        """
        Delete a pipeline
        """
        self.tw([self.cmd, "delete", "--name", name])

    def export_pipeline(self, name):
        """
        Export a pipeline
        """
        return self.tw([self.cmd, "export", "--name", name, name + ".json"])

    def import_pipeline(self, name, config, credentials):
        """
        Import a pipeline
        """
        self.tw(
            [self.cmd, "import", "--name", name, config, "--credentials", credentials]
        )

    def add(self, name, config, repository):
        """
        Add a pipeline to the workspace
        """
        self.tw([self.cmd, "add", "--name", name, "--params-file", config, repository])

    # TODO: add labels method
