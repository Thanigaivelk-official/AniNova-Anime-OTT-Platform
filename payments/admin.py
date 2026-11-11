from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('razorpay_order_id', 'user', 'plan', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'plan')
    search_fields = ('user__username', 'razorpay_order_id', 'razorpay_payment_id')
