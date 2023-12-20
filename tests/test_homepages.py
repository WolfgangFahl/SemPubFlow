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
        self.results = []
        self.debug = debug

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
            show_progress (bool, optional): Whether to show a progress bar. Defaults to False.
        """
        total_volumes = len(self.volumes)
        slot_size = total_volumes // self.set_number

        # Initialize the progress bar with the total number of homepages to check
        if show_progress:
            progress_bar = tqdm(
                total=self.set_number * self.sample_size, desc="Checking homepages"
            )

        for set_index in range(self.set_number):
            start_index = set_index * slot_size
            middle_start = start_index + (slot_size - self.sample_size) // 2
            middle_end = middle_start + self.sample_size

            sample_volumes = self.volumes[middle_start:middle_end]

            for volume in sample_volumes:
                homepage = volume.get("homepage")
                is_accessible = self.check_availability(homepage)
                self.results.append(
                    (set_index + 1, volume["number"], homepage, is_accessible)
                )

                # Update the progress bar
                if show_progress:
                    progress_bar.update(1)

        if show_progress:
            progress_bar.close()

    def generate_summary_table(self):
        """
        Generate a summary table of the results.

        Returns:
            str: The generated summary table in ASCII format.
        """
        if self.debug:
            headers = ["Set", "Volume Number", "Homepage", "Is Accessible"]
            table_data = self.results
        else:
            headers = ["Set", "Accessible", "Total", "Percentage"]
            set_results = {}
            for set_index, _, _, is_accessible in self.results:
                if set_index not in set_results:
                    set_results[set_index] = [0, 0]  # [accessible count, total count]
                set_results[set_index][1] += 1
                if is_accessible:
                    set_results[set_index][0] += 1

            table_data = [
                (set_index, *counts, f"{(counts[0] / counts[1]) * 100:.2f}%")
                for set_index, counts in set_results.items()
            ]

        return tabulate(table_data, headers=headers, tablefmt="grid")


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
        checker = HomepageChecker(self.volumes, set_number=3, sample_size=10)

        checker.process_samples(show_progress=True)

        # Print the summary table
        print(checker.generate_summary_table())
