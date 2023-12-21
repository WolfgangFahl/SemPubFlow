"""
Created on 2023-12-20

@author: wf
"""
import json
import os
from tqdm import tqdm
from ngwidgets.basetest import Basetest
from sempubflow.homepage import (
    HomepageChecker,
    PercentageTable,
)
from sempubflow.llm import LLM
from sempubflow.plot import Histogram


class TestHomepages(Basetest):
    """
    test CEUR-WS homepages
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.llm = LLM()
        self.ceurws_path = os.path.expanduser("~/.ceurws")
        self.volumes_path = os.path.join(self.ceurws_path, "volumes.json")
        self.volumes = self.get_volumes()
        self.checker = self.get_checker()

    def get_volumes(self):
        # Path to the volumes.json file
        # Ensure the file exists
        if not os.path.exists(self.volumes_path):
            return None
        # Read the JSON data
        with open(self.volumes_path, "r") as file:
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
        if self.checker is None:
            return
        with_save=True
        self.checker.process_samples(show_progress=True,with_save=with_save)

        # Print the summary table
        print(self.checker.generate_summary_table())

    def get_checker(self):
        # Initialize HomepageChecker with the volumes
        if self.volumes is None:
            return None

        checker = HomepageChecker(self.volumes)

        # Load existing homepages
        checker.load_homepages_cache()
        return checker

    def test_content_len_statistics(self):
        """
        get content len statistics
        """
        if not self.checker:
            return
        # Extract content lengths and filter based on max_content_length
        max_content_length = 100000
        content_lengths = [
            hp.content_len
            for hp in self.checker.homepages.homepages
            if hp.content_len is not None and hp.content_len <= max_content_length
        ]
        over_max_length = sum(
            1
            for hp in self.checker.homepages.homepages
            if hp.content_len is not None and hp.content_len > max_content_length
        )

        # Prepare the table data
        total_volumes = len(self.volumes)
        homepage_count = sum(1 for volume in self.volumes if volume.get("homepage"))
        volumes_with_available_urls = len(
            [hp for hp in self.checker.homepages.homepages if hp.available]
        )
        # Calculate and print the average content length separately
        if content_lengths:
            average_length = sum(content_lengths) / len(content_lengths)
            print(f"Average Content Length: {average_length:.2f}")

        # Initialize the percentage table
        table = PercentageTable(column_title="Category", total=total_volumes, digits=2)
        table.add_value(row_title="Volumes with Homepages", value=homepage_count)
        table.add_value(
            row_title="Volumes with Available URLs", value=volumes_with_available_urls
        )
        table.add_value(
            row_title=f"Analysed Homepages <= {max_content_length}",
            value=len(content_lengths),
        )
        table.add_value(
            row_title=f"Volumes over {max_content_length}", value=over_max_length
        )

        # Generate and print the table
        print(table.generate_table(tablefmt='mediawiki'))

    def create_histogramm(
        self, data, title: str, file_name: str, xlabel: str
    ):
        # Create and configure a Histogram instance
        histogram = Histogram(
            data,
            bins=50,
            title=title,
            xlabel=xlabel,
            ylabel="Number of Homepages",
            log_scale_x=False,
        )
        histogram.create_histogram()

        histogram_path = os.path.join(self.ceurws_path, file_name)
        for file_format in ["png", "svg"]:
            # Save plot
            histogram.save_plot(f"{histogram_path}", file_format)
            # Plot and show the histogram

        if self.debug:
            histogram.plt.show()

    def test_histogram_content_len(self):
        """
        Create a histogram of the content lengths of the homepages.
        """
        if not self.checker:
            return

        # Extract content lengths
        max_content_length = 100000
        content_lengths = [
            hp.content_len
            for hp in self.checker.homepages.homepages
            if hp.content_len is not None and hp.content_len <= max_content_length
        ]
        self.create_histogramm(
            content_lengths,
            title="Histogram of Homepage Content Lengths",
            file_name="content_length_histogram",
            xlabel="Content Length",
        )

    def test_histogram_text_len(self):
        """
        Create and save a histogram of the text lengths of the homepages.
        """
        if not self.checker:
            return

        # Extract text lengths
        text_lengths = [
            len(hp.text) for hp in self.checker.homepages.homepages if hp.text
        ]
        self.create_histogramm(
            text_lengths,
            title="Histogram of Homepage Text Lengths",
            file_name="text_length_histogram",
            xlabel="Text Length",
        )

    def test_get_text(self):
        """
        test getting text from homepages
        """
        return
        checker = self.get_checker()
        if not checker:
            return
        # Extract content lengths
        force = False
        max_content_len = 100000
        modified = 0
        for homepage in tqdm(checker.homepages.homepages):
            if homepage.content_len and homepage.content_len <= max_content_len:
                if not homepage.text or force:
                    homepage.text = homepage.get_text()
                    modified += 1
        if self.debug:
            print(f"{modified} homepage texts")
        if modified > 0:
            checker.save_homepages_cache()
