"""
Created 2023

@author: th
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Affiliation:
    """
    affiliation of a scholar
    """
    name: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    wikidata_id: Optional[str] = None
    
    @property
    def ui_label(self) -> str:
        if not self.name:
            return "❓"  # empty
        else:
            return self.name