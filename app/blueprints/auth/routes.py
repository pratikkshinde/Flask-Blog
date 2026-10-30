from urllib.parse import urlparse
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.blueprints.auth import auth_bp
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post


def is_safe_url(target):
    """Ensure redirect URL stays within the application."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('', 'http', 'https') and ref_url.netloc == test_url.netloc or not test_url.netloc


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            if not next_page or not is_safe_url(next_page):
                next_page = url_for('auth.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard displaying user's posts, stats, and management buttons."""
    page = request.args.get('page', 1, type=int)
    posts_query = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc())
    posts = posts_query.all()
    total_posts = len(posts)

    return render_template(
        'auth/dashboard.html',
        title='My Dashboard',
        user=current_user,
        posts=posts,
        total_posts=total_posts
    )


@auth_bp.route('/profile')
@login_required
def profile():
    """Current user profile."""
    return user_profile(current_user.username)


@auth_bp.route('/profile/<username>')
def user_profile(username):
    """View user profile and published posts."""
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    total_posts = len(posts)

    return render_template(
        'auth/profile.html',
        title=f'{user.username}\'s Profile',
        user=user,
        posts=posts,
        total_posts=total_posts
    )
