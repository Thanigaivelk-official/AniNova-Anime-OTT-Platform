from django.db import models
from django.contrib.auth.models import User
from subscriptions.models import SubscriptionPlan


class Payment(models.Model):
    """
    Razorpay transaction audit logs for user subscription payments.
    """
    STATUS_CHOICES = (
        ('created', 'Order Created'),
        ('successful', 'Payment Successful'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, related_name='payments')
    razorpay_order_id = models.CharField(max_length=150, unique=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in INR")
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', db_index=True)
    error_code = models.CharField(max_length=100, blank=True, null=True)
    error_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'streamflix_payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.razorpay_order_id} - ₹{self.amount} ({self.status})"
