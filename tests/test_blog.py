from app import db
from app.models import Post, Category


def test_create_post(client, auth, test_users, app):
    """Test creating a new blog post as an authenticated user."""
    auth.login(email='alice@example.com', password='Password123!')

    with app.app_context():
        category = Category.query.first()
        cat_id = category.id

    response = client.post('/posts/create', data={
        'title': 'Test Blog Article by Alice',
        'category_id': cat_id,
        'content': 'This is a detailed post content with **bold** text and code snippet.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your blog post has been published successfully!' in response.data
    assert b'Test Blog Article by Alice' in response.data

    with app.app_context():
        post = Post.query.filter_by(title='Test Blog Article by Alice').first()
        assert post is not None
        assert post.author.username == 'alice'


def test_view_post_detail(client, test_post, app):
    """Test viewing a post's detail page."""
    response = client.get(f'/posts/{test_post}')
    assert response.status_code == 200
    assert b"Alice&#39;s First Post" in response.data or b"Alice's First Post" in response.data
    assert b'alice' in response.data
    assert b'Python architecture' in response.data
    assert b'Comments' in response.data


def test_edit_own_post(client, auth, test_users, test_post, app):
    """Test owner can successfully edit their post."""
    auth.login(email='alice@example.com', password='Password123!')

    with app.app_context():
        category = Category.query.first()
        cat_id = category.id

    response = client.post(f'/posts/{test_post}/edit', data={
        'title': 'Updated Post Title by Alice',
        'category_id': cat_id,
        'content': 'Updated content with improved explanations.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your blog post has been updated successfully!' in response.data
    assert b'Updated Post Title by Alice' in response.data

    with app.app_context():
        post = db.session.get(Post, test_post)
        assert post.title == 'Updated Post Title by Alice'


def test_prevent_unauthorized_post_edit(client, auth, test_users, test_post):
    """Test that another user (bob) cannot edit alice's post (must return 403 Forbidden)."""
    # Login as bob
    auth.login(email='bob@example.com', password='Password123!')

    # Try to access edit page
    response = client.get(f'/posts/{test_post}/edit')
    assert response.status_code == 403

    # Try to submit an edit
    response = client.post(f'/posts/{test_post}/edit', data={
        'title': 'Hacked Title',
        'category_id': 1,
        'content': 'Attempting unauthorized modification.'
    })
    assert response.status_code == 403


def test_delete_own_post(client, auth, test_users, test_post, app):
    """Test owner can delete their post."""
    auth.login(email='alice@example.com', password='Password123!')

    response = client.post(f'/posts/{test_post}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Blog post has been deleted successfully' in response.data

    with app.app_context():
        post = db.session.get(Post, test_post)
        assert post is None


def test_prevent_unauthorized_post_delete(client, auth, test_users, test_post, app):
    """Test that another user cannot delete alice's post (must return 403 Forbidden)."""
    # Login as bob
    auth.login(email='bob@example.com', password='Password123!')

    response = client.post(f'/posts/{test_post}/delete')
    assert response.status_code == 403

    with app.app_context():
        post = db.session.get(Post, test_post)
        assert post is not None


def test_user_dashboard_only_shows_own_posts(client, auth, test_users, test_post, app):
    """Test that dashboard only displays the current user's posts."""
    # Create a post for bob as well
    with app.app_context():
        category = Category.query.first()
        bobs_post = Post(
            title="Bob's Private Post",
            content="Only bob should see this in his dashboard.",
            category_id=category.id,
            user_id=test_users['bob_id']
        )
        db.session.add(bobs_post)
        db.session.commit()

    # Login as alice
    auth.login(email='alice@example.com', password='Password123!')
    response = client.get('/auth/dashboard')
    assert response.status_code == 200
    assert b"Alice&#39;s First Post" in response.data or b"Alice's First Post" in response.data
    assert b"Bob&#39;s Private Post" not in response.data and b"Bob's Private Post" not in response.data
