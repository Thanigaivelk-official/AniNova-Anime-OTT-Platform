from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from movies.models import Movie, Category, Genre
from subscriptions.models import UserSubscription, SubscriptionPlan
from payments.models import Payment
from streaming.models import VideoAsset


@staff_member_required(login_url='accounts:login')
def admin_dashboard(request):
    """
    Administrative Executive Dashboard: metrics, revenue, subscriptions, user management.
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
    """Admin view to inspect, search, and manage movies."""
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
    """Add a new movie or web series into StreamFlix."""
    categories = Category.objects.all()
    genres = Genre.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        content_type = request.POST.get('content_type', 'movie')
        synopsis = request.POST.get('synopsis')
        release_year = int(request.POST.get('release_year', 2024))
        duration_minutes = int(request.POST.get('duration_minutes', 120))
        language = request.POST.get('language', 'English')
        age_rating = request.POST.get('age_rating', 'U/A 13+')
        is_featured = bool(request.POST.get('is_featured'))
        is_trending = bool(request.POST.get('is_trending'))
        is_premium = bool(request.POST.get('is_premium'))
        genre_ids = request.POST.getlist('genres')

        movie = Movie.objects.create(
            title=title,
            category_id=category_id if category_id else None,
            content_type=content_type,
            synopsis=synopsis,
            release_year=release_year,
            duration_minutes=duration_minutes,
            language=language,
            age_rating=age_rating,
            is_featured=is_featured,
            is_trending=is_trending,
            is_premium=is_premium,
        )

        if 'poster' in request.FILES:
            movie.poster = request.FILES['poster']
        if 'backdrop' in request.FILES:
            movie.backdrop = request.FILES['backdrop']
        movie.save()

        if genre_ids:
            movie.genres.set(genre_ids)

        messages.success(request, f"Movie '{movie.title}' created successfully!")
        return redirect('dashboard:movie_list')

    return render(request, 'dashboard/movie_form.html', {
        'categories': categories,
        'genres': genres,
        'action': 'Add New Content',
    })


@staff_member_required(login_url='accounts:login')
def movie_delete(request, id):
    """Delete a movie."""
    movie = get_object_or_404(Movie, id=id)
    title = movie.title
    movie.delete()
    messages.success(request, f"Title '{title}' was deleted successfully.")
    return redirect('dashboard:movie_list')
