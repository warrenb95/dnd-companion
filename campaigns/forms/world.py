from django import forms

from ..models import Location, NPC


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "description", "region", "tags"]


class NPCForm(forms.ModelForm):
    class Meta:
        model = NPC
        fields = ["name", "description", "role", "location", "status", "tags"]