from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from ..models import Campaign, Chapter, Encounter
from ..forms import ChapterForm, EncounterFormSet


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
        last_chapter = self.campaign.chapters.order_by("-order").first()
        form.instance.order = (last_chapter.order + 1) if last_chapter else 1

        if formset.is_valid():
            self.object = form.save()
            encounters = formset.save(commit=False)

            # Get the highest order number for existing encounters
            last_encounter = self.object.encounters.order_by("-order").first()
            next_order = (last_encounter.order + 1) if last_encounter else 1

            for enc in encounters:
                enc.chapter = self.object
                enc.owner = self.request.user
                # Only set order for new encounters (those without an ID)
                if not enc.id:
                    enc.order = next_order
                    next_order += 1
                enc.save()

            formset.save_m2m()
            messages.success(self.request, "Chapter created successfully.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class ChapterQuickCreateView(LoginRequiredMixin, CreateView):
    model = Chapter
    form_class = ChapterForm
    template_name = "chapters/chapter_quick_form.html"

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
        return context

    def form_valid(self, form):
        form.instance.campaign = self.campaign
        form.instance.owner = self.request.user

        # Auto-increment chapter number
        last_chapter = self.campaign.chapters.order_by("-order").first()
        form.instance.order = (last_chapter.order + 1) if last_chapter else 1

        messages.success(self.request, f"Chapter '{form.instance.title}' created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class ChapterDeleteView(LoginRequiredMixin, DeleteView):
    model = Chapter
    template_name = "chapters/chapter_delete_confirmation.html"
    pk_url_kwarg = 'chapter_id'

    def get_queryset(self):
        # Ensure only the chapter owner can delete from the correct campaign
        campaign_id = self.kwargs['campaign_id']
        return Chapter.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

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
    pk_url_kwarg = 'chapter_id'

    def get_queryset(self):
        # Only allow editing chapters if the user owns the parent campaign
        campaign_id = self.kwargs['campaign_id']
        return Chapter.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

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
            encounters = formset.save(commit=False)

            # Get the highest order number for existing encounters
            last_encounter = self.object.encounters.order_by("-order").first()
            next_order = (last_encounter.order + 1) if last_encounter else 1

            for enc in encounters:
                # Only set order for new encounters (those without an ID)
                if not enc.id:
                    enc.order = next_order
                    next_order += 1
                enc.save()

            formset.save_m2m()
            messages.success(self.request, "Chapter and encounters updated.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class ChapterDetailView(LoginRequiredMixin, DetailView):
    model = Chapter
    template_name = "chapters/chapter_detail.html"
    context_object_name = "chapter"
    pk_url_kwarg = 'chapter_id'

    def get_queryset(self):
        # Restrict chapters to ones owned by the current user via their campaign
        campaign_id = self.kwargs['campaign_id']
        return Chapter.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["encounters"] = self.object.encounters.order_by('order')
        return context


class ChapterStatusToggleView(LoginRequiredMixin, View):
    def post(self, request, campaign_id, chapter_id):
        chapter = get_object_or_404(
            Chapter.objects.select_related('campaign').filter(
                campaign__owner=request.user,
                campaign_id=campaign_id
            ),
            pk=chapter_id
        )
        
        # Cycle through status options
        status_cycle = {
            'not_started': 'in_progress',
            'in_progress': 'completed', 
            'completed': 'not_started'
        }
        
        chapter.status = status_cycle.get(chapter.status, 'not_started')
        chapter.save()
        
        # Return updated status for HTMX
        return render(request, 'chapters/components/_status_badge.html', {
            'chapter': chapter
        })


class ChapterReorderView(LoginRequiredMixin, View):
    def post(self, request, campaign_id):
        campaign = get_object_or_404(
            Campaign.objects.filter(owner=request.user),
            pk=campaign_id
        )
        
        # Get the new order from the request
        chapter_ids = request.POST.getlist('chapter_order')
        
        # Update each chapter's order
        for index, chapter_id in enumerate(chapter_ids):
            Chapter.objects.filter(
                id=chapter_id, 
                campaign=campaign
            ).update(order=index + 1)
        
        messages.success(request, "Chapter order updated successfully.")
        return JsonResponse({'status': 'success'})