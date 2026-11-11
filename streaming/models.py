from django.db import models
from movies.models import Movie, Episode


class VideoAsset(models.Model):
    """
    Manages raw source video files and generated HLS (.m3u8) adaptive streaming files.
    Avoids storing heavy binary BLOBs inside MySQL; stores relative filesystem/cloud URLs.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending FFmpeg Processing'),
        ('processing', 'Transcoding to HLS'),
        ('ready', 'Ready for Streaming'),
        ('failed', 'Transcoding Failed'),
    )

    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='video_asset')
    episode = models.OneToOneField(Episode, on_delete=models.CASCADE, null=True, blank=True, related_name='video_asset')

    source_file = models.FileField(upload_to='videos/sources/', help_text="Original uploaded MP4/MKV video file")
    hls_master_playlist = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Path or URL to master .m3u8 playlist file"
    )
    resolutions_available = models.CharField(
        max_length=150,
        default='360p,480p,720p,1080p',
        help_text="Comma-separated generated HLS bitrates/resolutions"
    )
    duration_seconds = models.PositiveIntegerField(default=0, help_text="Exact duration in seconds")
    file_size_bytes = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'streamflix_video_assets'
        verbose_name = 'Video Asset'
        verbose_name_plural = 'Video Assets'

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.movie and not self.episode:
            raise ValidationError("A VideoAsset must be attached to either a Movie or an Episode.")
        if self.movie and self.episode:
            raise ValidationError("A VideoAsset cannot be attached to both a Movie and an Episode.")

    def __str__(self):
        target = self.movie.title if self.movie else str(self.episode)
        return f"VideoAsset: {target} [{self.get_status_display()}]"
