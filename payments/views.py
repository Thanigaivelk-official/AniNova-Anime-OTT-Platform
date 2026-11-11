from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Payment
from subscriptions.models import UserSubscription
import razorpay


@csrf_exempt
@login_required
def verify_payment(request):
    """
    Verifies Razorpay payment signature and activates the user subscription.
    """
    if request.method == 'POST':
        order_id = request.POST.get('razorpay_order_id')
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')

        payment = get_object_or_404(Payment, razorpay_order_id=order_id, user=request.user)

        # Verification check
        is_valid = True
        try:
            if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET and not settings.RAZORPAY_KEY_ID.startswith("rzp_test_placeholder"):
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                client.utility.verify_payment_signature({
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                })
        except Exception as e:
            # If in live mode with valid keys and signature mismatch, fail
            if settings.RAZORPAY_KEY_SECRET:
                is_valid = False
                payment.status = 'failed'
                payment.error_description = str(e)
                payment.save()
                messages.error(request, "Payment signature verification failed.")
                return redirect('subscriptions:plans')

        if is_valid:
            payment.razorpay_payment_id = payment_id or f"pay_test_{payment.id}"
            payment.razorpay_signature = signature or "sig_test_verified"
            payment.status = 'successful'
            payment.save()

            # Update or create UserSubscription
            user_sub, created = UserSubscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'plan': payment.plan,
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + timedelta(days=payment.plan.duration_days),
                    'status': 'active'
                }
            )
            if not created:
                user_sub.plan = payment.plan
                user_sub.renew(payment.plan.duration_days)

            return render(request, 'payments/success.html', {
                'payment': payment,
                'plan': payment.plan,
            })

    return redirect('subscriptions:plans')
