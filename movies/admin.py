from django.contrib import admin
from .models import Genre, Category, Movie, Season, Episode, Review


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 1
    fields = ('episode_number', 'title', 'duration_minutes', 'skip_intro_start', 'skip_intro_end', 'skip_outro_start', 'skip_outro_end')


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('series', 'season_number', 'title', 'release_date')
    list_filter = ('series',)
    inlines = [EpisodeInline]


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('season', 'episode_number', 'title', 'duration_minutes', 'skip_intro_start', 'skip_intro_end')
    list_filter = ('season__series', 'season')
    search_fields = ('title', 'season__series__title')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'japanese_title', 'studio_name', 'content_type', 'status', 'imdb_rating', 'is_featured', 'is_trending', 'is_popular', 'is_premium')
    list_filter = ('content_type', 'status', 'studio_name', 'category', 'genres', 'is_featured', 'is_trending', 'is_popular', 'is_premium')
    search_fields = ('title', 'japanese_title', 'studio_name', 'director', 'synopsis')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'movie__title')
