from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q

from ..models import Campaign
from ..forms.campaigns import AddCoDMForm, RemoveCoDMForm


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
        # Return campaigns where user is owner or co-DM
        return Campaign.objects.filter(
            Q(owner=self.request.user) | 
            Q(collaborators__user=self.request.user, collaborators__permission_level='co_dm')
        ).distinct()


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = "campaigns/campaign_detail.html"
    context_object_name = "campaign"
    pk_url_kwarg = 'campaign_id'

    def get_queryset(self):
        # Return campaigns where user is owner or co-DM
        return Campaign.objects.filter(
            Q(owner=self.request.user) | 
            Q(collaborators__user=self.request.user, collaborators__permission_level='co_dm')
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = self.get_object()
        
        # Add co-DM management forms if user is the owner
        if campaign.owner == self.request.user:
            context['add_codm_form'] = AddCoDMForm(campaign=campaign)
            context['remove_codm_form'] = RemoveCoDMForm(campaign=campaign)
        
        # Add co-DM information
        context['co_dms'] = campaign.get_co_dms()
        context['is_owner'] = campaign.owner == self.request.user
        context['can_edit'] = campaign.can_edit(self.request.user)
        
        # Add scheduled sessions information
        if campaign.owner == self.request.user or context['can_edit']:
            # Get recent and upcoming scheduled sessions
            scheduled_sessions = []
            for schedule in campaign.session_schedules.filter(status='scheduled').order_by('-updated_at')[:5]:
                if hasattr(schedule, 'scheduled_session'):
                    scheduled_sessions.append(schedule.scheduled_session)
            context['scheduled_sessions'] = scheduled_sessions
        
        return context


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

        # Export encounters with their session notes
        for encounter in chapter.encounters.order_by("order"):
            lines += [
                f"#### {encounter.order}. {encounter.title} ({encounter.type})",
                f"**Summary:** {encounter.summary}",
                "",
            ]
            
            # Add session notes for this encounter
            session_notes = encounter.session_notes.order_by("date")
            for note in session_notes:
                lines += [
                    "<details>",
                    f"<summary><strong>Session on {note.date}</strong></summary>",
                    "",
                    "#### Raw Notes:",
                    note.content.strip(),
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


class AddCoDMView(LoginRequiredMixin, View):
    def get(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        
        # Only the owner can add co-DMs
        if campaign.owner != request.user:
            return HttpResponse("Unauthorized", status=403)
        
        form = AddCoDMForm(campaign=campaign)
        return render(request, 'campaigns/components/_codm_form.html', {
            'form': form,
            'campaign': campaign
        })
    
    def post(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        
        # Only the owner can add co-DMs
        if campaign.owner != request.user:
            return HttpResponse("Unauthorized", status=403)
        
        form = AddCoDMForm(request.POST, campaign=campaign)
        if form.is_valid():
            user = form.cleaned_data['username_or_email']
            success, message = campaign.add_co_dm(user)
            
            if success:
                return render(request, 'campaigns/components/_codm_success.html', {
                    'message': f"Successfully added {user.username} as a co-DM.",
                    'campaign': campaign
                })
            else:
                # Return form with error message
                return render(request, 'campaigns/components/_codm_form.html', {
                    'form': form,
                    'campaign': campaign,
                    'error_message': message
                })
        else:
            # Return form with validation errors
            return render(request, 'campaigns/components/_codm_form.html', {
                'form': form,
                'campaign': campaign
            })


class RemoveCoDMView(LoginRequiredMixin, View):
    def post(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        
        # Only the owner can remove co-DMs
        if campaign.owner != request.user:
            messages.error(request, "Only the campaign owner can remove co-DMs.")
            return redirect(campaign.get_absolute_url())
        
        form = RemoveCoDMForm(request.POST, campaign=campaign)
        if form.is_valid():
            user = form.cleaned_data['user_id']
            success, message = campaign.remove_co_dm(user)
            
            if success:
                messages.success(request, f"Successfully removed {user.username} as a co-DM.")
            else:
                messages.error(request, message)
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
        
        return redirect(campaign.get_absolute_url())