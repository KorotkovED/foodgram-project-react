from django import forms
from .models import Tags


class TagForm(forms.ModelForm):
    class Meta:
        model = Tags
        fields = '__all__'
