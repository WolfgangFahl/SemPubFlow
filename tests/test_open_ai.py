'''
Created on 2023-06-21

@author: wf
'''
from ngwidgets.basetest import Basetest
from sempubflow.llm import LLM
from sempubflow.event_info import EventInfo
import unittest
import openai

class TestOpenAi(Basetest):
    """
    test https://github.com/openai/openai-python library
    """
    
    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.llm=LLM()
        
    @unittest.skipIf(Basetest.inPublicCI(), "chatgpt")
    def testOpenAI(self):    
        # list models
        models = openai.Model.list()
        for model in models.data:
            if self.debug:
                print(model)
        pass

    
    @unittest.skipIf(Basetest.inPublicCI(), "chatgpt")
    def testChatGpt(self):
        """
        test the chatgpt interface
        """
        result=self.llm.ask("What's your model version?")
        debug=True
        if debug:
            print(result)
        self.assertTrue("OpenAI" in result)
            
    @unittest.skipIf(Basetest.inPublicCI(), "event info")
    def testEventInfo(self):
        """
        test getting event information
        """
        event_info=EventInfo(self.llm)
        url="https://escape33-ath.gr/"
        for model in ["gpt-3.5-turbo","gpt-4"]:
            result=event_info.get_meta_data(url,model=model)
            #url="https://www.wp-cape.eu/index.php/resources/escape-series/"
            #for all parts of the series 
            debug=True
            if debug:
                print(result)