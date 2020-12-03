from django.forms import forms
from django.core.validators import FileExtensionValidator


class FileUploadVarsPlaybookForm(forms.Form):
    uploaded_file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['xls', 'xlsx']),],
                                    required=True)
