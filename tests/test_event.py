"""
Created on 2023-06-19

@author: wf
"""
from ngwidgets.basetest import Basetest
from sempubflow.jsoncache import JsonCacheManager
from sempubflow.homepage import Homepage

class TestEvent(Basetest):
    """
    test handling events
    """

    def testHomepages(self):
        """
        test homepage handling
        """
        jm = JsonCacheManager()
        vol_list = jm.load_lod("volumes")
        self.assertTrue(len(vol_list)>3300)
        limit=10
        count=0
        for vol in vol_list:
            homepage=vol["homepage"]
            if homepage:
                homepage=homepage.strip()
                count+=1
                is_avail=Homepage.check_url(homepage)
                print(f"{count}:{homepage} {is_avail}",flush=True)
                if count>limit:
                    break
                
    def testGetText(self):
        """
        test getting the text from a homepage
        """
        url="https://escape33-ath.gr/"
        homepage=Homepage(url)
        text=homepage.get_text()
        chars=len(text)
        lines=text.count('\n')
        if self.debug:
            print(f"{url} contains {lines} lines and {chars} chars")
        self.assertTrue(lines>100)