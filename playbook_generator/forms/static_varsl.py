from django import forms
from playbook_generator.models import StaticVarsValue


class StaticVarsValueModelForm(forms.ModelForm):

    class Meta:
        model = StaticVarsValue
        fields = ('key', 'value',)
