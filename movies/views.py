from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Movie, Category, Genre, Season, Episode, Review
from watchlist.models import Watchlist, WatchHistory


def home(request):
    """
    AniNova Anime Homepage - Cyber-purple dark theme with anime spotlight hero,
    trending simulcasts, top-rated anime, and Otaku categories.
    """
    featured_anime = Movie.objects.prefetch_related('genres').filter(is_featured=True).first()
    if not featured_anime:
        featured_anime = Movie.objects.prefetch_related('genres').first()

    base_qs = Movie.objects.prefetch_related('genres')
    trending_anime = base_qs.filter(is_trending=True)[:10]
    popular_anime = base_qs.order_by('-views_count')[:10]
    simulcast_series = base_qs.filter(content_type='series')[:10]
    anime_movies = base_qs.filter(content_type='movie')[:10]
    top_rated_anime = base_qs.order_by('-imdb_rating')[:10]

    continue_watching = []
    user_watchlist_ids = []
    if request.user.is_authenticated:
        continue_watching = WatchHistory.objects.filter(user=request.user, is_completed=False).select_related('movie', 'episode')[:8]
        user_watchlist_ids = list(Watchlist.objects.filter(user=request.user).values_list('movie_id', flat=True))

    genres = Genre.objects.all()

    context = {
        'featured_anime': featured_anime,
        'trending_anime': trending_anime,
        'popular_anime': popular_anime,
        'simulcast_series': simulcast_series,
        'anime_movies': anime_movies,
        'top_rated_anime': top_rated_anime,
        'continue_watching': continue_watching,
        'user_watchlist_ids': user_watchlist_ids,
        'genres': genres,
    }
    return render(request, 'movies/home.html', context)


def movie_detail(request, slug):
    """
    Comprehensive Anime Details Page:
    Japanese title, Studio, Director, MAL Rating, Sub/Dub options, Seasons & Episodes.
    """
    anime = get_object_or_404(Movie, slug=slug)
    Movie.objects.filter(pk=anime.pk).update(views_count=anime.views_count + 1)

    is_in_watchlist = False
    if request.user.is_authenticated:
        is_in_watchlist = Watchlist.objects.filter(user=request.user, movie=anime).exists()

    seasons = anime.seasons.prefetch_related('episodes').all()

    # Similar anime in the same genres
    genre_ids = anime.genres.values_list('id', flat=True)
    similar_anime = Movie.objects.filter(genres__in=genre_ids).exclude(pk=anime.pk).distinct()[:6]

    reviews = anime.reviews.select_related('user').all()

    context = {
        'anime': anime,
        'movie': anime,  # compatibility alias
        'is_in_watchlist': is_in_watchlist,
        'seasons': seasons,
        'similar_anime': similar_anime,
        'reviews': reviews,
    }
    return render(request, 'movies/movie_detail.html', context)


def category_view(request, slug):
    """Filtered browse page by Anime Category (e.g. Anime Series, Movies)."""
    category = get_object_or_404(Category, slug=slug)
    anime_list = Movie.objects.filter(category=category)
    return render(request, 'movies/catalog_list.html', {
        'title': category.name,
        'subtitle': category.description,
        'anime_list': anime_list,
        'movies': anime_list,
    })


def genre_view(request, slug):
    """Filtered browse page by Anime Genre (e.g. Isekai, Shonen Action)."""
    genre = get_object_or_404(Genre, slug=slug)
    anime_list = Movie.objects.filter(genres=genre)
    return render(request, 'movies/catalog_list.html', {
        'title': f"{genre.name} Anime",
        'subtitle': f"Discover the best {genre.name} anime series and movies on AniNova.",
        'anime_list': anime_list,
        'movies': anime_list,
    })


def search(request):
    """Full-text anime search across titles, Japanese titles, studios, and genres."""
    query = request.GET.get('q', '').strip()
    anime_list = Movie.objects.none()
    if query:
        anime_list = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(japanese_title__icontains=query) |
            Q(studio_name__icontains=query) |
            Q(synopsis__icontains=query) |
            Q(genres__name__icontains=query)
        ).distinct()

    return render(request, 'movies/catalog_list.html', {
        'title': f"Search Anime: '{query}'" if query else "Search AniNova",
        'subtitle': f"Found {anime_list.count()} anime title(s)" if query else "Search by English title, Japanese Kanji, or studio name.",
        'anime_list': anime_list,
        'movies': anime_list,
        'search_query': query,
    })


def add_review(request, slug):
    """Submit user anime review and star rating."""
    if not request.user.is_authenticated:
        messages.error(request, "Please sign in to rate this anime.")
        return redirect('accounts:login')

    anime = get_object_or_404(Movie, slug=slug)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()

        Review.objects.update_or_create(
            user=request.user,
            movie=anime,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, f"Review submitted for {anime.title}!")
    return redirect('movies:movie_detail', slug=slug)
