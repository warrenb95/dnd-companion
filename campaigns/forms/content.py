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

    def __init__(self, *args, **kwargs):
        campaign = kwargs.pop('campaign', None)
        super().__init__(*args, **kwargs)
        
        # Style the location field if it exists
        if 'location' in self.fields:
            self.fields['location'].widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-md border border-gray-600 bg-gray-700 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
            })
            
            if campaign:
                # Filter location to only show ones from this campaign
                self.fields['location'].queryset = campaign.locations.all()
            
            # Add empty choice for location
            self.fields['location'].empty_label = "No specific location"


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