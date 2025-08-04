from django.db import models
from django.contrib.auth.models import User

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
    maximum_hit_points = models.PositiveIntegerField(default=0)
    notable_traits = models.TextField(blank=True)
    heroic_inspiration = models.BooleanField(default=False)
    alive = models.BooleanField(default=True)
    
    # D&D 5e Conditions
    blinded = models.BooleanField(default=False)
    charmed = models.BooleanField(default=False)
    deafened = models.BooleanField(default=False)
    frightened = models.BooleanField(default=False)
    grappled = models.BooleanField(default=False)
    incapacitated = models.BooleanField(default=False)
    invisible = models.BooleanField(default=False)
    paralyzed = models.BooleanField(default=False)
    petrified = models.BooleanField(default=False)
    poisoned = models.BooleanField(default=False)
    prone = models.BooleanField(default=False)
    restrained = models.BooleanField(default=False)
    stunned = models.BooleanField(default=False)
    unconscious = models.BooleanField(default=False)
    
    # Additional tracking fields
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='character_summaries', null=True, blank=True)

    def __str__(self):
        return f"{self.character_name} ({self.player_name})"
    
    @property
    def health_percentage(self):
        """Calculate health as a percentage for visual indicators"""
        if self.maximum_hit_points == 0:
            return 0
        return min(100, (self.current_hit_points / self.maximum_hit_points) * 100)
    
    @property
    def active_conditions(self):
        """Return list of active D&D conditions"""
        conditions = []
        condition_fields = [
            'blinded', 'charmed', 'deafened', 'frightened', 'grappled',
            'incapacitated', 'invisible', 'paralyzed', 'petrified', 
            'poisoned', 'prone', 'restrained', 'stunned', 'unconscious'
        ]
        
        for condition in condition_fields:
            if getattr(self, condition, False):
                conditions.append(condition.title())
        return conditions