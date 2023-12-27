"""
Created on 2023-12-27

@author: wf
"""

from tabulate import tabulate
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SyncPair:
    """
    A class to represent a pair of data sources for synchronization.
    
    Attributes:
        title (str): The title of the synchronization pair.
        l_name (str): Name of the left data source (e.g., 'local').
        r_name (str): Name of the right data source (e.g., 'wikidata').
        l_data (List[Dict[str, Any]]): A list of dictionaries from the left data source.
        r_data (List[Dict[str, Any]]): A list of dictionaries from the right data source.
        l_key (str): The field name in the left data source dictionaries used as a unique identifier for synchronization.
        r_key (str): The field name in the right data source dictionaries used as a unique identifier for synchronization.
        
            
 Example usage:
 l_data = [{'id_l': '1', 'value': 'a'}, {'id_l': '2', 'value': 'b'}]
 r_data = [{'id_r': '2', 'value': 'b'}, {'id_r': '3', 'value': 'c'}]
 pair = SyncPair("Title", "local", "wikidata", l_data, r_data, 'id_l', 'id_r')
 sync = Sync(pair)
 print(sync.status_table())
    """
    title: str
    l_name: str
    r_name: str
    l_data: List[Dict[str, Any]]
    r_data: List[Dict[str, Any]]
    l_key: str
    r_key: str


class Sync:
    """
    A class to help with synchronization between two sets of data, each represented as a list of dictionaries.
    """

    def __init__(self, pair: SyncPair):
        """
        Initialize the Sync class with the given Synchronization Pair.
        """
        self.pair = pair
        self.sync_dict = self._create_sync_dict()
        self.directions = ['←', '↔', '→']

    def _create_sync_dict(self) -> dict:
        """
        Create a dictionary representing the synchronization state between left and right data sources.
        """
        l_keys = {d[self.pair.l_key] for d in self.pair.l_data if self.pair.l_key in d}
        r_keys = {d[self.pair.r_key] for d in self.pair.r_data if self.pair.r_key in d}
        
        sync_dict= {
            '←': r_keys - l_keys,  # Present in right but not in left
            '↔': l_keys.intersection(r_keys),  # Present in both
            '→': l_keys - r_keys   # Present in left but not in right
        }
        return sync_dict

    def get_keys(self, direction: str) -> set:
        """
        Get the keys for a given direction of synchronization.
        """
        if direction in self.sync_dict:
            return self.sync_dict[direction]
        else:
            raise ValueError("Invalid direction. Use '←', '↔', or '→'.")

    def status_table(self, tablefmt: str = "grid") -> str:
        """
        Create a table representing the synchronization status.
        """
        total_records = sum(len(keys) for keys in self.sync_dict.values())
        if total_records == 0:  # Avoid division by zero
            total_records = 1

        table_data = []
        for direction, keys in self.sync_dict.items():
            num_records = len(keys)
            percentage = (num_records / total_records) * 100
            table_data.append({
                "left": self.pair.l_name,
                "↔": direction,
                "right": self.pair.r_name,
                "#": num_records,
                "%": f"{percentage:7.2f}%"
            })

        markup=tabulate(table_data, headers='keys', tablefmt=tablefmt, colalign=("right","center","left","right","right"))
        return markup