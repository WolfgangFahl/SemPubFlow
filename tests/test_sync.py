"""
Created on 2023-12-27

@author: wf
"""
from ngwidgets.basetest import Basetest
from sempubflow.sync import Sync, SyncPair


class TestSync(Basetest):
    """
    test Synchronization utitity
    """

    def test_Sync(self):
        """
        Test the Sync class with lists of dictionaries, using distinct keys for left and right data sources.
        """
        # Define lists of dictionaries for both local and wikidata to simulate data sources
        local_data = [
            {"id_l": "1", "value": "a"},
            {"id_l": "2", "value": "b"},
            {"id_l": "4", "value": "d"},
            {"id_l": "5", "value": "e"},
        ]
        wikidata_data = [
            {"id_r": "1", "value": "a"},
            {"id_r": "2", "value": "b"},
            {"id_r": "3", "value": "c"},
        ]

        # Create a SyncPair object with the given names, data, and key fields
        pair = SyncPair(
            title="Local to Wikidata Sync",
            l_name="local",
            r_name="wikidata",
            l_data=local_data,
            r_data=wikidata_data,
            l_key="id_l",
            r_key="id_r",
        )

        # Initialize the Sync object with the SyncPair
        sync = Sync(pair)

        # Print the status table
        print("Status Table:")
        print(sync.status_table())

        # Iterate through directions and print the keys for each direction
        for direction in sync.directions:
            keys = sync.get_keys(direction)
            print(f"Keys for direction {direction}: {keys}")
