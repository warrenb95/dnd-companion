from django import forms
from ..models import CombatSession


class CombatSessionForm(forms.ModelForm):
    class Meta:
        model = CombatSession
        fields = ['name', 'dm_notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500',
                'placeholder': 'Combat session name (optional)'
            }),
            'dm_notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500',
                'placeholder': 'DM notes for this combat session...',
                'rows': 4
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['dm_notes'].required = False