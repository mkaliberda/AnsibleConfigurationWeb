from django import  forms
from playbook_generator.models import ConfigUpload

class PlaybookModeForm(forms.Form):
    tags = forms.ChoiceField(choices = ConfigUpload.TAGS)
