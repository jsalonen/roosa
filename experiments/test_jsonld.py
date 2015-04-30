from rdflib import Graph, plugin
from rdflib.serializer import Serializer

testrdf = '''@prefix dc: <http://purl.org/dc/terms/> .
<http://example.org/about> dc:title "Someone's Homepage"@en .'''

g = Graph().parse(data=testrdf, format='n3')

print(g.serialize(format='json-ld', indent=4))
