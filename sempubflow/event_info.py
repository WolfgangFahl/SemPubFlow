'''
Created on 2023-06-22

@author: wf
'''
from sempubflow.homepage import Homepage
import json
class EventInfo:
    """
    check the event metadata
    """
    
    def __init__(self,llm):
        self.llm=llm
        self.text=None
        self.homepage=None
        self.chars=0
        self.lines=0
        
    def status_msg(self)->str:
        if self.text:
            self.chars=len(self.text)
            self.lines=self.text.count('\n')
            result=f"✅ {self.lines} lines and {self.chars} chars"
        else:
            result="❌"
        return result
        
    def get_meta_data(self,url):
        """
        get the metadata for the given url
        """
        self.homepage=Homepage(url)
        self.text=self.homepage.get_text()
        result_dict={}
        if self.llm.available():
            prompt=f""""provide title acronym location and time of event in json format using the template {{
      "title": Second International Symposium on Wearable Computers",
      "ordinal": 24,
      "acronym: ISWC 1998",
      "location": "Pittsburgh",
      "homepage": ""
      "proceedings-doi": "https://doi.org/10.1109/ISWC.1998"
      "iso-code": "US",
      "region": "PA",
      "country": "US",
      "start_date": "1998-10-19",
      "end_date": "1998-10-20",
      }}  described by the following text:{self.text}"""
            result_str=self.llm.ask(prompt)
            result_dict=json.loads(result_str)
            return result_dict
        