import json
import re

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
from django.views.decorators.http import require_POST

from .models import (
    Campaign,
    Chapter,
    Location,
    NPC,
    SessionNote,
    ChatMessage,
    ChapterChatMessage,
)
from .forms import (
    ChatMessageForm,
    ChapterForm,
    LocationForm,
    NPCForm,
    SessionNoteForm,
    ChapterChatMessageForm,
)
from .llm import (
    extract_multiple_npcs,
    extract_locations_from_text,
    get_campaign_chat_response,
    generate_session_summary,
    generate_chapter_from_context,
    get_chapter_chat_response,
)


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
        last_chapter = campaign.chapters.order_by("-order").first()
        form.instance.order = (last_chapter.order + 1) if last_chapter else 1

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

    for chapter in campaign.chapters.order_by("order"):
        lines += [
            f"### Chapter {chapter.order}: {chapter.title}",
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


def campaign_chat_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    chat_history = campaign.chat_messages.order_by("created_at")
    form = ChatMessageForm()

    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            user_message = form.save(commit=False)
            user_message.campaign = campaign
            user_message.role = "user"
            user_message.save()

            # Get LLM response
            assistant_reply = get_campaign_chat_response(
                campaign, chat_history | ChatMessage.objects.filter(pk=user_message.pk)
            )
            ChatMessage.objects.create(
                campaign=campaign, role="assistant", content=assistant_reply
            )
            return redirect("campaigns:campaign_chat", campaign_id=campaign.id)

    return render(
        request,
        "campaigns/campaign_chat.html",
        {"campaign": campaign, "messages": chat_history, "form": form},
    )


class ChatMessageEditView(UpdateView):
    model = ChatMessage
    fields = ["content"]
    template_name = "campaigns/chat_edit.html"

    def get_success_url(self):
        return reverse_lazy(
            "campaigns:campaign_chat", kwargs={"campaign_id": self.object.campaign.id}
        )


class ChatMessageDeleteView(DeleteView):
    model = ChatMessage
    template_name = "campaigns/chat_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "campaigns:campaign_chat", kwargs={"campaign_id": self.object.campaign.id}
        )


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


def chapter_chat_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    messages = campaign.chapter_chat_messages.order_by("created_at")
    form = ChapterChatMessageForm()

    if request.method == "POST":
        form = ChapterChatMessageForm(request.POST)
        if form.is_valid():
            user_msg = form.save(commit=False)
            user_msg.campaign = campaign
            user_msg.role = "user"
            user_msg.save()

            # Generate LLM reply
            llm_response = get_chapter_chat_response(
                campaign, messages | ChapterChatMessage.objects.filter(pk=user_msg.pk)
            )
            ChapterChatMessage.objects.create(
                campaign=campaign, role="assistant", content=llm_response
            )
            return redirect("campaigns:chapter_chat", campaign_id=campaign.id)

    return render(
        request,
        "campaigns/chapter_chat.html",
        {
            "campaign": campaign,
            "messages": messages,
            "form": form,
        },
    )


def generate_chapter_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    messages = campaign.chapter_chat_messages.order_by("created_at")
    previous_chapters = campaign.chapters.order_by("order")
    recent_notes = (
        Chapter.objects.filter(campaign=campaign)
        .prefetch_related("session_notes")
        .order_by("-order")
    )

    try:
        chapter_json = generate_chapter_from_context(
            campaign,
            messages,
            previous_chapters,
            recent_notes,
        )
        # Strip markdown code block if present
        clean_json = re.sub(
            r"^```(json)?|```$", "", chapter_json.strip(), flags=re.MULTILINE
        )

        parsed = json.loads(clean_json)

        return render(
            request,
            "campaigns/chapter_draft_preview.html",
            {
                "campaign": campaign,
                "chapter_json_raw": clean_json,
                "draft": parsed,  # ✅ this is what you'll render in the template
            },
        )

    except Exception as e:
        messages.error(request, f"Chapter generation failed: {e}")
        return redirect("campaigns:chapter_chat", campaign_id=campaign.id)


@require_POST
def confirm_generated_chapter_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)

    try:
        raw = request.POST.get("chapter_json", "")
        parsed = json.loads(raw)

        # Auto-increment order
        last_chapter = campaign.chapters.order_by("-order").first()
        next_order = (last_chapter.order + 1) if last_chapter else 1

        chapter = Chapter.objects.create(
            campaign=campaign,
            title=parsed.get("title", "Untitled Chapter"),
            summary=parsed.get("summary", ""),
            order=next_order,
            status="not_started",  # or whatever your default status is
        )

        messages.success(request, f"Chapter '{chapter.title}' added to campaign.")
        return redirect("campaigns:campaign_detail", campaign_id=campaign.id)

    except Exception as e:
        messages.error(request, f"Could not confirm chapter: {e}")
        return redirect("campaigns:generate_chapter", campaign_id=campaign.id)
