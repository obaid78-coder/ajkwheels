# AJK Wheels - Auto Marketplace

Pakistan's PakWheels-inspired car & bike marketplace built with Flask + SQLite.

## Pages
- `/` — Homepage with featured listings, search, stats
- `/cars` — Cars listing with sidebar filters, sorting, pagination
- `/car/<id>` — Car detail with gallery, specs, seller info
- `/bikes` — Bikes listing
- `/bike/<id>` — Bike detail page
- `/compare` — Side-by-side car comparison tool
- `/post-ad` — Post a car or bike ad (login required)
- `/my-ads` — Manage your listings (login required)
- `/profile` — User profile page (login required)
- `/login` `/register` — Auth pages

## Setup & Run

```bash
pip install flask
python app.py
```

Open: http://localhost:5050

## Demo Login
- Email: demo@ajkwheels.com
- Password: demo123

## Tech Stack
- Backend: Python Flask
- Database: SQLite (auto-created on first run)
- Frontend: Vanilla HTML/CSS/JS (no frameworks needed)
- Icons: Font Awesome 6
- Fonts: Syne + DM Sans (Google Fonts)
