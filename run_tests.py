import os
import unittest
import signal
import subprocess
import requests
import json

DATA_NEW_WINERY_IN_JSON = """
{
  "data": [
    [
      "rdf:type",
      "vin:Winery"
    ],
    [
      "dc:title",
      "A new winery"
    ]
  ],
  "backlinks": [
    [
      "vin:KathrynKennedy",
      "vin:hasMaker"
    ]
  ]
}
"""

DATA_WINERY_NEW_TRIPLES = """
{
    "data": [
        ["dc:title", "This is new title"]
    ],
    "backlinks": [] 
}
"""

class testRestfulRDFAPI(unittest.TestCase):
    """
    A test class for REST API
    """

    def setUp(self):
        self.api_url = 'http://localhost:8080/api/instances/'
        self.server_process = subprocess.Popen(['python', 'roosa.py'])

    def testGetJson(self):
        url = '%svin:Winery' % self.api_url
        headers = {"accept": "application/json; application/xml;q=0.9"}
        r = requests.get(url, headers=headers)
        assert( r.status_code == 200 ) # OK
        assert( r.headers['content-type'] == 'application/json' )
        assert( json.loads(r.text) )

    def testGetNotFound(self):
        url = '%sunknownNamespace:NonExistingResource' % self.api_url
        headers = {"accept": "application/json; application/xml;q=0.9"}
        r = requests.get(url, headers=headers)
        assert( r.status_code == 404 ) # NOT FOUND

    def testDelete(self):
        url = '%svin:KathrynKennedy' % self.api_url

        # GET should succeed before DELETE
        r = requests.get(url)
        assert( r.status_code == 200 ) # OK

        # DELETE 
        r = requests.delete(url)
        assert( r.status_code == 200 ) # DELETED

        # GET should fail now
        r = requests.get(url)
        assert( r.status_code == 404 ) # NOT FOUND

    def testPutNew(self):
        url = '%svin:NewWinery' % self.api_url

        # GET should fail before PUT
        r = requests.get(url)
        assert( r.status_code == 404 ) # NOT FOUND

        # PUT
        data = DATA_NEW_WINERY_IN_JSON
        headers = {"content-type": "application/json"}
        r = requests.put(url, data, headers=headers)
        assert( r.status_code == 200 ) # OK

        # GET should succeed now
        r = requests.get(url)
        assert( r.status_code == 200 ) # OK

    def testPutOverride(self):
        url = '%svin:SomeOtherWinery' % self.api_url

        DATA_ORIGINAL = """
            {
                "data": [
                    ["dc:title", "Original title"]
                ],
                "backlinks": [
                    [ "vin:KathrynKennedy", "vin:hasMaker"]
                ]
            }"""

        DATA_OVERRIDE = """
            {
                "data": [
                    ["dc:description", "Only description"]
                ],
                "backlinks": [
                    [ "vin:KathrynKennedy", "vin:hadMaker"]
                ]   
            }"""

        # 2x PUT
        headers = {"content-type": "application/json"}
        r = requests.put(url, DATA_ORIGINAL, headers=headers)
        r = requests.put(url, DATA_OVERRIDE, headers=headers)

        # GET
        r = requests.get(url, headers={"accept": "application/json"})
        data_back = json.loads(r.text)
        data_back_match = json.loads(DATA_OVERRIDE)
        assert ( data_back == data_back_match )

    def testPutNewBadJson(self):
        # PUT
        url = '%svin:NewWinery2' % self.api_url
        data = DATA_NEW_WINERY_IN_JSON
        headers = {"content-type": "application/json"}
        r = requests.put(url, data+'invalidjson', headers=headers)
        assert( r.status_code == 400 ) # BAD REQUEST

    def testPutNewBadContentType(self):
        # PUT
        url = '%svin:NewWinery3' % self.api_url
        headers = {"content-type": "application/unsupported-type"}
        data = 'placeholder for data'
        r = requests.put(url, data, headers=headers)
        assert( r.status_code == 400 ) # BAD REQUEST

    def testPost(self):
        # POST
        url = '%svin:Winery' % self.api_url     
        data = DATA_WINERY_NEW_TRIPLES
        headers = {"content-type": "application/json"}
        r = requests.post(url, data, headers=headers)
        assert( r.status_code == 200 ) # OK

        # GET
        headers = {"accept": "application/json; application/xml;q=0.9"}
        r = requests.get(url, headers=headers)
        assert( r.status_code == 200 ) # OK
        assert( r.headers['content-type'] == 'application/json' )
        data_back = json.loads(r.text)

        # Data should contain both old data + new data from post
        for p, o in data_back['data']:
            if p == u'dc:title':
                assert( o == u'This is new title' )
            if p == u'rdf:type':
                assert( o == u'owl:Class' )
        assert( len(data_back['data']) > 1 )

    def tearDown(self):
        # TODO: kill doesn't always work as expected
        os.kill(self.server_process.pid, signal.SIGTERM)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testRestfulRDFApi))
    return suite

if __name__ == '__main__':
    unittest.main()
