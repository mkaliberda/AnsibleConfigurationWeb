from django.shortcuts import render
from django.views import generic
from .models import Site


class SitesListConfigsView(generic.ListView):
    model = Site
    queryset = Site.objects.all()
    template_name = 'sites_config_table.html'
    context_object_name = 'sites'

    def dispatch(self, request, *args, **kwargs):
        self.service_type = kwargs.get("service_type")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({ 'service_type': self.service_type })
        return super().get_context_data(**kwargs)
