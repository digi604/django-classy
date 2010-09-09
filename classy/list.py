# -*- coding: utf-8 -*-
from classy.base import View

class ListView(View):
    model = None
    
    def get_queryset(self, request, **kwargs):
        return self.model.objects.all()
    
    def get(self, request, **kwargs):
        list = self.get_queryset(request, **kwargs)
        return {'objects':list}
