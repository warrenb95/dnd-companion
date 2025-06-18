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
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

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
    EncounterFormSet,
    LocationForm,
    NPCForm,
    SessionNoteForm,
    CharacterSummaryForm,
    StyledAuthenticationForm,
)
from .llm import (
    generate_session_summary,
)

logger = logging.getLogger(__name__)
logger.setLevel(level="DEBUG")

class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('campaigns:campaign_list') 
        return render(request, 'landing.html')

class CampaignListView(ListView):
    model = Campaign
    template_name = "campaigns/campaign_list.html"
    context_object_name = "campaigns"

    def get_queryset(self):
        return Campaign.objects.filter(owner=self.request.user)


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = "campaigns/campaign_detail.html"
    context_object_name = "campaign"

    def get_queryset(self):
        return Campaign.objects.filter(owner=self.request.user)


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    fields = ["title", "description"]
    template_name = "campaigns/campaign_form.html"
    success_url = reverse_lazy("campaigns:campaign_list")

    def form_valid(self, form):
        # Assign the campaign to the logged-in user
        form.instance.owner = self.request.user
        messages.success(self.request, "Campaign created successfully.")
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Optionally: add Tailwind CSS classes to form fields
        for field in form.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-md border border-gray-300 text-black'
            })
        return form


class ChapterCreateView(LoginRequiredMixin, CreateView):
    model = Chapter
    form_class = ChapterForm
    template_name = "chapters/chapter_create_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Fetch and cache the campaign object once
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        if self.request.POST:
            context["formset"] = EncounterFormSet(self.request.POST)
        else:
            context["formset"] = EncounterFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        form.instance.campaign = self.campaign
        form.instance.owner = self.request.user

        # Auto-increment chapter number
        last_chapter = self.campaign.chapters.order_by("-number").first()
        form.instance.number = (last_chapter.number + 1) if last_chapter else 1

        if formset.is_valid():
            self.object = form.save()
            encounters = formset.save(commit=False)

            for enc in encounters:
                enc.chapter = self.object
                enc.save()

            formset.save_m2m()
            messages.success(self.request, "Chapter created successfully.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class ChapterDeleteView(LoginRequiredMixin, DeleteView):
    model = Chapter
    template_name = "chapters/chapter_delete_confirmation.html"

    def get_queryset(self):
        # Ensure only the chapter owner can delete
        return Chapter.objects.select_related('campaign').filter(campaign__owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f"Chapter '{self.object.title}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class ChapterUpdateView(LoginRequiredMixin, UpdateView):
    model = Chapter
    form_class = ChapterForm
    template_name = "chapters/chapter_update_form.html"

    def get_queryset(self):
        # Only allow editing chapters if the user owns the parent campaign
        return Chapter.objects.select_related('campaign').filter(campaign__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = EncounterFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = EncounterFormSet(instance=self.object)
        context["campaign"] = self.object.campaign
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if formset.is_valid():
            self.object = form.save()
            formset.save()
            messages.success(self.request, "Chapter and encounters updated.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context

    def form_valid(self, form):
        form.instance.campaign = self.campaign
        form.instance.owner = self.request.user
        messages.success(self.request, "Location created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"

    def get_queryset(self):
        # Only allow access to locations owned via campaign
        return Location.objects.select_related('campaign').filter(campaign__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def form_valid(self, form):
        messages.success(self.request, "Location updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCCreateView(LoginRequiredMixin, CreateView):
    model = NPC
    form_class = NPCForm
    template_name = "npcs/npc_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Restrict access to only campaigns owned by the user
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context

    def form_valid(self, form):
        form.instance.campaign = self.campaign
        form.instance.owner = self.request.user
        messages.success(self.request, "NPC created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCUpdateView(LoginRequiredMixin, UpdateView):
    model = NPC
    form_class = NPCForm
    template_name = "npcs/npc_form.html"

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        return NPC.objects.select_related('campaign').filter(campaign__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def form_valid(self, form):
        messages.success(self.request, "NPC updated successfully.")
        return super().form_valid(form)

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


class SessionNoteCreateView(LoginRequiredMixin, CreateView):
    model = SessionNote
    form_class = SessionNoteForm
    template_name = "sessions/session_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Securely fetch the chapter through campaign ownership
        self.chapter = get_object_or_404(
            Chapter.objects.select_related('campaign').filter(campaign__owner=request.user),
            pk=self.kwargs["chapter_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chapter"] = self.chapter
        return context

    def form_valid(self, form):
        form.instance.chapter = self.chapter
        form.instance.owner = self.request.user
        messages.success(self.request, "Session note added.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.chapter.get_absolute_url()


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


class UpdateCharacterView(LoginRequiredMixin, UpdateView):
    model = CharacterSummary
    form_class = CharacterSummaryForm
    template_name = "characters/character_form.html"

    def get_queryset(self):
        # Restrict updates to only characters owned by this user via the campaign
        return CharacterSummary.objects.select_related('campaign').filter(campaign__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def form_valid(self, form):
        messages.success(self.request, "Character updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class ChapterDetailView(LoginRequiredMixin, DetailView):
    model = Chapter
    template_name = "chapters/chapter_detail.html"
    context_object_name = "chapter"

    def get_queryset(self):
        # Restrict chapters to ones owned by the current user via their campaign
        return Chapter.objects.select_related('campaign').filter(campaign__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["encounters"] = self.object.encounters.all()
        return context


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        form = StyledAuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = StyledAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('campaigns:home')
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, self.template_name, {'form': form})

