from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Movie, Category, Genre, Season, Episode, Review
from watchlist.models import Watchlist, WatchHistory


def home(request):
    """
    Main OTT Homepage - Netflix-style dark theme with hero banner and horizontal rows.
    """
    featured_movie = Movie.objects.filter(is_featured=True).first()
    if not featured_movie:
        featured_movie = Movie.objects.first()

    trending_movies = Movie.objects.filter(is_trending=True)[:10]
    latest_movies = Movie.objects.filter(content_type='movie').order_by('-release_year', '-created_at')[:10]
    web_series = Movie.objects.filter(content_type='series')[:10]
    originals = Movie.objects.filter(category__name__icontains='Original')[:10]
    documentaries = Movie.objects.filter(category__name__icontains='Documentar')[:10]

    continue_watching = []
    user_watchlist_ids = []
    if request.user.is_authenticated:
        continue_watching = WatchHistory.objects.filter(user=request.user, is_completed=False).select_related('movie', 'episode')[:8]
        user_watchlist_ids = list(Watchlist.objects.filter(user=request.user).values_list('movie_id', flat=True))

    genres = Genre.objects.all()

    context = {
        'featured_movie': featured_movie,
        'trending_movies': trending_movies,
        'latest_movies': latest_movies,
        'web_series': web_series,
        'originals': originals,
        'documentaries': documentaries,
        'continue_watching': continue_watching,
        'user_watchlist_ids': user_watchlist_ids,
        'genres': genres,
    }
    return render(request, 'movies/home.html', context)


def movie_detail(request, slug):
    """
    Comprehensive details page with synopsis, trailer, seasons/episodes, and reviews.
    """
    movie = get_object_or_404(Movie, slug=slug)
    # Increment view count
    Movie.objects.filter(pk=movie.pk).update(views_count=movie.views_count + 1)

    is_in_watchlist = False
    if request.user.is_authenticated:
        is_in_watchlist = Watchlist.objects.filter(user=request.user, movie=movie).exists()

    seasons = []
    if movie.content_type == 'series':
        seasons = movie.seasons.prefetch_related('episodes').all()

    # Recommended similar movies (same genre)
    genre_ids = movie.genres.values_list('id', flat=True)
    similar_movies = Movie.objects.filter(genres__in=genre_ids).exclude(pk=movie.pk).distinct()[:6]

    reviews = movie.reviews.select_related('user').all()

    context = {
        'movie': movie,
        'is_in_watchlist': is_in_watchlist,
        'seasons': seasons,
        'similar_movies': similar_movies,
        'reviews': reviews,
    }
    return render(request, 'movies/movie_detail.html', context)


def category_view(request, slug):
    """Filtered browse page by Category (e.g. Movies, Web Series)."""
    category = get_object_or_404(Category, slug=slug)
    movies_list = Movie.objects.filter(category=category)
    return render(request, 'movies/catalog_list.html', {
        'title': category.name,
        'subtitle': category.description,
        'movies': movies_list,
    })


def genre_view(request, slug):
    """Filtered browse page by Genre."""
    genre = get_object_or_404(Genre, slug=slug)
    movies_list = Movie.objects.filter(genres=genre)
    return render(request, 'movies/catalog_list.html', {
        'title': f"{genre.name} Titles",
        'subtitle': f"Browse all {genre.name} content on StreamFlix",
        'movies': movies_list,
    })


def search(request):
    """Full-text search query across titles, synopsis, genres, and languages."""
    query = request.GET.get('q', '').strip()
    movies_list = Movie.objects.none()
    if query:
        movies_list = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(synopsis__icontains=query) |
            Q(genres__name__icontains=query) |
            Q(language__icontains=query)
        ).distinct()

    return render(request, 'movies/catalog_list.html', {
        'title': f"Search Results for '{query}'" if query else "Search StreamFlix",
        'subtitle': f"Found {movies_list.count()} matching title(s)" if query else "Enter a keyword above to find movies and series.",
        'movies': movies_list,
        'search_query': query,
    })


def add_review(request, slug):
    """Add user star rating and review."""
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to leave a review.")
        return redirect('accounts:login')

    movie = get_object_or_404(Movie, slug=slug)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()

        Review.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, "Your review has been submitted!")
    return redirect('movies:movie_detail', slug=slug)
