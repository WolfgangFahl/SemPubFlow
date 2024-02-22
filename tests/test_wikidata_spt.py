"""
Created on 2023-12-27

@author: wf
"""
import json
import os

from lodstorage.sparql import SPARQL
from ngwidgets.basetest import Basetest

from sempubflow.homepage import Homepage
from sempubflow.sync import Sync, SyncPair


class VolumeList:
    """
    a list of CEUR-WS Volume Proceedings
    """

    def __init__(self):
        # see also https://cr.bitplan.com/index.php/Q0.1
        self.sparql_query = """# CEUR-WS Proceedings Volumes
# Wolfgang Fahl - 2023-12-27
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX schema: <http://schema.org/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sVolume ?volume ?proceeding ?proceedingLabel ?ppnId ?urn ?dblpPublicationId
WHERE {
   # Instance of Proceedings
   ?proceeding wdt:P31 wd:Q1143604.
   # with english label
   ?proceeding rdfs:label ?proceedingLabel.
   FILTER(LANG(?proceedingLabel) = "en")
   # Part of the series
   ?proceeding p:P179 ?partOfTheSeries.
   # CEUR Workshop proceedings
   ?partOfTheSeries ps:P179 wd:Q27230297.
    # Volume via volume property
   OPTIONAL { ?proceeding p:P478 ?volume. }
   # Volumes via a a qualifier of the part of the series relation
   OPTIONAL { ?partOfTheSeries pq:P478 ?sVolume. }
   # K10plus PPN ID
   OPTIONAL{?proceeding wdt:P6721 ?ppnId.}
   # URN-NBN
   OPTIONAL{?proceeding wdt:P4109 ?urn.}
   # dlbp Publication Id
   OPTIONAL{?proceeding wdt:P8978 ?dblpPublicationId.}
} 
ORDER BY DESC (xsd:integer(?sVolume))"""
        endpoint_url = "https://query.wikidata.org/sparql"
        self.sparql = SPARQL(endpoint_url)

    def query(self):
        lod = self.sparql.queryAsListOfDicts(self.sparql_query)
        return lod

    def get_qid(self, wd_record: dict) -> str:
        """
        get the wikidata id of the wikidata record
        """
        qid = None
        if wd_record and "proceeding" in wd_record:
            proc_url = wd_record["proceeding"]
            qid = proc_url.replace("http://www.wikidata.org/entity/", "")
        return qid


class TestWikidataSpt(Basetest):
    """
    test CEUR-WS wikidata entries against the single point of truth
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.ceurws_path = os.path.expanduser("~/.ceurws")
        self.volumes_path = os.path.join(self.ceurws_path, "volumes.json")
        self.dblp_volumes_path = os.path.join(self.ceurws_path, "dblp/volumes.json")
        self.volumes = self.get_volumes()
        self.volume_list = VolumeList()

    def get_from_json(self, file_path):
        # Path to the volumes.json file
        # Ensure the file exists
        if not os.path.exists(file_path):
            return None
        # Read the JSON data
        with open(file_path, "r") as file:
            lod = json.load(file)
        return lod

    def get_volumes(self):
        lod = self.get_from_json(self.volumes_path)
        return lod

    def show_ceur_ws_pages(self, sync: Sync, direction: str):
        """
        Show pages from CEUR-WS volumes based on the synchronization direction.
        """
        vol_nrs = sync.get_keys(direction)
        vol_nrs = sorted(vol_nrs, key=lambda x: int(x))  # Sort keys as integers

        # Determine which data list and key to use based on direction
        data_list = sync.pair.r_data if direction == "←" else sync.pair.l_data
        data_key = sync.pair.r_key if direction == "←" else sync.pair.l_key

        for index, vol_nr in enumerate(vol_nrs):
            # Find the record in the appropriate data list
            record = next(
                (item for item in data_list if item[data_key] == vol_nr), None
            )
            url = f"https://ceur-ws.org/Vol-{vol_nr}"

            # Get URL or other info from the record if available
            wd_url = record.get("proceeding", "?") if record else "?"
            homepage = Homepage(vol_nr, url=url)
            text = homepage.get_text()
            short_text = text[:40] if text else "?"

            print(f"{index} {vol_nr:4}:{url} {short_text}\n{wd_url}")

    def show_sync(
        self, pair: SyncPair, tablefmt="github", debug: bool = False, key_type=str
    ):
        """
        Perform the synchronization and display the synchronization status.
        Args:
            pair (SyncPair): The pair containing the data and configuration for synchronization.
            tablefmt (str): The table format for the status table.
            debug (bool): Flag to turn on debug information.
            key_type (type): The type of the keys used for sorting (e.g., int, str).
        """
        sync = Sync(pair)
        print(pair.title)
        if debug:
            print(f"found {len(pair.l_data)} {pair.r_name} records")
            print(f"found {len(pair.r_data)} {pair.l_name} records")
        if debug:
            print(json.dumps(pair.l_data[:2], indent=2))
            print(json.dumps(pair.r_data[:2], indent=2))

        print(
            sync.status_table(tablefmt=tablefmt)
        )  # This will print out the synchronization status

        for direction in sync.directions:
            keys = sync.get_keys(direction)
            sorted_keys = sorted(
                keys, key=lambda x: key_type(x)
            )  # Sort keys as integers
            print(f"Keys for direction {direction}: {sorted_keys}")

        return sync

    def get_unused_volumes(self):
        # Assume self.volumes is already populated with volume data
        # Find the maximum volume number
        max_volume_number = max(v["number"] for v in self.volumes)

        # Generate the full set of volume numbers from 1 to max
        full_volume_set = set(range(1, max_volume_number + 1))

        # Extract the set of existing volume numbers
        existing_volumes = set(v["number"] for v in self.volumes)

        # Find missing volumes by subtracting the existing volumes from the full set
        missing_volumes = full_volume_set - existing_volumes

        print("Unused volume numbers:", missing_volumes)

    def get_valid_volumes(self):
        valid_volumes = self.filter_valid_volumes(self.volumes)
        return valid_volumes

    def filter_valid_volumes(self, lod, key: str = "number"):
        special_cases = {
            "2284": "Volume MLSA-2018 deleted upon editor request, 2019-02-28 ",
            "3021": "The volume number 3021 is not used by CEUR-WS.org",
        }
        # Remove any volumes that are in the special cases
        # Adapt the local volumes to have 'number_str' entry
        valid_volumes = []
        for volume in lod:
            if str(volume[key]) not in special_cases:
                # Add 'number_str' as a string representation of 'number'
                volume["number_str"] = str(volume[key])
                valid_volumes.append(volume)
        return valid_volumes

    def testUnusedVolumesNumbers(self):
        self.get_unused_volumes()

        invalid_volumes = [v["number"] for v in self.volumes if not v["valid"]]
        print(invalid_volumes)

    def testIdSync(self):
        """
        test id sync
        """
        valid_volumes = self.get_valid_volumes()

        # Fetch the volume records from the SPARQL query
        wd_volumes = self.volume_list.query()

        # Example keys for volumes, adjust as necessary based on actual data structure
        wd_key = "sVolume"
        lc_key = "number_str"

        # Create an instance of SyncPair and Sync class
        pair = SyncPair(
            title="Volume Synchronization",
            l_name="local",
            r_name="wikidata",
            l_data=valid_volumes,
            r_data=wd_volumes,
            l_key=lc_key,
            r_key=wd_key,
        )
        sync = self.show_sync(pair, debug=True, key_type=int)

        self.show_ceur_ws_pages(sync, "→")
        self.show_ceur_ws_pages(sync, "←")

    def test_dblp_sync(self):
        """
        test dblp synchronization
        """
        dblp_volumes = self.get_from_json(self.dblp_volumes_path)
        dblp_volumes = [
            {
                k: v.replace("https://dblp.org/rec/", "")
                if k == "dblp_publication_id"
                else v
                for k, v in d.items()
            }
            for d in dblp_volumes
        ]
        dblp_volumes = self.filter_valid_volumes(dblp_volumes, "volume_number")
        # Fetch the volume records from the SPARQL query
        wd_volumes = self.volume_list.query()
        dblp_key = "dblp_publication_id"
        wd_key = "dblpPublicationId"
        # "https://dblp.org/rec/conf/eumas/2006"

        pair = SyncPair(
            title=f"{dblp_key} Synchronization",
            l_name="dblp",
            r_name="wikidata",
            l_data=dblp_volumes,
            r_data=wd_volumes,
            l_key=dblp_key,
            r_key=wd_key,
            l_pkey="volume_number",
            r_pkey="sVolume",
        )
        sync = self.show_sync(pair, debug=True)
        dblp_ids = sync.get_keys("→")
        for dblp_id in dblp_ids:
            dblp_record = sync.get_record_by_key("left", dblp_id)
            if dblp_record:
                vol_number = str(dblp_record["volume_number"])
                print(f"Volume {vol_number}")
                wd_record = sync.get_record_by_pkey("right", vol_number)
                qid = self.volume_list.get_qid(wd_record)
                if qid:
                    print(f'''wd add-claim {qid} P8978 "{dblp_id}"''')

    def test_urn_checkdigits(self):
        """ """

    def test_urn_sync(self):
        """
        test synching by urn
        """
        valid_volumes = self.get_valid_volumes()

        # Fetch the volume records from the SPARQL query
        wd_volumes = self.volume_list.query()
        pair = SyncPair(
            title=f"CEUR-WS urn Synchronization",
            l_name="CEUR-WS",
            r_name="wikidata",
            l_data=valid_volumes,
            r_data=wd_volumes,
            l_key="urn",
            r_key="urn",
            l_pkey="number_str",
            r_pkey="sVolume",
        )
        sync = self.show_sync(pair, debug=True, tablefmt="latex")
        urn_ids = sync.get_keys("→")
        for urn_id in urn_ids:
            urn_record = sync.get_record_by_key("left", urn_id)
            if urn_record:
                vol_number = urn_record["number_str"]
                print(f"Volume {vol_number}")
                wd_record = sync.get_record_by_pkey("right", vol_number)
                qid = self.volume_list.get_qid(wd_record)
                if qid:
                    print(f'''wd add-claim {qid} P4109 "{urn_id}"''')
