from django import forms
from django.core.validators import FileExtensionValidator
from playbook_generator.models import ConfigUpload

class FileUploadVarsPlaybookForm(forms.Form):
    uploaded_file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['xls', 'xlsx']),],
                                    required=True)

    tags = forms.ChoiceField(choices=ConfigUpload.TAGS)
