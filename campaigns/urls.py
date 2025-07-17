from django.urls import path
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from dnd_companion import settings

from .views import CampaignListView, CampaignDetailView, CampaignCreateView, ChapterDeleteView, CharacterDetailView, EncounterNoteCreateView, EncounterNoteFormView, EncounterNoteEditView, EncounterNoteUpdateView, EncounterNoteDeleteView, HomeView, empty_fragment, ChapterStatusToggleView, ChapterReorderView, UserSettingsView, UpdateProfileView, UpdateAccountView, ChangePasswordView, user_profile_view
from .views import ChapterCreateView, ChapterQuickCreateView, ChapterUpdateView, ChapterDetailView, EncounterCreateView, EncounterUpdateView, EncounterDeleteView
from .views import CreateCharacterView, UpdateCharacterView
from .views import LocationCreateView, LocationUpdateView
from .views import NPCCreateView, NPCUpdateView
from .views import LoginView
from .views import (
    export_campaign_markdown,
    save_campaign_summary,
)
from .views.campaigns import AddCoDMView, RemoveCoDMView

app_name = "campaigns"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("campaigns/", CampaignListView.as_view(), name="campaign_list"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='campaigns:home'), name='logout'),
    path("<int:pk>/", CampaignDetailView.as_view(), name="campaign_detail"),
    path("create/", CampaignCreateView.as_view(), name="campaign_create"),
    path(
        "<int:campaign_id>/chapters/add/",
        ChapterCreateView.as_view(),
        name="chapter_create",
    ),
    path(
        "<int:campaign_id>/chapters/quick-add/",
        ChapterQuickCreateView.as_view(),
        name="chapter_quick_create",
    ),
    path(
        "chapters/<int:pk>/delete/",
        ChapterDeleteView.as_view(),
        name="chapter_delete",
    ),
    path("chapters/<int:pk>/edit/", ChapterUpdateView.as_view(), name="chapter_edit"),
    path("chapters/<int:pk>/", ChapterDetailView.as_view(), name="chapter_detail"),
    path("chapters/<int:pk>/toggle-status/", ChapterStatusToggleView.as_view(), name="chapter_status_toggle"),
    path("<int:campaign_id>/chapters/reorder/", ChapterReorderView.as_view(), name="chapter_reorder"),
    path(
        "chapters/<int:chapter_id>/encounters/add/",
        EncounterCreateView.as_view(),
        name="encounter_create",
    ),
    path(
        "encounters/<int:pk>/edit/",
        EncounterUpdateView.as_view(),
        name="encounter_edit",
    ),
    path(
        "encounters/<int:pk>/delete/",
        EncounterDeleteView.as_view(),
        name="encounter_delete",
    ),
    path(
        "<int:campaign_id>/locations/add/",
        LocationCreateView.as_view(),
        name="location_create",
    ),
    path(
        "locations/<int:pk>/edit/", LocationUpdateView.as_view(), name="location_edit"
    ),
    path("<int:campaign_id>/npcs/add/", NPCCreateView.as_view(), name="npc_create"),
    path("npcs/<int:pk>/edit/", NPCUpdateView.as_view(), name="npc_edit"),
    path("<int:encounter_id>/note-form/", EncounterNoteFormView.as_view(), name="encounter_note_form"),
    path("create-encounter-note/", EncounterNoteCreateView.as_view(), name="encounter_note_create"),
    path("notes/<int:note_id>/edit/", EncounterNoteEditView.as_view(), name="encounter_note_edit"),
    path("notes/<int:note_id>/update/", EncounterNoteUpdateView.as_view(), name="encounter_note_update"),
    path("notes/<int:note_id>/delete/", EncounterNoteDeleteView.as_view(), name="encounter_note_delete"),
    path("<int:campaign_id>/export/", export_campaign_markdown, name="export_markdown"),
    path(
        "<int:campaign_id>/save-campaign-summary/",
        save_campaign_summary,
        name="save_campaign_summary",
    ),
    path(
        "<int:campaign_id>/add-codm/",
        AddCoDMView.as_view(),
        name="add_codm",
    ),
    path(
        "<int:campaign_id>/remove-codm/",
        RemoveCoDMView.as_view(),
        name="remove_codm",
    ),
    path(
        "campaign/<int:campaign_id>/add_character/", CreateCharacterView.as_view(), name="add_character"
    ),
    path("character/<int:pk>/edit/", UpdateCharacterView.as_view(), name="update_character"),
    path("character/<int:pk>/view/", CharacterDetailView.as_view(), name="view_character"),
    path("settings/", UserSettingsView.as_view(), name="user_settings"),
    path("settings/profile/", UpdateProfileView.as_view(), name="update_profile"),
    path("settings/account/", UpdateAccountView.as_view(), name="update_account"),
    path("settings/password/", ChangePasswordView.as_view(), name="change_password"),
    path("profile/", user_profile_view, name="user_profile"),
    path("profile/<str:username>/", user_profile_view, name="user_profile_detail"),
    path("empty/", empty_fragment, name="empty_fragment"),
]

