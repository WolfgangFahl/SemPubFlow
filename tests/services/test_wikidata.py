import unittest

from sempubflow.models.scholar import Scholar, ScholarSearchMask
from sempubflow.services.wikidata import Wikidata
from ngwidgets.basetest import Basetest


class TestDblp(Basetest):
    """
    test Wikidata
    """

    def test_get_scholar_suggestions(self):
        """
        test suggestion of scholars from wikidata endpoint
        """
        search_mask = ScholarSearchMask(given_name="Ste", family_name="Decke")
        scholars = Wikidata(endpoint_url="http://qlever-api.wikidata.dbis.rwth-aachen.de/").get_scholar_suggestions(search_mask)
        self.assertGreaterEqual(len(scholars), 5)
        self.assertIsInstance(scholars[0], Scholar)
        self.assertIn("d/StefanDecker", [scholar.dblp_author_id for scholar in scholars])
        self.assertIn("0000-0001-6324-7164", [scholar.orcid_id for scholar in scholars])
        self.assertIn("Q54303353", [scholar.wikidata_id for scholar in scholars])

