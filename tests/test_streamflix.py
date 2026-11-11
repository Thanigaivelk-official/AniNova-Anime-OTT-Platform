from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from movies.models import Movie, Category, Genre
from subscriptions.models import SubscriptionPlan, UserSubscription
from watchlist.models import Watchlist, WatchHistory
from payments.models import Payment


class StreamFlixTestSuite(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.user = User.objects.create_user(username='testviewer', email='viewer@test.com', password='Password123!')
        self.admin = User.objects.create_superuser(username='testadmin', email='admin@test.com', password='Password123!')

        # Metadata
        self.category = Category.objects.create(name='Movies', slug='movies')
        self.genre = Genre.objects.create(name='Action', slug='action')

        # Movie
        self.movie = Movie.objects.create(
            title='Inception Matrix',
            category=self.category,
            synopsis='A mind-bending action thriller.',
            release_year=2024,
            duration_minutes=140,
            language='English',
            is_premium=False
        )
        self.movie.genres.add(self.genre)

        # Premium Movie
        self.premium_movie = Movie.objects.create(
            title='VIP Blockbuster',
            category=self.category,
            synopsis='Exclusive VIP release.',
            release_year=2024,
            duration_minutes=120,
            language='English',
            is_premium=True
        )

        # Plan
        self.plan = SubscriptionPlan.objects.create(
            name='Premium Plan',
            slug='premium-plan',
            price=499.00,
            duration_days=30
        )

    def test_homepage_renders(self):
        """Test homepage returns 200 and displays catalog."""
        response = self.client.get(reverse('movies:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'StreamFlix')
        self.assertContains(response, 'Inception Matrix')

    def test_movie_detail_view(self):
        """Test movie detail page loads with correct title and view counter."""
        initial_views = self.movie.views_count
        response = self.client.get(reverse('movies:movie_detail', kwargs={'slug': self.movie.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception Matrix')

        self.movie.refresh_from_db()
        self.assertEqual(self.movie.views_count, initial_views + 1)

    def test_user_authentication_flow(self):
        """Test user login and session."""
        login_success = self.client.login(username='testviewer', password='Password123!')
        self.assertTrue(login_success)

        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testviewer')

    def test_watchlist_toggle(self):
        """Test adding and removing movie from watchlist."""
        self.client.login(username='testviewer', password='Password123!')

        # Add
        response = self.client.post(reverse('watchlist:toggle', kwargs={'movie_id': self.movie.id}))
        self.assertTrue(Watchlist.objects.filter(user=self.user, movie=self.movie).exists())

        # Toggle Remove
        response = self.client.post(reverse('watchlist:toggle', kwargs={'movie_id': self.movie.id}))
        self.assertFalse(Watchlist.objects.filter(user=self.user, movie=self.movie).exists())

    def test_premium_content_restriction(self):
        """Test that free viewer cannot access premium movie without subscription."""
        self.client.login(username='testviewer', password='Password123!')
        response = self.client.get(reverse('streaming:play', kwargs={'slug': self.premium_movie.slug}))
        # Redirected to plans
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('subscriptions:plans'), response.url)

    def test_search_functionality(self):
        """Test search query returns matching results."""
        response = self.client.get(reverse('movies:search') + '?q=Matrix')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception Matrix')
