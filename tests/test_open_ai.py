'''
Created on 2023-06-21

@author: wf
'''
from tests.basetest import Basetest
import openai
import os

class TestOpenAi(Basetest):
    """
    test https://github.com/openai/openai-python library
    """
    
    def testChatGpt(self):
        """
        test the chatgpt interface
        """
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
        # list models
        models = openai.Model.list()
        
        # print the first model's id
        print(models.data[0].id)
        
        # create a chat completion
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
        
        # print the chat completion
        print(chat_completion.choices[0].message.content)
            
    