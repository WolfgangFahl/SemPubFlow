"""
Created on 2023-07-14

@author: wf
"""
import os
import json
from typing import Optional

from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session


class ORCIDAuth:
    """A class for handling ORCID API authentication.

    Attributes:
        config_path (str): The path to the configuration file with client id and secret.
        client_id (str): The client id for the ORCID API.
        client_secret (str): The client secret for the ORCID API.
        base_url (str): The base url for the ORCID API.
        token_url (str): The url to get the access token.
        client (BackendApplicationClient): The OAuth2 client.
        oauth (OAuth2Session): The OAuth2 session.
        token (dict): The access token.
    """

    def __init__(self, client_id=None, client_secret=None, sandbox=True):
        """Initializes the ORCIDAuth object.

        If client_id or client_secret is None, they are loaded from a local JSON configuration file.

        Args:
            client_id (str, optional): The client id for the ORCID API. Defaults to None.
            client_secret (str, optional): The client secret for the ORCID API. Defaults to None.
            sandbox (bool, optional): Whether to use the sandbox base url or the production base url. Defaults to True.
        """
        self.config_path = os.path.join(os.path.expanduser('~'), '.orcid', 'sempubflow.json')
        if not client_id or not client_secret:
            self.load_config()
        else:
            self.client_id = client_id
            self.client_secret = client_secret
        self.base_url = 'https://sandbox.orcid.org' if sandbox else 'https://orcid.org'
        self.token_url = f'{self.base_url}/oauth/token'
        self.client = BackendApplicationClient(client_id=self.client_id)
        self.oauth: Optional[OAuth2Session] = None
        self.token = None
        
    def open(self):    
        """
        open a session
        """
        self.oauth = OAuth2Session(client=self.client)
        self.token = self.get_token()

    def load_config(self):
        """Loads the client id and secret from a local JSON configuration file."""

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            self.client_id = config.get('client_id')
            self.client_secret = config.get('client_secret')
        except FileNotFoundError:
            print(f"Config file not found at {self.config_path}")
            exit(1)

    def get_token(self):
        """Fetches the access token from the ORCID API.

        Returns:
            dict: The access token.
        """

        token = self.oauth.fetch_token(
                token_url=self.token_url,
                auth=HTTPBasicAuth(self.client_id, self.client_secret)
        )
        return token

    def get_authorization_url(self, redirect_uri):
        """Gets the authorization URL.

        Args:
            redirect_uri (str): The redirect URI.

        Returns:
            tuple: The authorization URL and the state.
        """

        authorization_url, state = self.oauth.authorization_url(self.token_url, redirect_uri=redirect_uri)
        return authorization_url, state

    def fetch_token(self, authorization_response, redirect_uri):
        """Fetches the access token using the authorization response.

        Args:
            authorization_response (str): The authorization response.
            redirect_uri (str): The redirect URI.

        Returns:
            dict: The access token.
        """

        token = self.oauth.fetch_token(self.token_url,
                                       authorization_response=authorization_response,
                                       redirect_uri=redirect_uri)
        return token

    def get(self, url, **kwargs):
        """Sends a GET request to the ORCID API.

        Args:
            url (str): The API URL.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The API response.
        """

        return self.oauth.get(url, **kwargs)
