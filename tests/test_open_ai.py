'''
Created on 2023-06-21

@author: wf
'''
from tests.basetest import Basetest
from sempubflow.homepage import Homepage
import openai
import os

class TestOpenAi(Basetest):
    """
    test https://github.com/openai/openai-python library
    """
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def testChatGpt(self):
        """
        test the chatgpt interface
        """
        if self.inPublicCI():
            return
    
        # list models
        models = openai.Model.list()
        
        # print the first model's id
        print(models.data[0].id)
        
        # create a chat completion
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
        
        # print the chat completion
        print(chat_completion.choices[0].message.content)
            
    def testEventInfo(self):
        """
        """
        url="https://escape33-ath.gr/"
        homepage=Homepage(url)
        text=homepage.get_text()
        prompt=f""""provide title acronym location and time of event in json format using the template {{
  "title": 24th International Conference on Semantic Web",
  "acronym: ISWC 2013",
  "location": "New York",
  "iso-code": "US",
  "region": "NY",
  "country": "US",
  "start_date": "2013-05-07",
  "end_date": "2013-05-09",
  }}  described by the following text:{text}"""
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        print(chat_completion.choices[0].message.content)