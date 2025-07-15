"""
User-related views for profile management and settings.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse_lazy

from ..models import UserProfile
from ..forms.users import UserProfileForm, UserAccountForm, StyledPasswordChangeForm


class UserSettingsView(LoginRequiredMixin, TemplateView):
    """
    Main user settings page that displays profile information and provides
    access to various user management functions.
    """
    template_name = 'users/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        
        context.update({
            'profile': profile,
            'user': self.request.user,
            'profile_form': UserProfileForm(instance=profile),
            'account_form': UserAccountForm(instance=self.request.user),
            'password_form': StyledPasswordChangeForm(user=self.request.user),
        })
        
        return context


class UpdateProfileView(LoginRequiredMixin, View):
    """
    Handle profile updates via HTMX or regular form submission.
    """
    
    def post(self, request):
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        form = UserProfileForm(request.POST, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('campaigns:user_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
            
            # Re-render the settings page with form errors
            context = {
                'profile': profile,
                'user': request.user,
                'profile_form': form,
                'account_form': UserAccountForm(instance=request.user),
                'password_form': StyledPasswordChangeForm(user=request.user),
            }
            return render(request, 'users/settings.html', context)


class UpdateAccountView(LoginRequiredMixin, View):
    """
    Handle account information updates.
    """
    
    def post(self, request):
        form = UserAccountForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account information has been updated successfully.')
            return redirect('campaigns:user_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
            
            # Get profile for context
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Re-render the settings page with form errors
            context = {
                'profile': profile,
                'user': request.user,
                'profile_form': UserProfileForm(instance=profile),
                'account_form': form,
                'password_form': StyledPasswordChangeForm(user=request.user),
            }
            return render(request, 'users/settings.html', context)


class ChangePasswordView(LoginRequiredMixin, View):
    """
    Handle password changes with proper session management.
    """
    
    def post(self, request):
        form = StyledPasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            # Save the new password
            user = form.save()
            
            # Important: Update the session to prevent logout
            update_session_auth_hash(request, user)
            
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('campaigns:user_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
            
            # Get profile for context
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Re-render the settings page with form errors
            context = {
                'profile': profile,
                'user': request.user,
                'profile_form': UserProfileForm(instance=profile),
                'account_form': UserAccountForm(instance=request.user),
                'password_form': form,
            }
            return render(request, 'users/settings.html', context)


@login_required
def user_profile_view(request, username=None):
    """
    View user profile - only allow viewing own profile for security.
    """
    # Security: Only allow users to view their own profile
    if username and username != request.user.username:
        messages.error(request, 'You can only view your own profile.')
        return redirect('campaigns:user_settings')
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
        'user': request.user,
        'is_own_profile': True,
    }
    
    return render(request, 'users/profile.html', context)