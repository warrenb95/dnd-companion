from django.urls import path

from .views import (
    CampaignListView,
    CampaignDetailView,
    CampaignCreateView,
    confirm_generated_chapter_view,
    generate_chapter_view,
    save_campaign_summary,
)
from .views import ChapterCreateView, ChapterUpdateView
from .views import LocationCreateView, LocationUpdateView
from .views import NPCCreateView, NPCUpdateView
from .views import GenerateSessionSummaryView, SessionNoteCreateView
from .views import (
    export_campaign_markdown,
    campaign_chat_view,
    create_from_chat,
    create_locations_from_chat,
    chapter_chat_view,
    add_character,
    update_character,
)
from .views import ChatMessageEditView, ChatMessageDeleteView

app_name = "campaigns"

urlpatterns = [
    path("", CampaignListView.as_view(), name="campaign_list"),
    path("<int:pk>/", CampaignDetailView.as_view(), name="campaign_detail"),
    path("create/", CampaignCreateView.as_view(), name="campaign_create"),
    path(
        "<int:campaign_id>/chapters/add/",
        ChapterCreateView.as_view(),
        name="chapter_create",
    ),
    path("chapters/<int:pk>/edit/", ChapterUpdateView.as_view(), name="chapter_edit"),
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
    path(
        "sessions/<int:pk>/generate-summary/",
        GenerateSessionSummaryView.as_view(),
        name="generate_summary",
    ),
    path(
        "chapters/<int:chapter_id>/sessions/add/",
        SessionNoteCreateView.as_view(),
        name="session_create",
    ),
    path("<int:campaign_id>/export/", export_campaign_markdown, name="export_markdown"),
    path("<int:campaign_id>/chat/", campaign_chat_view, name="campaign_chat"),
    path("chat/<int:pk>/edit/", ChatMessageEditView.as_view(), name="chat_edit"),
    path("chat/<int:pk>/delete/", ChatMessageDeleteView.as_view(), name="chat_delete"),
    path(
        "<int:campaign_id>/chat/add-entity/", create_from_chat, name="create_from_chat"
    ),
    path(
        "<int:campaign_id>/chat/add-locations/",
        create_locations_from_chat,
        name="create_locations_from_chat",
    ),
    path(
        "<int:campaign_id>/save-campaign-summary/",
        save_campaign_summary,
        name="save_campaign_summary",
    ),
    path("<int:campaign_id>/chapter-chat/", chapter_chat_view, name="chapter_chat"),
    path(
        "<int:campaign_id>/generate-chapter/",
        generate_chapter_view,
        name="generate_chapter",
    ),
    path(
        "<int:campaign_id>/chapters/confirm/",
        confirm_generated_chapter_view,
        name="confirm_generated_chapter",
    ),
    path(
        "campaign/<int:campaign_id>/add_character/", add_character, name="add_character"
    ),
    path("character/<int:pk>/edit/", update_character, name="update_character"),
]
