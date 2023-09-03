'''
Created on 2023-07-14

@author: wf
'''
from tests.basetest import Basetest
import os
from sempubflow.orcid_auth import ORCIDAuth


class TestORCIDAuth(Basetest):
    """Unit test suite for testing the ORCIDAuth class.
    
    Attributes:
        config_path (str): The path to the configuration file with client id and secret.
    """

    def setUp(self):
        """Set up test fixtures, if any."""
        super().setUp()
        self.config_path = os.path.join(os.path.expanduser('~'), '.orcid', 'sempubflow.json')

    def test_load_config(self):
        """Test if the client_id and client_secret are loaded correctly from the configuration file.

        The test only runs if the configuration file is available.
        """
        if os.path.isfile(self.config_path):
            auth = ORCIDAuth()
            self.assertTrue(hasattr(auth, 'client_id'))
            self.assertTrue(hasattr(auth, 'client_secret'))

    def test_authentication(self):
        """Test if the authentication process successfully obtains a token.

        The test only runs if the configuration file is available.
        """
        if os.path.isfile(self.config_path):
            for sandbox in [True,False]:
                with self.subTest(f"sandbox {sandbox}",sandbox=sandbox):
                    auth = ORCIDAuth(sandbox)
                    auth.open()
                    self.assertIsNotNone(auth.token)

    def test_expanded_search(self):
        """
        tests expanded-seachr api
        """
        import requests

        url = "https://pub.orcid.org/v3.0/expanded-search/?q=family-name=Decker+AND+given-name=Stefan&rows=7"
        auth = ORCIDAuth()
        payload = {}
        headers = {'Authorization': auth.client_secret}

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

if __name__ == "__main__":
    TestORCIDAuth().run()

