from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.home, name='home'),
    path('watch/<slug:slug>/', views.movie_detail, name='movie_detail'),
    path('category/<slug:slug>/', views.category_view, name='category_view'),
    path('genre/<slug:slug>/', views.genre_view, name='genre_view'),
    path('search/', views.search, name='search'),
    path('review/<slug:slug>/', views.add_review, name='add_review'),
]
