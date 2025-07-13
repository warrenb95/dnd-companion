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
    EncounterNoteCreateView
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
    
    # API views
    'empty_fragment',
]
