from django import forms
from django.core.validators import FileExtensionValidator
from playbook_generator.models import ConfigUpload
from sites.models import Site

class FileUploadVarsPlaybookForm(forms.Form):
    uploaded_file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['xls', 'xlsx']),],
                                    required=True)
    tags = forms.ChoiceField(choices=ConfigUpload.TAGS)
    site = forms.ModelChoiceField(queryset=Site.objects.all(), to_field_name="name", required=True)

