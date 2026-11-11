from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from movies.models import Movie, Category, Genre, Season, Episode
from subscriptions.models import UserSubscription, SubscriptionPlan
from payments.models import Payment
from streaming.models import VideoAsset


@staff_member_required(login_url='accounts:login')
def admin_dashboard(request):
    """
    AniNova Administrative Executive Dashboard:
    Simulcast metrics, subscriber analytics, payment logs, and catalog management.
    """
    total_users = User.objects.count()
    total_movies = Movie.objects.count()
    active_subscriptions = UserSubscription.objects.filter(status='active').count()
    total_revenue = Payment.objects.filter(status='successful').aggregate(total=Sum('amount'))['total'] or 0

    recent_payments = Payment.objects.select_related('user', 'plan').order_by('-created_at')[:8]
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:8]
    recent_movies = Movie.objects.select_related('category').order_by('-created_at')[:8]

    context = {
        'total_users': total_users,
        'total_movies': total_movies,
        'active_subscriptions': active_subscriptions,
        'total_revenue': total_revenue,
        'recent_payments': recent_payments,
        'recent_users': recent_users,
        'recent_movies': recent_movies,
    }
    return render(request, 'dashboard/dashboard.html', context)


@staff_member_required(login_url='accounts:login')
def movie_list(request):
    """Admin view to inspect, search, and manage anime catalog."""
    movies_qs = Movie.objects.select_related('category').prefetch_related('genres').all()
    query = request.GET.get('q', '').strip()
    if query:
        movies_qs = movies_qs.filter(title__icontains=query)

    return render(request, 'dashboard/movie_list.html', {
        'movies': movies_qs,
        'query': query,
    })


@staff_member_required(login_url='accounts:login')
def movie_create(request):
    """
    Upload and publish a new Anime title, with poster, backdrop, and video file asset.
    """
    categories = Category.objects.all()
    genres = Genre.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        japanese_title = request.POST.get('japanese_title', '')
        studio_name = request.POST.get('studio_name', 'MAPPA')
        director = request.POST.get('director', '')
        category_id = request.POST.get('category')
        content_type = request.POST.get('content_type', 'series')
        status = request.POST.get('status', 'ongoing')
        synopsis = request.POST.get('synopsis')
        release_year = int(request.POST.get('release_year', 2024))
        duration_minutes = int(request.POST.get('duration_minutes', 24))
        age_rating = request.POST.get('age_rating', 'PG-13')
        imdb_rating = float(request.POST.get('imdb_rating', 8.5))
        language = request.POST.get('language', 'Japanese')
        audio_languages = request.POST.get('audio_languages', 'Japanese (Original), English Dub')
        subtitle_languages = request.POST.get('subtitle_languages', 'English, Spanish, Hindi, German')

        is_featured = bool(request.POST.get('is_featured'))
        is_trending = bool(request.POST.get('is_trending'))
        is_popular = bool(request.POST.get('is_popular'))
        is_premium = bool(request.POST.get('is_premium'))
        has_dub = bool(request.POST.get('has_dub'))
        has_sub = bool(request.POST.get('has_sub'))
        genre_ids = request.POST.getlist('genres')

        anime = Movie.objects.create(
            title=title,
            japanese_title=japanese_title,
            studio_name=studio_name,
            director=director,
            category_id=category_id if category_id else None,
            content_type=content_type,
            status=status,
            synopsis=synopsis,
            release_year=release_year,
            duration_minutes=duration_minutes,
            age_rating=age_rating,
            imdb_rating=imdb_rating,
            language=language,
            audio_languages=audio_languages,
            subtitle_languages=subtitle_languages,
            is_featured=is_featured,
            is_trending=is_trending,
            is_popular=is_popular,
            is_premium=is_premium,
            has_dub=has_dub,
            has_sub=has_sub,
        )

        if 'poster' in request.FILES:
            anime.poster = request.FILES['poster']
        if 'backdrop' in request.FILES:
            anime.backdrop = request.FILES['backdrop']
        anime.save()

        if genre_ids:
            anime.genres.set(genre_ids)

        # Video File Upload (Handles raw MP4 / MKV upload)
        if 'video_file' in request.FILES:
            vfile = request.FILES['video_file']
            if anime.content_type == 'movie':
                VideoAsset.objects.create(
                    movie=anime,
                    source_file=vfile,
                    duration_seconds=anime.duration_minutes * 60,
                    status='ready'
                )
            else:
                # If series, create Season 1 Episode 1 and attach video asset
                season, _ = Season.objects.get_or_create(series=anime, season_number=1, defaults={'title': 'Season 1'})
                episode = Episode.objects.create(
                    season=season,
                    episode_number=1,
                    title=f"Episode 1: The Beginning",
                    overview=f"Premiere episode of {anime.title}.",
                    duration_minutes=anime.duration_minutes
                )
                VideoAsset.objects.create(
                    episode=episode,
                    source_file=vfile,
                    duration_seconds=anime.duration_minutes * 60,
                    status='ready'
                )

        messages.success(request, f"Anime '{anime.title}' published successfully with uploaded media!")
        return redirect('dashboard:movie_list')

    return render(request, 'dashboard/movie_form.html', {
        'categories': categories,
        'genres': genres,
        'action': 'Upload New Anime Title',
    })


@staff_member_required(login_url='accounts:login')
def movie_delete(request, id):
    """Delete an anime title."""
    movie = get_object_or_404(Movie, id=id)
    title = movie.title
    movie.delete()
    messages.success(request, f"Anime '{title}' was deleted successfully.")
    return redirect('dashboard:movie_list')
