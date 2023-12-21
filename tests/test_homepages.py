"""
Created on 2023-12-20

@author: wf
"""
import json
import os
from datetime import datetime
from ngwidgets.basetest import Basetest
from sempubflow.homepage import VolumeSetInfo, Homepage,Homepages,HomepageChecker
from sempubflow.llm import LLM
from tqdm import tqdm

class TestHomepages(Basetest):
    """
    test CEUR-WS homepages
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.llm = LLM()
        self.volumes = self.get_volumes()

    def get_volumes(self):
        # Path to the volumes.json file
        volumes_path = os.path.expanduser("~/.ceurws/volumes.json")

        # Ensure the file exists
        if not os.path.exists(volumes_path):
            return None
        # Read the JSON data
        with open(volumes_path, "r") as file:
            volumes_data = json.load(file)
        return volumes_data
    
    def test_update_content_len(self):
        """
        Update the content length of each homepage.
        """
        # Initialize HomepageChecker with the volumes
        if self.volumes is None:
            print("No volumes found.")
            return

        checker = HomepageChecker(self.volumes)

        # Load existing homepages
        checker.load_homepages_cache()

        # Update content length for each homepage with a progress bar
        for homepage in tqdm(checker.homepages.homepages, desc="Updating content length"):
            homepage.check_url()

        # Save updated homepages back to cache
        checker.save_homepages_cache()

        if self.debug:
            print(f"Updated content length for {len(checker.homepages.homepages)} homepages.")

         
    def test_home_pages_count(self):
        """
        test the home page count
        """
        if self.volumes is None:
            return
        # Count the number of set homepages
        homepage_count = sum(1 for volume in self.volumes if volume.get("homepage"))

        # Calculate the percentage of volumes with a homepage
        total_volumes = len(self.volumes)
        homepage_percentage = (
            (homepage_count / total_volumes) * 100 if total_volumes > 0 else 0
        )

        if self.debug:
            print(f"Number of set homepages: {homepage_count}")
            print(f"Percentage of volumes with a homepage: {homepage_percentage:.2f}%")

    def test_homepage_availability(self):
        """
        test which homepages are accessible
        """
        if self.volumes is None:
            return
        checker = HomepageChecker(self.volumes, set_number=1200, sample_size=3)

        checker.process_samples(show_progress=True)

        # Print the summary table
        print(checker.generate_summary_table())
