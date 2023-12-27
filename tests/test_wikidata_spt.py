"""
Created on 2023-12-27

@author: wf
"""
from ngwidgets.basetest import Basetest
from lodstorage.sparql import SPARQL

class VolumeList:
    """
    a list of CEUR-WS Volume Proceedings
    """
    def __init__(self):
        # see also https://cr.bitplan.com/index.php/Q0.1
        self.sparql_query="""# CEUR-WS Proceedings Volumes
# Wolfgang Fahl - 2023-12-27
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX schema: <http://schema.org/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sVolume ?proceeding ?proceedingLabel ?ppnId ?urn ?dblpPublicationId
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
   # Volumes via a a qualifier of the part of the series relation
   ?partOfTheSeries pq:P478 ?sVolume.
   # K10plus PPN ID
   OPTIONAL{?proceeding wdt:P6721 ?ppnId.}
   # URN-NBN
   OPTIONAL{?proceeding wdt:P4109 ?urn.}
   # dlbp Publication Id
   OPTIONAL{?proceeding wdt:P8978 ?dblpPublicationId.}
} ORDER BY DESC (xsd:integer(?sVolume))"""
        endpoint_url="https://query.wikidata.org/sparql"
        self.sparql=SPARQL(endpoint_url)
        
    def query(self):
        lod=self.sparql.queryAsListOfDicts(self.sparql_query)
        return lod

class TestWikidataSpt(Basetest):
    """
    test CEUR-WS wikidata entries against the single point of truth
    """

    def testIdSync(self):
        """
        test id sync
        """
        volume_list=VolumeList()
        volume_records=volume_list.query()
        print (f"found {len(volume_records)} volumes")
        
