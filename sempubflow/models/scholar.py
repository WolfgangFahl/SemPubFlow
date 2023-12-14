from dataclasses import dataclass
from typing import List, Optional

from sempubflow.models.affiliation import Affiliation


@dataclass
class Scholar:
    """
    a scholar
    """
    label: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    wikidata_id: Optional[str] = None
    dblp_author_id: Optional[str] = None
    orcid_id: Optional[str] = None
    image: Optional[str] = None
    affiliation: Optional[List[Affiliation]] = None
    official_website: Optional[str] = None


    @property
    def name(self) -> str:
        return f"{self.given_name} {self.family_name}"


class ScholarSearchMask(Scholar):
    """
    search mask for a scholar
    contains incomplete information about a scholar
    """