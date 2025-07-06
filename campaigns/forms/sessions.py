import datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from ..models import SessionNote


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