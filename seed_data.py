"""
StreamFlix Seed Script - Populates initial demo data for testing and UI demonstration.
Run via: python seed_data.py
"""

import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile
from movies.models import Genre, Category, Movie, Season, Episode
from subscriptions.models import SubscriptionPlan, UserSubscription
from watchlist.models import Watchlist, WatchHistory


def seed():
    print("[*] Seeding StreamFlix Database...")

    # 1. Admin Superuser
    admin_user, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@streamflix.com',
        'is_staff': True,
        'is_superuser': True,
    })
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        admin_user.profile.role = 'admin'
        admin_user.profile.is_verified = True
        admin_user.profile.save()
        print("[+] Superuser created: admin / admin123")
    else:
        print("[i] Superuser already exists: admin")

    # 2. Demo Customer User
    demo_user, created = User.objects.get_or_create(username='viewer', defaults={
        'email': 'viewer@streamflix.com',
    })
    if created:
        demo_user.set_password('viewer123')
        demo_user.save()
        demo_user.profile.role = 'customer'
        demo_user.profile.is_verified = True
        demo_user.profile.save()
        print("[+] Viewer created: viewer / viewer123")

    # 3. Categories
    categories_data = [
        ("Movies", "Full-length Hollywood, Bollywood and International cinema"),
        ("Web Series", "Binge-worthy multi-episode drama and thriller series"),
        ("Originals", "StreamFlix Exclusive productions and world premieres"),
        ("Documentaries", "Real-world stories, nature, and true crime investigations"),
    ]
    categories = {}
    for name, desc in categories_data:
        cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
        categories[name] = cat
    print(f"[+] {len(categories)} Categories verified")

    # 4. Genres
    genres_data = ["Action", "Sci-Fi", "Thriller", "Drama", "Crime", "Comedy", "Adventure", "Fantasy", "Horror"]
    genres = {}
    for gname in genres_data:
        g, _ = Genre.objects.get_or_create(name=gname)
        genres[gname] = g
    print(f"[+] {len(genres)} Genres verified")

    # 5. Subscription Plans
    plans_data = [
        {
            'name': 'Free Tier',
            'slug': 'free-tier',
            'duration_type': 'monthly',
            'duration_days': 365,
            'price': 0.00,
            'max_screens': 1,
            'max_quality': '480p SD',
            'has_ads': True,
            'description': 'Enjoy access to selected free movie library with standard quality.',
        },
        {
            'name': 'Standard HD',
            'slug': 'standard-hd',
            'duration_type': 'monthly',
            'duration_days': 30,
            'price': 499.00,
            'max_screens': 2,
            'max_quality': '1080p Full HD',
            'has_ads': False,
            'description': 'Unlimited ad-free movies and series in Full HD on phone, tablet, and TV.',
        },
        {
            'name': 'Premium 4K Ultra HD',
            'slug': 'premium-4k-ultra-hd',
            'duration_type': 'monthly',
            'duration_days': 30,
            'price': 799.00,
            'max_screens': 4,
            'max_quality': '4K Ultra HD + HDR',
            'has_ads': False,
            'description': 'The best entertainment experience. 4K Ultra HD, spatial audio, 4 devices at once.',
        },
        {
            'name': 'Annual VIP All-Access',
            'slug': 'annual-vip-all-access',
            'duration_type': 'yearly',
            'duration_days': 365,
            'price': 1999.00,
            'max_screens': 4,
            'max_quality': '4K Ultra HD + Dolby Atmos',
            'has_ads': False,
            'description': 'Yearly plan with massive discount. Stream on 4 devices in 4K.',
        },
    ]
    plans = {}
    for p_info in plans_data:
        slug = p_info.pop('slug')
        plan, _ = SubscriptionPlan.objects.get_or_create(slug=slug, defaults=p_info)
        plans[slug] = plan
    print(f"[+] {len(plans)} Subscription plans verified")

    # Give demo user a premium subscription
    UserSubscription.objects.get_or_create(user=demo_user, defaults={
        'plan': plans['premium-4k-ultra-hd'],
        'start_date': timezone.now(),
        'end_date': timezone.now() + timedelta(days=30),
        'status': 'active',
    })

    # 6. Sample Movies & Series
    movies_data = [
        {
            'title': 'Cyberverse 2099',
            'content_type': 'movie',
            'category': categories['Originals'],
            'genres': [genres['Sci-Fi'], genres['Action']],
            'synopsis': 'In a rain-drenched dystopian metropolis governed by artificial superintelligence, a rogue cyber-detective uncovers a simulation conspiracy threatening biological human existence.',
            'release_year': 2024,
            'duration_minutes': 148,
            'language': 'English',
            'age_rating': 'U/A 16+',
            'is_featured': True,
            'is_trending': True,
            'is_premium': True,
            'views_count': 125400,
        },
        {
            'title': 'Shadow Protocol',
            'content_type': 'movie',
            'category': categories['Movies'],
            'genres': [genres['Action'], genres['Thriller']],
            'synopsis': 'An elite black-ops operative is framed for an international covert disaster and must race across European capitals to clear his name and neutralize a rogue syndicate.',
            'release_year': 2024,
            'duration_minutes': 132,
            'language': 'English',
            'age_rating': 'U/A 16+',
            'is_featured': False,
            'is_trending': True,
            'is_premium': True,
            'views_count': 94500,
        },
        {
            'title': 'The Quantum Paradox',
            'content_type': 'movie',
            'category': categories['Movies'],
            'genres': [genres['Sci-Fi'], genres['Thriller']],
            'synopsis': 'When an experimental particle accelerator fractures temporal dimensions, a team of astrophysicists must repair the timeline before their present reality collapses.',
            'release_year': 2023,
            'duration_minutes': 118,
            'language': 'English',
            'age_rating': 'U/A 13+',
            'is_featured': False,
            'is_trending': True,
            'is_premium': False,
            'views_count': 82100,
        },
        {
            'title': 'Silicon Empire',
            'content_type': 'series',
            'category': categories['Web Series'],
            'genres': [genres['Drama'], genres['Crime']],
            'synopsis': 'The ruthless, Machiavellian rise of high-stakes technology venture capitalists, covert boardroom espionage, and billion-dollar valuations in the digital era.',
            'release_year': 2024,
            'duration_minutes': 55,
            'language': 'English',
            'age_rating': 'A',
            'is_featured': False,
            'is_trending': True,
            'is_premium': True,
            'views_count': 210000,
        },
        {
            'title': 'Neon Tokyo Underground',
            'content_type': 'movie',
            'category': categories['Movies'],
            'genres': [genres['Action'], genres['Crime']],
            'synopsis': 'High-octane street racers, underground syndicates, and a high-stakes heist through the neon-lit expressways of modern Tokyo.',
            'release_year': 2023,
            'duration_minutes': 124,
            'language': 'Japanese',
            'age_rating': 'U/A 16+',
            'is_featured': False,
            'is_trending': False,
            'is_premium': False,
            'views_count': 67300,
        },
        {
            'title': 'Deep Ocean: Secrets of the Abyss',
            'content_type': 'movie',
            'category': categories['Documentaries'],
            'genres': [genres['Adventure']],
            'synopsis': 'Pioneering marine scientists descend into the Mariana Trench to document bioluminescent creatures and hydrothermal vent ecosystems never before captured on camera.',
            'release_year': 2024,
            'duration_minutes': 96,
            'language': 'English',
            'age_rating': 'U',
            'is_featured': False,
            'is_trending': False,
            'is_premium': False,
            'views_count': 45200,
        },
    ]

    for m_info in movies_data:
        m_genres = m_info.pop('genres')
        title = m_info['title']
        movie, m_created = Movie.objects.get_or_create(title=title, defaults=m_info)
        if m_created:
            movie.genres.set(m_genres)
            print(f"[+] Created movie/series: {title}")

            # If it's a web series, add a season and 3 demo episodes
            if movie.content_type == 'series':
                season, _ = Season.objects.get_or_create(series=movie, season_number=1, defaults={'title': 'Season 1'})
                Episode.objects.get_or_create(season=season, episode_number=1, defaults={
                    'title': 'The Disruptor Protocol',
                    'overview': 'A brilliant engineer creates an unprecedented AI algorithm and attracts unwanted interest from dangerous venture capital titans.',
                    'duration_minutes': 54,
                })
                Episode.objects.get_or_create(season=season, episode_number=2, defaults={
                    'title': 'Hostile Takeover',
                    'overview': 'Boardroom alliances shatter as insider leaks threaten the upcoming public IPO.',
                    'duration_minutes': 58,
                })
                Episode.objects.get_or_create(season=season, episode_number=3, defaults={
                    'title': 'Zero-Day Vulnerability',
                    'overview': 'A covert cyber-attack exposes the company’s darkest trade secrets.',
                    'duration_minutes': 50,
                })

    print("[OK] Database seeding completed successfully!")


if __name__ == '__main__':
    seed()
