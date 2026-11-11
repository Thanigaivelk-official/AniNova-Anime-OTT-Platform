from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from movies.models import Movie, Episode, Season
from .models import VideoAsset
from watchlist.models import WatchHistory
from subscriptions.models import UserSubscription
import json


def check_user_access(user, movie):
    """
    Validates if user has permission to stream content based on tier.
    Free anime is accessible to all viewers; VIP simulcasts require active membership.
    """
    if not movie.is_premium:
        return True, ""

    if not user.is_authenticated:
        return False, "Please sign in to stream this VIP simulcast anime."

    if user.is_staff or user.is_superuser:
        return True, ""

    sub = UserSubscription.objects.filter(user=user).first()
    if sub and sub.is_currently_valid and sub.plan.price > 0:
        return True, ""

    return False, "This simulcast title requires an active AniNova Otaku VIP membership."


def play_movie(request, slug):
    """
    Stream anime movie or forward to episode 1 if it is a multi-episode anime series.
    """
    movie = get_object_or_404(Movie, slug=slug)

    # If it is a TV series, redirect to the first available episode or resume point
    if movie.content_type == 'series':
        first_ep = Episode.objects.filter(season__series=movie).order_by('season__season_number', 'episode_number').first()
        if first_ep:
            return redirect('streaming:play_episode', episode_id=first_ep.id)

    has_access, reason = check_user_access(request.user, movie)
    if not has_access:
        messages.warning(request, reason)
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return redirect('subscriptions:plans')

    start_time = 0
    if request.user.is_authenticated:
        history = WatchHistory.objects.filter(user=request.user, movie=movie).first()
        if history and not history.is_completed:
            start_time = history.last_position_seconds

    video_asset = getattr(movie, 'video_asset', None)
    stream_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    is_hls = False

    if video_asset and video_asset.status == 'ready' and video_asset.hls_master_playlist:
        stream_url = video_asset.hls_master_playlist
        is_hls = True
    elif video_asset and video_asset.source_file:
        stream_url = video_asset.source_file.url

    context = {
        'title': movie.title,
        'anime': movie,
        'movie': movie,
        'stream_url': stream_url,
        'is_hls': is_hls,
        'start_time': start_time,
        'content_type': 'movie',
        'content_id': movie.id,
        'skip_intro_start': 0,
        'skip_intro_end': 0,
        'skip_outro_start': 0,
        'skip_outro_end': 0,
        'next_episode': None,
        'season_episodes': [],
    }
    return render(request, 'streaming/player.html', context)


def play_episode(request, episode_id):
    """
    Stream Anime Episode with:
      - Skip Intro (OP) and Skip Outro (ED)
      - Episode drawer selection
      - Next episode autoplay
      - Japanese / English audio & subtitle toggles
    """
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

    video_asset = getattr(episode, 'video_asset', None)
    stream_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
    is_hls = False

    if video_asset and video_asset.status == 'ready' and video_asset.hls_master_playlist:
        stream_url = video_asset.hls_master_playlist
        is_hls = True
    elif video_asset and video_asset.source_file:
        stream_url = video_asset.source_file.url

    # In-player episode selector list for current season
    season_episodes = episode.season.episodes.order_by('episode_number')

    context = {
        'title': f"{movie.title} - S{episode.season.season_number}E{episode.episode_number}: {episode.title}",
        'anime': movie,
        'movie': movie,
        'episode': episode,
        'stream_url': stream_url,
        'is_hls': is_hls,
        'start_time': start_time,
        'content_type': 'episode',
        'content_id': episode.id,
        'skip_intro_start': episode.skip_intro_start,
        'skip_intro_end': episode.skip_intro_end,
        'skip_outro_start': episode.skip_outro_start,
        'skip_outro_end': episode.skip_outro_end,
        'next_episode': episode.next_episode,
        'season_episodes': season_episodes,
    }
    return render(request, 'streaming/player.html', context)


@login_required
@csrf_exempt
def update_progress_api(request):
    """
    AJAX endpoint called periodically by the player to store anime watch position.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content_type = data.get('content_type')
            content_id = int(data.get('content_id'))
            current_time = int(float(data.get('current_time', 0)))
            duration = int(float(data.get('duration', 0)))

            is_completed = (current_time / duration >= 0.90) if duration > 0 else False

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
