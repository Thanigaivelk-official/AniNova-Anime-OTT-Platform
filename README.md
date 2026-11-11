# StreamFlix – Enterprise OTT Streaming Platform

StreamFlix is a production-ready, full-stack video streaming web application built with Python, Django, MySQL, Django REST Framework, HLS (Adaptive Bitrate Streaming with FFmpeg), and Razorpay payment integration.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.12+, Django 5.1, Django REST Framework
- **Database:** MySQL (configured with PyMySQL + utf8mb4)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Font Awesome, AJAX
- **Streaming:** HTML5 Video Player, FFmpeg, HLS (.m3u8, .ts chunks)
- **Payment Gateway:** Razorpay (Test Mode)
- **Security:** CSRF, Signed Stream URLs, Role-based Access Control (RBAC), Environment Variables

---

## 📂 Project Architecture
```text
OTT/
├── config/                  # Core Django project settings & URL routing
├── accounts/                # User authentication, profiles, role-based permissions
├── movies/                  # Movie, series, season, episode, genre & category catalog
├── streaming/               # Video asset management, HLS stream delivery, progress tracker
├── subscriptions/           # Subscription plans, tiers, user subscription status
├── watchlist/               # Watchlist, watch history, continue watching
├── payments/                # Razorpay transactions, webhook handling, invoices
├── recommendations/         # Basic content-based recommendations & trending algorithms
├── dashboard/               # Administrative analytics, movie & subscriber management
├── templates/               # Global & module-specific HTML templates
├── static/                  # CSS, JavaScript, and UI image assets
├── media/                   # Posters, banners, trailers, avatars, and HLS video chunks
├── tests/                   # Automated unit & integration test suites
├── .env.example             # Template for environment variables
├── requirements.txt         # Project Python dependencies
└── manage.py                # Django CLI management utility
```

---

## 🚀 Phase 1 Setup Instructions

### 1. Prerequisites
- Python 3.12+ installed
- MySQL Server installed (MySQL 8 or XAMPP MySQL)
- VS Code (recommended extensions: Python, Django, MySQL)

### 2. Activate Virtual Environment
In your Windows PowerShell or Command Prompt:
```powershell
cd E:\OTT
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and verify your MySQL credentials:
```ini
DEBUG=True
SECRET_KEY=your-secret-key
USE_SQLITE=False
DB_NAME=streamflix_db
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 5. Run Development Server
```powershell
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.
