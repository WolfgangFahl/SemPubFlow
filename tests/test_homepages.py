"""
Created on 2023-12-20

@author: wf
"""
import json
import os

import requests
from ngwidgets.basetest import Basetest
from tabulate import tabulate
from tqdm import tqdm

from sempubflow.llm import LLM

from dataclasses import dataclass

@dataclass
class VolumeSetInfo:
    """
    a set of volumes
    """
    set_index: int
    from_volume: int
    to_volume: int
    accessible_count: int = 0
    total_count: int = 0

    def update(self, volume_number, is_accessible):
        self.from_volume = min(self.from_volume, volume_number)
        self.to_volume = max(self.to_volume, volume_number)
        self.total_count += 1
        if is_accessible:
            self.accessible_count += 1

    def to_dict(self):
        return {
            "#": self.set_index,
            "From": self.from_volume,
            "To": self.to_volume,
            "Accessible": self.accessible_count,
            "Total": self.total_count,
            "Percentage": f"{(self.accessible_count / self.total_count) * 100:.2f}%" if self.total_count > 0 else "N/A"
        }


class HomepageChecker:
    """
    test the availability of homepages for the given volumes
    """

    def __init__(self, volumes, set_number=1, sample_size=None, debug: bool = False):
        """
        Initialize the HomepageChecker.

        Args:
            volumes (list): A list of volume dictionaries.
            set_number (int, optional): The number of sets to divide the volumes into. Defaults to 1.
            sample_size (int, optional): The size of each sample to check. If None, checks all volumes in a set. Defaults to None.
            debug (bool, optional): If True, shows detailed debug information. Defaults to False.

        """
        self.volumes = [
            v for v in volumes if v.get("homepage")
        ]  # Filter volumes with homepages
        self.set_number = set_number
        self.sample_size = (
            sample_size if sample_size is not None else len(volumes) // set_number
        )
        self.debug = debug
        self.results = []  # Store detailed results
        self.set_infos = []  # Store summary for each set


    def check_availability(self, url, timeout: float = 1.0):
        """
        Check if the given URL is accessible.

        Args:
            url (str): The URL to check.
            timeout(float): timeout in secs - default: 1.0

        Returns:
            bool: True if the URL is accessible, False otherwise.
        """
        try:
            response = requests.head(url, allow_redirects=True, timeout=timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def process_samples(self, show_progress=False):
        """
        Process the samples and check the availability of homepages.

        Args:
            show_progress (bool): Whether to show a progress bar.
        """
        total_volumes = len(self.volumes)
        slot_size = total_volumes // self.set_number

        if show_progress:
            progress_bar = tqdm(total=self.set_number * self.sample_size, desc="Checking homepages")

        for set_index in range(self.set_number):
            start_index = set_index * slot_size
            middle_start = start_index + (slot_size - self.sample_size) // 2
            middle_end = middle_start + self.sample_size
            sample_volumes = self.volumes[middle_start:middle_end]

            set_info = VolumeSetInfo(set_index + 1, float('inf'), -1)

            for volume in sample_volumes:
                volume_number = volume["number"]
                homepage = volume["homepage"]
                is_accessible = self.check_availability(homepage)

                # Update set_info and store detailed result
                set_info.update(volume_number, is_accessible)
                self.results.append((set_index + 1, volume_number, homepage, is_accessible))

                if show_progress:
                    progress_bar.update(1)

            self.set_infos.append(set_info)

        if show_progress:
            progress_bar.close()

    def prepare_summary_data(self):
        """
        Prepare the summary data.

        Returns:
            list: The prepared summary data.
        """
        summary_data = [set_info.to_dict() for set_info in self.set_infos]
        return summary_data

    def prepare_detailed_data(self):
        """
        Prepare the detailed result data.

        Returns:
            list: The prepared detailed data.
        """
        detailed_data = [
            {
                "#": index + 1, 
                "Set": set_index, 
                "Volume Number": volume_number, 
                "Homepage": homepage, 
                "Is Accessible": is_accessible
            }
            for index, (set_index, volume_number, homepage, is_accessible) in enumerate(self.results)
        ]
        return detailed_data

    def create_formatted_table(self, data, table_format="grid"):
        """
        Create a formatted table.

        Args:
            data (list): The data for the table, which should be a list of dictionaries.
            table_format (str): The format of the table.

        Returns:
            str: The formatted table in string format.
        """
        if not data:
            return ""
        return tabulate(data, headers="keys", tablefmt=table_format)

    def generate_summary_table(self):
        """
        Generate a summary table of the results.

        Returns:
            str: The generated summary table in ASCII format.
        """
        data = self.prepare_detailed_data() if self.debug else self.prepare_summary_data()
        return self.create_formatted_table(data)


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
        checker = HomepageChecker(self.volumes, set_number=3, sample_size=5)

        checker.process_samples(show_progress=True)

        # Print the summary table
        print(checker.generate_summary_table())
