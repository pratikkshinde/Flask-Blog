from app.models import User


def test_register_success(client, auth, app):
    """Test successful user registration."""
    response = auth.register(username='newuser', email='new@example.com', password='Password123!')
    assert response.status_code == 200
    assert b'Your account has been created successfully' in response.data

    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'new@example.com'
        assert user.check_password('Password123!')


def test_register_duplicate_email(client, auth):
    """Test that duplicate email registration is rejected."""
    auth.register(username='user1', email='shared@example.com', password='Password123!')
    response = auth.register(username='user2', email='shared@example.com', password='Password123!')
    assert b'An account with this email already exists' in response.data


def test_register_duplicate_username(client, auth):
    """Test that duplicate username registration is rejected."""
    auth.register(username='unique_name', email='user1@example.com', password='Password123!')
    response = auth.register(username='unique_name', email='user2@example.com', password='Password123!')
    assert b'This username is already taken' in response.data


def test_login_valid_credentials(client, auth, test_users):
    """Test login with valid email and password."""
    response = auth.login(email='alice@example.com', password='Password123!')
    assert response.status_code == 200
    assert b'Welcome back, alice!' in response.data
    assert b'Dashboard' in response.data
    assert b'Logout' in response.data


def test_login_invalid_password(client, auth, test_users):
    """Test login with incorrect password."""
    response = auth.login(email='alice@example.com', password='WrongPassword!')
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_login_nonexistent_user(client, auth):
    """Test login with an unregistered email."""
    response = auth.login(email='ghost@example.com', password='Password123!')
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_logout(client, auth, test_users):
    """Test logging out an authenticated session."""
    auth.login(email='alice@example.com', password='Password123!')
    response = auth.logout()
    assert response.status_code == 200
    assert b'You have been logged out successfully' in response.data
    assert b'Sign In' in response.data or b'Login' in response.data


def test_protected_routes_require_login(client):
    """Test that sensitive routes redirect unauthenticated visitors to login."""
    endpoints = [
        '/posts/create',
        '/auth/dashboard',
        '/auth/profile',
        '/posts/1/edit',
    ]
    for url in endpoints:
        response = client.get(url, follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']
