from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    """
    Anime Genres:
    Action, Adventure, Romance, Comedy, Fantasy, Isekai, Thriller,
    Horror, Sci-Fi, Sports, Slice of Life, Mystery, Supernatural, Drama, Psychological
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'streamflix_genres'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Catalog types (Anime Series, Anime Movies, Simulcasts, AniNova Exclusives)."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'streamflix_categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Movie(models.Model):
    """
    Core Anime Model representing Anime Series, Movies, and OVAs.
    """
    AGE_RATING_CHOICES = (
        ('PG', 'PG - Children & Teens'),
        ('PG-13', 'PG-13 - Teens 13 or older'),
        ('R-17+', 'R - 17+ (Violence & Profanity)'),
        ('R+', 'R+ - Mild Nudity / Explicit'),
    )

    CONTENT_TYPE_CHOICES = (
        ('series', 'Anime Series (TV)'),
        ('movie', 'Anime Movie (Feature Film)'),
        ('ova', 'OVA / Special'),
    )

    STATUS_CHOICES = (
        ('ongoing', 'Ongoing / Airing'),
        ('completed', 'Completed'),
        ('upcoming', 'Upcoming / Announced'),
    )

    title = models.CharField(max_length=255, db_index=True)
    japanese_title = models.CharField(max_length=255, blank=True, null=True, help_text="Kanji/Romaji title (e.g. 進撃の巨人)")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='series')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='movies')
    genres = models.ManyToManyField(Genre, related_name='movies')
    synopsis = models.TextField()

    # Anime Production details
    studio_name = models.CharField(max_length=150, default='MAPPA', help_text="Animation Studio (e.g. Ufotable, MAPPA, Wit)")
    director = models.CharField(max_length=150, blank=True, null=True, help_text="Chief Director")
    release_year = models.PositiveIntegerField(default=2024, db_index=True)
    duration_minutes = models.PositiveIntegerField(help_text="Average duration in minutes", default=24)
    age_rating = models.CharField(max_length=10, choices=AGE_RATING_CHOICES, default='PG-13')
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, default=8.5, help_text="MAL / IMDb community score")

    # Audio & Subtitle metadata
    language = models.CharField(max_length=50, default='Japanese', db_index=True)
    audio_languages = models.CharField(max_length=150, default='Japanese (Original), English Dub')
    subtitle_languages = models.CharField(max_length=150, default='English, Spanish, Hindi, German, French')
    has_dub = models.BooleanField(default=True, help_text="English dubbed audio track available")
    has_sub = models.BooleanField(default=True, help_text="English subtitles available")

    # Visual assets
    poster = models.ImageField(upload_to='posters/', blank=True, null=True, help_text="Vertical anime poster")
    backdrop = models.ImageField(upload_to='backdrops/', blank=True, null=True, help_text="Horizontal hero anime art (16:9)")
    poster_url = models.URLField(blank=True, null=True, help_text="External poster image fallback URL")
    backdrop_url = models.URLField(blank=True, null=True, help_text="External backdrop image fallback URL")
    trailer_video = models.FileField(upload_to='trailers/', blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True, help_text="Trailer / Opening sequence embed URL")

    # Curation & Engagement
    is_featured = models.BooleanField(default=False, db_index=True, help_text="Display in top hero billboard")
    is_trending = models.BooleanField(default=False, db_index=True, help_text="Highlight in Trending Anime row")
    is_popular = models.BooleanField(default=False, db_index=True, help_text="Highlight in Most Popular row")
    is_premium = models.BooleanField(default=False, db_index=True, help_text="Requires VIP / Premium membership")
    views_count = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'streamflix_movies'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Movie.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def total_episodes_count(self):
        return Episode.objects.filter(season__series=self).count()

    @property
    def seasons_count(self):
        return self.seasons.count()

    @property
    def display_poster(self):
        if self.poster and hasattr(self.poster, 'url'):
            return self.poster.url
        if self.poster_url:
            return self.poster_url
        return 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=400&q=80'

    @property
    def display_backdrop(self):
        if self.backdrop and hasattr(self.backdrop, 'url'):
            return self.backdrop.url
        if self.backdrop_url:
            return self.backdrop_url
        return 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1920&q=80'

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return float(self.imdb_rating)

    def __str__(self):
        jp = f" ({self.japanese_title})" if self.japanese_title else ""
        return f"{self.title}{jp} [{self.release_year}]"


class Season(models.Model):
    """Season arc for multi-season Anime."""
    series = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='seasons')
    season_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=150, blank=True)
    overview = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'streamflix_seasons'
        unique_together = ('series', 'season_number')
        ordering = ['season_number']

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"Season {self.season_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.series.title} - {self.title}"


class Episode(models.Model):
    """Individual Anime Episode with anime streaming controls (Skip Intro / Outro)."""
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=200)
    overview = models.TextField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=24)
    thumbnail = models.ImageField(upload_to='episodes/', blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)

    # Anime player controls: Skip Opening (OP) & Ending (ED)
    skip_intro_start = models.PositiveIntegerField(default=90, help_text="Intro OP start seconds")
    skip_intro_end = models.PositiveIntegerField(default=180, help_text="Intro OP end seconds")
    skip_outro_start = models.PositiveIntegerField(default=1320, help_text="Outro ED start seconds")
    skip_outro_end = models.PositiveIntegerField(default=1410, help_text="Outro ED end seconds")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'streamflix_episodes'
        unique_together = ('season', 'episode_number')
        ordering = ['episode_number']

    @property
    def display_thumbnail(self):
        if self.thumbnail and hasattr(self.thumbnail, 'url'):
            return self.thumbnail.url
        if self.thumbnail_url:
            return self.thumbnail_url
        return 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=400&q=80'

    @property
    def next_episode(self):
        """Returns the following episode in the season or next season."""
        next_ep = Episode.objects.filter(season=self.season, episode_number=self.episode_number + 1).first()
        if not next_ep:
            next_season = Season.objects.filter(series=self.season.series, season_number=self.season.season_number + 1).first()
            if next_season:
                next_ep = Episode.objects.filter(season=next_season, episode_number=1).first()
        return next_ep

    def __str__(self):
        return f"{self.season.series.title} S{self.season.season_number}E{self.episode_number}: {self.title}"


class Review(models.Model):
    """User reviews and 1-5 star ratings for anime titles."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'streamflix_reviews'
        unique_together = ('user', 'movie')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating}★)"
