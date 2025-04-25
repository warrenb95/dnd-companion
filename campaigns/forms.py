import datetime
from django import forms
from .models import Chapter
from .models import Location, NPC
from .models import SessionNote
from .models import ChatMessage
from .models import ChapterChatMessage


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ["title", "summary", "status"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Ask the LLM something..."}
            )
        }


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


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Ask the LLM something..."}
            )
        }


class ChapterChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChapterChatMessage
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Plan your next chapter..."}
            ),
        }
