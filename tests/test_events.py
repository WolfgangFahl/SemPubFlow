'''
Created on 22.12.2023

@author: wf
'''
import os
import glob
import json
from ngwidgets.basetest import Basetest
from sempubflow.event import Events, Event
from sklearn.metrics import precision_recall_fscore_support

class TestEvents(Basetest):
    """
    test the Events and Events YamlAble dataclasses
    """
    
    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.ceurws_path = os.path.expanduser("~/.ceurws")
        self.volumes_path = os.path.join(self.ceurws_path, "volumes.json")
        self.volumes = self.get_volumes()
        self.volumes_by_number = {volume['number']: volume for volume in self.volumes if 'number' in volume}

 
    def get_volumes(self):
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
            end_date="2022-06-10"
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
            event_reach="International"
        )
    
        events.events.append(event1)
        events.events.append(event2)
        if self.debug:
            print(events.to_yaml())
            print (event1.to_yaml())

    
    def test_event_from_yaml(self):
        """
        test getting an event from a YAML string
        """
        yaml_str="""acronym: "BMAW 2015"
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
        event=Event.from_yaml(yaml_str)
        if self.debug:
            print(event)
        self.assertEqual("Amsterdam",event.city)
        
    def get_events(self,date_iso):
        # Define the directory and date_iso according to your requirements
        home_directory = os.path.expanduser("~/.ceurws/llm/")
        pattern = os.path.join(home_directory, f'events-{date_iso}*.yaml')
        yaml_files = glob.glob(pattern)
        events=Events()
        for yaml_file in yaml_files:
            yf_events=Events.load_from_file(yaml_file)
            events.events.extend(yf_events.events)
        if self.debug:
            print(f"loaded {len(events.events)} events from {len(yaml_files)} YAML files")
        return events.events
    
    def get_unique_events(self,events):
        # Filter events to remove duplicates, keeping only the first occurrence
        unique_events = []
        seen_volumes = {}
        for event in events:
            if event.volume not in seen_volumes:
                unique_events.append(event)
                seen_volumes[event.volume]=event
            else:
                # Directly compare the two event dataclasses
                if self.debug:
                    original_event = seen_volumes[event.volume]
                    if event == original_event:
                        print(f"Duplicate identical event for volume {event.volume} removed")
                    else:
                        print(f"Warning: Duplicate event for volume {event.volume} differs from original.")
        sorted_events=sorted(unique_events, key=lambda x: x.volume)
        return sorted_events            
            
    def check_quality(self, events, volumes, attr_name, na="N/A"):
        """
        Check the quality of event attributes against volumes data for a given attribute.
        :param events: List of Event objects.
        :param volumes: List of volume data (dicts) from volumes.json.
        :param attr_name: The name of the attribute to check (e.g., 'acronym', 'title').
        :param na: Placeholder for missing or unavailable data (default is "N/A").
        """
        # Prepare ground truth (gt) and predictions lists
        gt_attributes = [str(volume.get(attr_name, na)) for volume in volumes]
        pred_attributes = [str(getattr(event, attr_name, na)) or na for event in events]
    
        # Debugging: Print sample data
        sample_len=10
        if self.debug:
            print("Sample GT:", gt_attributes[:sample_len])  # Adjust as needed
            print("Sample Predictions:", pred_attributes[:sample_len])  # Adjust as needed
    
        # Calculate precision, recall, and F1 score
        precision, recall, f1, _ = precision_recall_fscore_support(
            gt_attributes, pred_attributes, average='weighted', zero_division=0
        )
    
        # Print or return the precision, recall, and F1 score
        print(f"{attr_name} - Precision: {precision:.2f}, Recall: {recall:.2f}, F1 Score: {f1:.2f}")

    def test_collect_and_parse_yaml_files(self):
        """
        Test for collecting YAML files and parsing them into events.
        """
        if self.inPublicCI():
            return
        events= self.get_events("2023-12-22") # Replace with the actual date you want to use
        unique_events=self.get_unique_events(events)
        volumes = [volume for volume in self.volumes if 'number' in volume and volume['number'] in [event.volume for event in events]]
        # Checking if the lengths of events and volumes are the same
        if len(unique_events) != len(volumes):
            print(f"Warning: The number of events ({len(unique_events)}) does not match the number of volumes ({len(volumes)}).")
        else:
            for attribute in ["acronym","year","title"]:
                self.check_quality(unique_events, volumes, attribute)