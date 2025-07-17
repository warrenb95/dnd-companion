from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from ..models import Campaign


class AddCoDMForm(forms.Form):
    username_or_email = forms.CharField(
        max_length=150,
        label="Username or Email",
        help_text="Enter the username or email of the user you want to add as a co-DM",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'username or email@example.com'
        })
    )
    
    def __init__(self, *args, campaign=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.campaign = campaign
    
    def clean_username_or_email(self):
        identifier = self.cleaned_data['username_or_email']
        
        try:
            user = User.objects.get(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            )
            
            # Check if user is already the owner
            if self.campaign and user == self.campaign.owner:
                raise forms.ValidationError("This user is already the campaign owner.")
            
            # Check if user is already a co-DM
            if self.campaign and self.campaign.collaborators.filter(user=user, permission_level='co_dm').exists():
                raise forms.ValidationError("This user is already a co-DM for this campaign.")
            
            return user
            
        except User.DoesNotExist:
            raise forms.ValidationError("User not found. Please check the username or email.")
        except User.MultipleObjectsReturned:
            raise forms.ValidationError("Multiple users found. Please be more specific.")


class RemoveCoDMForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    
    def __init__(self, *args, campaign=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.campaign = campaign
    
    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        
        try:
            user = User.objects.get(pk=user_id)
            
            # Check if user is actually a co-DM for this campaign
            if self.campaign and not self.campaign.collaborators.filter(user=user, permission_level='co_dm').exists():
                raise forms.ValidationError("This user is not a co-DM for this campaign.")
            
            return user
            
        except User.DoesNotExist:
            raise forms.ValidationError("User not found.")


# Campaign forms would go here if we had custom campaign forms
# Currently Campaign uses generic forms in views, but we can add them here later