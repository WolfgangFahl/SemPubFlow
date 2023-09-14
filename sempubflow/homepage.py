'''
Created on 2023-06-19

@author: wf
'''
import urllib.request
from bs4 import BeautifulSoup

class Homepage:
    """
    a homepage
    """
    
    def __init__(self,url:str,timeout:float=2.0):
        self.url=url
        self.timeout=timeout
        
    @classmethod
    def check_url(self,url:str,timeout:float=0.5)->bool:
        """
        
        check the url
        
        Args:
            url(str): the url to check
        
        Returns:
            bool: True if the url is reachable
        """
        try:
            code = urllib.request.urlopen(url,timeout=timeout).getcode()
        except Exception as _ex:
            return False
        return code == 200
    
    def read(self)->str:
        """
        read my html
        """
        self.html = urllib.request.urlopen(self.url,timeout=self.timeout).read()
        return self.html
    
    def get_text(self)->str:
        """
        get the text from my url
        """
        self.read()
        soup = BeautifulSoup(self.html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out
        
        # get text
        text = soup.body.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text