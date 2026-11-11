from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie, Episode


class Watchlist(models.Model):
    """User's bookmarked movies and web series."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_items')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='in_watchlists')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'streamflix_watchlist'
        unique_together = ('user', 'movie')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username}'s Watchlist: {self.movie.title}"


class WatchHistory(models.Model):
    """
    Playback progress tracker powering 'Continue Watching' and watch history.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_histories')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='watch_histories')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True, blank=True, related_name='watch_histories')

    last_position_seconds = models.PositiveIntegerField(default=0, help_text="Playback bookmark point")
    duration_seconds = models.PositiveIntegerField(default=0, help_text="Total video duration")
    is_completed = models.BooleanField(default=False)
    last_watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'streamflix_watch_history'
        ordering = ['-last_watched_at']

    @property
    def progress_percentage(self):
        if self.duration_seconds > 0:
            return min(100, int((self.last_position_seconds / self.duration_seconds) * 100))
        return 0

    def __str__(self):
        target = self.movie.title if self.movie else str(self.episode)
        return f"{self.user.username} watched {target} ({self.progress_percentage}%)"
