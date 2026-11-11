from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extends standard Django User model with AniNova anime profile details,
    customizable anime avatar, and role-based permissions.
    """
    ROLE_CHOICES = (
        ('customer', 'Anime Enthusiast / Viewer'),
        ('creator', 'Anime Content Creator'),
        ('admin', 'AniNova Platform Administrator'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True, max_length=500)
    favorite_anime = models.CharField(max_length=200, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'streamflix_user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    @property
    def avatar_url(self):
        """Returns the user uploaded avatar URL if present, otherwise an anime avatar seed."""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return f"https://api.dicebear.com/7.x/adventurer/svg?seed={self.user.username}"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Signal receiver ensuring each Django User always has a corresponding UserProfile."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()


class Notification(models.Model):
    """
    In-app alerts for users regarding new anime episodes, simulcast releases, and renewals.
    """
    TYPE_CHOICES = (
        ('info', 'Information'),
        ('subscription', 'Subscription Update'),
        ('release', 'New Episode / Anime Release'),
        ('watchlist', 'Watchlist Reminder'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'streamflix_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
