import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .content import Encounter
from .world import Enemy
from .characters import CharacterSummary


class CombatSession(models.Model):
    """
    Tracks the state of an active combat encounter
    """
    STATUS_CHOICES = [
        ('setup', 'Setup'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name='combat_sessions'
    )
    name = models.CharField(
        max_length=200,
        help_text="Custom name for this combat session"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='setup'
    )
    current_round = models.PositiveIntegerField(default=1)
    current_turn = models.PositiveIntegerField(default=0)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_rounds = models.PositiveIntegerField(default=0)
    
    # Initiative tracking
    initiative_rolled = models.BooleanField(default=False)
    
    # Notes and summary
    dm_notes = models.TextField(
        blank=True,
        help_text="DM notes during combat"
    )
    combat_summary = models.TextField(
        blank=True,
        help_text="Summary of what happened in this combat"
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='combat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.encounter.title}) - Round {self.current_round}"
    
    def start_combat(self):
        """Start the combat session"""
        self.status = 'active'
        self.started_at = timezone.now()
        self.save()
    
    def end_combat(self):
        """End the combat session"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.total_rounds = self.current_round
        self.save()
    
    def next_turn(self):
        """Advance to the next turn in initiative order"""
        participants = self.participants.filter(is_active=True).order_by('initiative_order')
        
        if not participants.exists():
            return
            
        self.current_turn += 1
        
        # If we've gone through all participants, start a new round
        if self.current_turn >= participants.count():
            self.current_turn = 0
            self.current_round += 1
            
        self.save()
    
    def get_current_participant(self):
        """Get the participant whose turn it currently is"""
        participants = self.participants.filter(is_active=True).order_by('initiative_order')
        if participants.exists() and self.current_turn < participants.count():
            return participants[self.current_turn]
        return None
    
    def roll_initiative(self):
        """Roll initiative for all participants"""
        if self.initiative_rolled:
            return
            
        # Roll for enemies
        for participant in self.participants.filter(participant_type='enemy'):
            if participant.enemy:
                initiative_roll = random.randint(1, 20) + participant.enemy.get_dexterity_modifier()
                participant.initiative_roll = initiative_roll
                participant.save()
        
        # Players will need to enter their initiative manually
        self.initiative_rolled = True
        self._assign_initiative_order()
        self.save()
    
    def _assign_initiative_order(self):
        """Assign initiative order based on rolls"""
        participants = list(self.participants.all())
        # Sort by initiative roll (highest first), then by dexterity modifier as tiebreaker
        participants.sort(key=lambda p: (
            p.initiative_roll or 0,
            p.get_dexterity_modifier()
        ), reverse=True)
        
        for index, participant in enumerate(participants):
            participant.initiative_order = index
            participant.save()


class CombatParticipant(models.Model):
    """
    Represents a participant in combat (player character or enemy)
    """
    PARTICIPANT_TYPES = [
        ('player', 'Player Character'),
        ('enemy', 'Enemy'),
        ('ally', 'Ally NPC'),
    ]
    
    combat_session = models.ForeignKey(
        CombatSession, on_delete=models.CASCADE, related_name='participants'
    )
    participant_type = models.CharField(max_length=20, choices=PARTICIPANT_TYPES)
    
    # References to the actual entities
    character = models.ForeignKey(
        CharacterSummary, on_delete=models.CASCADE, null=True, blank=True
    )
    enemy = models.ForeignKey(
        Enemy, on_delete=models.CASCADE, null=True, blank=True
    )
    
    # Combat state
    name = models.CharField(max_length=200)  # Display name (can be customized)
    current_hp = models.IntegerField()
    max_hp = models.IntegerField()
    temp_hp = models.IntegerField(default=0)
    
    # Initiative
    initiative_roll = models.IntegerField(null=True, blank=True)
    initiative_order = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)  # False if unconscious/dead
    is_hidden = models.BooleanField(default=False)  # For surprise/stealth
    
    # Position (for future map integration)
    position_x = models.IntegerField(null=True, blank=True)
    position_y = models.IntegerField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, help_text="Combat notes for this participant")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['initiative_order']
    
    def __str__(self):
        status = "Active" if self.is_active else "Down"
        return f"{self.name} ({self.participant_type}) - {self.current_hp}/{self.max_hp} HP [{status}]"
    
    @property
    def is_bloodied(self):
        """Check if participant is bloodied (below half HP)"""
        return self.current_hp <= (self.max_hp // 2)
    
    @property
    def is_unconscious(self):
        """Check if participant is unconscious (0 HP)"""
        return self.current_hp <= 0
    
    def get_dexterity_modifier(self):
        """Get dexterity modifier for initiative tiebreaking"""
        if self.character:
            return self.character.dexterity_modifier if hasattr(self.character, 'dexterity_modifier') else 0
        elif self.enemy:
            return self.enemy.get_dexterity_modifier()
        return 0
    
    def take_damage(self, damage):
        """Apply damage to the participant"""
        # Apply to temp HP first
        if self.temp_hp > 0:
            if damage <= self.temp_hp:
                self.temp_hp -= damage
                damage = 0
            else:
                damage -= self.temp_hp
                self.temp_hp = 0
        
        # Apply remaining damage to HP
        self.current_hp = max(0, self.current_hp - damage)
        
        # Check if participant is knocked unconscious
        if self.current_hp <= 0:
            self.is_active = False
            
        self.save()
    
    def heal(self, healing):
        """Apply healing to the participant"""
        self.current_hp = min(self.max_hp, self.current_hp + healing)
        
        # If healed above 0, reactivate
        if self.current_hp > 0 and not self.is_active:
            self.is_active = True
            
        self.save()
    
    def add_temp_hp(self, temp_hp):
        """Add temporary hit points"""
        # Temp HP doesn't stack, take the higher value
        self.temp_hp = max(self.temp_hp, temp_hp)
        self.save()


class StatusEffect(models.Model):
    """
    Tracks status effects on combat participants
    """
    EFFECT_TYPES = [
        ('condition', 'Condition'),
        ('buff', 'Buff'),
        ('debuff', 'Debuff'),
        ('spell', 'Spell Effect'),
    ]
    
    participant = models.ForeignKey(
        CombatParticipant, on_delete=models.CASCADE, related_name='status_effects'
    )
    name = models.CharField(max_length=100)
    effect_type = models.CharField(max_length=20, choices=EFFECT_TYPES, default='condition')
    description = models.TextField(blank=True)
    
    # Duration
    duration_rounds = models.IntegerField(null=True, blank=True)  # None = permanent
    rounds_remaining = models.IntegerField(null=True, blank=True)
    
    # Effects on stats (for common conditions)
    affects_attack = models.BooleanField(default=False)
    affects_damage = models.BooleanField(default=False)
    affects_saves = models.BooleanField(default=False)
    affects_movement = models.BooleanField(default=False)
    
    # Automatic effects
    auto_damage_per_turn = models.IntegerField(default=0)  # For ongoing damage
    auto_healing_per_turn = models.IntegerField(default=0)  # For regeneration
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        duration_str = f" ({self.rounds_remaining} rounds)" if self.rounds_remaining else ""
        return f"{self.participant.name}: {self.name}{duration_str}"
    
    def advance_round(self):
        """Called at the start of each round to handle duration and effects"""
        # Apply automatic effects
        if self.auto_damage_per_turn > 0:
            self.participant.take_damage(self.auto_damage_per_turn)
        
        if self.auto_healing_per_turn > 0:
            self.participant.heal(self.auto_healing_per_turn)
        
        # Reduce duration
        if self.rounds_remaining is not None:
            self.rounds_remaining -= 1
            if self.rounds_remaining <= 0:
                self.delete()
                return
        
        self.save()


class CombatAction(models.Model):
    """
    Log of actions taken during combat
    """
    ACTION_TYPES = [
        ('attack', 'Attack'),
        ('damage', 'Damage'),
        ('heal', 'Healing'),
        ('spell', 'Spell'),
        ('move', 'Movement'),
        ('other', 'Other'),
    ]
    
    combat_session = models.ForeignKey(
        CombatSession, on_delete=models.CASCADE, related_name='actions'
    )
    round_number = models.PositiveIntegerField()
    participant = models.ForeignKey(
        CombatParticipant, on_delete=models.CASCADE, related_name='actions'
    )
    target = models.ForeignKey(
        CombatParticipant, on_delete=models.CASCADE, null=True, blank=True,
        related_name='targeted_actions'
    )
    
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    
    # Numeric values for damage/healing
    value = models.IntegerField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        target_str = f" vs {self.target.name}" if self.target else ""
        return f"R{self.round_number}: {self.participant.name} - {self.description}{target_str}"