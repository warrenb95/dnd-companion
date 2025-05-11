import json
import re
import logging

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages

from .models import (
    Campaign,
    Chapter,
    Location,
    NPC,
    SessionNote,
    ChatMessage,
    CharacterSummary,
    create_chapter_and_encounters_from_llm,
)
from .forms import (
    ChapterForm,
    LocationForm,
    NPCForm,
    SessionNoteForm,
    CharacterSummaryForm,
    ChapterUploadForm,
)
from .llm import (
    extract_multiple_npcs,
    extract_locations_from_text,
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
    template_name = "campaigns/chapter_form.html"

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


class ChapterUpdateView(UpdateView):
    model = Chapter
    form_class = ChapterForm
    template_name = "campaigns/chapter_form.html"

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class LocationCreateView(CreateView):
    model = Location
    form_class = LocationForm
    template_name = "campaigns/location_form.html"

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        form.instance.campaign = campaign
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class LocationUpdateView(UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "campaigns/location_form.html"

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCCreateView(CreateView):
    model = NPC
    form_class = NPCForm
    template_name = "campaigns/npc_form.html"

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        form.instance.campaign = campaign
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCUpdateView(UpdateView):
    model = NPC
    form_class = NPCForm
    template_name = "campaigns/npc_form.html"

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
    template_name = "campaigns/session_form.html"

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

def create_from_chat(request, campaign_id):
    if request.method == "POST":
        content = request.POST.get("content")
        campaign = get_object_or_404(Campaign, pk=campaign_id)

        try:
            npc_data_json = extract_multiple_npcs(content)
            # Strip markdown code block if present
            clean_json = re.sub(
                r"^```(json)?|```$", "", npc_data_json.strip(), flags=re.MULTILINE
            )

            npc_list = json.loads(clean_json)
            print("🔍 LLM RAW NPC JSON:\n", npc_list)
            npc_list = json.loads(npc_data_json)
            created_npcs = []

            for npc_data in npc_list:
                npc = NPC.objects.create(
                    campaign=campaign,
                    name=npc_data.get("name", "Unnamed"),
                    description=npc_data.get("description", ""),
                    role=npc_data.get("role", ""),
                    tags=", ".join(npc_data.get("tags", [])),
                    status=npc_data.get("status", "alive"),
                )

                npc.save()
                created_npcs.append(npc.name)

            messages.success(
                request,
                f"Created {len(created_npcs)} NPC(s): {', '.join(created_npcs)}.",
            )
            return redirect("campaigns:campaign_chat", campaign_id=campaign_id)

        except Exception as e:
            messages.error(request, f"NPC parsing failed: {e}")
            return redirect("campaigns:campaign_chat", campaign_id=campaign_id)


def create_locations_from_chat(request, campaign_id):
    if request.method == "POST":
        content = request.POST.get("content")
        campaign = get_object_or_404(Campaign, pk=campaign_id)

        try:
            location_data_json = extract_locations_from_text(content)
            # Strip markdown code block if present
            clean_json = re.sub(
                r"^```(json)?|```$", "", location_data_json.strip(), flags=re.MULTILINE
            )
            location_list = json.loads(clean_json)
            print("🔍 LLM RAW NPC JSON:\n", location_list)
            created_locs = []

            for loc in location_list:
                location = Location.objects.create(
                    campaign=campaign,
                    name=loc.get("name", "Unnamed"),
                    description=loc.get("description", ""),
                    region=loc.get("region", ""),
                    tags=", ".join(loc.get("tags", [])),
                )
                location.save()
                created_locs.append(location.name)

            messages.success(
                request,
                f"Created {len(created_locs)} Location(s): {', '.join(created_locs)}.",
            )
            return redirect("campaigns:campaign_chat", campaign_id=campaign_id)

        except Exception as e:
            messages.error(request, f"Location parsing failed: {e}")
            return redirect("campaigns:campaign_chat", campaign_id=campaign_id)

def clean_llm_json(raw_text):
    # Remove markdown code block
    clean = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE)

    # Replace all single quotes with double quotes
    clean = clean.replace("'", '"')

    # Fix bad quotes inside text: change something like entity"s to entity's
    clean = re.sub(r'(\w)"(\w)', r"\1'\2", clean)

    # Remove trailing commas
    clean = re.sub(r",\s*}", "}", clean)
    clean = re.sub(r",\s*]", "]", clean)

    return clean


class CreateCharacterView(CreateView):
    model = CharacterSummary
    form_class = CharacterSummaryForm
    template_name = "campaigns/character_form.html"

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
    template_name = "campaigns/character_form.html"

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class ChapterCreateFromPDFView(View):
    template_name = "campaigns/upload.html"

    def get(self, request, campaign_id):
        form = ChapterUploadForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, campaign_id):
        form = ChapterUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data["pdf_file"]
            try:
                campaign = get_object_or_404(Campaign, id=campaign_id)
                chapter = create_chapter_and_encounters_from_llm(pdf_file, campaign)
                chapter.save()
                return redirect("campaigns:chapter_preview", pk=chapter.pk, )
            except Exception as e:
                form.add_error(None, f"Error processing PDF: {str(e)}")
        else:
            logger.warning("Form submission failed. Errors: %s", form.errors)
            logger.info("Cleaned data (partial): %s", form.cleaned_data)
        return render(request, self.template_name, {"form": form})


class ChapterPreviewView(View):
    template_name = "campaigns/chapter_preview.html"

    def get(self, request, pk):
        chapter = get_object_or_404(Chapter, pk=pk)
        encounters = chapter.encounters.all()
        return render(
            request, self.template_name, {"chapter": chapter, "encounters": encounters}
        )


class ChapterDetailView(View):
    template_name = "campaigns/chapter_detail.html"

    def get(self, request, pk):
        chapter = get_object_or_404(Chapter, pk=pk)
        encounters = chapter.encounters.all()
        return render(
            request, self.template_name, {"chapter": chapter, "encounters": encounters}
        )
