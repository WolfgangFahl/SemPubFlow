'''
Created on 2023-06-19

@author: wf
'''
import os
import orjson
import urllib
from pathlib import Path

class JsonCacheManager():
    """
    a json based cache manager
    """
    def __init__(self,base_url:str="http://cvb.bitplan.com"):
        """
        constructor
        
        base_url(str): the base url to use for the json provider
        """
        self.base_url=base_url
        
    def json_path(self,lod_name:str)->str:
        """
        get the json path for the given list of dicts name
        
        Args:
            lod_name(str): the name of the list of dicts cache to read
            
        Returns:
            str: the path to the list of dict cache
        """
        root_path=f"{Path.home()}/.ceurws"
        os.makedirs(root_path, exist_ok=True)
        json_path=f"{root_path}/{lod_name}.json"
        return json_path
        
    def load_lod(self,lod_name:str)->list:
        """
        load my list of dicts
        
        Args:
            lod_name(str): the name of the list of dicts cache to read
            
        Returns:
            list: the list of dicts
        """
        json_path=self.json_path(lod_name)
        if os.path.isfile(json_path):
            try:
                with open(json_path) as json_file:
                    json_str=json_file.read()
                    lod = orjson.loads(json_str)
            except Exception as ex:
                msg=f"Could not read {lod_name} from {json_path} due to {str(ex)}"
                raise Exception(msg)
        else:
            try:
                url=f"{self.base_url}/{lod_name}.json"
                with urllib.request.urlopen(url) as source:
                    json_str=source.read()
                    lod = orjson.loads(json_str)
            except Exception as ex:
                msg=f"Could not read {lod_name} from {url} due to {str(ex)}"
                raise Exception(msg)
        return lod

    def store(self,lod_name:str,lod:list):
        """
        store my list of dicts
        
        Args:
            lod_name(str): the name of the list of dicts cache to write
            lod(list): the list of dicts to write
        """
        with open(self.json_path(lod_name), 'wb') as json_file:
            json_str=orjson.dumps(lod)
            json_file.write(json_str)
            pass