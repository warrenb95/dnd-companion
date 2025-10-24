from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from .base import Campaign


class Chapter(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="chapters"
    )
    order = models.PositiveIntegerField() # add default ordering
    title = models.CharField(max_length=200)

    summary = models.TextField(
        blank=True,
        help_text="One-paragraph overview of the chapter's purpose."
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="not_started",
        help_text="Track campaign progress."
    )

    intro = models.TextField(
        blank=True,
        help_text="Adventure hook or opening scene to kick things off."
    )
    
    dm_notes = models.TextField(
        blank=True,
        help_text="Flexible notes: secrets, pacing tips, foreshadowing, etc."
    )
    
    conclusion = models.TextField(
        blank=True,
        help_text="How the chapter wraps up or links to future chapters."
    )

    level_range = models.CharField(
        max_length=50,
        blank=True,
        help_text="E.g. Levels 4–5"
    )

    is_optional = models.BooleanField(
        default=False,
        help_text="Mark this chapter as a side quest or optional content."
    )

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chapters'
    )

    def get_absolute_url(self):
        return reverse("campaigns:chapter_detail", kwargs={
            'campaign_id': self.campaign.id,
            'chapter_id': self.id
        })

    class Meta:
        ordering = ['order']  # Ascending order by default

    def __str__(self):
        return f"{self.order} - {self.title} (lvl {self.level_range})"


class Encounter(models.Model):
    CHOICES = [
        ("combat", "Combat"),
        ("social", "Social"),
        ("puzzle", "Puzzle"),
        ("exploration", "Exploration"),
        ("mixed", "Mixed/Other"),
    ]

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="encounters")
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=CHOICES, default="combat")

    summary = models.TextField(help_text="Quick description of the encounter purpose.")
    setup = models.TextField(blank=True, help_text="Scene setup, triggers, and conditions.")
    read_aloud = models.TextField(blank=True, help_text="Optional boxed text or narration.")
    dm_notes = models.TextField(
        blank=True,
        help_text="All-purpose field: tactics, loot, stat block refs, etc."
    )

    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The location where this encounter takes place"
    )
    npcs = models.ManyToManyField(
        'NPC',
        blank=True,
        related_name='encounters',
        help_text="NPCs that appear in this specific encounter"
    )
    map_reference = models.TextField(
        blank=True,
        help_text="Notes about map location, grid coordinates, or other spatial references"
    )

    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional tags like 'boss', 'undead', 'trap', 'ambush' (comma-separated)"
    )

    danger_level = models.CharField(
        max_length=20,
        choices=[("low", "Low"), ("moderate", "Moderate"), ("high", "High"), ("deadly", "Deadly")],
        blank=True,
        help_text="At-a-glance danger estimation."
    )

    is_optional = models.BooleanField(
        default=False,
        help_text="Tick this if the encounter is skippable or side content."
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='encounters')
    order = models.PositiveIntegerField(default=1, help_text="Order of the encounter in the chapter")

    class Meta:
        ordering = ['order']  # Ascending order by default

    def tags_as_list(self):
        return self.tags.split(",")

    def __str__(self):
        return f"{self.title} (Chapter {self.chapter.order})"