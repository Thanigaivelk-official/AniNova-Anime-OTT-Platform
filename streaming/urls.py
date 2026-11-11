from django.urls import path
from . import views

app_name = 'streaming'

urlpatterns = [
    path('movie/<slug:slug>/', views.play_movie, name='play'),
    path('episode/<int:episode_id>/', views.play_episode, name='play_episode'),
    path('api/progress/', views.update_progress_api, name='update_progress'),
]
