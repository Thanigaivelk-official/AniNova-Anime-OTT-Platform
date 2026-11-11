from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/new/', views.movie_create, name='movie_create'),
    path('movies/delete/<int:id>/', views.movie_delete, name='movie_delete'),
]
