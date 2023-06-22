'''
Created on 2023-06-23

@author: wf
'''
import openai
import os

class LLM:
    """
    large language model
    """
    
    def __init__(self,api_key:str=None,model="gpt-3.5-turbo"):
        """
        constructor
        
        Args:
            api_key(str): the access key
            model(str): the model to use
        """
        self.model=model
        if api_key is None:
            api_key=os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key
        
    def available(self):
        """
        check availability of API by making sure there is an api_key
        
        Returns:
            bool: True if the Large Language Model is available
        """
        return openai.api_key is not None
        
    def ask(self,prompt:str)->str:
        """
        ask a prompt
        
        Args:
            prompt(str)
        Returns:
            str: the answer
        """
        chat_completion = openai.ChatCompletion.create(model=self.model, messages=[{"role": "user", "content": prompt}])
        result=chat_completion.choices[0].message.content
        return result
        
