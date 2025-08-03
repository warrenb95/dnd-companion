from django.db import models
from django.contrib.auth.models import User

from .base import Campaign


class Location(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="locations"
    )
    name = models.CharField(max_length=200, help_text="The location's name")
    description = models.TextField(blank=True, help_text="General description of the location")
    region = models.CharField(max_length=200, blank=True, help_text="Geographic region or area")
    tags = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Comma-separated tags for organization (e.g., 'dungeon, city, tavern')"
    )
    map_image = models.ImageField(
        upload_to="images/locations/", 
        blank=True,
        help_text="Optional map or visual reference for this location"
    )
    
    # Relationships
    chapters = models.ManyToManyField(
        'Chapter',
        blank=True,
        related_name='involved_locations',
        help_text="Chapters where this location is featured or visited"
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')

    class Meta:
        ordering = ['name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return str(self.name)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('campaigns:location_detail', kwargs={
            'campaign_id': self.campaign.id,
            'location_id': self.id
        })


class NPC(models.Model):
    ALIGNMENT_CHOICES = [
        ('lawful_good', 'Lawful Good'),
        ('neutral_good', 'Neutral Good'), 
        ('chaotic_good', 'Chaotic Good'),
        ('lawful_neutral', 'Lawful Neutral'),
        ('true_neutral', 'True Neutral'),
        ('chaotic_neutral', 'Chaotic Neutral'),
        ('lawful_evil', 'Lawful Evil'),
        ('neutral_evil', 'Neutral Evil'),
        ('chaotic_evil', 'Chaotic Evil'),
        ('unaligned', 'Unaligned'),
    ]
    
    STATUS_CHOICES = [
        ("alive", "Alive"),
        ("dead", "Dead"),
        ("missing", "Missing"),
        ("unknown", "Unknown"),
    ]
    
    SIZE_CHOICES = [
        ('tiny', 'Tiny'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('huge', 'Huge'),
        ('gargantuan', 'Gargantuan'),
    ]
    
    CREATURE_TYPE_CHOICES = [
        ('humanoid', 'Humanoid'),
        ('beast', 'Beast'),
        ('monstrosity', 'Monstrosity'),
        ('dragon', 'Dragon'),
        ('fey', 'Fey'),
        ('fiend', 'Fiend'),
        ('celestial', 'Celestial'),
        ('undead', 'Undead'),
        ('construct', 'Construct'),
        ('elemental', 'Elemental'),
        ('giant', 'Giant'),
        ('aberration', 'Aberration'),
        ('ooze', 'Ooze'),
        ('plant', 'Plant'),
    ]

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="npcs"
    )
    name = models.CharField(max_length=200, help_text="The NPC's full name")
    
    # Core NPC Details
    alignment = models.CharField(
        max_length=20, 
        choices=ALIGNMENT_CHOICES, 
        blank=True,
        help_text="The NPC's moral and ethical alignment"
    )
    appearance = models.TextField(
        blank=True, 
        help_text="Physical description, clothing, distinctive features"
    )
    
    # D&D 5e Stat Block Fields
    creature_type = models.CharField(
        max_length=20,
        choices=CREATURE_TYPE_CHOICES,
        default='humanoid',
        help_text="The creature's type (humanoid, beast, etc.)"
    )
    size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES,
        default='medium',
        help_text="The creature's size category"
    )
    
    # Core Stats
    armor_class = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Armor Class (AC)"
    )
    hit_points = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Maximum hit points"
    )
    hit_dice = models.CharField(
        max_length=50, blank=True,
        help_text="Hit dice formula (e.g., 2d8+2)"
    )
    speed = models.CharField(
        max_length=100, blank=True,
        help_text="Movement speeds (e.g., 30 ft., fly 60 ft.)"
    )
    
    # Ability Scores
    strength = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Strength score (1-30)"
    )
    dexterity = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Dexterity score (1-30)"
    )
    constitution = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Constitution score (1-30)"
    )
    intelligence = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Intelligence score (1-30)"
    )
    wisdom = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Wisdom score (1-30)"
    )
    charisma = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Charisma score (1-30)"
    )
    
    # Skills and Abilities
    saving_throws = models.CharField(
        max_length=200, blank=True,
        help_text="Proficient saving throws (e.g., Dex +5, Wis +3)"
    )
    skills = models.CharField(
        max_length=300, blank=True,
        help_text="Proficient skills (e.g., Perception +5, Stealth +7)"
    )
    damage_resistances = models.CharField(
        max_length=200, blank=True,
        help_text="Damage resistances (e.g., fire, cold)"
    )
    damage_immunities = models.CharField(
        max_length=200, blank=True,
        help_text="Damage immunities (e.g., poison, necrotic)"
    )
    condition_immunities = models.CharField(
        max_length=200, blank=True,
        help_text="Condition immunities (e.g., charmed, frightened)"
    )
    senses = models.CharField(
        max_length=200, blank=True,
        help_text="Special senses (e.g., darkvision 60 ft., passive Perception 13)"
    )
    languages = models.CharField(
        max_length=200, blank=True,
        help_text="Known languages (e.g., Common, Elvish)"
    )
    challenge_rating = models.CharField(
        max_length=10, blank=True,
        help_text="Challenge Rating (e.g., 1/2, 2, 5)"
    )
    proficiency_bonus = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Proficiency bonus (+2 to +9)"
    )
    
    # Special Abilities and Actions
    special_abilities = models.TextField(
        blank=True,
        help_text="Special abilities, traits, and features"
    )
    actions = models.TextField(
        blank=True,
        help_text="Available actions in combat"
    )
    legendary_actions = models.TextField(
        blank=True,
        help_text="Legendary actions (if applicable)"
    )
    
    personality = models.TextField(
        blank=True,
        help_text="Personality traits, mannerisms, speech patterns, motivations"
    )
    secret = models.TextField(
        blank=True,
        help_text="Hidden information, plot hooks, or secrets only the DM knows"
    )
    role = models.CharField(max_length=100, blank=True, help_text="Role in the story or society")
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Primary location where this NPC can be found"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="alive",
        help_text="Current status of the NPC"
    )
    tags = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Comma-separated tags for organization (e.g., 'merchant, guild member, quest giver')"
    )
    
    # Relationships
    chapters = models.ManyToManyField(
        'Chapter',
        blank=True,
        related_name='involved_npcs',
        help_text="Chapters where this NPC is involved or appears"
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='npcs')

    class Meta:
        ordering = ['name']
        verbose_name = 'NPC'
        verbose_name_plural = 'NPCs'

    def __str__(self):
        return str(self.name)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('campaigns:npc_detail', kwargs={
            'campaign_id': self.campaign.id,
            'npc_id': self.id
        })
    
    # Utility methods for D&D calculations
    def get_ability_modifier(self, score):
        """Calculate ability modifier from ability score."""
        if score is None:
            return None
        return (score - 10) // 2
    
    def get_strength_modifier(self):
        return self.get_ability_modifier(self.strength)
    
    def get_dexterity_modifier(self):
        return self.get_ability_modifier(self.dexterity)
    
    def get_constitution_modifier(self):
        return self.get_ability_modifier(self.constitution)
    
    def get_intelligence_modifier(self):
        return self.get_ability_modifier(self.intelligence)
    
    def get_wisdom_modifier(self):
        return self.get_ability_modifier(self.wisdom)
    
    def get_charisma_modifier(self):
        return self.get_ability_modifier(self.charisma)
    
    def format_modifier(self, modifier):
        """Format ability modifier with proper +/- sign."""
        if modifier is None:
            return ""
        return f"+{modifier}" if modifier >= 0 else str(modifier)
    
    # Template-friendly formatted modifier properties
    @property
    def strength_modifier_formatted(self):
        return self.format_modifier(self.get_strength_modifier())
    
    @property 
    def dexterity_modifier_formatted(self):
        return self.format_modifier(self.get_dexterity_modifier())
    
    @property
    def constitution_modifier_formatted(self):
        return self.format_modifier(self.get_constitution_modifier())
    
    @property
    def intelligence_modifier_formatted(self):
        return self.format_modifier(self.get_intelligence_modifier())
    
    @property
    def wisdom_modifier_formatted(self):
        return self.format_modifier(self.get_wisdom_modifier())
    
    @property
    def charisma_modifier_formatted(self):
        return self.format_modifier(self.get_charisma_modifier())
    
    def has_structured_stats(self):
        """Check if this NPC has any structured stat block data."""
        return any([
            self.armor_class, self.hit_points, self.strength, self.dexterity,
            self.constitution, self.intelligence, self.wisdom, self.charisma,
            self.challenge_rating, self.special_abilities, self.actions
        ])


class Enemy(models.Model):
    """
    Streamlined model for combat encounters - contains only essential D&D 5e stats 
    needed for combat without roleplay/campaign organization overhead.
    """
    SIZE_CHOICES = [
        ('tiny', 'Tiny'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('huge', 'Huge'),
        ('gargantuan', 'Gargantuan'),
    ]
    
    CREATURE_TYPE_CHOICES = [
        ('humanoid', 'Humanoid'),
        ('beast', 'Beast'),
        ('monstrosity', 'Monstrosity'),
        ('dragon', 'Dragon'),
        ('fey', 'Fey'),
        ('fiend', 'Fiend'),
        ('celestial', 'Celestial'),
        ('undead', 'Undead'),
        ('construct', 'Construct'),
        ('elemental', 'Elemental'),
        ('giant', 'Giant'),
        ('aberration', 'Aberration'),
        ('ooze', 'Ooze'),
        ('plant', 'Plant'),
    ]
    
    # Basic Identity
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="enemies"
    )
    name = models.CharField(max_length=200, help_text="Enemy name or type")
    size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES,
        default='medium',
        help_text="The creature's size category"
    )
    creature_type = models.CharField(
        max_length=20,
        choices=CREATURE_TYPE_CHOICES,
        default='humanoid',
        help_text="The creature's type"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief combat-relevant description or tactics notes"
    )
    
    # Core Combat Stats
    armor_class = models.PositiveIntegerField(
        help_text="Armor Class (AC)"
    )
    hit_points = models.PositiveIntegerField(
        help_text="Maximum hit points"
    )
    hit_dice = models.CharField(
        max_length=50, blank=True,
        help_text="Hit dice formula (e.g., 2d8+2)"
    )
    speed = models.CharField(
        max_length=100,
        help_text="Movement speeds (e.g., 30 ft., fly 60 ft.)"
    )
    
    # Ability Scores (required for combat calculations)
    strength = models.PositiveIntegerField(
        default=10,
        help_text="Strength score (1-30)"
    )
    dexterity = models.PositiveIntegerField(
        default=10,
        help_text="Dexterity score (1-30)"
    )
    constitution = models.PositiveIntegerField(
        default=10,
        help_text="Constitution score (1-30)"
    )
    intelligence = models.PositiveIntegerField(
        default=10,
        help_text="Intelligence score (1-30)"
    )
    wisdom = models.PositiveIntegerField(
        default=10,
        help_text="Wisdom score (1-30)"
    )
    charisma = models.PositiveIntegerField(
        default=10,
        help_text="Charisma score (1-30)"
    )
    
    # Combat Mechanics
    challenge_rating = models.CharField(
        max_length=10,
        help_text="Challenge Rating (e.g., 1/2, 2, 5)"
    )
    proficiency_bonus = models.PositiveIntegerField(
        default=2,
        help_text="Proficiency bonus (+2 to +9)"
    )
    saving_throws = models.CharField(
        max_length=200, blank=True,
        help_text="Proficient saving throws (e.g., Dex +5, Wis +3)"
    )
    skills = models.CharField(
        max_length=300, blank=True,
        help_text="Proficient skills (e.g., Perception +5, Stealth +7)"
    )
    
    # Defenses
    damage_resistances = models.CharField(
        max_length=200, blank=True,
        help_text="Damage resistances (e.g., fire, cold)"
    )
    damage_immunities = models.CharField(
        max_length=200, blank=True,
        help_text="Damage immunities (e.g., poison, necrotic)"
    )
    condition_immunities = models.CharField(
        max_length=200, blank=True,
        help_text="Condition immunities (e.g., charmed, frightened)"
    )
    senses = models.CharField(
        max_length=200, blank=True,
        help_text="Special senses (e.g., darkvision 60 ft., passive Perception 13)"
    )
    
    # Combat Actions
    special_abilities = models.TextField(
        blank=True,
        help_text="Special abilities, traits, and features for combat"
    )
    actions = models.TextField(
        blank=True,
        help_text="Available actions in combat"
    )
    legendary_actions = models.TextField(
        blank=True,
        help_text="Legendary actions (if applicable)"
    )
    
    # Relationships
    encounters = models.ManyToManyField(
        'Encounter',
        blank=True,
        related_name='enemies',
        help_text="Encounters where this enemy appears"
    )
    chapters = models.ManyToManyField(
        'Chapter',
        blank=True,
        related_name='involved_enemies',
        help_text="Chapters where this enemy is involved or appears"
    )
    source_npc = models.ForeignKey(
        NPC,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Source NPC if this enemy was converted from an NPC"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enemies')
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Enemy'
        verbose_name_plural = 'Enemies'
    
    def __str__(self):
        return f"{self.name} (CR {self.challenge_rating})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('campaigns:enemy_detail', kwargs={
            'campaign_id': self.campaign.id,
            'enemy_id': self.id
        })
    
    # Ability modifier calculations (same as NPC)
    def get_ability_modifier(self, score):
        """Calculate ability modifier from ability score."""
        return (score - 10) // 2
    
    def get_strength_modifier(self):
        return self.get_ability_modifier(self.strength)
    
    def get_dexterity_modifier(self):
        return self.get_ability_modifier(self.dexterity)
    
    def get_constitution_modifier(self):
        return self.get_ability_modifier(self.constitution)
    
    def get_intelligence_modifier(self):
        return self.get_ability_modifier(self.intelligence)
    
    def get_wisdom_modifier(self):
        return self.get_ability_modifier(self.wisdom)
    
    def get_charisma_modifier(self):
        return self.get_ability_modifier(self.charisma)
    
    def format_modifier(self, modifier):
        """Format ability modifier with proper +/- sign."""
        return f"+{modifier}" if modifier >= 0 else str(modifier)
    
    # Template-friendly formatted modifier properties
    @property
    def strength_modifier_formatted(self):
        return self.format_modifier(self.get_strength_modifier())
    
    @property 
    def dexterity_modifier_formatted(self):
        return self.format_modifier(self.get_dexterity_modifier())
    
    @property
    def constitution_modifier_formatted(self):
        return self.format_modifier(self.get_constitution_modifier())
    
    @property
    def intelligence_modifier_formatted(self):
        return self.format_modifier(self.get_intelligence_modifier())
    
    @property
    def wisdom_modifier_formatted(self):
        return self.format_modifier(self.get_wisdom_modifier())
    
    @property
    def charisma_modifier_formatted(self):
        return self.format_modifier(self.get_charisma_modifier())
    
    @property
    def initiative_modifier(self):
        """Calculate initiative modifier from dexterity."""
        return self.get_dexterity_modifier()
    
    @property
    def initiative_modifier_formatted(self):
        """Formatted initiative modifier for display."""
        return self.format_modifier(self.initiative_modifier)
    
    @classmethod
    def create_from_npc(cls, npc):
        """
        Create an Enemy instance from an existing NPC, 
        copying only combat-relevant fields.
        """
        enemy = cls(
            campaign=npc.campaign,
            name=npc.name,
            size=npc.size,
            creature_type=npc.creature_type,
            description=npc.appearance[:500] if npc.appearance else "",  # Truncate if too long
            armor_class=npc.armor_class or 10,
            hit_points=npc.hit_points or 1,
            hit_dice=npc.hit_dice,
            speed=npc.speed or "30 ft.",
            strength=npc.strength or 10,
            dexterity=npc.dexterity or 10,
            constitution=npc.constitution or 10,
            intelligence=npc.intelligence or 10,
            wisdom=npc.wisdom or 10,
            charisma=npc.charisma or 10,
            challenge_rating=npc.challenge_rating or "0",
            proficiency_bonus=npc.proficiency_bonus or 2,
            saving_throws=npc.saving_throws,
            skills=npc.skills,
            damage_resistances=npc.damage_resistances,
            damage_immunities=npc.damage_immunities,
            condition_immunities=npc.condition_immunities,
            senses=npc.senses,
            special_abilities=npc.special_abilities,
            actions=npc.actions,
            legendary_actions=npc.legendary_actions,
            source_npc=npc,
            owner=npc.owner
        )
        return enemy