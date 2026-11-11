from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from collections import Counter
from movies.models import Movie
from watchlist.models import Watchlist, WatchHistory


def get_recommended_movies(user, limit=8):
    """
    Content-Based Recommendation Engine:
    Extracts preferred genres from the user's Watchlist and WatchHistory,
    scores candidate movies by genre overlap and popularity, and returns top matches.
    """
    if not user.is_authenticated:
        return Movie.objects.filter(is_trending=True)[:limit]

    # 1. Collect all movies watched or bookmarked by user
    watched_movie_ids = list(WatchHistory.objects.filter(user=user, movie__isnull=False).values_list('movie_id', flat=True))
    watchlist_movie_ids = list(Watchlist.objects.filter(user=user).values_list('movie_id', flat=True))
    interacted_movie_ids = set(watched_movie_ids + watchlist_movie_ids)

    # 2. Extract genres from interacted movies
    user_movies = Movie.objects.filter(id__in=interacted_movie_ids).prefetch_related('genres')
    genre_ids = []
    for m in user_movies:
        genre_ids.extend(m.genres.values_list('id', flat=True))

    if not genre_ids:
        # Fallback to trending
        return Movie.objects.filter(is_trending=True).exclude(id__in=interacted_movie_ids)[:limit]

    # 3. Find top preferred genre IDs
    genre_counts = Counter(genre_ids)
    top_genre_ids = [gid for gid, _ in genre_counts.most_common(3)]

    # 4. Fetch candidate movies matching top genres, excluding already interacted
    recommended = Movie.objects.filter(genres__in=top_genre_ids).exclude(id__in=interacted_movie_ids).distinct().order_by('-views_count', '-release_year')[:limit]

    if recommended.count() < limit:
        # Pad with other trending movies if needed
        filler = Movie.objects.exclude(id__in=interacted_movie_ids).exclude(id__in=recommended.values_list('id', flat=True))[:limit - recommended.count()]
        return list(recommended) + list(filler)

    return recommended


def recommendations_api(request):
    """API endpoint returning personalized recommendations in JSON."""
    movies = get_recommended_movies(request.user, limit=8)
    data = []
    for m in movies:
        data.append({
            'id': m.id,
            'title': m.title,
            'slug': m.slug,
            'year': m.release_year,
            'age_rating': m.age_rating,
            'duration': m.duration_minutes,
            'is_premium': m.is_premium,
        })
    return JsonResponse({'status': 'success', 'recommendations': data})
