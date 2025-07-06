from django import forms

from ..models import CharacterSummary


class CharacterSummaryForm(forms.ModelForm):
    class Meta:
        model = CharacterSummary
        exclude = ["campaign"]