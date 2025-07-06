from django.db import models

from .base import Campaign


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