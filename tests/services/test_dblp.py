import unittest

from sempubflow.models.scholar import Scholar, ScholarSearchMask
from sempubflow.services.dblp import Dblp
from ngwidgets.basetest import Basetest


class TestDblp(Basetest):
    """
    test Dblp
    """

    def test_get_scholar_suggestions(self):
        """
        test suggestion of scholars from dblp endpoint
        """
        search_mask = ScholarSearchMask(given_name="Ste", family_name="Decke")
        scholars = Dblp().get_scholar_suggestions(search_mask)
        self.assertGreaterEqual(len(scholars), 11)
        self.assertIsInstance(scholars[0], Scholar)
        dblp_ids = [scholar.dblp_author_id for scholar in scholars]
        self.assertIn("d/StefanDecker", dblp_ids)


if __name__ == '__main__':
    unittest.main()
