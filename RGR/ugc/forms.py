from .models import Profile
from django import forms

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'external_id',
            'name'
        )
        widgets = {
            'name':  forms.TextInput,
        }