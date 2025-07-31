from django.urls import path
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from dnd_companion import settings

from .views import CampaignListView, CampaignDetailView, CampaignCreateView, CampaignUpdateView, CampaignDeleteView, ChapterDeleteView, CharacterDetailView, EncounterNoteCreateView, EncounterNoteFormView, EncounterNoteEditView, EncounterNoteUpdateView, EncounterNoteDeleteView, HomeView, empty_fragment, ChapterStatusToggleView, ChapterReorderView, UserSettingsView, UpdateProfileView, UpdateAccountView, ChangePasswordView, user_profile_view, SessionScheduleListView, SessionScheduleCreateView, SessionScheduleDetailView, PlayerAvailabilityView, ScheduleSessionView
from .views import ChapterCreateView, ChapterQuickCreateView, ChapterUpdateView, ChapterDetailView, EncounterCreateView, EncounterUpdateView, EncounterDeleteView
from .views import CreateCharacterView, UpdateCharacterView
from .views import LocationCreateView, LocationUpdateView
from .views import NPCCreateView, NPCUpdateView
from .views import LoginView
from .views import (
    export_campaign_markdown,
    save_campaign_summary,
)
from . import htmx_views
from .views.campaigns import AddCoDMView, RemoveCoDMView
from . import redirect_views

app_name = "campaigns"

urlpatterns = [
    # Authentication & Static Pages
    path("", HomeView.as_view(), name="home"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='campaigns:home'), name='logout'),
    path("settings/", UserSettingsView.as_view(), name="user_settings"),
    path("settings/profile/", UpdateProfileView.as_view(), name="update_profile"),
    path("settings/account/", UpdateAccountView.as_view(), name="update_account"),
    path("settings/password/", ChangePasswordView.as_view(), name="change_password"),
    path("profile/", user_profile_view, name="user_profile"),
    path("profile/<str:username>/", user_profile_view, name="user_profile_detail"),
    path("empty/", empty_fragment, name="empty_fragment"),
    
    # Campaign Management
    path("campaigns/", CampaignListView.as_view(), name="campaign_list"),
    path("campaigns/create/", CampaignCreateView.as_view(), name="campaign_create"),
    path("campaigns/<int:campaign_id>/", CampaignDetailView.as_view(), name="campaign_detail"),
    path("campaigns/<int:campaign_id>/edit/", CampaignUpdateView.as_view(), name="campaign_edit"),
    path("campaigns/<int:campaign_id>/delete/", CampaignDeleteView.as_view(), name="campaign_delete"),
    path("campaigns/<int:campaign_id>/export/", export_campaign_markdown, name="export_markdown"),
    path("campaigns/<int:campaign_id>/save-summary/", save_campaign_summary, name="save_campaign_summary"),
    
    # Campaign Collaboration
    path("campaigns/<int:campaign_id>/collaborators/add/", AddCoDMView.as_view(), name="add_codm"),
    path("campaigns/<int:campaign_id>/collaborators/remove/", RemoveCoDMView.as_view(), name="remove_codm"),
    
    # Chapter Management (Nested under Campaign)
    path("campaigns/<int:campaign_id>/chapters/add/", ChapterCreateView.as_view(), name="chapter_create"),
    path("campaigns/<int:campaign_id>/chapters/quick-add/", ChapterQuickCreateView.as_view(), name="chapter_quick_create"),
    path("campaigns/<int:campaign_id>/chapters/reorder/", ChapterReorderView.as_view(), name="chapter_reorder"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/", ChapterDetailView.as_view(), name="chapter_detail"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/edit/", ChapterUpdateView.as_view(), name="chapter_edit"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/delete/", ChapterDeleteView.as_view(), name="chapter_delete"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/toggle-status/", ChapterStatusToggleView.as_view(), name="chapter_status_toggle"),
    
    # Encounter Management (Nested under Chapter)
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/encounters/add/", EncounterCreateView.as_view(), name="encounter_create"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/encounters/<int:encounter_id>/edit/", EncounterUpdateView.as_view(), name="encounter_edit"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/encounters/<int:encounter_id>/delete/", EncounterDeleteView.as_view(), name="encounter_delete"),
    
    # Session Notes (Nested under Encounter)
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/encounters/<int:encounter_id>/notes/form/", EncounterNoteFormView.as_view(), name="encounter_note_form"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/encounters/<int:encounter_id>/notes/add/", EncounterNoteCreateView.as_view(), name="encounter_note_create"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/encounters/<int:encounter_id>/notes/<int:note_id>/edit/", EncounterNoteEditView.as_view(), name="encounter_note_edit"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/encounters/<int:encounter_id>/notes/<int:note_id>/update/", EncounterNoteUpdateView.as_view(), name="encounter_note_update"),
    path("campaigns/<int:campaign_id>/chapters/<int:chapter_id>/encounters/<int:encounter_id>/notes/<int:note_id>/delete/", EncounterNoteDeleteView.as_view(), name="encounter_note_delete"),
    
    # Campaign World Resources (Nested under Campaign)
    path("campaigns/<int:campaign_id>/locations/add/", LocationCreateView.as_view(), name="location_create"),
    path("campaigns/<int:campaign_id>/locations/<int:location_id>/edit/", LocationUpdateView.as_view(), name="location_edit"),
    path("campaigns/<int:campaign_id>/npcs/add/", NPCCreateView.as_view(), name="npc_create"),
    path("campaigns/<int:campaign_id>/npcs/<int:npc_id>/edit/", NPCUpdateView.as_view(), name="npc_edit"),
    path("campaigns/<int:campaign_id>/characters/add/", CreateCharacterView.as_view(), name="add_character"),
    path("campaigns/<int:campaign_id>/characters/<int:character_id>/view/", CharacterDetailView.as_view(), name="view_character"),
    path("campaigns/<int:campaign_id>/characters/<int:character_id>/edit/", UpdateCharacterView.as_view(), name="update_character"),
    
    # Session Scheduling (Nested under Campaign)
    path("campaigns/<int:campaign_id>/schedule/", SessionScheduleListView.as_view(), name="session_schedule_list"),
    path("campaigns/<int:campaign_id>/schedule/create/", SessionScheduleCreateView.as_view(), name="session_schedule_create"),
    path("campaigns/<int:campaign_id>/schedule/<int:schedule_id>/", SessionScheduleDetailView.as_view(), name="session_schedule_detail"),
    path("campaigns/<int:campaign_id>/schedule/<int:schedule_id>/confirm/", ScheduleSessionView.as_view(), name="schedule_session"),
    
    # Public player availability URL (no login required)
    path("schedule/<uuid:token>/", PlayerAvailabilityView.as_view(), name="player_availability"),
    
    # HTMX endpoints
    path("campaigns/<int:campaign_id>/encounter-form/add/", htmx_views.add_encounter_form, name="add_encounter_form"),
    path("encounter-form/<int:form_index>/remove/", htmx_views.remove_encounter_form, name="remove_encounter_form"),
    path("campaigns/<int:campaign_id>/encounter-form/empty/", htmx_views.get_empty_encounter_form, name="get_empty_encounter_form"),
    path("notification/<int:notification_id>/dismiss/", htmx_views.dismiss_notification, name="dismiss_notification"),
    path("campaigns/<int:campaign_id>/refresh/", htmx_views.refresh_campaign_detail, name="refresh_campaign_detail"),
    
    # Redirects for old URL patterns (temporary compatibility)
    path("chapters/<int:pk>/", redirect_views.redirect_chapter_detail, name="chapter_detail_redirect"),
    path("chapters/<int:pk>/edit/", redirect_views.redirect_chapter_edit, name="chapter_edit_redirect"),
    path("chapters/<int:pk>/delete/", redirect_views.redirect_chapter_delete, name="chapter_delete_redirect"),
    path("locations/<int:pk>/edit/", redirect_views.redirect_location_edit, name="location_edit_redirect"),
    path("npcs/<int:pk>/edit/", redirect_views.redirect_npc_edit, name="npc_edit_redirect"),
    path("character/<int:pk>/view/", redirect_views.redirect_character_view, name="character_view_redirect"),
    path("character/<int:pk>/edit/", redirect_views.redirect_character_edit, name="character_edit_redirect"),
]

