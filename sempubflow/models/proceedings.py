from dataclasses import dataclass, fields
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sempubflow.models.scholar import Scholar


class EventType(Enum):
    """
    type of form the event took place
    """
    ONLINE = "online"
    HYBRID = "hybrid"
    PRESENCE = "presence"

    @classmethod
    def get_record(cls) -> dict:
        res = {}
        for t in cls:
            res[t.name] = t.value
        return res

@dataclass
class Event:
    """
    event
    """
    title: Optional[str] = None
    acronym: Optional[str] = None
    start_time: Optional[date] = None
    end_time: Optional[date] = None
    type: Optional[EventType] = EventType.PRESENCE
    location: Optional[str] = None
    country: Optional[str] = None
    official_website: Optional[str] = None

    @property
    def date_range(self) -> dict:
        return {
            'from': self.start_time.isoformat() if self.start_time else None,
            'to': self.end_time.isoformat() if self.end_time else None
        }

    @date_range.setter
    def date_range(self, data: dict):
        """
        set date range
        Expected input {'from': '2023-07-02', 'to': '2023-07-20'}
        Args:
            data:

        Returns:

        """
        self.start_time = date.fromisoformat(data.get("from"))
        self.end_time = date.fromisoformat(data.get("to"))

    def dict_factory(self):
        record = dict()
        for field in fields(self.__class__):
            if field.name in ["type"]:
                record[field.name] = self.type.value
            else:
                record[field.name] = getattr(self, field.name)


    def get_full_location(self) -> str:
        res = ""
        if self.location:
            res += self.location
        if self.country:
            res += f", {self.country}"
        return res


class Conference(Event):
    """
    academic Conference
    """


class Workshop(Event):
    """
    academic workshop
    """
    is_colocated_with: Optional[Conference] = None


@dataclass
class Proceedings:
    """
    proceedings of scholarly articles
    """
    title: Optional[str] = None
    event: Optional[List[Event]] = None
    editor: Optional[List[Scholar]] = None
    publication_date: Optional[datetime] = None


class CustomDict(dict):
    def __init__(self, data):
        res = []
        for field, value in data:
            if isinstance(value, EventType):
                value = value.value
            elif isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, date):
                value = value.isoformat()
            res.append((field, value))
        super().__init__(x for x in res if x[1] is not None)