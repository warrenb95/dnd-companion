from django import forms
from django.forms import inlineformset_factory

from ..models import Chapter, Encounter


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        exclude = ["campaign", "owner", "order"]


class EncounterForm(forms.ModelForm):
    class Meta:
        model = Encounter
        exclude = ['chapter', 'owner', 'order']


# Create an inline formset: relate Encounter to Chapter
EncounterFormSet = inlineformset_factory(
    Chapter,
    Encounter,
    form = EncounterForm,
    extra = 1,            # start with 1 blank encounter form
    can_delete = True,    # allow users to remove encounters
)


class ChapterUploadForm(forms.Form):
    pdf_file = forms.FileField(label="Adventure Chapter PDF")