import logging

from django.views.generic import (
    DeleteView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse

from .models import (
    Campaign,
    Chapter,
    Location,
    NPC,
    SessionNote,
    CharacterSummary,
)
from .forms import (
    ChapterForm,
    LocationForm,
    NPCForm,
    SessionNoteForm,
    CharacterSummaryForm,
)
from .llm import (
    generate_session_summary,
)

logger = logging.getLogger(__name__)
logger.setLevel(level="DEBUG")


class CampaignListView(ListView):
    model = Campaign
    template_name = "campaigns/campaign_list.html"
    context_object_name = "campaigns"


class CampaignDetailView(DetailView):
    model = Campaign
    template_name = "campaigns/campaign_detail.html"
    context_object_name = "campaign"


class CampaignCreateView(CreateView):
    model = Campaign
    fields = ["title", "description"]
    template_name = "campaigns/campaign_form.html"
    success_url = reverse_lazy("campaigns:campaign_list")


class ChapterCreateView(CreateView):
    model = Chapter
    form_class = ChapterForm
    template_name = "chapters/chapter_create_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        context["campaign"] = campaign
        return context

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        form.instance.campaign = campaign

        # Auto-increment order field
        last_chapter = campaign.chapters.order_by("-number").first()
        form.instance.number = (last_chapter.number + 1) if last_chapter else 1

        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()

class ChapterDeleteView(DeleteView):
    model = Chapter
    template_name = "chapters/chapter_delete_confirmation.html"

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()

class ChapterUpdateView(UpdateView):
    model = Chapter
    form_class = ChapterForm
    template_name = "chapters/chapter_update_form.html"

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class LocationCreateView(CreateView):
    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        context["campaign"] = campaign
        return context

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        form.instance.campaign = campaign
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class LocationUpdateView(UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location: Location = self.object
        context["campaign"] = location.campaign
        return context

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCCreateView(CreateView):
    model = NPC
    form_class = NPCForm
    template_name = "npcs/npc_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        context["campaign"] = campaign
        return context

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        form.instance.campaign = campaign
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCUpdateView(UpdateView):
    model = NPC
    form_class = NPCForm
    template_name = "npcs/npc_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        npc: NPC = self.object
        context["campaign"] = npc.campaign
        return context

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class GenerateSessionSummaryView(View):
    def post(self, request, pk):
        session = SessionNote.objects.get(pk=pk)
        if not session.notes:
            return HttpResponseRedirect(reverse("campaigns:campaign_list"))

        summary = generate_session_summary(
            session.notes, chapter_title=session.chapter.title
        )
        session.summary = summary
        session.save()

        return HttpResponseRedirect(session.chapter.campaign.get_absolute_url())


class SessionNoteCreateView(CreateView):
    model = SessionNote
    form_class = SessionNoteForm
    template_name = "sessions/session_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = get_object_or_404(Chapter, pk=self.kwargs["chapter_id"])
        context["campaign"] = chapter.campaign
        return context


    def form_valid(self, form):
        chapter = get_object_or_404(Chapter, pk=self.kwargs["chapter_id"])
        form.instance.chapter = chapter
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.chapter.campaign.get_absolute_url()


def export_campaign_markdown(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    lines = [
        f"# {campaign.title}",
        "",
        campaign.description or "",
        "",
        "---",
        "",
        "## 📍 Locations",
    ]

    for loc in campaign.locations.all():
        lines += [
            f"### **{loc.name}**",
            f"- **Region:** {loc.region or '_Unknown_'}",
            f"- **Tags:** {loc.tags or '_None_'}",
            "",
            f"{loc.description.strip() if loc.description else '_No description_'}",
            "",
        ]

    lines += ["", "## 👤 NPCs"]

    for npc in campaign.npcs.all():
        lines += [
            f"### **{npc.name}**",
            f"- **Role:** {npc.role or '_Unknown_'}",
            f"- **Status:** {npc.status.capitalize()}",
            f"- **Location:** {npc.location.name if npc.location else '_Unknown_'}",
            f"- **Tags:** {npc.tags or '_None_'}",
            "",
            f"{npc.description.strip() if npc.description else '_No description_'}",
            "",
        ]

    lines += ["", "---", "", "## 📖 Chapters"]

    for chapter in campaign.chapters.order_by("number"):
        lines += [
            f"### Chapter {chapter.number}: {chapter.title}",
            f"**Status:** {chapter.status.replace('_', ' ').capitalize()}",
            "",
            chapter.summary or "_No summary yet_",
            "",
        ]

        session_notes = chapter.session_notes.order_by("date")
        for note in session_notes:
            lines += [
                "<details>",
                f"<summary><strong>Session on {note.date}</strong></summary>",
                "",
                "#### Raw Notes:",
                note.notes.strip(),
                "",
                "#### Summary:",
                note.summary.strip() if note.summary else "_No summary available_",
                "",
                "</details>",
                "",
            ]

    # Generate response
    markdown_text = "\n".join(lines)
    response = HttpResponse(markdown_text, content_type="text/markdown")
    response["Content-Disposition"] = (
        f'attachment; filename="{campaign.title.lower().replace(" ", "_")}_export.md"'
    )
    return response

def save_campaign_summary(request, campaign_id):
    if request.method == "POST":
        content = request.POST.get("content")
        campaign = get_object_or_404(Campaign, pk=campaign_id)

        campaign.generated_summary = content
        campaign.save()
        return redirect(campaign.get_absolute_url())

class CharacterDetailView(DetailView):
    model = CharacterSummary
    template_name = "characters/details.html"
    context_object_name = "character"

class CreateCharacterView(CreateView):
    model = CharacterSummary
    form_class = CharacterSummaryForm
    template_name = "characters//character_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        context["campaign"] = campaign
        return context

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        form.instance.campaign = campaign

        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class UpdateCharacterView(UpdateView):
    model = CharacterSummary
    form_class = CharacterSummaryForm
    template_name = "characters/character_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character: CharacterSummary = self.object
        context["campaign"] = character.campaign
        return context

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()

class ChapterDetailView(View):
    template_name = "chapters/chapter_detail.html"

    def get(self, request, pk):
        chapter = get_object_or_404(Chapter, pk=pk)
        encounters = chapter.encounters.all()
        return render(
            request, self.template_name, {"chapter": chapter, "encounters": encounters}
        )
