from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, UserSubscription
from payments.models import Payment
import razorpay
import uuid


def plans_view(request):
    """Browse all available subscription tiers with comparison."""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    current_sub = None
    if request.user.is_authenticated:
        current_sub = UserSubscription.objects.filter(user=request.user).first()

    context = {
        'plans': plans,
        'current_sub': current_sub,
    }
    return render(request, 'subscriptions/plans.html', context)


@login_required
def initiate_checkout(request, plan_id):
    """
    Creates a Razorpay order for the selected subscription plan.
    """
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    # Free tier handling
    if plan.price <= 0:
        sub, _ = UserSubscription.objects.get_or_create(user=request.user, defaults={
            'plan': plan,
            'end_date': timezone.now() + timedelta(days=plan.duration_days)
        })
        sub.plan = plan
        sub.renew(plan.duration_days)
        messages.success(request, f"You are now on the {plan.name}!")
        return redirect('accounts:profile')

    # Convert INR to paise for Razorpay
    amount_in_paise = int(plan.price * 100)

    # Initialize Razorpay Client (fallback to test simulation if keys not populated yet)
    order_id = f"order_sf_{uuid.uuid4().hex[:12]}"
    razorpay_key = settings.RAZORPAY_KEY_ID or "rzp_test_StreamFlixDemo"

    try:
        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET and not settings.RAZORPAY_KEY_ID.startswith("rzp_test_placeholder"):
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            rzp_order = client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': 1,
            })
            order_id = rzp_order['id']
    except Exception as e:
        print(f"Razorpay Client fallback mode: {e}")

    # Record payment transaction
    payment = Payment.objects.create(
        user=request.user,
        plan=plan,
        razorpay_order_id=order_id,
        amount=plan.price,
        currency='INR',
        status='created'
    )

    context = {
        'plan': plan,
        'payment': payment,
        'razorpay_order_id': order_id,
        'razorpay_key': razorpay_key,
        'amount_in_paise': amount_in_paise,
    }
    return render(request, 'payments/checkout.html', context)
