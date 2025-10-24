# Import all forms for backwards compatibility
from .content import ChapterForm, EncounterForm, EncounterFormSet, ChapterUploadForm, ReadAloudForm
from .world import LocationForm, NPCForm, EnemyForm
from .characters import CharacterSummaryForm
from .sessions import SessionNoteForm, StyledAuthenticationForm
from .combat import CombatSessionForm

# Make all forms available when importing from campaigns.forms
__all__ = [
    # Content forms
    'ChapterForm',
    'EncounterForm',
    'EncounterFormSet',
    'ChapterUploadForm',
    'ReadAloudForm',
    
    # World forms
    'LocationForm',
    'NPCForm',
    'EnemyForm',
    
    # Character forms
    'CharacterSummaryForm',
    
    # Session forms
    'SessionNoteForm',
    'StyledAuthenticationForm',
    
    # Combat forms
    'CombatSessionForm',
]