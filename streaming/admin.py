from django.contrib import admin
from .models import VideoAsset


@admin.register(VideoAsset)
class VideoAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_target', 'status', 'duration_seconds', 'resolutions_available', 'created_at')
    list_filter = ('status',)
    search_fields = ('movie__title', 'episode__title')

    def get_target(self, obj):
        return obj.movie.title if obj.movie else str(obj.episode)
    get_target.short_description = 'Content Target'
