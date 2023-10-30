'''
Created on 2023-06-19

@author: wf
'''
from ngwidgets.cmd import WebserverCmd
from sempubflow.webserver import WebServer
import sys

class SemPubFlowCmd(WebserverCmd):
    """
    command line handling for Semantic Publishing Workflow
    """
    def __init__(self):
        """
        constructor
        """
        config=WebServer.get_config()
        WebserverCmd.__init__(self, config, WebServer, DEBUG)
        pass
  
        
def main(argv:list=None):
    """
    main call
    """
    cmd=SemPubFlowCmd()
    exit_code=cmd.cmd_main(argv)
    return exit_code
        
DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())