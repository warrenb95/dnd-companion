import datetime

from django import forms
from django.forms import inlineformset_factory

from .models import Chapter, Encounter
from .models import Location, NPC
from .models import SessionNote
from .models import CharacterSummary


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        exclude = ["campaign", "number"]

class EncounterForm(forms.ModelForm):
    class Meta:
        model = Encounter
        exclude = ['chapter']

# Create an inline formset: relate Encounter to Chapter
EncounterFormSet = inlineformset_factory(
    Chapter,
    Encounter,
    form = EncounterForm,
    extra = 5,            # how many blank encounter forms to show by default
    can_delete = True,    # allow users to remove encounters
)

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "description", "region", "tags"]


class NPCForm(forms.ModelForm):
    class Meta:
        model = NPC
        fields = ["name", "description", "role", "location", "status", "tags"]


class SessionNoteForm(forms.ModelForm):
    class Meta:
        model = SessionNote
        fields = ["date", "notes"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",  # this gives you a native date picker in modern browsers
                    "value": datetime.date.today().isoformat(),  # sets default to today
                }
            ),
            "notes": forms.Textarea(attrs={"rows": 6}),
        }


class CharacterSummaryForm(forms.ModelForm):
    class Meta:
        model = CharacterSummary
        exclude = ["campaign"]


class ChapterUploadForm(forms.Form):
    pdf_file = forms.FileField(label="Adventure Chapter PDF")
