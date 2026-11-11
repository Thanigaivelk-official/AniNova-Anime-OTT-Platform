from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('api/', views.recommendations_api, name='api'),
]
