"""
AniNova Anime Seed Script - Seeds Anime categories, studios, and anime titles.
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


def seed_anime():
    print("[*] Seeding AniNova Anime Platform...")

    # 1. Admin Superuser & Viewer
    admin_user, _ = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@aninova.tv',
        'is_staff': True,
        'is_superuser': True,
    })
    admin_user.set_password(os.getenv('ADMIN_PASSWORD', 'admin123'))
    admin_user.save()
    admin_user.profile.role = 'admin'
    admin_user.profile.is_verified = True
    admin_user.profile.save()

    demo_user, _ = User.objects.get_or_create(username='viewer', defaults={
        'email': 'viewer@aninova.tv',
    })
    demo_user.set_password(os.getenv('VIEWER_PASSWORD', 'viewer123'))
    demo_user.save()
    demo_user.profile.role = 'customer'
    demo_user.profile.is_verified = True
    demo_user.profile.save()

    # 2. Anime Categories (Catalog Types)
    cat_names = [
        ("Anime Series", "Multi-episode serialized anime broadcasts"),
        ("Anime Movies", "Theatrical anime films and cinematic masterpieces"),
        ("AniNova Originals", "Exclusive co-productions and worldwide simulcasts"),
        ("OVAs & Specials", "Original Video Animations, side-stories, and movies"),
    ]
    categories = {}
    for c_name, c_desc in cat_names:
        c, _ = Category.objects.get_or_create(name=c_name, defaults={'description': c_desc})
        categories[c_name] = c

    # 3. 15 Required Anime Genres
    genre_list = [
        "Action", "Adventure", "Romance", "Comedy", "Fantasy",
        "Isekai", "Thriller", "Horror", "Sci-Fi", "Sports",
        "Slice of Life", "Mystery", "Supernatural", "Drama", "Psychological"
    ]
    genres = {}
    for g_name in genre_list:
        g, _ = Genre.objects.get_or_create(name=g_name)
        genres[g_name] = g
    print(f"[+] Verified {len(genres)} Anime Genres")

    # 4. AniNova VIP Subscription Plans
    plans_data = [
        {
            'name': 'Fan (Free)',
            'slug': 'fan-free',
            'duration_type': 'monthly',
            'duration_days': 365,
            'price': 0.00,
            'max_screens': 1,
            'max_quality': '720p HD',
            'has_ads': True,
            'description': 'Standard anime library with ads. Watch 1 week after Japan broadcast.',
        },
        {
            'name': 'Mega Fan',
            'slug': 'mega-fan',
            'duration_type': 'monthly',
            'duration_days': 30,
            'price': 199.00,
            'max_screens': 2,
            'max_quality': '1080p Full HD',
            'has_ads': False,
            'description': 'Simulcast 1 hour after Japan airing. Ad-free anime, offline viewing, 2 devices.',
        },
        {
            'name': 'Ultra Otaku VIP',
            'slug': 'ultra-otaku-vip',
            'duration_type': 'monthly',
            'duration_days': 30,
            'price': 499.00,
            'max_screens': 4,
            'max_quality': '4K Ultra HD + Hi-Fi Audio',
            'has_ads': False,
            'description': 'Simulcast access, 4K quality, 4 screens, exclusive AniNova anime events & digital manga.',
        },
        {
            'name': 'Annual Hokage All-Access',
            'slug': 'annual-hokage-all-access',
            'duration_type': 'yearly',
            'duration_days': 365,
            'price': 1499.00,
            'max_screens': 4,
            'max_quality': '4K Ultra HD + Dolby Atmos',
            'has_ads': False,
            'description': 'Full year VIP pass. Complete anime collection in 4K, 16% discount, 4 simultaneous screens.',
        },
    ]
    plans = {}
    for p in plans_data:
        slug = p.pop('slug')
        plan, _ = SubscriptionPlan.objects.get_or_create(slug=slug, defaults=p)
        plans[slug] = plan

    UserSubscription.objects.get_or_create(user=demo_user, defaults={
        'plan': plans['ultra-otaku-vip'],
        'start_date': timezone.now(),
        'end_date': timezone.now() + timedelta(days=365),
        'status': 'active',
    })

    # 5. Rich Anime Catalog Data
    anime_titles = [
        {
            'title': 'Demon Slayer: Kimetsu no Yaiba',
            'japanese_title': '鬼滅の刃',
            'content_type': 'series',
            'category': categories['Anime Series'],
            'genres': [genres['Action'], genres['Supernatural'], genres['Fantasy'], genres['Drama']],
            'studio_name': 'Ufotable',
            'director': 'Haruo Sotozaki',
            'status': 'ongoing',
            'synopsis': 'Tanjiro Kamado, a kindhearted boy who sells charcoal, finds his family slaughtered by a demon. To make matters worse, his younger sister Nezuko has been transformed into a demon herself. Tanjiro embarks on a dangerous journey to slay demons and turn Nezuko back into a human.',
            'release_year': 2024,
            'duration_minutes': 24,
            'age_rating': 'R-17+',
            'imdb_rating': 8.9,
            'language': 'Japanese',
            'audio_languages': 'Japanese (Original), English Dub, Hindi Dub',
            'subtitle_languages': 'English, Spanish, Hindi, German, French',
            'has_dub': True,
            'has_sub': True,
            'poster_url': 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=450&q=80',
            'backdrop_url': 'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=1920&q=80',
            'is_featured': True,
            'is_trending': True,
            'is_popular': True,
            'is_premium': True,
            'views_count': 1450000,
        },
        {
            'title': 'Jujutsu Kaisen',
            'japanese_title': '呪術廻戦',
            'content_type': 'series',
            'category': categories['Anime Series'],
            'genres': [genres['Action'], genres['Supernatural'], genres['Fantasy'], genres['Psychological']],
            'studio_name': 'MAPPA',
            'director': 'Sunghoo Park / Shota Goshozono',
            'status': 'ongoing',
            'synopsis': 'A boy swallows a cursed talisman - the finger of a demon - and becomes cursed himself. He enters a shaman school to be able to locate the demons other body parts and thus exorcise himself.',
            'release_year': 2024,
            'duration_minutes': 24,
            'age_rating': 'R-17+',
            'imdb_rating': 8.6,
            'language': 'Japanese',
            'audio_languages': 'Japanese, English Dub',
            'subtitle_languages': 'English, French, German',
            'has_dub': True,
            'has_sub': True,
            'poster_url': 'https://images.unsplash.com/photo-1563089145-599997674d42?auto=format&fit=crop&w=450&q=80',
            'backdrop_url': 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=1920&q=80',
            'is_featured': False,
            'is_trending': True,
            'is_popular': True,
            'is_premium': True,
            'views_count': 1280000,
        },
        {
            'title': 'Solo Leveling',
            'japanese_title': '俺だけレベルアップな件',
            'content_type': 'series',
            'category': categories['AniNova Originals'],
            'genres': [genres['Action'], genres['Fantasy'], genres['Adventure']],
            'studio_name': 'A-1 Pictures',
            'director': 'Shunsuke Nakashige',
            'status': 'ongoing',
            'synopsis': 'In a world where hunters, humans who possess magical abilities, battle deadly monsters, a notoriously weak hunter named Sung Jinwoo is brutally killed in a high-rank dungeon. He awakens with a mysterious player quest window only he can see.',
            'release_year': 2024,
            'duration_minutes': 24,
            'age_rating': 'R-17+',
            'imdb_rating': 8.5,
            'language': 'Japanese',
            'audio_languages': 'Japanese, English Dub, Korean',
            'subtitle_languages': 'English, Spanish, Hindi',
            'has_dub': True,
            'has_sub': True,
            'poster_url': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=450&q=80',
            'backdrop_url': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1920&q=80',
            'is_featured': False,
            'is_trending': True,
            'is_popular': True,
            'is_premium': True,
            'views_count': 920000,
        },
        {
            'title': 'Frieren: Beyond Journey’s End',
            'japanese_title': '葬送のフリーレン',
            'content_type': 'series',
            'category': categories['Anime Series'],
            'genres': [genres['Adventure'], genres['Drama'], genres['Fantasy'], genres['Slice of Life']],
            'studio_name': 'Madhouse',
            'director': 'Keiichiro Saito',
            'status': 'completed',
            'synopsis': 'An elf mage and her fellow adventurers have defeated the Demon King, bringing peace to the land. But being an elf, Frieren will see her former companions slowly pass away. She embarks on a journey to reflect on human life, mortality, and meaningful memories.',
            'release_year': 2024,
            'duration_minutes': 24,
            'age_rating': 'PG-13',
            'imdb_rating': 9.1,
            'language': 'Japanese',
            'audio_languages': 'Japanese, English Dub',
            'subtitle_languages': 'English, German, French',
            'has_dub': True,
            'has_sub': True,
            'poster_url': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=450&q=80',
            'backdrop_url': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1920&q=80',
            'is_featured': False,
            'is_trending': True,
            'is_popular': True,
            'is_premium': False,
            'views_count': 840000,
        },
        {
            'title': 'Your Name',
            'japanese_title': '君の名は。',
            'content_type': 'movie',
            'category': categories['Anime Movies'],
            'genres': [genres['Romance'], genres['Drama'], genres['Supernatural'], genres['Fantasy']],
            'studio_name': 'CoMix Wave Films',
            'director': 'Makoto Shinkai',
            'status': 'completed',
            'synopsis': 'Two high school students, Mitsuha in the countryside and Taki in Tokyo, find that they are suddenly and mysteriously swapping bodies. When a cosmic event draws near, they race across time and space to find one another.',
            'release_year': 2016,
            'duration_minutes': 107,
            'age_rating': 'PG',
            'imdb_rating': 8.4,
            'language': 'Japanese',
            'audio_languages': 'Japanese, English Dub',
            'subtitle_languages': 'English, Spanish, Hindi, Japanese',
            'has_dub': True,
            'has_sub': True,
            'poster_url': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=450&q=80',
            'backdrop_url': 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=1920&q=80',
            'is_featured': False,
            'is_trending': False,
            'is_popular': True,
            'is_premium': False,
            'views_count': 1950000,
        },
        {
            'title': 'Spirited Away',
            'japanese_title': '千と千尋の神隠し',
            'content_type': 'movie',
            'category': categories['Anime Movies'],
            'genres': [genres['Adventure'], genres['Fantasy'], genres['Supernatural']],
            'studio_name': 'Studio Ghibli',
            'director': 'Hayao Miyazaki',
            'status': 'completed',
            'synopsis': 'During her family’s move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts.',
            'release_year': 2001,
            'duration_minutes': 125,
            'age_rating': 'PG',
            'imdb_rating': 8.6,
            'language': 'Japanese',
            'audio_languages': 'Japanese, English Dub',
            'subtitle_languages': 'English, French, German',
            'has_dub': True,
            'has_sub': True,
            'poster_url': 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=450&q=80',
            'backdrop_url': 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=1920&q=80',
            'is_featured': False,
            'is_trending': False,
            'is_popular': True,
            'is_premium': False,
            'views_count': 2300000,
        },
        {
            'title': 'Attack on Titan: The Final Season',
            'japanese_title': '進撃の巨人 The Final Season',
            'content_type': 'series',
            'category': categories['Anime Series'],
            'genres': [genres['Action'], genres['Drama'], genres['Fantasy'], genres['Mystery'], genres['Psychological']],
            'studio_name': 'MAPPA',
            'director': 'Yuichiro Hayashi',
            'status': 'completed',
            'synopsis': 'The war for Paradis zeroes in on Shiganshina just as Eren unchains the Rumbling to protect Eldia. As the line between savior and destroyer disappears, former comrades must make a final stand.',
            'release_year': 2023,
            'duration_minutes': 25,
            'age_rating': 'R-17+',
            'imdb_rating': 9.0,
            'language': 'Japanese',
            'audio_languages': 'Japanese, English Dub, German',
            'subtitle_languages': 'English, Spanish, Hindi',
            'has_dub': True,
            'has_sub': True,
            'poster_url': 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=450&q=80',
            'backdrop_url': 'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=1920&q=80',
            'is_featured': False,
            'is_trending': True,
            'is_popular': True,
            'is_premium': True,
            'views_count': 3100000,
        },
        {
            'title': 'Re:Zero - Starting Life in Another World',
            'japanese_title': 'Re:ゼロから始める異世界生活',
            'content_type': 'series',
            'category': categories['Anime Series'],
            'genres': [genres['Isekai'], genres['Fantasy'], genres['Psychological'], genres['Thriller']],
            'studio_name': 'White Fox',
            'director': 'Masaharu Watanabe',
            'status': 'ongoing',
            'synopsis': 'Subaru Natsuki is suddenly summoned to another world with no explanation. Armed only with the ability to rewind time by dying ("Return by Death"), he struggles to save those he loves from gruesome fates.',
            'release_year': 2024,
            'duration_minutes': 24,
            'age_rating': 'R-17+',
            'imdb_rating': 8.3,
            'language': 'Japanese',
            'audio_languages': 'Japanese, English Dub',
            'subtitle_languages': 'English, Spanish',
            'has_dub': True,
            'has_sub': True,
            'poster_url': 'https://images.unsplash.com/photo-1563089145-599997674d42?auto=format&fit=crop&w=450&q=80',
            'backdrop_url': 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=1920&q=80',
            'is_featured': False,
            'is_trending': True,
            'is_popular': True,
            'is_premium': True,
            'views_count': 980000,
        },
    ]

    for a_data in anime_titles:
        g_list = a_data.pop('genres')
        title = a_data['title']
        anime, _ = Movie.objects.update_or_create(title=title, defaults=a_data)
        anime.genres.set(g_list)
        print(f"[+] Synced anime: {title}")

        # Add Season 1 and sample episodes with Intro/Outro skip timestamps
        if anime.content_type == 'series':
            season, _ = Season.objects.get_or_create(series=anime, season_number=1, defaults={'title': 'Season 1'})
            episodes_sample = [
                (1, 'To the World Beyond', 'The journey begins as an unexpected encounter changes destiny.', 90, 180),
                (2, 'Blade of Resolve', 'Stakes rise when ancient demonic powers awaken in the shadow.', 85, 175),
                (3, 'Cursed Domain Expansion', 'A clash of immense magical wills tests mortal limits.', 90, 180),
                (4, 'The Unbreakable Oath', 'Sacrifices are made as allies unite against insurmountable odds.', 90, 180),
            ]
            for ep_num, ep_title, ep_desc, s_in, e_in in episodes_sample:
                Episode.objects.update_or_create(
                    season=season,
                    episode_number=ep_num,
                    defaults={
                        'title': ep_title,
                        'overview': ep_desc,
                        'duration_minutes': 24,
                        'skip_intro_start': s_in,
                        'skip_intro_end': e_in,
                        'skip_outro_start': 1320,
                        'skip_outro_end': 1410,
                    }
                )

    print("[OK] AniNova Anime Seeding Complete!")


if __name__ == '__main__':
    seed_anime()
