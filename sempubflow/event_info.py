'''
Created on 2023-06-22

@author: wf
'''
from sempubflow.homepage import Homepage
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
        result=None
        if self.llm.available():
            prompt=f""""provide title acronym location and time of event in json format using the template {{
      "title": 24th International Conference on Semantic Web",
      "ordinal": 24,
      "acronym: ISWC 2013",
      "location": "New York",
      "homepage": ""
      "iso-code": "US",
      "region": "NY",
      "country": "US",
      "start_date": "2013-05-07",
      "end_date": "2013-05-09",
      }}  described by the following text:{self.text}"""
            result=self.llm.ask(prompt)
            return result
        