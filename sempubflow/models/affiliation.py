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