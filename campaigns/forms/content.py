from django import forms
from django.forms import inlineformset_factory

from ..models import Chapter, Encounter


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        exclude = ["campaign", "owner", "order"]
        widgets = {
            'summary': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Brief overview of the chapter. Markdown supported: **bold**, *italic*, ## Headers, etc.'
            }),
            'intro': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Adventure hook or opening scene. Markdown supported: **bold**, *italic*, [links](url), etc.'
            }),
            'dm_notes': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Secrets, pacing tips, foreshadowing. Markdown supported: - bullets, 1. numbered lists, etc.'
            }),
            'conclusion': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'How the chapter wraps up or links to future chapters. Markdown supported.'
            }),
        }


class EncounterForm(forms.ModelForm):
    class Meta:
        model = Encounter
        exclude = ['chapter', 'owner', 'order']
        widgets = {
            'summary': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Quick description of encounter purpose. Markdown supported: **bold**, *italic*, etc.'
            }),
            'setup': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Scene setup, triggers, and conditions. Markdown supported: - bullets, [links](url), etc.'
            }),
            'read_aloud': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Optional boxed text or narration. Markdown supported for emphasis and formatting.'
            }),
            'dm_notes': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tactics, loot, stat block refs, etc. Markdown supported: - bullets, 1. lists, etc.'
            }),
            'map_reference': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Map location, grid coordinates, or spatial references. Markdown supported.'
            }),
        }

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
        
        # Style and filter the NPCs field
        if 'npcs' in self.fields:
            self.fields['npcs'].widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-md border border-gray-600 bg-gray-700 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'size': '6'  # Show multiple options
            })
            
            if campaign:
                # Filter NPCs to only show ones from this campaign
                self.fields['npcs'].queryset = campaign.npcs.all()
            
            # Add help text
            self.fields['npcs'].help_text = 'Hold Ctrl/Cmd to select multiple NPCs that appear in this encounter'
        
        # Style and filter the Enemies field
        if 'enemies' in self.fields:
            self.fields['enemies'].widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-md border border-gray-600 bg-gray-700 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'size': '6'  # Show multiple options
            })
            
            if campaign:
                # Filter enemies to only show ones from this campaign
                self.fields['enemies'].queryset = campaign.enemies.all()
            
            # Add help text
            self.fields['enemies'].help_text = 'Hold Ctrl/Cmd to select multiple enemies that appear in this encounter'


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