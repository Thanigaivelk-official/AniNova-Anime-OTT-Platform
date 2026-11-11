# AniNova – A New World of Anime ⚡

AniNova is an enterprise-grade, full-stack **Anime OTT Video Streaming Platform** engineered with Python, Django 5.1, MySQL, Django REST Framework, HLS Adaptive Streaming, and Razorpay payment integration.

---

## 🌸 Brand Identity & Highlights
- **Platform Name:** AniNova
- **Tagline:** *A New World of Anime.*
- **Aesthetic:** Cyberpunk Dark Theme with obsidian surfaces (`#0b0a12`), electric purple accents (`#8A2BE2`), and neon sakura pink highlights (`#ff2a85`).
- **Catalog Coverage:** 15 Anime Genres, Simulcast Series, Theatrical Films, Japanese & English Dubbed tracks, multi-language subtitles, and MAL/IMDb ratings.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.12+, Django 5.1, Django REST Framework
- **Database:** MySQL (PyMySQL with `utf8mb4_unicode_ci`)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Font Awesome
- **Video Delivery:** HTML5 Player, HLS.js Adaptive Bitrate Streaming, FFmpeg Transcoder
- **Anime Player Features:** 
  - Dynamic **Skip Opening (OP)** and **Skip Ending (ED)**
  - **Next Episode Autoplay** with 8s countdown
  - Season / Episode drawer navigation
  - Multi-track Audio (Japanese / English Dub) and Subtitles selector
  - Auto-bookmarking watch progress every 6 seconds to `/stream/api/progress/`
- **Payment Gateway:** Razorpay Test Mode for Otaku VIP subscription tiers
- **User Profile Management:**
  - Dynamic **Profile Photo Upload** (JPG, JPEG, PNG, WEBP up to 5MB)
  - Real-time JavaScript image preview before saving
  - 1-click **Remove Custom Photo** reverting to anime character avatar
  - Otaku account details: username, email, phone, favorite anime, and bio

---

## 📂 Project Structure
```text
E:\OTT/
├── config/                  # Core Django project settings & URL routing
├── accounts/                # User authentication, profiles, photo uploads
├── movies/                  # Anime titles, seasons, episodes, studios, genres
├── streaming/               # Cinema player, skip OP/ED, progress tracker, HLS
├── subscriptions/           # Otaku VIP membership plans & validity
├── watchlist/               # Bookmarked anime & watch history
├── payments/                # Razorpay transactions & signature validation
├── recommendations/         # Content-based anime recommendation engine
├── dashboard/               # AniNova Studio Admin control center
├── templates/               # Global & module-specific anime templates
├── static/                  # CSS, JavaScript, and UI assets
├── media/                   # Anime posters, backdrops, avatars, video chunks
├── tests/                   # Automated unit & integration test suites
├── requirements.txt         # Pinned production packages
└── manage.py                # Django CLI management utility
```

---

## 🚀 Quickstart Guide

### 1. Start MySQL Server
Make sure MySQL is running on port 3306:
```powershell
cd C:\xampp
.\mysql\bin\mysqld.exe --defaults-file=mysql\bin\my.ini --standalone
```

### 2. Activate Virtual Environment & Migrate
```powershell
cd E:\OTT
.\venv\Scripts\activate
python manage.py migrate
```

### 3. Seed Anime Catalog & Test Data
```powershell
python seed_data.py
```

### 4. Run Development Server
```powershell
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your browser.

---

## 🔑 Demo Credentials
| Account Type | Username | Password | Role |
|---|---|---|---|
| **AniNova Studio Admin** | `admin` | `admin123` | Full Studio Dashboard (`/dashboard/`) & Django Admin (`/admin/`) |
| **Otaku VIP Viewer** | `viewer` | `viewer123` | Ultra Otaku VIP Subscriber Access |

---

## 🧪 Run Automated Tests
```powershell
python manage.py test tests --noinput
```
