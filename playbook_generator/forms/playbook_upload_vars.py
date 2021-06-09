from django import forms
from django.core.validators import FileExtensionValidator
from playbook_generator.models import ConfigUpload
from sites.models import Site
from playbook_generator.models.types import PlaybookServiceTypes

class FileUploadVarsPlaybookForm(forms.Form):
    uploaded_file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['xls', 'xlsx']),],
                                    required=True)
    tags = forms.ChoiceField(choices=ConfigUpload.TAGS)
    site = forms.ModelChoiceField(queryset=Site.objects.all(), to_field_name="name", required=True)

    def __init__(self, *args, **kwargs):
        service_type = kwargs.pop('service_type', None)
        super().__init__(*args, **kwargs)
        if service_type:
            self.fields['site'].queryset = Site.objects.filter(service_type=service_type)
