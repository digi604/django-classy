Django Classy
=============


An approach to class based Views
--------------------------------

Instead of functions use classes as views.
This approach won't return a HttpResponse.
It will only return a dictionary. This allows
depending on who is connecting to transform the
dictionary into JSON, HTML, AMF, XML.

Example:

	from classy.base import View

	class MyView(View):
		template = "myapp/mytemplate.html"
	
		def get(request, id):
			instance = get_object_or_404(MyModel, pk=id)
			return {'object':object}
		
There are already base classes for form views, complete model instance edit classes and list classes.
More to follow.

