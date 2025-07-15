from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from ..models import Chapter, Encounter, SessionNote
from ..forms import EncounterForm


class EncounterCreateView(LoginRequiredMixin, CreateView):
    model = Encounter
    form_class = EncounterForm
    template_name = "encounters/encounter_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Fetch and cache the chapter object, ensuring user ownership
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
        # Auto-assign the encounter to the correct chapter and owner
        form.instance.chapter = self.chapter
        form.instance.owner = self.request.user
        
        # Auto-increment the order field (find highest order in chapter + 1)
        last_encounter = self.chapter.encounters.order_by("-order").first()
        form.instance.order = (last_encounter.order + 1) if last_encounter else 1
        
        messages.success(self.request, f"Encounter '{form.instance.title}' created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect back to chapter detail view after success
        return self.chapter.get_absolute_url()


class EncounterUpdateView(LoginRequiredMixin, UpdateView):
    model = Encounter
    form_class = EncounterForm
    template_name = "encounters/encounter_form.html"

    def get_queryset(self):
        # Only allow editing encounters if the user owns the parent campaign
        return Encounter.objects.select_related('chapter__campaign').filter(chapter__campaign__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chapter"] = self.object.chapter
        return context

    def form_valid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        
        # Log form submission details
        logger.info(f"Processing encounter form submission - User: {self.request.user.id}, "
                   f"Encounter: {form.instance.id}, Title: {form.instance.title}")
        
        # Check if map_image was uploaded
        if 'map_image' in form.changed_data:
            map_image = form.cleaned_data.get('map_image')
            if map_image:
                logger.info(f"New map image uploaded - Name: {map_image.name}, "
                           f"Size: {map_image.size} bytes, Content type: {map_image.content_type}")
            else:
                logger.info("Map image field was changed but no file provided")
        else:
            logger.info("No map image changes detected")
        
        try:
            result = super().form_valid(form)
            logger.info(f"Encounter saved successfully - ID: {form.instance.id}")
            
            # Log final map_image details if it exists
            if form.instance.map_image:
                logger.info(f"Final map image details - Name: {form.instance.map_image.name}, "
                           f"URL: {form.instance.map_image.url}")
            
            messages.success(self.request, f"Encounter '{form.instance.title}' updated successfully.")
            return result
        except Exception as e:
            logger.error(f"Error saving encounter - ID: {form.instance.id}, Error: {str(e)}")
            messages.error(self.request, f"Error saving encounter: {str(e)}")
            raise

    def get_success_url(self):
        # Redirect back to chapter detail view after success
        return self.object.chapter.get_absolute_url()


class EncounterDeleteView(LoginRequiredMixin, DeleteView):
    model = Encounter
    template_name = "encounters/encounter_delete_confirmation.html"

    def get_queryset(self):
        # Ensure only the encounter owner can delete (via campaign ownership)
        return Encounter.objects.select_related('chapter__campaign').filter(chapter__campaign__owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f"Encounter '{self.object.title}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.chapter.get_absolute_url()


class EncounterNoteFormView(View):
    def get(self, request, encounter_id):
        encounter = get_object_or_404(Encounter, pk=encounter_id)
        return render(request, "encounters/components/_note_form.html", {"encounter": encounter})


class EncounterNoteCreateView(View):
    def post(self, request):
        content = request.POST.get("content")
        encounter_id = request.POST.get("encounter")
        encounter = None

        if content and encounter_id:
            encounter = get_object_or_404(Encounter, pk=encounter_id)
            SessionNote.objects.create(encounter=encounter, content=content, owner=request.user)

        # Re-render the updated notes list as HTML
        return render(request, "encounters/components/_notes_list.html", {"enc": encounter})


class EncounterNoteEditView(LoginRequiredMixin, View):
    def get(self, request, note_id):
        note = get_object_or_404(
            SessionNote.objects.select_related('encounter__chapter__campaign'),
            pk=note_id,
            owner=request.user
        )
        return render(request, "encounters/components/_note_edit_form.html", {"note": note})


class EncounterNoteUpdateView(LoginRequiredMixin, View):
    def post(self, request, note_id):
        note = get_object_or_404(
            SessionNote.objects.select_related('encounter__chapter__campaign'),
            pk=note_id,
            owner=request.user
        )
        
        content = request.POST.get("content")
        date = request.POST.get("date")
        
        if content and date:
            note.content = content
            note.date = date
            note.save()
            messages.success(request, "Note updated successfully.")
        
        # Re-render the updated notes list as HTML
        return render(request, "encounters/components/_notes_list.html", {"enc": note.encounter})


class EncounterNoteDeleteView(LoginRequiredMixin, View):
    def delete(self, request, note_id):
        note = get_object_or_404(
            SessionNote.objects.select_related('encounter__chapter__campaign'),
            pk=note_id,
            owner=request.user
        )
        
        encounter = note.encounter
        note.delete()
        messages.success(request, "Note deleted successfully.")
        
        # Re-render the updated notes list as HTML
        return render(request, "encounters/components/_notes_list.html", {"enc": encounter})