# Roosa - A RESTful Ontology Server and Applications

This repository contains Roosa - A RESTful ontology server and some
exemplary applications.

Roosa is *unstable* and *experimental*.

## Getting Started

Python is required. We recommend 2.6 or 2.7. Python 3 doesn't work. We recommend
installing Roosa using [pip](http://pypi.python.org/pypi/pip) and [virtualenv](http://pypi.python.org/pypi/virtualenv).

Get copy of roosa and open shell in its location. Create new virtualenv:

    virtualenv roosa-venv

Activate it:

- In Unix/Linux: `source venv-roosa/bin/activate`
- In Windows PowerShell: `.\venv-roosa\Scripts\activate.ps1`
- In Windows command-prompt: `venv-roosa\Scripts\activate`

Install dependencies into virtualenv:

	pip install -r requirements.txt

Additionally, you need to manually install [rdflib-jsonld](https://github.com/RDFLib/rdflib-jsonld):

	git clone https://github.com/RDFLib/rdflib-jsonld.git
	cd rdflib-jsonld
	python setup.py install

You are done!

Launch Roosa server (in test mode) by invoking:

	python roosa.py

For deployment, we recommend you to use Tornado. Try it out by running:

	python run_tornado.py

Right now, both run by default at port `8080` (`http://localhost:8080`).
