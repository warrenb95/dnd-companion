from django.urls import path

from .views import CampaignListView, CampaignDetailView, CampaignCreateView, ChapterDeleteView
from .views import ChapterCreateView, ChapterUpdateView, ChapterDetailView
from .views import CreateCharacterView, UpdateCharacterView
from .views import LocationCreateView, LocationUpdateView
from .views import NPCCreateView, NPCUpdateView
from .views import GenerateSessionSummaryView, SessionNoteCreateView
from .views import (
    export_campaign_markdown,
    save_campaign_summary,
)

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
    path(
        "chapters/<int:pk>/delete/",
        ChapterDeleteView.as_view(),
        name="chapter_delete",
    ),
    path("chapters/<int:pk>/edit/", ChapterUpdateView.as_view(), name="chapter_edit"),
    path("chapters/<int:pk>/", ChapterDetailView.as_view(), name="chapter_detail"),
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
    path(
        "<int:campaign_id>/save-campaign-summary/",
        save_campaign_summary,
        name="save_campaign_summary",
    ),
    path(
        "campaign/<int:campaign_id>/add_character/", CreateCharacterView.as_view(), name="add_character"
    ),
    path("character/<int:pk>/edit/", UpdateCharacterView.as_view(), name="update_character"),
]
