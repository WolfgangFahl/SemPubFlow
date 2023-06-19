'''
Created on 2023-06-19

@author: wf
'''
import urllib.request

class Homepage:
    """
    a homepage
    """
    
    def __init__(self,url:str):
        self.url=url
        
    @classmethod
    def check_url(self,url:str)->bool:
        """
        
        check the url
        
        Args:
            url(str): the url to check
        
        Returns:
            bool: True if the url is reachable
        """
        try:
            code = urllib.request.urlopen(url,timeout=0.5).getcode()
        except Exception as _ex:
            return False
        return code == 200