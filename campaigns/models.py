from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

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
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
    )
    level_range = models.CharField(max_length=50, blank=True)
    adventure_hook = models.TextField(
        help_text="Trigger or reason for party to start the chapter."
    )
    overview = models.TextField(
        help_text="Brief summary of the chapter's events and objectives."
    )
    background = models.TextField(
        help_text="World context and relevant history.", blank=True
    )
    dm_guidance = models.TextField(
        help_text="Tips and guidance for running the chapter.", blank=True
    )

    locations_description = models.TextField(
        help_text="DM notes for locations, including read-aloud text and hidden details.",
        blank=True,
    )

    conclusion = models.TextField(
        help_text="How the chapter ends and transitions forward.", blank=True
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chapters')

    def get_absolute_url(self):
        return reverse("campaigns:chapter_detail", args=[str(self.id)])

    def __str__(self):
        return f"{self.number} - {self.title}"


class Encounter(models.Model):
    CHOICES = [
        ("combat", "Combat"),
        ("social", "Social"),
        ("puzzle", "Puzzle"),
        ("exploration", "Exploration"),
        ("mixed", "Mixed/Other"),
    ]

    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="encounters"
    )
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=CHOICES, default="combat")
    level_range = models.CharField(max_length=50, blank=True)

    summary = models.TextField(help_text="Purpose and context of the encounter.")
    setup = models.TextField(help_text="Initial conditions and encounter details.")
    read_aloud = models.TextField(help_text="Narrative for the DM to read to players.")
    tactics = models.TextField(
        help_text="Enemy strategy and dynamic notes.", blank=True
    )
    stat_blocks = models.TextField(
        help_text="Stat blocks or reference notes.", blank=True
    )
    treasure = models.TextField(
        help_text="Loot and rewards after the encounter.", blank=True
    )
    map_reference = models.TextField(
        help_text="Map or layout references for this encounter.", blank=True
    )
    map_image = models.ImageField(upload_to="images/", blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='encounters')

    def __str__(self):
        return f"{self.title} (Chapter {self.chapter.number})"


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
        return f"Session on {self.date} - Chapter {self.chapter.title}"


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

