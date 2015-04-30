$(function() {	
	var DirectoryView = Backbone.View.extend({
		el: '#directory',
		template: _.template($('#directory-template').html()),
		initialize: function(options) {
			var self = this;

			//$.get('/api/namespaces/', function(nss) {
			//	self.nss = nss;
			$.get('/api/resources/', function(data) {
  				self.resources = data;
				if(options && options.success) {
					options.success();
				}
			});
			//});
		},
		render: function() {
			this.el.innerHTML = this.template({ resources: this.resources });
			$('.action-resource').click(function() {
				router.navigate( '/browser/' + $(this).data('uri'), true );
				return false;
			});
		}
	});

	var ResourceView = Backbone.View.extend({
		el: '#main',
		template: _.template($('#resource-template').html()),
		initialize: function(options) {
			var self = this;
			this.resourceUri = options.resourceUri;
			$.get('/api/resources/' + this.resourceUri.replace('#', '\%23'), function(resource) {
				self.resource = resource;

				if(options && options.success) {
					options.success();
				}
			})
		},
		render: function() {
			var self = this;
			//jsonld.compact(this.resource, {}, function(err, compacted) {
			self.el.innerHTML = self.template({ uri: self.resourceUri, jsonld: self.resource });
			//});
		}
	});

	var Router = Backbone.Router.extend({
		routes: {
			"browser/*uri": "resource"
      	},
      	resource: function(uri) {
			var view = new DirectoryView({
				success: function() {
					view.render();

					if(uri) {
						var resourceView = new ResourceView({
							resourceUri: uri.replace('\%23', '#'),
							success: function() {
								view.render();
								resourceView.render();
							}
						});
					}
				}
			});
      	}
	});	

	var router = new Router();
	Backbone.history.start({pushState: true});

	// Some tests
	//$.get('/api/resources/http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine%23Winery', function(data) {
  		//console.log(data);

  		/*
  		jsonld.normalize(data, function(err, normalized) {
  			console.log('normalized');
  			console.log(err);
  			console.log(normalized);
  		});  		

  		jsonld.toRDF(data, {}, function(err, statement) {
  			console.log('toRDF');
  			console.log(statement);
  		});
		*/

		/*
		jsonld.expand(data, {}, function(err, expanded) {
			console.dir(expanded);
		});
		*/

		/*
		{
		    "@context": {
		        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
		        "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
		    },
		    "@graph": [
		        {
		            "@id": "http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#RieslingGrape",
		            "@type": "http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#WineGrape"
		        },
		        {
		            "http://www.w3.org/2002/07/owl#hasValue": {
		                "@id": "http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#RieslingGrape"
		            }
		        }
		    ]
		}
		*/
	//});
});
