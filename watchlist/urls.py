from django.urls import path
from . import views

app_name = 'watchlist'

urlpatterns = [
    path('', views.my_list, name='my_list'),
    path('toggle/<int:movie_id>/', views.toggle_watchlist, name='toggle'),
]
