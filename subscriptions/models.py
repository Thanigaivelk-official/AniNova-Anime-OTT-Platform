from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    """
    Available membership tiers (Free, Basic HD, Premium 4K Ultra HD, etc.).
    """
    DURATION_CHOICES = (
        ('monthly', 'Monthly (30 Days)'),
        ('quarterly', 'Quarterly (90 Days)'),
        ('yearly', 'Yearly (365 Days)'),
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    duration_type = models.CharField(max_length=20, choices=DURATION_CHOICES, default='monthly')
    duration_days = models.PositiveIntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Price in INR")
    max_screens = models.PositiveIntegerField(default=1, help_text="Concurrent streams allowed")
    max_quality = models.CharField(max_length=30, default='1080p Full HD')
    has_ads = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'streamflix_subscription_plans'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - ₹{self.price} / {self.get_duration_type_display()}"


class UserSubscription(models.Model):
    """
    Tracks an individual user's active membership validity.
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='user_subscriptions')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'streamflix_user_subscriptions'

    @property
    def is_currently_valid(self):
        return self.status == 'active' and self.end_date > timezone.now()

    def renew(self, days=None):
        if not days:
            days = self.plan.duration_days
        now = timezone.now()
        base = self.end_date if self.end_date > now else now
        self.end_date = base + timedelta(days=days)
        self.status = 'active'
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} (Expires: {self.end_date.strftime('%Y-%m-%d')})"
