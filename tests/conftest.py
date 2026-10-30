import pytest
from app import create_app, db
from app.models import User, Category, Post, Comment


@pytest.fixture
def app():
    """Create and configure a clean application instance for each test."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        Category.seed_defaults()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner."""
    return app.test_cli_runner()


class AuthActions:
    """Helper methods for authentication actions in tests."""
    def __init__(self, client):
        self._client = client

    def register(self, username='testuser', email='test@example.com', password='Password123!', confirm_password='Password123!'):
        return self._client.post('/auth/register', data={
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': confirm_password
        }, follow_redirects=True)

    def login(self, email='test@example.com', password='Password123!'):
        return self._client.post('/auth/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True)


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def test_users(app):
    """Pre-create two test users."""
    with app.app_context():
        u1 = User(username='alice', email='alice@example.com')
        u1.set_password('Password123!')

        u2 = User(username='bob', email='bob@example.com')
        u2.set_password('Password123!')

        db.session.add_all([u1, u2])
        db.session.commit()

        return {
            'alice_id': u1.id,
            'bob_id': u2.id
        }


@pytest.fixture
def test_post(app, test_users):
    """Pre-create a test post owned by alice."""
    with app.app_context():
        category = Category.query.first()
        post = Post(
            title="Alice's First Post",
            content="This is an article written by Alice about Python architecture.",
            category_id=category.id,
            user_id=test_users['alice_id']
        )
        db.session.add(post)
        db.session.commit()
        return post.id
