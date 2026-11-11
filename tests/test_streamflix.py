from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from movies.models import Movie, Category, Genre
from subscriptions.models import SubscriptionPlan, UserSubscription
from watchlist.models import Watchlist, WatchHistory
from accounts.models import UserProfile


class AniNovaTestSuite(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.user = User.objects.create_user(username='otaku_test', email='otaku@test.com', password='Password123!')
        self.admin = User.objects.create_superuser(username='admin_test', email='admin@test.com', password='Password123!')

        # Metadata
        self.category = Category.objects.create(name='Anime Series', slug='anime-series')
        self.genre = Genre.objects.create(name='Action', slug='action')

        # Anime
        self.anime = Movie.objects.create(
            title='Demon Slayer',
            japanese_title='鬼滅の刃',
            category=self.category,
            synopsis='A young boy battles demons to save his sister.',
            release_year=2024,
            duration_minutes=24,
            language='Japanese',
            studio_name='Ufotable',
            imdb_rating=8.9,
            is_premium=False
        )
        self.anime.genres.add(self.genre)

        # VIP Anime
        self.vip_anime = Movie.objects.create(
            title='VIP Simulcast World',
            category=self.category,
            synopsis='Exclusive simulcast stream.',
            release_year=2024,
            duration_minutes=24,
            language='Japanese',
            is_premium=True
        )

        # Plan
        self.plan = SubscriptionPlan.objects.create(
            name='Ultra Otaku VIP',
            slug='ultra-otaku-vip',
            price=499.00,
            duration_days=30
        )

    def test_homepage_renders_aninova(self):
        """Test homepage returns 200 and displays AniNova branding and anime catalog."""
        response = self.client.get(reverse('movies:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AniNova')
        self.assertContains(response, 'A New World of Anime')
        self.assertContains(response, 'Demon Slayer')

    def test_anime_detail_view(self):
        """Test anime detail page loads with Japanese title and studio."""
        initial_views = self.anime.views_count
        response = self.client.get(reverse('movies:movie_detail', kwargs={'slug': self.anime.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Demon Slayer')
        self.assertContains(response, 'Ufotable')

        self.anime.refresh_from_db()
        self.assertEqual(self.anime.views_count, initial_views + 1)

    def test_profile_photo_upload_and_preview(self):
        """Test user can upload profile photo and avatar_url reflects the uploaded file."""
        import io
        from PIL import Image

        self.client.login(username='otaku_test', password='Password123!')

        # Generate a real valid PNG image with Pillow
        image = Image.new('RGB', (100, 100), color='purple')
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        uploaded_image = SimpleUploadedFile("avatar.png", buf.getvalue(), content_type="image/png")

        response = self.client.post(reverse('accounts:profile'), {
            'action': 'update_photo',
            'avatar': uploaded_image
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        profile = UserProfile.objects.get(user=self.user)
        self.assertTrue(bool(profile.avatar))
        self.assertIn('avatar', profile.avatar_url)

    def test_watchlist_toggle(self):
        """Test adding and removing anime from watchlist."""
        self.client.login(username='otaku_test', password='Password123!')

        # Add
        response = self.client.post(reverse('watchlist:toggle', kwargs={'movie_id': self.anime.id}))
        self.assertTrue(Watchlist.objects.filter(user=self.user, movie=self.anime).exists())

        # Toggle Remove
        response = self.client.post(reverse('watchlist:toggle', kwargs={'movie_id': self.anime.id}))
        self.assertFalse(Watchlist.objects.filter(user=self.user, movie=self.anime).exists())

    def test_vip_simulcast_restriction(self):
        """Test that free viewer is redirected to Otaku VIP plans when accessing premium simulcast."""
        self.client.login(username='otaku_test', password='Password123!')
        response = self.client.get(reverse('streaming:play', kwargs={'slug': self.vip_anime.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('subscriptions:plans'), response.url)

    def test_anime_search(self):
        """Test search query filters anime by English or Japanese title."""
        response = self.client.get(reverse('movies:search') + '?q=Slayer')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Demon Slayer')
