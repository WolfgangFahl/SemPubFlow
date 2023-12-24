"""
Created on 2023-11-22

@author: wf
"""
from dataclasses import dataclass, field
from typing import List, Optional

from ngwidgets.yamlable import YamlAble


@dataclass
class Event(YamlAble["Event"]):
    """
    a single event
    """

    volume: Optional[int] = 0
    acronym: Optional[str] = None
    ordinal: Optional[int] = None
    frequency: Optional[str] = None
    event_reach: Optional[str] = None
    event_type: Optional[str] = None
    year: Optional[int] = None
    start_date: Optional[str] = None  # iso date str
    end_date: Optional[str] = None  # iso date str
    country: Optional[str] = None  # 2 letter iso country code
    region: Optional[str] = None  # 3 letter iso country code
    city: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None


@dataclass
class Events(YamlAble["Events"]):
    """
    a collection of events
    """

    events: List[Event] = field(default_factory=list)
