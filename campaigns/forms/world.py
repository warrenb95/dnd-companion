from django import forms

from ..models import Location, NPC


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "description", "region", "tags", "map_image", "chapters"]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-md border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'placeholder': 'Enter location name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-md border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Describe the location, its features, atmosphere...'
            }),
            'region': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-md border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'placeholder': 'e.g., Northern Territories, Capital District'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-md border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'placeholder': 'dungeon, city, tavern, forest'
            }),
            'map_image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 rounded-md border border-gray-600 bg-gray-700 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'accept': 'image/*'
            }),
            'chapters': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-2 rounded-md border border-gray-600 bg-gray-700 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'size': '4'
            }),
        }

    def __init__(self, *args, **kwargs):
        campaign = kwargs.pop('campaign', None)
        super().__init__(*args, **kwargs)
        
        if campaign:
            # Filter chapters to only show ones from this campaign
            self.fields['chapters'].queryset = campaign.chapters.all()
        
        # Add help text to fields
        self.fields['chapters'].help_text = 'Hold Ctrl/Cmd to select multiple chapters where this location appears'


class NPCForm(forms.ModelForm):
    class Meta:
        model = NPC
        fields = [
            # Basic Info
            "name", "creature_type", "size", "alignment", "appearance", "personality", 
            "role", "location", "status", "tags", "chapters",
            
            # Core Stats
            "armor_class", "hit_points", "hit_dice", "speed",
            
            # Ability Scores
            "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
            
            # Skills and Resistances
            "saving_throws", "skills", "damage_resistances", "damage_immunities", 
            "condition_immunities", "senses", "languages", "challenge_rating", "proficiency_bonus",
            
            # Abilities and Actions
            "special_abilities", "actions", "legendary_actions",
            
            # DM Notes
            "secret"
        ]
        widgets = {
            # Textareas for longer content
            'appearance': forms.Textarea(attrs={'rows': 3}),
            'personality': forms.Textarea(attrs={'rows': 3}),
            'secret': forms.Textarea(attrs={'rows': 3}),
            'special_abilities': forms.Textarea(attrs={'rows': 4}),
            'actions': forms.Textarea(attrs={'rows': 4}),
            'legendary_actions': forms.Textarea(attrs={'rows': 3}),
            
            # Number inputs with constraints
            'armor_class': forms.NumberInput(attrs={'min': 1, 'max': 30}),
            'hit_points': forms.NumberInput(attrs={'min': 1, 'max': 999}),
            'strength': forms.NumberInput(attrs={'min': 1, 'max': 30}),
            'dexterity': forms.NumberInput(attrs={'min': 1, 'max': 30}),
            'constitution': forms.NumberInput(attrs={'min': 1, 'max': 30}),
            'intelligence': forms.NumberInput(attrs={'min': 1, 'max': 30}),
            'wisdom': forms.NumberInput(attrs={'min': 1, 'max': 30}),
            'charisma': forms.NumberInput(attrs={'min': 1, 'max': 30}),
            'proficiency_bonus': forms.NumberInput(attrs={'min': 2, 'max': 9}),
        }
        
    def __init__(self, *args, **kwargs):
        campaign = kwargs.pop('campaign', None)
        super().__init__(*args, **kwargs)
        
        # Filter location and chapter choices to only show items from the current campaign
        if campaign:
            self.fields['location'].queryset = Location.objects.filter(campaign=campaign)
            self.fields['chapters'].queryset = campaign.chapters.all()