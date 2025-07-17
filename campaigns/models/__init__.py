# Import all models for Django migrations compatibility
from .base import Campaign, CampaignCollaborator
from .content import Chapter, Encounter
from .world import Location, NPC
from .characters import CharacterSummary
from .sessions import SessionNote, ChatMessage, ChapterChatMessage
from .users import UserProfile

# Make all models available when importing from campaigns.models
__all__ = [
    'Campaign',
    'CampaignCollaborator',
    'Chapter', 
    'Encounter',
    'Location',
    'NPC',
    'CharacterSummary',
    'SessionNote',
    'ChatMessage',
    'ChapterChatMessage',
    'UserProfile',
]