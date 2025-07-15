"""
User profile models for different user types in the D&D Campaign Companion.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    """
    Base user profile model that extends Django's default User model.
    """
    USER_TYPE_CHOICES = [
        ('DM', 'Dungeon Master'),
        ('PLAYER', 'Player'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='DM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Profile information
    preferred_name = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="How you'd like to be addressed (optional)"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    @property
    def display_name(self):
        """Return preferred name if set, otherwise username."""
        return self.preferred_name if self.preferred_name else self.user.username
    
    @property
    def is_dm(self):
        """Check if user is a Dungeon Master."""
        return self.user_type == 'DM'
    
    @property
    def is_player(self):
        """Check if user is a Player."""
        return self.user_type == 'PLAYER'
    
    def get_absolute_url(self):
        """Return URL for user profile."""
        return reverse('campaigns:user_settings')


# Signal to automatically create user profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()