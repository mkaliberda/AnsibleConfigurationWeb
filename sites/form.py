from django import forms
from django.forms.widgets import DateTimeBaseInput
from sites.models import Site
from playbook_generator.models.types import PlaybookServiceTypes


class CreateEditSitesForm(forms.Form):
    name = forms.CharField(max_length=128)
    service_type = forms.ChoiceField(choices=PlaybookServiceTypes.choices(), required=True)

    def __init__(self, *args, **kwargs):
        service_type = kwargs.pop('service_type', None)
        kwargs.update({'initial': { 'service_type': service_type }})
        super(CreateEditSitesForm, self).__init__(*args, **kwargs)


