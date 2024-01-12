"""
Created on 2023-06-22

@author: wf
"""
from sempubflow.llm import LLM
from sempubflow.homepage import Homepage
from sempubflow.event import Event

class EventInfo:
    """
    check the event metadata
    """

    def __init__(self, llm, debug:bool=False):
        """
        construct me with the given llm
        
        Args:
            llm(LLM): the large language model to use
        """
        self.llm = llm
        self.text = None
        self.homepage = None
        self.debug=debug
        self.chars = 0
        self.lines = 0
        self.prompt_prefix="""
        provide the event signature elements:
- Acronym: The short name of the conference, often in uppercase.
- Frequency: How often the event occurs, like annual or biennial.
- Event reach: The geographical or demographic reach of the event, like International or European.
- Event type: The format of the event, such as Conference, Workshop, or Symposium.
- Year: The year in which the event takes place.
- Ordinal: The instance number of the event, like 18th or 1st.
- Date: The start and end date or date range of the event.
- Location: The country, region, and city of the event, and sometimes specific venue details.
- Title: The full title of the event, often indicating the scope and subject.
- Subject: The main topic or focus of the event.

in YAML Format.
use lowercase/underscore for the element names and leave out elements hat are not found. 
Use ISO date format for dates. 
Use start_date and end_date as field names. 
Give the year as a 4 digit integer.
Give the location as country/region and city
Give the country using a 2 digit ISO 3166-1 alpha-2 code
Give the region using ISO_3166-2 code
Give the city with it's english label 
Answer with the raw yaml only with no further comments outside the yaml. If you must comment use a comments field.
Do not add any fields beyond the given list above.
Stick to the requested fields only, and never ever add any extra information.

valid answers e.g. would look like
# AVICH 2022
acronym: "AVICH 2022"
event_type: "Workshop"
year: 2022
start_date: "2022-06-06"
end_date: "2022-06-10"
country: "IT"  # Italy
region: "IT-62"   # Lazio
city: "Frascati"
title: "Workshop on Advanced Visual Interfaces and Interactions in Cultural Heritage"
subject: "Advanced Visual Interfaces and Interactions in Cultural Heritage"

# BMAW 2024
acronym: "BMAW 2014"
frequency: "Annual"
event_reach: "International"
event_type: "Workshop"
year: 2014
country: "NL"  # Netherlands
region: "NL-NH" # Noord-Holland
city: "Amsterdam"
title: "Bayesian Modeling Applications Workshop"
subject: "Bayesian Modeling Applications"
  
# LM-KBC 2023  
acronym: "LM-KBC 2023"
event_type: "Challenge"
ordinal: 2
title: "Language Models for Knowledge Base Construction"
subject: "Knowledge Base Construction"
year: 2023
start_date: "2023-11-01"
end_date: "2023-11-01"
country: "GR"  # Greece
region: "GR-I"  # Attica
city: "Athens"  

Extract as instructed from the following homepage text:
"""

    def status_msg(self) -> str:
        """
        provide a status message
        """
        if self.text:
            self.chars = len(self.text)
            self.lines = self.text.count("\n")
            result = f"✅ {self.lines} lines and {self.chars} chars"
        else:
            result = "❌"
        return result

    def get_event_metadata_from_homepage(self, homepage:Homepage=None, model:str=LLM.DEFAULT_MODEL,temperature:float=0.0):
        """
        get the metadata for the given homepage
        """
        self.homepage=homepage
        self.text = self.homepage.get_text()
        event=None
        if self.llm.available():
            prompt_text=f"{self.prompt_prefix}\n{self.text}"
            yaml_str=self.llm.ask(prompt_text,model=model,temperature=temperature)
            if self.debug:
                print (f"{self.homepage.volume}:\n{yaml_str}")
            event=Event.from_yaml(yaml_str)
        return event 
   
