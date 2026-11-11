from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import (
    UserRegisterForm,
    UserAccountUpdateForm,
    UserProfilePhotoForm,
    UserProfileInfoForm,
)
from subscriptions.models import UserSubscription
from watchlist.models import Watchlist, WatchHistory


def register_view(request):
    """User account registration for AniNova."""
    if request.user.is_authenticated:
        return redirect('movies:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f"Welcome to AniNova, {user.username}! Explore a new world of anime.")
            login(request, user)
            return redirect('movies:home')
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login into AniNova."""
    if request.user.is_authenticated:
        return redirect('movies:home')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

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
            messages.success(request, f"Okaeri, {user.username}! Welcome back to AniNova.")
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
    messages.info(request, "You have been signed out from AniNova. See you next time!")
    return redirect('movies:home')


@login_required
def profile_view(request):
    """
    AniNova User Profile with photo editing, live preview, account info update,
    and membership details.
    """
    user = request.user
    profile = user.profile
    subscription = UserSubscription.objects.filter(user=user).first()
    watchlist_count = Watchlist.objects.filter(user=user).count()
    watched_count = WatchHistory.objects.filter(user=user, is_completed=True).count()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_photo':
            photo_form = UserProfilePhotoForm(request.POST, request.FILES, instance=profile)
            if photo_form.is_valid():
                photo_form.save()
                messages.success(request, "Your profile photo has been updated successfully!")
                return redirect('accounts:profile')
            else:
                for error in photo_form.errors.values():
                    messages.error(request, error)

        elif action == 'update_info':
            account_form = UserAccountUpdateForm(request.POST, instance=user)
            info_form = UserProfileInfoForm(request.POST, instance=profile)

            if account_form.is_valid() and info_form.is_valid():
                account_form.save()
                info_form.save()
                messages.success(request, "Profile details updated successfully!")
                return redirect('accounts:profile')
            else:
                messages.error(request, "Please check the submitted information.")

    account_form = UserAccountUpdateForm(instance=user)
    photo_form = UserProfilePhotoForm(instance=profile)
    info_form = UserProfileInfoForm(instance=profile)

    context = {
        'profile': profile,
        'account_form': account_form,
        'photo_form': photo_form,
        'info_form': info_form,
        'subscription': subscription,
        'watchlist_count': watchlist_count,
        'watched_count': watched_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def remove_avatar_view(request):
    """Removes user's custom uploaded avatar, resetting to default anime character."""
    if request.method == 'POST':
        profile = request.user.profile
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save()
            messages.success(request, "Custom profile photo removed. Anime avatar restored.")
    return redirect('accounts:profile')
