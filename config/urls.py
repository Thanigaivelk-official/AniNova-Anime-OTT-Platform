"""
StreamFlix URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls', namespace='movies')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('stream/', include('streaming.urls', namespace='streaming')),
    path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
    path('watchlist/', include('watchlist.urls', namespace='watchlist')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('recommendations/', include('recommendations.urls', namespace='recommendations')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
