""" Roosa - A RESTful Ontology Server and Applications """
__author__ = "Jaakko Salonen, Juha Nurmi"
__copyright__ = "Copyright 2012, Jaakko Salonen, Juha Nurmi"
__version__ = "0.2.0"
__license__ = "MIT"
__status__ = "Prototype"

from flask import Flask, Blueprint, url_for, render_template, Response, make_response, request
from flask_rest import RESTResource
from rdflib import Graph, Namespace, plugin, query
from rdflib.serializer import Serializer
from curie import uri2curie, curie2uri

import os
import xml.etree.ElementTree # If I don't load this here I get error: AttributeError: 'module' object has no attribute 'ElementTree'
import rdflib
import json
import mimetypes

# Register RDFLib plugins
plugin.register('sparql', query.Processor, 'rdfextras.sparql.processor', 'Processor')
plugin.register('sparql', query.Result, 'rdfextras.sparql.query', 'SPARQLQueryResult')
plugin.register('sparql', query.Result, 'rdfextras.sparql.query', 'SPARQLQueryResult')

app = Flask(__name__)
app.REST_API_URL = 'http://localhost/api/resources/'
app.g = Graph()
app.debug = True
app.nss = \
    dict(
         dc=Namespace("http://purl.org/dc/elements/1.1/"),
         rdf=Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
         owl=Namespace("http://www.w3.org/2002/07/owl#"),
         vin=Namespace("http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#")
    )
app.g.parse('data/wine.rdf')

def serve_file(filepath):
    with open('./public/'+filepath, "r") as f:
        (mimetype_prefix, mimetype_suffix) = mimetypes.guess_type(filepath)
        text = f.read()
    return Response(text, mimetype=mimetype_prefix)

@app.route('/<path:filepath>')
def public(filepath):
    try:
        return serve_file(filepath)
    except IOError:
        try:
            return serve_file(filepath+'index.html')
        except IOError:
            current = ''
            parts = filepath.split('/')
            for part in parts:
                current += part+'/'
                try:
                    print "serve_file(%s)" % current
                    return serve_file(current)
                except IOError:
                    pass
                try:
                    print "serve_file(%sindex.html)" % current
                    return serve_file(current+'index.html')
                except IOError:
                    pass
            return "Not Found", 404

@app.route('/')
def index():
    return public('index.html')

@app.route("/graph/<apicall>")
def graph(apicall):
    f = open('./client/index.html', "r")
    text = f.read()
    f.close()
    return text

"""
@app.route("/browser/")
@app.route("/browser/<uri>")
def browse_uri(uri=None):    
    resource = {}
    resources = {}

    if uri:
        instance_uri = curie2uri(uri, app.nss)
        search = app.g.triples((instance_uri, None, None))
        resource['data'] = [ (uri2curie(p, app.nss), uri2curie(o, app.nss)) for s, p, o in search ]
        search = app.g.triples((None, None, instance_uri))
        resource['backlinks'] = [ (uri2curie(s, app.nss), uri2curie(p, app.nss)) for s, p, o in search ]

    else:
        # URI not given -> display index        
        for s, p, o in app.g:
            curie = uri2curie(s, app.nss)
            if resources.has_key(curie):
                resources[curie]['triples'] += 1
            else:
                resources[curie] = {'triples': 1}
    return render_template('browser.html', uri=uri,
                           resource=resource, resources=resources)
"""

@app.route('/api/namespaces/')
def api_namespaces_index(method=['GET']):
    return Response(json.dumps(app.nss), mimetype='application/json')

@app.route('/api/resources/')
def api_resources_index(method=['GET']):
    # Get list of all mentioned URIs
    uris = []
    for s, p, o in app.g.triples((None, None, None)):
        if type(s) is rdflib.URIRef and not s in uris:
            uris.append(s)
        if type(o) is rdflib.URIRef and not o in uris:
            uris.append(o)

    return Response(json.dumps(uris), mimetype='application/json')
    

@app.route('/api/resources/<path:curie_or_uri>')
def api_resources(curie_or_uri=None, methods=['GET']):
    if request.method == 'GET':
        return api_resources_get(curie_or_uri)
    else:
        raise Exception("Invalid method")

def api_resources_get(curie_or_uri):
    # Result resource
    result = Graph()

    # Resolve full URI
    uri = curie2uri(curie_or_uri, app.nss)
    print(uri)

    # <instance_uri> ?predicate ?object
    search = app.g.triples((uri, None, None))
    for t in search:
        result.add(t)

    # ?subject ?predicate <instance_uri>
    search = app.g.triples((None, None, uri))
    for t in search:
        result.add(t)

    # Nothing found? -> return 404 not found
    if len(result) == 0:
        return "Not Found", 404

    # Return
    return Response(result.serialize(format='json-ld', indent=4), mimetype='application/json')

"""
# Blueprint for API
api = Blueprint("api", __name__, url_prefix="/api")

class InstanceHandler(object):
    def get(self, instance_id):
        print(instance_id)

        # Result resource
        result_resource = {}
        result_graph = Graph()
        
        # Resolve full URI
        instance_uri = curie2uri(instance_id, app.nss)

        # <instance_uri> ?predicate ?object
        search = app.g.triples((instance_uri, None, None))
        result_resource['data'] = [
          (uri2curie(p, app.nss), uri2curie(o, app.nss)) for s, p, o in search
        ]

        # JSON-LD: <instance_uri> ?predicate ?object
        search = app.g.triples((instance_uri, None, None))
        for t in search:
            result_graph.add(t)

        # ?subject ?predicate <instance_uri>
        search = app.g.triples((None, None, instance_uri))
        result_resource['backlinks'] = [
          (uri2curie(s, app.nss), uri2curie(p, app.nss)) for s, p, o in search
        ]

        # JSON-LD: ?subject ?predicate <instance_uri>
        search = app.g.triples((None, None, instance_uri))
        for t in search:
            result_graph.add(t)

        # Nothing found? -> return 404 not found
        if (not result_resource['data'] and 
            not result_resource['backlinks']):
                return 404, "Not Found"

        # Return result resource
        #return 200, result_resource

        # Return JSON-LD
        return 200, json.loads(result_graph.serialize(format='json-ld', indent=4))


    def add(self, instance_id):
        return self.update(instance_id, update=False)

    def update(self, instance_id, update=True):
        # Resolve full URI
        instance_uri = curie2uri(instance_id, app.nss)
        triples = []

        # Process data: JSON
        if request.headers['content-type'] == 'application/json':
            # parse
            try:
                data_json = json.loads(request.data)
            except ValueError:
                # Bad data
                return 400, "Bad Request"

            # Triples in
            for p, o in data_json['data']:
                p_uri = curie2uri(p, app.nss)
                o_uri = curie2uri(o, app.nss)
                triples.append( (instance_uri, p_uri, o_uri) )

            # Triples out
            for o, p in data_json['backlinks']:
                p_uri = curie2uri(p, app.nss)
                o_uri = curie2uri(o, app.nss)
                triples.append( (o_uri, p_uri, instance_uri) )

        else:
            # Unknown data type -> error
            return 400, "Bad Request"

        # Remove old triples
        #if update:
        #    app.g.remove((instance_uri, None, None))
        #    app.g.remove((None, None, instance_uri))

        # Add triples to graph
        for s, p, o in triples:
            app.g.add((s, p, o))

        # Response
        return 200, "OK"

    def delete(self, instance_id):
        # Resolve full URI
        instance_uri = curie2uri(instance_id, app.nss)

        # Not found?
        # TODO: refactor
        triples = app.g.triples((None, None, instance_uri))
        count = 0
        for t in triples:
            count += 1
        if count == 0:
            # Not found
            return 404, "Not Found"

        # Remove triples where this URI is the subject
        app.g.remove((instance_uri, None, None))

        # Remove triples where this URI is the object
        app.g.remove((None, None, instance_uri))

        # Success
        return 200, "Deleted"

instances_resource = RESTResource(
    name="instance",
    route="/resources",
    app=api,
    actions=["add", "update", "delete", "get"],
    handler=InstanceHandler())

# Register blueprints
app.register_blueprint(api)
"""

if __name__ == "__main__":
    # Run app in debug mode
    app.run(port=8080, debug=app.debug, host='0.0.0.0')
