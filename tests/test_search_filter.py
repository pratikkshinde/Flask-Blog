from datetime import datetime, timedelta, timezone
from app import db
from app.models import Post, Category, User


def create_search_fixtures(app):
    """Seed posts with diverse titles, content, categories, and authors."""
    with app.app_context():
        u1 = User(username='pythonista', email='py@example.com')
        u1.set_password('Pass123!')
        u2 = User(username='devops_guru', email='guru@example.com')
        u2.set_password('Pass123!')
        db.session.add_all([u1, u2])
        db.session.commit()

        cat_web = Category.query.filter_by(slug='web-development').first()
        cat_ai = Category.query.filter_by(slug='artificial-intelligence').first()

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        p1 = Post(
            title="Async Architecture in Python",
            content="Learn asynchronous programming and event loops.",
            created_at=now - timedelta(days=2),
            user_id=u1.id,
            category_id=cat_web.id
        )

        p2 = Post(
            title="Kubernetes for Developers",
            content="Deploying microservices and managing pods in production.",
            created_at=now - timedelta(days=1),
            user_id=u2.id,
            category_id=cat_web.id
        )

        p3 = Post(
            title="Deep Learning with PyTorch",
            content="Building neural networks and transformer models.",
            created_at=now,
            user_id=u1.id,
            category_id=cat_ai.id
        )

        db.session.add_all([p1, p2, p3])
        db.session.commit()


def test_search_by_title(client, app):
    """Test searching posts by title."""
    create_search_fixtures(app)

    response = client.get('/?q=Async')
    assert response.status_code == 200
    assert b'Async Architecture in Python' in response.data
    assert b'Kubernetes for Developers' not in response.data
    assert b'Deep Learning with PyTorch' not in response.data


def test_search_by_content(client, app):
    """Test searching posts by keywords in content."""
    create_search_fixtures(app)

    response = client.get('/?q=transformer')
    assert response.status_code == 200
    assert b'Deep Learning with PyTorch' in response.data
    assert b'Kubernetes for Developers' not in response.data


def test_search_by_username(client, app):
    """Test searching posts by author username."""
    create_search_fixtures(app)

    response = client.get('/?q=devops_guru')
    assert response.status_code == 200
    assert b'Kubernetes for Developers' in response.data
    assert b'Async Architecture in Python' not in response.data


def test_filter_by_category(client, app):
    """Test filtering posts by category slug."""
    create_search_fixtures(app)

    response = client.get('/?category=artificial-intelligence')
    assert response.status_code == 200
    assert b'Deep Learning with PyTorch' in response.data
    assert b'Async Architecture in Python' not in response.data
    assert b'Kubernetes for Developers' not in response.data


def test_sorting_newest_and_oldest(client, app):
    """Test sorting order: newest vs oldest."""
    create_search_fixtures(app)

    # Newest first: Deep Learning (day 0) should appear before Async (day -2)
    response_newest = client.get('/?sort=newest')
    assert response_newest.status_code == 200
    idx_p3 = response_newest.data.find(b'Deep Learning with PyTorch')
    idx_p1 = response_newest.data.find(b'Async Architecture in Python')
    assert idx_p3 < idx_p1

    # Oldest first: Async (day -2) should appear before Deep Learning (day 0)
    response_oldest = client.get('/?sort=oldest')
    assert response_oldest.status_code == 200
    idx_p1_old = response_oldest.data.find(b'Async Architecture in Python')
    idx_p3_old = response_oldest.data.find(b'Deep Learning with PyTorch')
    assert idx_p1_old < idx_p3_old


def test_combined_search_category_and_sort(client, app):
    """Test combining search query, category filter, and sorting."""
    create_search_fixtures(app)

    # Search 'Python' in 'web-development'
    response = client.get('/?q=Python&category=web-development&sort=newest')
    assert response.status_code == 200
    assert b'Async Architecture in Python' in response.data
    # PyTorch has 'Python' in author but its category is AI, not web-development
    assert b'Deep Learning with PyTorch' not in response.data


def test_empty_search_query(client, app):
    """Test that empty search returns all posts without crashing."""
    create_search_fixtures(app)

    response = client.get('/?q=')
    assert response.status_code == 200
    assert b'Async Architecture in Python' in response.data
    assert b'Kubernetes for Developers' in response.data
    assert b'Deep Learning with PyTorch' in response.data


def test_no_results_found(client, app):
    """Test friendly message when query matches zero posts."""
    create_search_fixtures(app)

    response = client.get('/?q=UnmatchedKeywordXYZ123')
    assert response.status_code == 200
    assert b'No Matching Blog Posts Found' in response.data

