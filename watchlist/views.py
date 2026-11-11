from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from movies.models import Movie
from .models import Watchlist, WatchHistory


@login_required
def toggle_watchlist(request, movie_id):
    """Toggle a movie into or out of the user's watchlist."""
    movie = get_object_or_404(Movie, id=movie_id)
    watchlist_item = Watchlist.objects.filter(user=request.user, movie=movie).first()

    if watchlist_item:
        watchlist_item.delete()
        messages.info(request, f"Removed '{movie.title}' from your watchlist.")
    else:
        Watchlist.objects.create(user=request.user, movie=movie)
        messages.success(request, f"Added '{movie.title}' to your watchlist!")

    # Return to previous page or movie detail
    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('movies:movie_detail', slug=movie.slug)


@login_required
def my_list(request):
    """Displays user's saved watchlist items and watch history."""
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('movie')
    history_items = WatchHistory.objects.filter(user=request.user).select_related('movie', 'episode')[:12]

    context = {
        'watchlist_items': watchlist_items,
        'history_items': history_items,
    }
    return render(request, 'watchlist/my_list.html', context)
