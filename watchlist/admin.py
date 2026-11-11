from django.contrib import admin
from .models import Watchlist, WatchHistory


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'movie__title')


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_target', 'last_position_seconds', 'duration_seconds', 'progress_percentage', 'is_completed', 'last_watched_at')
    list_filter = ('is_completed', 'last_watched_at')
    search_fields = ('user__username', 'movie__title', 'episode__title')

    def get_target(self, obj):
        return obj.movie.title if obj.movie else str(obj.episode)
    get_target.short_description = 'Content Target'
