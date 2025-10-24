# Import all models for Django migrations compatibility
from .base import Campaign, CampaignCollaborator
from .content import Chapter, Encounter, ReadAloud
from .world import Location, NPC, Enemy
from .characters import CharacterSummary
from .sessions import SessionNote, ChatMessage, ChapterChatMessage, SessionSchedule, PlayerAvailability, ScheduledSession
from .users import UserProfile
from .combat import CombatSession, CombatParticipant, StatusEffect, CombatAction

# Make all models available when importing from campaigns.models
__all__ = [
    'Campaign',
    'CampaignCollaborator',
    'Chapter',
    'Encounter',
    'ReadAloud',
    'Location',
    'NPC',
    'Enemy',
    'CharacterSummary',
    'SessionNote',
    'ChatMessage',
    'ChapterChatMessage',
    'SessionSchedule',
    'PlayerAvailability',
    'ScheduledSession',
    'UserProfile',
    'CombatSession',
    'CombatParticipant',
    'StatusEffect',
    'CombatAction',
]