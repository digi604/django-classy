# -*- coding: utf-8 -*-
from classy.base import View
from django.forms.models import ModelForm
from classy.forms import FormView
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template.defaultfilters import title

class EditView(FormView):
    model = None
    form = None
    redirect = None
    name = "object"
    popup_template = None 
    
    def get_redirect(self, request, form, **kwargs):
        if "popup" in request.GET:
            return False
        if self.redirect:
            return HttpResponseRedirect(reverse(self.redirect, kwargs=kwargs))
        
    def get_template(self, request):
        if "popup" in request.GET:
            return self.popup_template
        else:
            return self.template
    
    def get_instance(self, request, **kwargs):
        if 'pk' in kwargs:
            try:
                return self.model.objects.get(pk=kwargs['pk'])
            except self.model.DoesNotExist:
                raise Http404
        else:
            return self.model()
    
    def get(self, request, **kwargs):
        form = self.get_form(request, instance=self.get_instance(request, **kwargs))
        return {'form':form}
    
    def post(self, request, **kwargs):
        form = self.get_form(request, data=request.POST, files=request.FILES, instance=self.get_instance(request, **kwargs))
        if form.is_valid():
            new = True
            if form.instance.pk > 0:
                new = False
            self.process_form(request, form, **kwargs)
            self.set_message(request, True, new, form)
            redirect = self.get_redirect(request, form, **kwargs)
            if redirect:
                return redirect
        else:
            self.set_message(request, False, False)
        return {'form':form, 'valid':form.is_valid()}
    
    def set_message(self, request, valid, new, form=None):
        if valid:
            if not new:
                messages.success(request, _('%s updated successfully.') % self.get_model_name())
            else:
                messages.success(request, _('%s created successfully.') % self.get_model_name())
        else:
            messages.error(request, _('There were some errors or missing information in the form.'))
            
    def get_model_name(self):
        return title(self.model._meta.verbose_name)
    
    def get_form(self, request, **kwargs):
        if self.form:
            form = self.form
        else:
            class FormClass(ModelForm):
                class Meta:
                    model = self.model 
            form = FormClass
        return form(**kwargs)
        
