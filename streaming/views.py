from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from movies.models import Movie, Episode
from .models import VideoAsset
from watchlist.models import WatchHistory
from subscriptions.models import UserSubscription
import json


def check_user_access(user, movie):
    """
    Validates if user has permission to stream content based on tier.
    Free movies are accessible to all registered users; premium movies require an active paid subscription.
    """
    if not movie.is_premium:
        return True, ""

    if not user.is_authenticated:
        return False, "Please sign in to stream this premium title."

    # Admins have master access
    if user.is_staff or user.is_superuser:
        return True, ""

    sub = UserSubscription.objects.filter(user=user).first()
    if sub and sub.is_currently_valid and sub.plan.price > 0:
        return True, ""

    return False, "This title requires an active StreamFlix Premium membership."


def play_movie(request, slug):
    """
    Cinematic streaming player view with access verification and resume bookmarking.
    """
    movie = get_object_or_404(Movie, slug=slug)

    # Access control verification
    has_access, reason = check_user_access(request.user, movie)
    if not has_access:
        messages.warning(request, reason)
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return redirect('subscriptions:plans')

    # Resume position
    start_time = 0
    if request.user.is_authenticated:
        history = WatchHistory.objects.filter(user=request.user, movie=movie).first()
        if history and not history.is_completed:
            start_time = history.last_position_seconds

    # Fetch video asset or demo stream
    video_asset = getattr(movie, 'video_asset', None)
    stream_url = ""
    is_hls = False

    if video_asset and video_asset.status == 'ready' and video_asset.hls_master_playlist:
        stream_url = video_asset.hls_master_playlist
        is_hls = True
    elif video_asset and video_asset.source_file:
        stream_url = video_asset.source_file.url
    else:
        # High quality royalty-free demo stream for development/demonstration
        stream_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"

    context = {
        'title': movie.title,
        'movie': movie,
        'stream_url': stream_url,
        'is_hls': is_hls,
        'start_time': start_time,
        'content_type': 'movie',
        'content_id': movie.id,
    }
    return render(request, 'streaming/player.html', context)


def play_episode(request, episode_id):
    """Play individual web series episode."""
    episode = get_object_or_404(Episode, id=episode_id)
    movie = episode.season.series

    has_access, reason = check_user_access(request.user, movie)
    if not has_access:
        messages.warning(request, reason)
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return redirect('subscriptions:plans')

    start_time = 0
    if request.user.is_authenticated:
        history = WatchHistory.objects.filter(user=request.user, episode=episode).first()
        if history and not history.is_completed:
            start_time = history.last_position_seconds

    # Fetch stream or demo
    video_asset = getattr(episode, 'video_asset', None)
    stream_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
    is_hls = False

    if video_asset and video_asset.status == 'ready' and video_asset.hls_master_playlist:
        stream_url = video_asset.hls_master_playlist
        is_hls = True
    elif video_asset and video_asset.source_file:
        stream_url = video_asset.source_file.url

    context = {
        'title': f"{movie.title} - S{episode.season.season_number}E{episode.episode_number}: {episode.title}",
        'movie': movie,
        'episode': episode,
        'stream_url': stream_url,
        'is_hls': is_hls,
        'start_time': start_time,
        'content_type': 'episode',
        'content_id': episode.id,
    }
    return render(request, 'streaming/player.html', context)


@login_required
@csrf_exempt
def update_progress_api(request):
    """
    AJAX endpoint called periodically by video player to save playback timestamp.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content_type = data.get('content_type')
            content_id = int(data.get('content_id'))
            current_time = int(float(data.get('current_time', 0)))
            duration = int(float(data.get('duration', 0)))

            is_completed = (current_time / duration >= 0.92) if duration > 0 else False

            if content_type == 'movie':
                movie = Movie.objects.get(id=content_id)
                WatchHistory.objects.update_or_create(
                    user=request.user,
                    movie=movie,
                    defaults={
                        'last_position_seconds': current_time,
                        'duration_seconds': duration,
                        'is_completed': is_completed,
                    }
                )
            elif content_type == 'episode':
                episode = Episode.objects.get(id=content_id)
                WatchHistory.objects.update_or_create(
                    user=request.user,
                    episode=episode,
                    defaults={
                        'last_position_seconds': current_time,
                        'duration_seconds': duration,
                        'is_completed': is_completed,
                    }
                )
            return JsonResponse({'status': 'success', 'saved_position': current_time})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'method_not_allowed'}, status=405)
