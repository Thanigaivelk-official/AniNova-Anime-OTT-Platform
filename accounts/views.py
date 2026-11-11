from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegisterForm, UserProfileForm
from subscriptions.models import UserSubscription
from watchlist.models import Watchlist, WatchHistory


def register_view(request):
    """User account registration."""
    if request.user.is_authenticated:
        return redirect('movies:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f"Welcome to StreamFlix, {user.username}! Your account has been created.")
            login(request, user)
            return redirect('movies:home')
        else:
            messages.error(request, "Please correct the errors below to register.")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login with validation and session creation."""
    if request.user.is_authenticated:
        return redirect('movies:home')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Allow login with either username or email
        user = None
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('movies:home')
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Safely log out user."""
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect('movies:home')


@login_required
def profile_view(request):
    """User profile, active subscription status, and viewing statistics."""
    profile = request.user.profile
    subscription = UserSubscription.objects.filter(user=request.user).first()
    watchlist_count = Watchlist.objects.filter(user=request.user).count()
    watched_count = WatchHistory.objects.filter(user=request.user, is_completed=True).count()

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        profile_form = UserProfileForm(instance=profile)

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'subscription': subscription,
        'watchlist_count': watchlist_count,
        'watched_count': watched_count,
    }
    return render(request, 'accounts/profile.html', context)
