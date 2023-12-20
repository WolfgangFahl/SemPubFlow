"""
Created on 2023-12-20

@author: wf
"""
import json
import os
from ngwidgets.basetest import Basetest
from sempubflow.llm import LLM

class TestHomepages(Basetest):
    """
    test CEUR-WS homepages
    """
    
    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.llm=LLM()
        self.volumes=self.get_volumes()
        
    def get_volumes(self):
        # Path to the volumes.json file
        volumes_path = os.path.expanduser("~/.ceurws/volumes.json")

        # Ensure the file exists
        if not os.path.exists(volumes_path):
            return None
        # Read the JSON data
        with open(volumes_path, 'r') as file:
            volumes_data = json.load(file)
        return volumes_data

    def test_home_pages_count(self):
        """
        test the home page count
        """
        if self.volumes is None:
            return
        # Count the number of set homepages
        homepage_count = sum(1 for volume in self.volumes if volume.get('homepage'))

        # Calculate the percentage of volumes with a homepage
        total_volumes = len(self.volumes)
        homepage_percentage = (homepage_count / total_volumes) * 100 if total_volumes > 0 else 0

        if self.debug:
            print(f"Number of set homepages: {homepage_count}")
            print(f"Percentage of volumes with a homepage: {homepage_percentage:.2f}%")

