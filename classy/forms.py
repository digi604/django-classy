# -*- coding: utf-8 -*-
from classy.base import View
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

class FormView(View):
    form = None
    redirect = None
    
    def get_form(self, request, **kwargs):
        if not self.form:
            raise ImproperlyConfigured("'%s' must provide a form." % self.__class__.__name__)
        return self.form(**kwargs)
    
    def get(self, request, **kwargs):
        form = self.get_form(request)
        return {'form':form}
    
    def get_redirect(self, request, form, **kwargs):
        if self.redirect:
            return HttpResponseRedirect(reverse(self.redirect, kwargs=kwargs))
    
    def post(self, request, **kwargs):
        form = self.get_form(request, data=request.POST, files=request.FILES, **kwargs)
        if form.is_valid():
            self.process_form(request, form, **kwargs)
            redirect = self.get_redirect(request, form, **kwargs)
            if redirect:
                return redirect
        return {'form':form}
    
    def process_form(self, request, form, **kwargs):
        form.save()
        if hasattr(form, 'save_m2m'):
            form.save_m2m()
    