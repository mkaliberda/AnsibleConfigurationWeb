
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import Site
from .form import CreateEditSitesForm
from  sites.models import Site

class SitesCreateEditForm(generic.FormView):
    template_name = 'sites_create_form.html'
    form_class = CreateEditSitesForm

    def get_success_url(self):
        return reverse('playbook_generator:playbook_step_upload',
                       kwargs={'service_type': self.kwargs.get('service_type')})


    def dispatch(self, request, *args, **kwargs):
        self.service_type = kwargs.get("service_type")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({ 'service_type': self.service_type })
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(SitesCreateEditForm, self).get_form_kwargs()
        kwargs.update({'service_type': self.service_type})
        return kwargs

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            service_type = form.cleaned_data.pop('service_type', None)
            name = form.cleaned_data.pop('name', None)
            kwargs.update({'service_type': self.service_type})
            Site.objects.update_or_create(
                service_type=service_type,
                name=name,
            )
            return redirect(to=self.get_success_url())
        else:
            return super().form_valid(form)


class SitesListView(generic.ListView):
    model = Site
    queryset = Site.objects.all()
    template_name = 'sites_list.html'
    context_object_name = 'sites'

    def dispatch(self, request, *args, **kwargs):
        self.service_type = kwargs.get("service_type")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({ 'service_type': self.service_type })
        return super().get_context_data(**kwargs)


class SiteDeleteView(generic.DeleteView):
    template_name = 'sites_delete_confirm_form.html'

    def get_success_url(self):
        self.success_url = reverse('sites:site_list_view',
                                   kwargs={'service_type': self.object.service_type})
        return super().get_success_url()

    def get_object(self, queryset=None):
        siteObj = get_object_or_404(Site, uuid=self.kwargs.get("uuid"))
        return siteObj

    def post(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = Site.objects.get(uuid=self.kwargs.get("uuid"))
        if request.POST.get('confirm_delete', None):
            self.object.delete()
        return HttpResponseRedirect(self.get_success_url())