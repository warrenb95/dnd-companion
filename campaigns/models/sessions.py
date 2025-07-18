from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from .base import Campaign
from .content import Encounter


class SessionNote(models.Model):
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="session_notes",
        null=True,    # Allows NULL in the database
    )
    date = models.DateField(default=timezone.now)
    content = models.TextField(help_text="Use bullet points or markdown.")
    summary = models.TextField(blank=True, help_text="Generated by LLM")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_notes')

    def __str__(self):
        return f"Session on {self.date} - {self.encounter.title if self.encounter else 'Unknown'}"


class ChatMessage(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="chat_messages"
    )
    role = models.CharField(
        max_length=10, choices=[("user", "User"), ("assistant", "Assistant")]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ordering = ["created_at"]
    confirmed_for_chapter = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"


class ChapterChatMessage(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="chapter_chat_messages"
    )
    role = models.CharField(
        max_length=10, choices=[("user", "User"), ("assistant", "Assistant")]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_for_generation = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"