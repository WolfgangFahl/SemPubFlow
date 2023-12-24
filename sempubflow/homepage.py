"""
Created on 2023-06-19

@author: wf
"""
import os
import sys
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from ngwidgets.yamlable import YamlAble
from tabulate import tabulate
from tqdm import tqdm


@dataclass
class Homepage(YamlAble["Homepage"]):
    """
    a CEUR-WS event homepage
    """

    volume: int
    url: Optional[str] = None
    text: Optional[str] = None
    available: bool = False
    content_len: Optional[int] = None
    availability_check: datetime = datetime.now()

    def __post_init__(self):
        # Strip leading and trailing whitespace from the URL
        self.read_timeout = 3.0
        if self.url:
            self.url = self.url.strip()

    def check_url(self, timeout: float = 0.5) -> bool:
        """
        Check the URL.

        Args:
            timeout (float): The timeout in seconds.

        Returns:
            bool: True if the URL is reachable, False otherwise.
        """
        # Skip if the URL is empty
        if not self.url:
            return False

        try:
            response = urllib.request.urlopen(self.url, timeout=timeout)
            self.available = response.getcode() == 200

            # Get content length if available
            if self.available:
                self.content_len = response.headers.get("Content-Length")
                if self.content_len is not None:
                    self.content_len = int(self.content_len)

        except Exception as _ex:
            self.available = False
            self.content_len = None

        return self.available

    def read(self) -> str:
        """
        read my html
        """
        self.html = urllib.request.urlopen(self.url, timeout=self.read_timeout).read()
        return self.html

    def get_text(self) -> str:
        """
        get the text from my url
        """
        text = None
        soup = None
        try:
            self.read()
            soup = BeautifulSoup(self.html, features="html.parser")

            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()  # rip it out
        except Exception as ex:
            # shall we log the exception here?
            print(str(ex), file=sys.stderr)
            pass

        if soup and soup.body:
            # get text
            text = soup.body.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = "\n".join(chunk for chunk in chunks if chunk)
        return text


@dataclass
class Homepages(YamlAble["Homepages"]):
    homepages: List[Homepage] = field(default_factory=list)


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
            "Percentage": f"{(self.accessible_count / self.total_count) * 100:.2f}%"
            if self.total_count > 0
            else "N/A",
        }


class PercentageTable:
    """
    A class for creating a table that displays values and their corresponding percentages of a total.

    Attributes:
        total (float): The total value used for calculating percentages.
        column_title (str): The title for the first column in the table.
        digits (int): The number of decimal places for rounding percentages.
        rows (list): A list of dictionaries representing rows in the table.
    """

    def __init__(self, column_title: str, total: float, digits: int):
        """
        Initializes the PercentageTable with a title for the column, a total value, and specified precision for percentages.

        Args:
            column_title (str): The title for the first column.
            total (float): The total value for calculating percentages.
            digits (int): The precision for percentage values.
        """
        self.total = total
        self.column_title = column_title
        self.digits = digits
        self.rows = [{self.column_title: "Total", "#": total, "%": 100.0}]

    def add_value(self, row_title: str, value: float):
        """
        Adds a row to the table with the given title and value, calculating the percentage of the total.

        Args:
            row_title (str): The title for the row.
            value (float): The value for the row, which is used to calculate its percentage of the total.
        """
        percentage = round((value / self.total) * 100, self.digits) if self.total else 0
        self.rows.append({self.column_title: row_title, "#": value, "%": percentage})

    def generate_table(self, tablefmt="grid") -> str:
        """
        Generates a string representation of the table using the tabulate library.

        Returns:
            str: The string representation of the table with headers and formatted rows.
        """
        if not self.rows:
            return ""
        tabulate_markup = tabulate(
            self.rows, headers="keys", tablefmt=tablefmt, floatfmt=f".{self.digits}f"
        )
        return tabulate_markup


class HomepageChecker:
    """Class to check the homepage availability and analyze TLDs."""

    def __init__(
        self,
        volumes: List[Dict],
        debug: bool = False,
        cache_file: str = None,
    ):
        """Initialize the HomepageChecker with caching mechanism.

        Args:
            volumes (List[Dict]): A list of volume dictionaries.
            debug (bool): If True, shows detailed debug information.
            cache_file (str): The filename for storing cache data.
        """
        self.volumes = [v for v in volumes if "homepage" in v]
        self.debug = debug
        self.results = []
        self.set_infos = []
        self.cache_file = cache_file or os.path.expanduser(
            "~/.ceurws/volume_homepages.yaml"
        )
        # load the homepages
        self.load_homepages_cache()
        self.homepages_by_volume = {hp.volume: hp for hp in self.homepages.homepages}

    def load_homepages_cache(self):
        """Load the homepages cache data from a file."""
        if os.path.exists(self.cache_file):
            self.homepages = Homepages.load_from_file(self.cache_file)

    def save_homepages_cache(self):
        """Save the homepages cache data to a file."""
        self.homepages.save_to_file(self.cache_file)

    def check_availability(self, url: str, volume_number: int) -> bool:
        """
        Check the availability of a homepage URL, using the cache if available.

        Args:
            url (str): The URL of the homepage.
            volume_number (int): The volume number associated with the homepage.

        Returns:
            bool: True if the homepage is accessible, False otherwise.
        """
        if volume_number not in self.homepages_by_volume:
            # Check availability and create a new Homepage instance
            new_homepage = Homepage(
                volume=volume_number,
                url=url,
                available=False,
                availability_check=datetime.now(),
            )
            new_homepage.check_url()
            # Append the new homepage to the homepages list and update the dictionary
            self.homepages.homepages.append(new_homepage)
            self.homepages_by_volume[volume_number] = new_homepage
            return new_homepage.available
        else:
            # Use existing Homepage availability
            return self.homepages_by_volume[volume_number].available

    def process_samples(
        self,
        set_number: int = 1,
        sample_size: int = None,
        show_progress=False,
        with_save: bool = False,
    ):
        """
        Process the samples and check the availability of homepages.

        Args:
            set_number (int): The number of sets to divide the volumes into.
            sample_size (int): The size of each sample to check.
            show_progress (bool): Whether to show a progress bar.
            with_save(bool): if True update the cache
        """

        self.set_number = set_number
        self.sample_size = sample_size or len(self.volumes) // set_number

        total_volumes = len(self.volumes)
        slot_size = total_volumes // self.set_number

        if show_progress:
            progress_bar = tqdm(
                total=self.set_number * self.sample_size, desc="Checking homepages"
            )

        for set_index in range(self.set_number):
            set_info = None

            start_index = set_index * slot_size
            middle_start = start_index + (
                (slot_size - self.sample_size) // 2 if self.set_number > 1 else 0
            )
            middle_end = middle_start + self.sample_size
            sample_volumes = self.volumes[middle_start:middle_end]

            for volume in sample_volumes:
                volume_number = volume["number"]
                homepage = volume["homepage"]
                is_accessible = self.check_availability(homepage, volume_number)
                # Create set_info only if it's the first volume in the set
                if set_info is None:
                    set_info = VolumeSetInfo(
                        set_index + 1, volume_number, volume_number
                    )

                # Update set_info and store detailed result
                set_info.update(volume_number, is_accessible)
                self.results.append(
                    (set_index + 1, volume_number, homepage, is_accessible)
                )

                if show_progress:
                    progress_bar.update(1)

            if set_info:
                self.set_infos.append(set_info)

        if show_progress:
            progress_bar.close()
        # Save homepages after processing
        if with_save:
            self.save_homepages_cache()

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
                "Is Accessible": is_accessible,
            }
            for index, (set_index, volume_number, homepage, is_accessible) in enumerate(
                self.results
            )
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
        data = (
            self.prepare_detailed_data() if self.debug else self.prepare_summary_data()
        )
        return self.create_formatted_table(data)
