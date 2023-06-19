"""
Created on 2023-06-19

@author: wf
"""
from tests.basetest import Basetest
from sempubflow.jsoncache import JsonCacheManager
from sempubflow.homepage import Homepage

class TestEvent(Basetest):
    """
    test handling events
    """

    def testHomepage(self):
        """
        test homepage handling
        """
        jm = JsonCacheManager()
        vol_list = jm.load_lod("Volumes")
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
