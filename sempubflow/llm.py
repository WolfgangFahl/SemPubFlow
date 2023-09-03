'''
Created on 2023-06-23

@author: wf
'''
import json
import openai
import os
from pathlib import Path

class LLM:
    """
    large language model
    """
    
    def __init__(self,api_key:str=None,model="gpt-3.5-turbo",force_key:bool=False):
        """
        constructor
        
        Args:
            api_key(str): the access key
            model(str): the model to use
        """
        self.model=model
        # Load the API key from the environment or a JSON file
        openai_api_key = os.getenv('OPENAI_API_KEY')
        json_file = Path.home() / ".openai" / "openai_api_key.json"

        if openai_api_key is None and json_file.is_file():
            with open(json_file, "r") as file:
                data = json.load(file)
                openai_api_key = data.get('OPENAI_API_KEY')

        if openai_api_key is None:
            if force_key:
                raise ValueError("No OpenAI API key found. Please set the 'OPENAI_API_KEY' environment variable or store it in `~/.openai/openai_api_key.json`.")
            else:
                return
        # set the global api key
        openai.api_key=openai_api_key
        
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
