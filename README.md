# Blogify — Modern Publishing Platform

> **Write. Share. Inspire.**

A modern, production-grade blogging platform developed using Python, Flask, SQLAlchemy, Flask-Login, Flask-Migrate, and Bootstrap 5 with custom brand identity.

🌐 **Live Application:** [https://blogify-by-ps.onrender.com/](https://blogify-by-ps.onrender.com/)

---

## 1. Project Overview

**Blogify** is a full-featured content publishing and community discussion platform. Building upon Phase 1's core foundation (authentication and post CRUD), Phase 2 introduces:

- Enhanced responsive user interfaces for desktops, tablets, and mobile devices.
- Multi-criteria real-time search (by title, content, and author).
- Category filtering and chronological sorting (newest/oldest).
- A complete commenting system with owner authorization and validation.
- User dashboard with author-specific management and statistics.
- Public user profiles showcasing published posts and member metrics.
- Rich text writing experience with a Markdown toolbar, live preview, and HTML XSS sanitization (via Bleach).
- Automated test suite with 38 unit and integration tests using `pytest`.
- Production WSGI deployment readiness with PostgreSQL compatibility.

---

## 2. Main Features

### 🎨 Frontend & User Interface
- **Modern Homepage**: Displays published posts as cards with categories, publication dates, author badges, content previews, and "Read More" links.
- **Dynamic Navigation Bar**: Adapts based on authentication state:
  - *Logged-out visitors*: Home, Explore Blogs, Login, Register.
  - *Logged-in users*: Home, Explore Blogs, Dashboard, Create Post, Profile / Account dropdown, Logout.
  - *Mobile Responsive*: Smooth hamburger menu and fluid typography across all viewports.
- **Explore Hub (`/explore`)**: Browse curated categories with post counts, platform metrics, and recent articles.
- **Error Handling**: Custom error pages for `404 Not Found`, `403 Forbidden`, and `500 Server Error`.

### 📝 Post Publishing & Rich Text Editor
- **Markdown & Rich Text Toolbar**: Quick-insertion buttons for bold (`**text**`), italics (`*text*`), headings (`## H2`), quotes (`> quote`), code blocks, bullet lists, and links.
- **Client-Side Live Preview**: Instant tab toggle between "Write" and "Live Preview" before publishing.
- **XSS Protection**: Markdown rendered with `bleach` sanitization to prevent script injection while preserving safe formatting.

### 💬 Community Commenting System
- Logged-in users can add comments under any published article.
- Comments display author, timestamp, and content.
- Comment authors can edit or delete their own comments.
- Unauthorized users are prohibited from modifying or deleting others' comments (`403 Forbidden`).
- Empty comments are prevented via server-side validation.
- Unauthenticated visitors are prompted to log in to participate.

### 🔍 Search, Category Filtering & Sorting
- **SQLAlchemy Search**: Case-insensitive search across post titles, post content, and author usernames (`Post.title.ilike(...) | Post.content.ilike(...) | User.username.ilike(...)`).
- **Category Filter**: Filter posts by category slugs (e.g. Technology, Web Development, Programming, Artificial Intelligence, Career & Growth, Tutorials).
- **Sorting**: Switch between Newest First and Oldest First.
- **Combined Queries**: Seamlessly combine search queries, category filters, and sorting parameters.
- **Friendly Empty States**: Helpful prompts when no posts match search criteria with an option to reset filters.

### 📊 User Dashboard & Profiles
- **User Dashboard (`/auth/dashboard`)**: Author welcome banner, total post count, total comment count, responsive management table with edit/delete buttons, and quick "Create New Post" call-to-action. Users only manage their own posts.
- **User Profile (`/auth/profile/<username>`)**: Username, email, member since date, total articles published, and list of author's posts.

---

## 3. Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.12+** | Core programming language |
| **Flask 3.1** | Lightweight WSGI web application framework |
| **Flask-SQLAlchemy 3.1** | SQLAlchemy ORM integration |
| **Flask-Login 0.6** | User session management and route protection |
| **Flask-Migrate 4.1 & Alembic** | Database schema versioning and migrations |
| **Flask-WTF & WTForms 3.3** | Form rendering, CSRF protection, and validation |
| **Bleach 6.4** | HTML sanitization and XSS security |
| **Markdown 3.11** | Markdown parsing and formatting |
| **Bootstrap 5.3 & Icons** | Responsive UI styling, grid layouts, and icons |
| **Gunicorn & Waitress** | Production WSGI application servers |
| **pytest 9.2** | Automated testing suite |
| **python-dotenv 1.2** | Environment variable management |

---

## 4. Project Architecture

The application adopts the Flask **Application Factory Pattern** with modular **Blueprints**:

```
Blog/
│
├── .env.example              # Sample environment configuration
├── .gitignore                # Git exclusions (venv, instance, cache)
├── config.py                 # Multi-environment config (Dev, Test, Prod)
├── Procfile                  # Gunicorn deployment process
├── pytest.ini                # Pytest configuration and warning filters
├── requirements.txt          # Pinned project dependencies
├── run.py                    # Local development runner
├── seed.py                   # Database seeding script (demo users & posts)
├── wsgi.py                   # Production WSGI entry point
├── README.md                 # Project documentation
│
├── app/                      # Application Package
│   ├── __init__.py           # Application factory & extension initialization
│   ├── models.py             # User, Category, Post, and Comment ORM models
│   ├── forms.py              # WTForms forms for auth, posts, and comments
│   ├── utils.py              # HTML sanitization & plain text preview utilities
│   │
│   ├── blueprints/           # Modular route controllers
│   │   ├── auth/             # Login, register, logout, dashboard, profile
│   │   ├── blog/             # Post CRUD, comment CRUD, authorization
│   │   ├── main/             # Homepage, search, explore, category filters
│   │   └── errors/           # 403, 404, 500 error handlers
│   │
│   ├── static/               # Static assets
│   │   ├── css/style.css     # Modern custom styling & responsive adjustments
│   │   └── js/main.js        # Markdown toolbar, live preview, delete confirm
│   │
│   └── templates/            # Jinja2 HTML templates
│       ├── base.html         # Master layout & responsive navigation bar
│       ├── index.html        # Homepage with search, filter, and post cards
│       ├── explore.html      # Category explorer & platform metrics
│       ├── auth/             # Login, register, dashboard, profile templates
│       ├── blog/             # Post detail, create post, edit post, edit comment
│       └── errors/           # 403, 404, 500 custom error pages
│
├── migrations/               # Alembic database migrations
│   └── versions/             # Auto-generated migration scripts
│
└── tests/                    # Automated Pytest suite
    ├── conftest.py           # Test fixtures, client, in-memory DB
    ├── test_auth.py          # Authentication tests
    ├── test_blog.py          # Post CRUD & owner permissions tests
    ├── test_comments.py      # Comment CRUD & authorization tests
    ├── test_search_filter.py # Search, categories, and sorting tests
    ├── test_ui_and_security.py # XSS prevention, markdown, and views tests
    └── test_errors.py        # 404 and 403 error page tests
```

---

## 5. Database Models

```
   ┌────────────────┐            ┌────────────────┐
   │      User      │            │    Category    │
   ├────────────────┤            ├────────────────┤
   │ id (PK)        │            │ id (PK)        │
   │ username       │            │ name           │
   │ email          │            │ slug           │
   │ password_hash  │            │ description    │
   │ created_at     │            └───────┬────────┘
   └───────┬────────┘                    │ 1
           │ 1                           │
           │                             │ *
           │ *           *               │
     ┌─────┴───────────────┐             │
     │        Post         ├─────────────┘
     ├─────────────────────┤
     │ id (PK)             │
     │ title               │
     │ content             │
     │ created_at          │
     │ updated_at          │
     │ user_id (FK)        │
     │ category_id (FK)    │
     └──────────┬──────────┘
                │ 1
                │
                │ *
     ┌──────────┴──────────┐
     │       Comment       │
     ├─────────────────────┤
     │ id (PK)             │
     │ content             │
     │ created_at          │
     │ updated_at          │
     │ user_id (FK)        │
     │ post_id (FK)        │
     └─────────────────────┘
```

- **User**: Implements `UserMixin` with secure password hashing (`generate_password_hash` / `check_password_hash`).
- **Category**: Tracks unique names and slugs; auto-seeds standard technical and creative categories.
- **Post**: Linked to User and Category with cascade deletion for comments.
- **Comment**: Linked to User (author) and Post with timestamps and cascade deletion.

---

## 6. Installation Instructions

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### Step-by-Step Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd Blog
   ```

2. **Create and activate a virtual environment**:
   - On Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - On Linux/macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 7. Environment Configuration

Create a `.env` file in the project root directory by copying `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` to configure your settings:

```ini
# Flask Environment
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secure-random-secret-key-here

# Database URL
# SQLite default:
DATABASE_URL=sqlite:///instance/blog.db

# Or for PostgreSQL production:
# DATABASE_URL=postgresql://username:password@localhost:5432/blog_db
```

---

## 8. Database Migration Instructions

The project uses **Flask-Migrate** to manage database schema updates:

1. **Apply existing migrations**:
   ```bash
   flask db upgrade
   ```

2. **Seed the database with sample users and posts**:
   ```bash
   python seed.py
   ```
   *Demo accounts created:*
   - `alex@example.com` / `Password123!` (username: `alex_dev`)
   - `sarah@example.com` / `Password123!` (username: `sarah_codes`)

3. **To generate new migrations after model changes**:
   ```bash
   flask db migrate -m "Description of changes"
   flask db upgrade
   ```

---

## 9. Running the Application

### Development Server
Run the application with the development runner:

```bash
python run.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Production Server (Local Test)
Using Waitress (Cross-platform):
```bash
waitress-serve --listen=127.0.0.1:5000 wsgi:app
```

Using Gunicorn (Linux/macOS):
```bash
gunicorn wsgi:app --bind 0.0.0.0:5000
```

---



