# Import all forms for backwards compatibility
from .content import ChapterForm, EncounterForm, EncounterFormSet, ChapterUploadForm
from .world import LocationForm, NPCForm
from .characters import CharacterSummaryForm
from .sessions import SessionNoteForm, StyledAuthenticationForm

# Make all forms available when importing from campaigns.forms
__all__ = [
    # Content forms
    'ChapterForm',
    'EncounterForm', 
    'EncounterFormSet',
    'ChapterUploadForm',
    
    # World forms
    'LocationForm',
    'NPCForm',
    
    # Character forms
    'CharacterSummaryForm',
    
    # Session forms
    'SessionNoteForm',
    'StyledAuthenticationForm',
]