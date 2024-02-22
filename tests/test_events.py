"""
Created on 22.12.2023

@author: wf
"""
import glob
import json
import os
from statistics import median  # Importing median function from statistics module
from typing import Dict, List, Optional, Tuple

from ngwidgets.basetest import Basetest
from sklearn.metrics import precision_recall_fscore_support
from tabulate import tabulate

from sempubflow.event import Event, Events


class TestEvents(Basetest):
    """
    test the Events and Events YamlAble dataclasses
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.ceurws_path = os.path.expanduser("~/.ceurws")
        self.volumes_path = os.path.join(self.ceurws_path, "volumes.json")
        self.volumes = self.get_volumes()
        self.volumes_by_number = {
            volume["number"]: volume for volume in self.volumes if "number" in volume
        }
        self.event_attribute_map = {
            "acronym": "acronym",  # str - "ALPSWS2008"
            "city": "city",  # str - "Udine"
            "country": "country",  # str - "IT"
            "end_date": "dateTo",  # str - "2008-12-13"
            "event_reach": None,  # NoneType - None
            "event_type": None,  # str - "Workshop"
            "frequency": None,  # NoneType - None
            "ordinal": None,  # NoneType/int - None or an integer
            "region": "loc_region",  # str - "IT-36"
            "start_date": "dateFrom",  # str - "2008-12-09"
            "subject": None,  # str - "Logic Programming, Semantic Web, Web Services"
            "title": "title",  # str - "International Workshop on Applications of Logic Programming to the (Semantic) Web and Web Services"
            "volume": None,  # int - 434
            "year": "year",  # int - 2008
        }

    def get_volumes(self) -> Optional[List[Dict]]:
        """Retrieve the volumes data from a JSON file.

        Returns:
            Optional[List[Dict]]: A list of volume dictionaries or None if file not found.
        """
        # Path to the volumes.json file
        # Ensure the file exists
        if not os.path.exists(self.volumes_path):
            return None
        # Read the JSON data
        with open(self.volumes_path, "r") as file:
            volumes_data = json.load(file)
        return volumes_data

    def test_events(self):
        """
        test a list of events
        """
        events = Events()

        # Event construction for AVICH 2022
        event1 = Event(
            volume=0,
            acronym="AVICH 2022",
            event_type="Workshop",
            year=2022,
            country="IT",
            region="IT-62",
            city="Frascati",
            title="Workshop on Advanced Visual Interfaces and Interactions in Cultural Heritage",
            subject="Advanced Visual Interfaces and Interactions in Cultural Heritage",
            start_date="2022-06-06",
            end_date="2022-06-10",
        )

        # Event construction for BMAW 2014
        event2 = Event(
            volume=0,
            acronym="BMAW 2014",
            event_type="Workshop",
            year=2014,
            country="NL",
            region="NL-NH",
            city="Amsterdam",
            title="Bayesian Modeling Applications Workshop",
            subject="Bayesian Modeling Applications",
            frequency="Annual",
            event_reach="International",
        )

        events.events.append(event1)
        events.events.append(event2)
        if self.debug:
            print(events.to_yaml())
            print(event1.to_yaml())

    def test_event_from_yaml(self):
        """
        test getting an event from a YAML string
        """
        yaml_str = """acronym: "BMAW 2015"
frequency: "Annual"
event_type: "Workshop"
year: 2015
start_date: "2015-07-16"
end_date: "2015-07-16"
country: "NL"  # Netherlands
region: "NL-NH"  # Noord-Holland
city: "Amsterdam"
title: "Bayesian Modeling Applications Workshop"
subject: "Bayesian Modeling Applications"
  """
        event = Event.from_yaml(yaml_str)
        if self.debug:
            print(event)
        self.assertEqual("Amsterdam", event.city)

    def get_events(self, date_iso: str) -> List[Event]:
        """
        Get the cached event results.

        Args:
            date_iso (str): Date in ISO format to use as wildcard.
            for event entries created on that date

        Returns:
            List[Event]: A list of Event objects.
        """
        # Define the directory and date_iso according to your requirements
        home_directory = os.path.expanduser("~/.ceurws/llm/")
        pattern = os.path.join(home_directory, f"events-{date_iso}*.yaml")
        yaml_files = glob.glob(pattern)
        events = Events()
        for yaml_file in yaml_files:
            yf_events = Events.load_from_file(yaml_file)
            events.events.extend(yf_events.events)
        if self.debug:
            print(
                f"loaded {len(events.events)} events from {len(yaml_files)} YAML files"
            )
        return events.events

    def get_unique_events(self, events: List[Event]) -> List[Event]:
        """
        Filter events to remove duplicates, keeping only unique ones.

        Args:
            events (List[Event]): A list of Event objects.

        Returns:
            List[Event]: A list of unique Event objects.
        """
        unique_events = []
        seen_volumes = {}
        for event in events:
            if event.volume not in seen_volumes:
                unique_events.append(event)
                seen_volumes[event.volume] = event
            else:
                # Directly compare the two event dataclasses
                if self.debug:
                    original_event = seen_volumes[event.volume]
                    if event == original_event:
                        print(
                            f"Duplicate identical event for volume {event.volume} removed"
                        )
                    else:
                        print(
                            f"Warning: Duplicate event for volume {event.volume} differs from original."
                        )
        sorted_events = sorted(unique_events, key=lambda x: x.volume)
        return sorted_events

    def calculate_precision_recall(
        self,
        gt_records: List[Dict],
        pred_records: List[Dict],
        gt_attr: str,
        pred_attr: str,
    ) -> Tuple[float, float, float]:
        """
        Calculate the precision, recall, and F1 score for given attributes.

        Args:
            gt_records (List[Dict]): Ground truth records.
            pred_records (List[Dict]): Prediction records.
            gt_attr (str): The attribute name in ground truth records.
            pred_attr (str): The attribute name in prediction records.

        Returns:
            Tuple[float, float, float]: Precision, recall, and F1 score.
        """
        aligned_gt_values = []
        aligned_pred_values = []

        # Align records by primary key and ensure both gt and pred values are present
        for key in gt_records:
            if key in pred_records:
                gt_record = gt_records[key]
                pred_record = pred_records[key]

                if gt_attr in gt_record and pred_attr in pred_record:
                    gt_value = gt_record[gt_attr]
                    pred_value = pred_record[pred_attr]

                    if gt_value is not None and pred_value is not None:
                        aligned_gt_values.append(str(gt_value))
                        aligned_pred_values.append(str(pred_value))
        # Ensure the lists have the same length
        if len(aligned_gt_values) != len(aligned_pred_values):
            # Handle this case as needed, e.g., by logging a warning
            return (0.0, 0.0, 0.0)
        else:
            sample_len = 10
        if self.debug:
            print("Sample GT:", aligned_gt_values[:sample_len])
            print("Sample Predictions:", aligned_pred_values[:sample_len])

        precision, recall, f1, _ = precision_recall_fscore_support(
            aligned_gt_values, aligned_pred_values, average="weighted", zero_division=0
        )
        return precision, recall, f1

    def get_events_and_volumes(self, iso_date: str) -> Tuple[List[Event], List[Dict]]:
        """
        Get events and corresponding volumes for a given ISO date.

        This function retrieves events created on a specific date and fetches the corresponding volume information.
        It ensures that each event is unique and correlates with the volumes data.

        Args:
            iso_date (str): The ISO format date to filter events.

        Returns:
            Tuple[List[Event], List[Dict]]: A tuple containing a list of unique events and a list of their corresponding volumes.
        """
        events = self.get_events(
            iso_date
        )  # Replace with the actual date you want to use
        unique_events = self.get_unique_events(events)
        volumes = [
            volume
            for volume in self.volumes
            if "number" in volume
            and volume["number"] in [event.volume for event in events]
        ]
        # Checking if the lengths of events and volumes are the same
        if len(unique_events) != len(volumes):
            print(
                f"Warning: The number of events ({len(unique_events)}) does not match the number of volumes ({len(volumes)})."
            )
        return unique_events, volumes

    def get_valid_records(
        self, lod: List[Dict], pkey_attr: str, attr: str, na: str = "N/A"
    ) -> Dict[str, Dict]:
        """
        Get valid records from a list of dictionaries based on attribute presence and value, indexed by a primary key.

        Args:
            lod (List[Dict]): List of dictionaries representing records (events or volumes).
            pkey_attr (str): The primary key attribute to use for indexing in the return dictionary.
            attr (str): The attribute name to check in each record.
            na (str): Placeholder for missing or unavailable data (default is "N/A").

        Returns:
            Dict[str, Dict]: A dictionary of dictionaries where the specified attribute is valid, indexed by the primary key.
        """
        valid_records = {}
        for record in lod:
            if not isinstance(record, dict):
                record = record.__dict__  # Convert to dictionary if not already
            if attr in record and pkey_attr in record:
                value = record[attr]
                pkey = record[pkey_attr]
                if value and value != na:
                    valid_records[pkey] = record
        return valid_records

    def calc_list_stats(self, somelist: List[float]) -> dict:
        """
        Calculate and return the statistical summary (min, max, average, median) of a list of numbers.

        This function calculates the minimum, maximum, average, and median values of a given list of numbers.
        It handles the case where the list is empty by returning None for each statistical value.

        Args:
            somelist (List[float]): The list of numbers for which to calculate statistics.

        Returns:
            dict: A dictionary containing the 'min', 'max', 'avg', and 'median' of the list. Each value is
            either a float or None if the list is empty.

        References:
            StackOverflow: https://stackoverflow.com/a/27009257/1497139
        """
        # Ensure the list is not empty to avoid division by zero or index errors
        if len(somelist) == 0:
            return {"max": None, "min": None, "avg": None, "median": None}

        # Calculate max, min, and avg
        max_value = max(somelist)
        min_value = min(somelist)
        avg_value = sum(somelist) / len(somelist)

        # Calculate median
        median_value = median(somelist)

        return {
            "count": len(somelist),
            "sum": sum(somelist),
            "max": max_value,
            "min": min_value,
            "avg": avg_value,
            "median": median_value,
        }

    from typing import Dict, List

    def stat_availability(
        self, stat: Dict[str, float], prefix: str, lod: List[any], valid_lod: List[any]
    ) -> float:
        """
        Add a statistics entry about the availability to the provided statistics dictionary.

        This method calculates the total number of items, the number of available (valid) items,
        and the percentage of items that are available. It updates the 'stat' dictionary with these
        values prefixed by the given prefix.

        Args:
            stat (Dict[str, float]): The dictionary to update with statistics.
            prefix (str): A string prefix used for the keys in 'stat'.
            lod (List[any]): The list of all items.
            valid_lod (List[any]): The list of available (valid) items.

        Returns:
            float: The percentage of available items in the list.

        Example:
            If you call `stat_availability(stat, "prefix", [1,2,3], [1,2])`,
            it will calculate the availability as 66.7 and update the 'stat' dictionary with
            'prefix total', 'prefix #', and 'prefix %' keys.
        """
        # Calculate total, available, and percentage

        total = len(lod)
        available = len(valid_lod)
        percent = available / total * 100
        stat[f"{prefix} total"] = total
        stat[f"{prefix} #"] = available
        stat[f"{prefix} %"] = f"{percent:7.1f}"
        return percent

    def test_collect_and_parse_yaml_files(self):
        """
        Test for collecting YAML files and parsing them into events.
        """
        if self.inPublicCI():
            return
        unique_events, volumes = self.get_events_and_volumes("2023-12-")
        stats = []
        avails = []
        # Iterate through each attribute in the event attribute map
        for event_attr, vol_attr in self.event_attribute_map.items():
            # Check and print availability stats for each attribute
            event_records = self.get_valid_records(unique_events, "volume", event_attr)
            stat = {}
            attr = f"{event_attr}"
            # if vol_attr and vol_attr!=event_attr:
            #    attr+=f"/{vol_attr}"

            if vol_attr:
                stat["attr"] = attr
                avail = self.stat_availability(
                    stat, "event", unique_events, event_records.values()
                )
                avails.append(avail)

                volume_records = self.get_valid_records(volumes, "number", vol_attr)
                self.stat_availability(stat, "volume", volumes, volume_records.values())
                if vol_attr and event_attr:
                    precision, recall, f1 = self.calculate_precision_recall(
                        volume_records, event_records, vol_attr, event_attr
                    )
                    stat["prec"] = f"{precision:.2f}" if precision else ""
                    stat["recall"] = f"{recall:.2f}" if recall else ""
                    stat["f1"] = f"{f1:.2f}" if f1 else ""
                stats.append(stat)
        markup = tabulate(stats, headers="keys", tablefmt="latex")
        print(markup)
        list_stats = self.calc_list_stats(avails)
        print(json.dumps(list_stats, indent=2))
