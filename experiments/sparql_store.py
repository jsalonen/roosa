import rdfextras
import rdflib

store=rdfextras.store.SPARQL.SPARQLStore("http://dbpedia.org/sparql")
app.g=rdflib.Graph(store)
app.nss = \
    dict(
         dc=Namespace("http://purl.org/dc/elements/1.1/"),
         rdf=Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
         owl=Namespace("http://www.w3.org/2002/07/owl#"),
         vin=Namespace("http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#"),
         dbpedia=Namespace("http://dbpedia.org/resource/")
    )
