"""
User-related forms for profile management and authentication.
"""

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from ..models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    
    class Meta:
        model = UserProfile
        fields = ['user_type', 'preferred_name']
        widgets = {
            'user_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'preferred_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'How you\'d like to be addressed'
            })
        }


class UserAccountForm(forms.ModelForm):
    """Form for updating basic user account information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Email address'
            })
        }


class StyledPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with consistent styling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style all password fields consistently
        password_field_attrs = {
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'autocomplete': 'off'
        }
        
        self.fields['old_password'].widget.attrs.update({
            **password_field_attrs,
            'placeholder': 'Current password'
        })
        
        self.fields['new_password1'].widget.attrs.update({
            **password_field_attrs,
            'placeholder': 'New password'
        })
        
        self.fields['new_password2'].widget.attrs.update({
            **password_field_attrs,
            'placeholder': 'Confirm new password'
        })
        
        # Update field labels
        self.fields['old_password'].label = 'Current Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'
        
        # Add help text
        self.fields['new_password1'].help_text = (
            'Your password must contain at least 8 characters and cannot be entirely numeric.'
        )