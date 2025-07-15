from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from .storage import get_encounter_image_path
from .validators import validate_encounter_image

class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    generated_summary = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')

    def get_absolute_url(self):
        return reverse("campaigns:campaign_detail", args=[str(self.id)])

    def __str__(self):
        return str(self.title)


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
        help_text="One-paragraph overview of the chapter’s purpose."
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
        return reverse("campaigns:chapter_detail", args=[str(self.id)])

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

    map_reference = models.CharField(max_length=100, blank=True)
    map_image = models.ImageField(
        upload_to=get_encounter_image_path,
        blank=True,
        validators=[validate_encounter_image],
        help_text="Upload an image file (JPG, PNG, WEBP). Max size: 5MB, Max dimensions: 6000x6000px"
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


class Location(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="locations"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    region = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')

    def __str__(self):
        return str(self.name)


class NPC(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="npcs"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    role = models.CharField(max_length=100, blank=True)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("alive", "Alive"),
            ("dead", "Dead"),
            ("missing", "Missing"),
            ("unknown", "Unknown"),
        ],
        default="alive",
    )
    tags = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='npcs')

    def __str__(self):
        return str(self.name)


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


class CharacterSummary(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="characters"
    )
    player_name = models.CharField(max_length=100)
    character_name = models.CharField(max_length=100)
    race = models.CharField(max_length=50)
    character_class = models.CharField(max_length=50, blank=True)
    character_sub_class = models.CharField(max_length=50, blank=True)
    level = models.PositiveIntegerField(default=1)
    background = models.CharField(max_length=500, blank=True)
    alignment = models.CharField(max_length=50, blank=True)
    passive_perception = models.PositiveIntegerField(default=10)
    armor_class = models.PositiveIntegerField(default=10)
    initiative_modifier = models.IntegerField(default=0)
    current_hit_points = models.PositiveIntegerField(default=0)
    notable_traits = models.TextField(blank=True)
    heroic_inspiration = models.BooleanField(default=False)
    alive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.character_name} ({self.player_name})"

