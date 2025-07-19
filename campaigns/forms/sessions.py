import datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from ..models import SessionNote, SessionSchedule, PlayerAvailability


class SessionNoteForm(forms.ModelForm):
    class Meta:
        model = SessionNote
        fields = ["date", "content"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",  # this gives you a native date picker in modern browsers
                    "value": datetime.date.today().isoformat(),  # sets default to today
                }
            ),
            "content": forms.Textarea(attrs={"rows": 6}),
        }


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        })


class SessionScheduleForm(forms.ModelForm):
    class Meta:
        model = SessionSchedule
        fields = ['title', 'date_range_start', 'date_range_end', 'session_duration', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Session Availability Poll'
            }),
            'date_range_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_range_end': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'session_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 12,
                'value': 4
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes for your players...'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('date_range_start')
        end_date = cleaned_data.get('date_range_end')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date must be after start date.")
            
            if start_date < datetime.date.today():
                raise forms.ValidationError("Start date cannot be in the past.")
        
        return cleaned_data


class PlayerAvailabilityForm(forms.ModelForm):
    class Meta:
        model = PlayerAvailability
        fields = ['player_name', 'character_name', 'email']
        widgets = {
            'player_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name',
                'required': True
            }),
            'character_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Character name (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            })
        }