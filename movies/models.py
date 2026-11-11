from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    """Movie & Series genres (Action, Drama, Thriller, Romance, Sci-Fi, etc.)."""
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
    """Catalog types (Movies, TV Series, Documentaries, StreamFlix Originals)."""
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
    Main catalog model covering both standalone feature movies and series containers.
    """
    AGE_RATING_CHOICES = (
        ('U', 'Universal (All Ages)'),
        ('U/A 7+', 'Parental Guidance 7+'),
        ('U/A 13+', 'Parental Guidance 13+'),
        ('U/A 16+', 'Parental Guidance 16+'),
        ('A', 'Adults Only 18+'),
    )

    CONTENT_TYPE_CHOICES = (
        ('movie', 'Movie (Feature Film)'),
        ('series', 'Web Series / TV Show'),
    )

    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='movie')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='movies')
    genres = models.ManyToManyField(Genre, related_name='movies')
    synopsis = models.TextField()
    release_year = models.PositiveIntegerField(default=2024, db_index=True)
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes (for single movies)", default=120)
    language = models.CharField(max_length=50, default='English', db_index=True)
    age_rating = models.CharField(max_length=10, choices=AGE_RATING_CHOICES, default='U/A 13+')

    # Visual assets
    poster = models.ImageField(upload_to='posters/', help_text="Vertical poster (2:3 aspect ratio)")
    backdrop = models.ImageField(upload_to='backdrops/', blank=True, null=True, help_text="Horizontal hero banner (16:9)")
    trailer_video = models.FileField(upload_to='trailers/', blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True, help_text="Optional YouTube/external trailer embed URL")

    # Access flags & curation
    is_featured = models.BooleanField(default=False, db_index=True, help_text="Display on top hero carousel")
    is_trending = models.BooleanField(default=False, db_index=True, help_text="Highlight in trending section")
    is_premium = models.BooleanField(default=True, db_index=True, help_text="Requires active paid subscription")
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
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0.0

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class Season(models.Model):
    """Season grouping for episodic Web Series."""
    series = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='seasons', limit_choices_to={'content_type': 'series'})
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
    """Individual episode within a Season."""
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=200)
    overview = models.TextField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=45)
    thumbnail = models.ImageField(upload_to='episodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'streamflix_episodes'
        unique_together = ('season', 'episode_number')
        ordering = ['episode_number']

    def __str__(self):
        return f"{self.season.series.title} S{self.season.season_number}E{self.episode_number}: {self.title}"


class Review(models.Model):
    """User reviews and 1-5 star ratings for movies and series."""
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
