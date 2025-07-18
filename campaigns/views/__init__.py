# Import all views for backwards compatibility with urls.py
from .campaigns import (
    HomeView, 
    CampaignListView, 
    CampaignDetailView, 
    CampaignCreateView,
    export_campaign_markdown,
    save_campaign_summary
)
from .chapters import (
    ChapterCreateView,
    ChapterQuickCreateView, 
    ChapterDeleteView,
    ChapterUpdateView,
    ChapterDetailView,
    ChapterStatusToggleView,
    ChapterReorderView
)
from .encounters import (
    EncounterCreateView,
    EncounterUpdateView,
    EncounterDeleteView,
    EncounterNoteFormView,
    EncounterNoteCreateView,
    EncounterNoteEditView,
    EncounterNoteUpdateView,
    EncounterNoteDeleteView
)
from .world import (
    LocationCreateView,
    LocationUpdateView,
    NPCCreateView,
    NPCUpdateView
)
from .characters import (
    CharacterDetailView,
    CreateCharacterView,
    UpdateCharacterView
)
from .auth import LoginView
from .api import empty_fragment
from .users import UserSettingsView, UpdateProfileView, UpdateAccountView, ChangePasswordView, user_profile_view

# Make all views available when importing from campaigns.views
__all__ = [
    # Campaign views
    'HomeView',
    'CampaignListView', 
    'CampaignDetailView', 
    'CampaignCreateView',
    'export_campaign_markdown',
    'save_campaign_summary',
    
    # Chapter views
    'ChapterCreateView',
    'ChapterQuickCreateView', 
    'ChapterDeleteView',
    'ChapterUpdateView',
    'ChapterDetailView',
    'ChapterStatusToggleView',
    'ChapterReorderView',
    
    # Encounter views
    'EncounterCreateView',
    'EncounterUpdateView',
    'EncounterDeleteView',
    'EncounterNoteFormView',
    'EncounterNoteCreateView',
    'EncounterNoteEditView',
    'EncounterNoteUpdateView',
    'EncounterNoteDeleteView',
    
    # World views
    'LocationCreateView',
    'LocationUpdateView',
    'NPCCreateView',
    'NPCUpdateView',
    
    # Character views
    'CharacterDetailView',
    'CreateCharacterView',
    'UpdateCharacterView',
    
    # Auth views
    'LoginView',
    
    # User views
    'UserSettingsView',
    'UpdateProfileView',
    'UpdateAccountView',
    'ChangePasswordView',
    'user_profile_view',
    
    # API views
    'empty_fragment',
]
