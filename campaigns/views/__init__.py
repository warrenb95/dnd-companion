# Import all views for backwards compatibility with urls.py
from .campaigns import (
    HomeView,
    CampaignListView,
    CampaignDetailView,
    CampaignCreateView,
    CampaignUpdateView,
    CampaignDeleteView,
    export_campaign_markdown,
    export_encounter_markdown,
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
    EncounterNoteDeleteView,
    EncounterPlayView,
)
from .world import (
    LocationCreateView,
    LocationUpdateView,
    LocationDetailView,
    LocationDeleteView,
    NPCCreateView,
    NPCUpdateView,
    NPCDetailView,
    NPCDeleteView,
    NPCToEnemyConvertView,
    NPCPopupView,
    EnemyCreateView,
    EnemyUpdateView,
    EnemyDetailView,
    EnemyDeleteView,
    EnemyPopupView,
    ChapterNPCListView,
    ChapterLocationListView,
    ChapterCharacterListView,
    CampaignNPCListView,
    CampaignEnemyListView,
    CampaignLocationListView,
    CampaignCharacterListView
)
from .characters import (
    CharacterDetailView,
    CreateCharacterView,
    UpdateCharacterView,
    CharacterPopupView
)
from .auth import LoginView
from .api import empty_fragment
from .users import UserSettingsView, UpdateProfileView, UpdateAccountView, ChangePasswordView, user_profile_view
from .sessions import (
    SessionScheduleListView,
    SessionScheduleCreateView, 
    SessionScheduleDetailView,
    PlayerAvailabilityView,
    ScheduleSessionView
)
from .combat import (
    CombatSessionCreateView,
    CombatSessionDetailView,
    CombatSessionUpdateView,
    CombatSessionDeleteView
)

# Make all views available when importing from campaigns.views
__all__ = [
    # Campaign views
    'HomeView',
    'CampaignListView', 
    'CampaignDetailView', 
    'CampaignCreateView',
    'CampaignUpdateView',
    'CampaignDeleteView',
    'export_campaign_markdown',
    'export_encounter_markdown',
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
    'EncounterPlayView',
    
    # World views
    'LocationCreateView',
    'LocationUpdateView',
    'LocationDetailView',
    'LocationDeleteView',
    'NPCCreateView',
    'NPCUpdateView',
    'NPCDetailView',
    'NPCDeleteView',
    'NPCToEnemyConvertView',
    'NPCPopupView',
    'EnemyCreateView',
    'EnemyUpdateView',
    'EnemyDetailView',
    'EnemyDeleteView',
    'EnemyPopupView',
    'ChapterNPCListView',
    'ChapterLocationListView',
    'ChapterCharacterListView',
    'CampaignNPCListView',
    'CampaignEnemyListView',
    'CampaignLocationListView',
    'CampaignCharacterListView',
    
    # Character views
    'CharacterDetailView',
    'CreateCharacterView',
    'UpdateCharacterView',
    'CharacterPopupView',
    
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
    
    # Session scheduling views
    'SessionScheduleListView',
    'SessionScheduleCreateView', 
    'SessionScheduleDetailView',
    'PlayerAvailabilityView',
    'ScheduleSessionView',
    
    # Combat views
    'CombatSessionCreateView',
    'CombatSessionDetailView',
    'CombatSessionUpdateView',
    'CombatSessionDeleteView',
]
