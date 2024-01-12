"""
Created on 2023-12-20

@author: wf
"""
import json
import os
import sys
import random
from tqdm import tqdm
from datetime import datetime
from ngwidgets.basetest import Basetest
from sempubflow.homepage import (
    HomepageChecker,
    PercentageTable,
)
from sempubflow.llm import LLM
from sempubflow.plot import Histogram
from sempubflow.event import Event, Events
from sempubflow.event_info import EventInfo


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
            
    def get_random_homepages(self,sample_size:10,max_len=20000)->list:
        # Filter the homepages based on the text length criteria
        eligible_homepages = [
            hp for hp in self.checker.homepages.homepages
            if hp.text and len(hp.text) < max_len
        ]

        # Select 10 random homepages from those that are eligible
        selected_homepages = random.sample(eligible_homepages, min(sample_size, len(eligible_homepages)))

        if self.debug:
            # Print the selected homepages
            for hp in selected_homepages:
                print(f"Volume: {hp.volume}, URL: {hp.url}, Text Length: {len(hp.text)}")
        volume_numbers=[hp.volume for hp in selected_homepages]
        return volume_numbers
           
    def test_random_homepages_with_max_length(self):
        """
        Select and print 10 random homepages with a text length of less than 20000 characters.
        """
        # Ensure there is a homepage checker and volumes are loaded
        if not self.checker:
            return
        
        max_len=20000
        sample_size = 10

        # Filter the homepages based on the text length criteria
        eligible_homepages = [
            hp for hp in self.checker.homepages.homepages
            if hp.text and len(hp.text) < max_len
        ]

        # Select 10 random homepages from those that are eligible
        selected_homepages = random.sample(eligible_homepages, min(sample_size, len(eligible_homepages)))

        # Print or process the selected homepages
        for hp in selected_homepages:
            print(f"Volume: {hp.volume}, URL: {hp.url}, Text Length: {len(hp.text)}")

        print("vol_numbers=[")
        for hp in selected_homepages:
            print(f"  {hp.volume},")
        print("]")
        
    def test_random_set(self):
        """
        test a random set of volumes
        """
        if not self.checker:
            return
        debug=self.debug
        debug=True
        vol_numbers=self.get_random_homepages(sample_size=50, max_len=10000)
        llm=LLM()   
        
        events=Events()
        log_path=os.path.join(self.ceurws_path,"llm")
        os.makedirs(log_path, exist_ok=True)  # Create llm directory if it doesn't exist.
        log_file = f"events-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.yaml"
        for vol_number in tqdm(vol_numbers):
            try:
                hp=self.checker.homepages_by_volume[vol_number]
                event_info=EventInfo(llm,debug=debug)
                event=event_info.get_event_metadata_from_homepage(hp,temperature=0.0)
                event.volume=vol_number
                events.events.append(event)
            except Exception as ex:
                print(str(ex),file=sys.stderr)
        events.save_to_file(os.path.join(log_path, log_file))
            