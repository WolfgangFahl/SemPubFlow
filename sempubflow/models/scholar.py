from dataclasses import dataclass
from typing import Optional


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


class ScholarSearchMask(Scholar):
    """
    search mask for a scholar
    contains incomplete information about a scholar
    """