from app import db
from app.models import Comment


def test_add_comment(client, auth, test_users, test_post, app):
    """Test adding a comment as an authenticated user."""
    auth.login(email='bob@example.com', password='Password123!')

    response = client.post(f'/posts/{test_post}', data={
        'content': 'This is a great tutorial, Alice! Really helped me understand.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your comment has been added successfully!' in response.data
    assert b'This is a great tutorial, Alice!' in response.data
    assert b'bob' in response.data

    with app.app_context():
        comment = Comment.query.filter_by(content='This is a great tutorial, Alice! Really helped me understand.').first()
        assert comment is not None
        assert comment.author.username == 'bob'
        assert comment.post_id == test_post


def test_prevent_empty_comment(client, auth, test_users, test_post, app):
    """Test that empty comments are rejected by validation."""
    auth.login(email='bob@example.com', password='Password123!')

    response = client.post(f'/posts/{test_post}', data={
        'content': '   '
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Comment content cannot be empty' in response.data

    with app.app_context():
        assert Comment.query.count() == 0


def test_unauthenticated_comment_redirects_to_login(client, test_post):
    """Test that unauthenticated visitor attempting to post comment is redirected to login."""
    response = client.post(f'/posts/{test_post}', data={
        'content': 'Anonymous comment'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_edit_own_comment(client, auth, test_users, test_post, app):
    """Test user can edit their own comment."""
    with app.app_context():
        comment = Comment(
            content="Original comment by bob",
            user_id=test_users['bob_id'],
            post_id=test_post
        )
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id

    auth.login(email='bob@example.com', password='Password123!')

    response = client.post(f'/posts/comments/{comment_id}/edit', data={
        'content': 'Updated edited comment by bob'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Comment updated successfully.' in response.data
    assert b'Updated edited comment by bob' in response.data

    with app.app_context():
        updated = db.session.get(Comment, comment_id)
        assert updated.content == 'Updated edited comment by bob'


def test_prevent_unauthorized_comment_edit(client, auth, test_users, test_post, app):
    """Test that alice cannot edit bob's comment (returns 403 Forbidden)."""
    with app.app_context():
        comment = Comment(
            content="Original comment by bob",
            user_id=test_users['bob_id'],
            post_id=test_post
        )
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id

    # Login as alice
    auth.login(email='alice@example.com', password='Password123!')

    # Try GET edit page
    response = client.get(f'/posts/comments/{comment_id}/edit')
    assert response.status_code == 403

    # Try POST update
    response = client.post(f'/posts/comments/{comment_id}/edit', data={
        'content': 'Attempted unauthorized edit by alice'
    })
    assert response.status_code == 403


def test_delete_own_comment(client, auth, test_users, test_post, app):
    """Test user can delete their own comment."""
    with app.app_context():
        comment = Comment(
            content="To be deleted by bob",
            user_id=test_users['bob_id'],
            post_id=test_post
        )
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id

    auth.login(email='bob@example.com', password='Password123!')

    response = client.post(f'/posts/comments/{comment_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Comment deleted successfully.' in response.data

    with app.app_context():
        assert db.session.get(Comment, comment_id) is None


def test_prevent_unauthorized_comment_delete(client, auth, test_users, test_post, app):
    """Test that alice cannot delete bob's comment (returns 403 Forbidden)."""
    with app.app_context():
        comment = Comment(
            content="Protected comment by bob",
            user_id=test_users['bob_id'],
            post_id=test_post
        )
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id

    # Login as alice
    auth.login(email='alice@example.com', password='Password123!')

    response = client.post(f'/posts/comments/{comment_id}/delete')
    assert response.status_code == 403

    with app.app_context():
        assert db.session.get(Comment, comment_id) is not None
