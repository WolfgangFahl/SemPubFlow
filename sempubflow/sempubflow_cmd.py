"""
Created on 2023-06-19

@author: wf
"""
import sys

from ngwidgets.cmd import WebserverCmd

from sempubflow.webserver import SemPubFlowWebServer


class SemPubFlowCmd(WebserverCmd):
    """
    command line handling for Semantic Publishing Workflow
    """

    def __init__(self):
        """
        constructor
        """
        config = SemPubFlowWebServer.get_config()
        WebserverCmd.__init__(self, config, SemPubFlowWebServer, DEBUG)
        pass


def main(argv: list = None):
    """
    main call
    """
    cmd = SemPubFlowCmd()
    exit_code = cmd.cmd_main(argv)
    return exit_code


DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
