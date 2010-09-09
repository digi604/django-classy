# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpRequest, HttpResponseNotAllowed
from django.core.exceptions import ImproperlyConfigured
from django.template.context import RequestContext

class CallableViewClass(type):
    def __call__(cls, *args, **kwargs):
        if args and isinstance(args[0], HttpRequest):
            instance = super(CallableViewClass, cls).__call__()
            return instance.__call__(*args, **kwargs)
        else:
            instance = super(CallableViewClass, cls).__call__(*args, **kwargs)
            return instance

ALLOWED = ('GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'CONNECT', 'TRACE')

class Responder(object):
    def __init__(self, view):
        self.view = view
    
    def get_response(self, request, context, **httpresponse_kwargs):
        raise NotImplemented

class TemplateResponder(Responder):
    
    def get_template(self, request):
        """
        Get a ``Template`` object for the given request.
        """
        names = self.get_template_names(request)
        if not names:
            raise ImproperlyConfigured("'%s' must provide template." % self.view.__class__.__name__)
        return self.load_template(request, names)
    
    def get_template_names(self, request):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if get_template is overridden.
        """
        template = self.view.get_template(request)
        if template is None:
            return []
        elif isinstance(template, basestring):
            return [template]
        else:
            return template
    
    def load_template(self, request, names=[]):
        """
        Load a template, using self.template_loader or the default.
        """
        return self.get_template_loader(request).select_template(names)
    
    def get_template_loader(self, request):
        """
        Get the template loader to be used for this request. Defaults to
        ``django.template.loader``.
        """
        import django.template.loader
        return django.template.loader
    
    def get_response(self, request, context, **httpresponse_kwargs):
        """
        Construct an `HttpResponse` object given the template and context.
        """
        template = self.get_template(request)
        return HttpResponse(unicode(template.render(context)), **httpresponse_kwargs)

class View(object):
    __metaclass__ = CallableViewClass
    
    def __init__(self, **kwargs):
        self._load_config_values(kwargs,
            mimetype = 'text/html',
            template = None,
            decorators = [],
        )
        if kwargs:
            raise TypeError("__init__() got an unexpected keyword argument '%s'" % iter(kwargs).next())
    
    def get(self, *args, **kwargs):
        return {}
    
    def get_template(self, request):
        return self.template
    
    def extra_context(self, request, *args, **kwargs):
        return {}
        
    def get_responder(self, request, context):
        return TemplateResponder(self)
    
    def get_method(self, request):
        method = getattr(self, request.method.lower())
        if self.decorators:
            print self.decorators
            for decorator in self.decorators:
                method = decorator(method)
        else:
            print 'no decorators'
        return method
    
    def __call__(self, request, *args, **kwargs):
        if hasattr(self, request.method.lower()) and request.method in ALLOWED:
            method = self.get_method(request)
            if hasattr(method, '__call__'):
                context = method(request, *args, **kwargs)
                if isinstance(context, HttpResponse):
                    return context
                extra = self.extra_context(request, *args, **kwargs)
                context.update(extra)
                processors = []
                final_context = RequestContext(request, context, processors)
                responder = self.get_responder(request, context)
                return responder.get_response(request, final_context, mimetype=self.mimetype)
        else:
            permitted_methods = []
            for method in ALLOWED:
                if hasattr(getattr(self, method.lower(), None), '__call__'):
                    permitted_methods.append(method)
            return HttpResponseNotAllowed(permitted_methods)
        
    def _load_config_values(self, initkwargs, **defaults):
        """
        Set on self some config values possibly taken from __init__, or
        attributes on self.__class__, or some default.
        """
        for k in defaults:
            default = getattr(self.__class__, k, defaults[k])
            value = initkwargs.pop(k, default)
            setattr(self, k, value)

"""
class MyView(View):
    def __init__(self, arg=None):
        self.arg = arg
    def GET(request):
        return HttpResponse(self.arg or 'No args passed')

@login_required
class MyOtherView(View):
    def POST(request):
        return HttpResponse()

# in urls.py
# And all the following work as expected.
urlpatterns = patterns(''
    url(r'^myview1$', 'myapp.views.MyView', name='myview1'),
    url(r'^myview2$', myapp.views.MyView, name='myview2'),
    url(r'^myview3$', myapp.views.MyView('foobar'), name='myview3'),
    url(r'^myotherview$', 'myapp.views.MyOtherView', name='otherview'),
)
"""