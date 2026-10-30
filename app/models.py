from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app.utils import render_markdown_safe, get_plain_summary


def utc_now():
    """Return timezone-naive UTC datetime for compatibility with database backends."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def post_count(self) -> int:
        return self.posts.count()

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200), nullable=True)

    # Relationships
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    @classmethod
    def seed_defaults(cls):
        """Seed default categories if none exist."""
        defaults = [
            ("Technology", "technology", "Gadgets, computing, software engineering, and industry news."),
            ("Web Development", "web-development", "Frontend, backend, APIs, and modern web frameworks."),
            ("Programming", "programming", "Python, clean code, algorithms, and software design."),
            ("Artificial Intelligence", "artificial-intelligence", "Machine learning, LLMs, neural networks, and AI tools."),
            ("Career & Growth", "career-growth", "Career paths, interview prep, productivity, and soft skills."),
            ("Tutorials", "tutorials", "Hands-on step-by-step guides and walkthroughs."),
            ("General", "general", "General discussions, lifestyle, and miscellaneous topics.")
        ]
        created = False
        for name, slug, desc in defaults:
            existing = cls.query.filter_by(slug=slug).first()
            if not existing:
                cat = cls(name=name, slug=slug, description=desc)
                db.session.add(cat)
                created = True
        if created:
            db.session.commit()

    def __repr__(self):
        return f'<Category {self.name}>'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)

    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def html_content(self):
        """Render markdown to sanitized HTML."""
        return render_markdown_safe(self.content)

    def summary(self, length: int = 160) -> str:
        """Return plain text preview."""
        return get_plain_summary(self.content, length=length)

    @property
    def comment_count(self) -> int:
        return self.comments.count()

    def __repr__(self):
        return f'<Post {self.title}>'


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)

    def __repr__(self):
        return f'<Comment {self.id} on Post {self.post_id}>'
