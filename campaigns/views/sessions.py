from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.http import JsonResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import json

from ..models import Campaign, SessionSchedule, PlayerAvailability, ScheduledSession
from ..forms.sessions import SessionScheduleForm, PlayerAvailabilityForm


class SessionScheduleListView(LoginRequiredMixin, ListView):
    model = SessionSchedule
    template_name = "sessions/schedule_list.html"
    context_object_name = "schedules"

    def get_queryset(self):
        campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_id'], owner=self.request.user)
        return SessionSchedule.objects.filter(campaign=campaign)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = get_object_or_404(Campaign, pk=self.kwargs['campaign_id'], owner=self.request.user)
        return context


class SessionScheduleCreateView(LoginRequiredMixin, CreateView):
    model = SessionSchedule
    form_class = SessionScheduleForm
    template_name = "sessions/schedule_form.html"

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_id'], owner=self.request.user)
        form.instance.campaign = campaign
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Session schedule created! Share this link with your players: {self.request.build_absolute_uri(self.object.get_player_url())}")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = get_object_or_404(Campaign, pk=self.kwargs['campaign_id'], owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('campaigns:session_schedule_detail', kwargs={
            'campaign_id': self.kwargs['campaign_id'],
            'pk': self.object.pk
        })


class SessionScheduleDetailView(LoginRequiredMixin, DetailView):
    model = SessionSchedule
    template_name = "sessions/schedule_detail.html"
    context_object_name = "schedule"

    def get_queryset(self):
        campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_id'], owner=self.request.user)
        return SessionSchedule.objects.filter(campaign=campaign)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule = self.get_object()
        context['campaign'] = schedule.campaign
        context['player_url'] = self.request.build_absolute_uri(schedule.get_player_url())
        
        # Get only the most recent response per email to avoid duplicates
        latest_responses = []
        seen_emails = set()
        for response in schedule.player_availabilities.order_by('-updated_at'):
            if response.email not in seen_emails:
                latest_responses.append(response)
                seen_emails.add(response.email)
        
        context['responses'] = latest_responses
        
        # Build availability grid for display using latest responses
        context['availability_grid'] = self.build_availability_grid(schedule, latest_responses)
        
        # Add time slots for template
        context['time_slots'] = self.get_time_slots()
        
        # Calculate most popular time slots
        context['popular_slots'] = self.calculate_popular_slots(schedule, latest_responses)
        
        return context

    def build_availability_grid(self, schedule, responses=None):
        """Build a grid showing all player availability for easy viewing (Friday-Sunday only)"""
        grid = {}
        if responses is None:
            responses = schedule.player_availabilities.all()
        
        current_date = schedule.date_range_start
        while current_date <= schedule.date_range_end:
            # Only include Friday (4), Saturday (5), and Sunday (6)
            if current_date.weekday() in [4, 5, 6]:
                date_str = current_date.strftime('%Y-%m-%d')
                grid[date_str] = {
                    'date': current_date,
                    'players': []
                }
                
                for response in responses:
                    availability = response.get_availability_for_date(date_str)
                    grid[date_str]['players'].append({
                        'name': response.player_name,
                        'character': response.character_name,
                        'available_times': availability
                    })
            
            current_date += timedelta(days=1)
        
        return grid
    
    def get_time_slots(self):
        """Get available time slots"""
        return [
            ('morning', 'Morning (9:00 AM - 12:00 PM)'),
            ('afternoon', 'Afternoon (1:00 PM - 5:00 PM)'),
            ('evening', 'Evening (6:00 PM - 10:00 PM)'),
            ('late', 'Late Night (8:00 PM - 12:00 AM)'),
        ]
    
    def calculate_popular_slots(self, schedule, responses):
        """Calculate the most popular date-time combinations"""
        slot_counts = {}
        time_slot_names = {
            'morning': 'Morning (9:00 AM - 12:00 PM)',
            'afternoon': 'Afternoon (1:00 PM - 5:00 PM)', 
            'evening': 'Evening (6:00 PM - 10:00 PM)',
            'late': 'Late Night (8:00 PM - 12:00 AM)',
        }
        
        # Count availability for each date-time combination
        current_date = schedule.date_range_start
        while current_date <= schedule.date_range_end:
            # Only include Friday (4), Saturday (5), and Sunday (6)
            if current_date.weekday() in [4, 5, 6]:
                date_str = current_date.strftime('%Y-%m-%d')
                
                for time_slot, time_label in self.get_time_slots():
                    available_players = []
                    for response in responses:
                        if time_slot in response.get_availability_for_date(date_str):
                            available_players.append(response.player_name)
                    
                    if available_players:
                        slot_counts[(current_date, time_slot)] = {
                            'date': current_date,
                            'time_slot': time_slot,
                            'time_display': time_slot_names[time_slot],
                            'count': len(available_players),
                            'players': available_players
                        }
            
            current_date += timedelta(days=1)
        
        # Sort by count (descending) and return top 5
        popular_slots = sorted(slot_counts.values(), key=lambda x: x['count'], reverse=True)[:5]
        return popular_slots


class PlayerAvailabilityView(View):
    """Public view for players to submit availability - no login required"""
    
    def get(self, request, token):
        schedule = get_object_or_404(SessionSchedule, shareable_token=token)
        
        if schedule.status != 'collecting':
            return render(request, 'sessions/availability_closed.html', {'schedule': schedule})
        
        # Check if user already submitted (by email if provided)
        existing_response = None
        if 'email' in request.GET:
            existing_response = PlayerAvailability.objects.filter(
                session_schedule=schedule, 
                email=request.GET['email']
            ).first()
        
        form = PlayerAvailabilityForm()
        
        context = {
            'schedule': schedule,
            'form': form,
            'existing_response': existing_response,
            'date_range': self.get_date_range(schedule),
            'time_slots': self.get_time_slots()
        }
        
        return render(request, 'sessions/player_availability.html', context)
    
    def post(self, request, token):
        schedule = get_object_or_404(SessionSchedule, shareable_token=token)
        
        if schedule.status != 'collecting':
            return render(request, 'sessions/availability_closed.html', {'schedule': schedule})
        
        form = PlayerAvailabilityForm(request.POST)
        
        if form.is_valid():
            # Get or create player availability
            availability, created = PlayerAvailability.objects.get_or_create(
                session_schedule=schedule,
                email=form.cleaned_data['email'],
                defaults={
                    'player_name': form.cleaned_data['player_name'],
                    'character_name': form.cleaned_data.get('character_name', ''),
                }
            )
            
            if not created:
                # Update existing response
                availability.player_name = form.cleaned_data['player_name']
                availability.character_name = form.cleaned_data.get('character_name', '')
            
            # Process availability data from form
            availability_data = {}
            for key, value in request.POST.items():
                if key.startswith('times_'):
                    date_str = key.replace('times_', '')
                    time_slots = request.POST.getlist(key)
                    if time_slots:  # If any time slots are selected
                        availability_data[date_str] = time_slots
            
            availability.availability_data = availability_data
            availability.save()
            
            messages.success(request, "Thank you! Your availability has been submitted.")
            return render(request, 'sessions/availability_success.html', {
                'schedule': schedule,
                'availability': availability
            })
        
        context = {
            'schedule': schedule,
            'form': form,
            'date_range': self.get_date_range(schedule),
            'time_slots': self.get_time_slots()
        }
        
        return render(request, 'sessions/player_availability.html', context)
    
    def get_date_range(self, schedule):
        """Get list of dates in the schedule range (Friday-Sunday only)"""
        dates = []
        current_date = schedule.date_range_start
        while current_date <= schedule.date_range_end:
            # Only include Friday (4), Saturday (5), and Sunday (6)
            if current_date.weekday() in [4, 5, 6]:
                dates.append(current_date)
            current_date += timedelta(days=1)
        return dates
    
    def get_time_slots(self):
        """Get available time slots"""
        return [
            ('morning', 'Morning (9:00 AM - 12:00 PM)'),
            ('afternoon', 'Afternoon (1:00 PM - 5:00 PM)'),
            ('evening', 'Evening (6:00 PM - 10:00 PM)'),
            ('late', 'Late Night (8:00 PM - 12:00 AM)'),
        ]


class ScheduleSessionView(LoginRequiredMixin, View):
    """DM confirms a session time"""
    
    def post(self, request, campaign_id, pk):
        campaign = get_object_or_404(Campaign, pk=campaign_id, owner=request.user)
        schedule = get_object_or_404(SessionSchedule, pk=pk, campaign=campaign)
        
        if not schedule.can_schedule:
            messages.error(request, "Cannot schedule session at this time.")
            return redirect('campaigns:session_schedule_detail', campaign_id=campaign_id, pk=pk)
        
        # Get the selected datetime from form
        selected_date = request.POST.get('selected_date')
        selected_time = request.POST.get('selected_time')
        
        if not selected_date or not selected_time:
            messages.error(request, "Please select a date and time.")
            return redirect('campaigns:session_schedule_detail', campaign_id=campaign_id, pk=pk)
        
        # Convert to datetime
        try:
            # Map time slots to actual times
            time_mapping = {
                'morning': '09:00',
                'afternoon': '13:00', 
                'evening': '18:00',
                'late': '20:00'
            }
            
            time_str = time_mapping.get(selected_time, '18:00')
            scheduled_datetime = datetime.strptime(f"{selected_date} {time_str}", "%Y-%m-%d %H:%M")
            scheduled_datetime = timezone.make_aware(scheduled_datetime)
            
        except ValueError:
            messages.error(request, "Invalid date or time selected.")
            return redirect('campaigns:session_schedule_detail', campaign_id=campaign_id, pk=pk)
        
        # Create scheduled session
        scheduled_session = ScheduledSession.objects.create(
            session_schedule=schedule,
            scheduled_datetime=scheduled_datetime,
            duration_hours=schedule.session_duration
        )
        
        # Add participants who are available at this time
        date_str = selected_date
        for availability in schedule.player_availabilities.all():
            if selected_time in availability.get_availability_for_date(date_str):
                scheduled_session.participants.add(availability)
        
        # Update schedule status
        schedule.status = 'scheduled'
        schedule.save()
        
        # Send email notifications
        self.send_confirmation_emails(scheduled_session)
        
        messages.success(request, f"Session scheduled for {scheduled_datetime.strftime('%B %d, %Y at %I:%M %p')}")
        return redirect('campaigns:session_schedule_detail', campaign_id=campaign_id, pk=pk)
    
    def send_confirmation_emails(self, scheduled_session):
        """Send email notifications to participants"""
        if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
            return  # Skip if email not configured
        
        subject = f"D&D Session Scheduled - {scheduled_session.session_schedule.campaign.title}"
        
        for participant in scheduled_session.participants.all():
            message = f"""
Hi {participant.player_name},

Your D&D session has been scheduled!

Campaign: {scheduled_session.session_schedule.campaign.title}
Date & Time: {scheduled_session.scheduled_datetime.strftime('%B %d, %Y at %I:%M %p')}
Duration: {scheduled_session.duration_hours} hours

See you at the table!
"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [participant.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Silently fail email sending