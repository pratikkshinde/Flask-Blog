from flask import render_template, request, current_app
from sqlalchemy import or_
from app.blueprints.main import main_bp
from app.models import Post, Category, User
from app.forms import SearchForm


@main_bp.route('/')
@main_bp.route('/api/index')
@main_bp.route('/api')
def index():
    """
    Homepage displaying published blog posts with search, category filtering,
    and sorting options.
    """
    # Ensure default categories are seeded
    try:
        Category.seed_defaults()
    except Exception:
        pass

    q = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'newest').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 9)

    # Base query joined with User and Category
    query = Post.query.join(User, Post.user_id == User.id).join(Category, Post.category_id == Category.id)

    # Search filter: Title, Content, Author Username
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Post.title.ilike(search_pattern),
                Post.content.ilike(search_pattern),
                User.username.ilike(search_pattern)
            )
        )

    # Category filter
    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter(Post.category_id == selected_category.id)

    # Sorting
    if sort == 'oldest':
        query = query.order_by(Post.created_at.asc())
    else:
        sort = 'newest'
        query = query.order_by(Post.created_at.desc())

    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items

    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'index.html',
        title='Home - Latest Stories & Insights',
        posts=posts,
        pagination=pagination,
        categories=categories,
        selected_category=selected_category,
        category_slug=category_slug,
        q=q,
        sort=sort
    )


@main_bp.route('/explore')
@main_bp.route('/api/index/explore')
@main_bp.route('/api/explore')
def explore():
    """Explore all topics, featured categories, and trending discussions."""
    try:
        Category.seed_defaults()
    except Exception:
        pass

    categories = Category.query.order_by(Category.name.asc()).all()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(6).all()
    total_posts = Post.query.count()
    total_authors = User.query.count()

    return render_template(
        'explore.html',
        title='Explore Blogs & Topics',
        categories=categories,
        recent_posts=recent_posts,
        total_posts=total_posts,
        total_authors=total_authors
    )


@main_bp.route('/category/<slug>')
def category_posts(slug):
    """View posts under a specific category."""
    category = Category.query.filter_by(slug=slug).first_or_404()
    sort = request.args.get('sort', 'newest').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 9)

    query = Post.query.filter_by(category_id=category.id)
    if sort == 'oldest':
        query = query.order_by(Post.created_at.asc())
    else:
        sort = 'newest'
        query = query.order_by(Post.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items
    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'index.html',
        title=f'Category: {category.name}',
        posts=posts,
        pagination=pagination,
        categories=categories,
        selected_category=category,
        category_slug=category.slug,
        q='',
        sort=sort
    )

