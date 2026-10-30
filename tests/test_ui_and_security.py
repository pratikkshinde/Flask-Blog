from app.utils import render_markdown_safe, get_plain_summary
from app.models import Category


def test_markdown_sanitization_xss_protection():
    """Verify that malicious script tags and inline handlers are neutralized."""
    # 1. Script tag injection: tags must be stripped so no execution occurs
    malicious_script = "# Safe Header\n<script>alert('attack')</script>\nNormal text."
    rendered = render_markdown_safe(malicious_script)
    assert '<script>' not in str(rendered)
    assert '</script>' not in str(rendered)
    assert '<script' not in str(rendered)
    assert 'Safe Header' in str(rendered)

    # 2. Onerror handler in img or svg
    malicious_event = 'Text before <img src="invalid.jpg" onerror="alert(\'xss\')"> text after'
    rendered_event = render_markdown_safe(malicious_event)
    assert 'onerror' not in str(rendered_event)

    # 3. JavaScript URL scheme in markdown link
    malicious_link = '[Click Here](javascript:alert("hacked"))'
    rendered_link = render_markdown_safe(malicious_link)
    assert 'javascript:' not in str(rendered_link)


def test_markdown_safe_tags_allowed():
    """Verify standard markdown elements render correctly."""
    md = """
## Architecture
Here is a list of features:
- **Bold feature**
- *Italic note*
- `code snippet`

> A wise quote

```python
def hello():
    print("world")
```
"""
    rendered = render_markdown_safe(md)
    html = str(rendered)
    assert '<h2>Architecture</h2>' in html
    assert '<strong>Bold feature</strong>' in html
    assert '<em>Italic note</em>' in html
    assert '<code>code snippet</code>' in html
    assert '<blockquote>' in html
    assert '<pre><code' in html


def test_plain_summary_helper():
    """Verify summary extraction strips formatting and limits length."""
    text = "## Big Title\nThis is **bold** and *italic* text with a [link](https://example.com)."
    summary = get_plain_summary(text, length=30)
    assert "##" not in summary
    assert "**" not in summary
    assert "http" not in summary
    assert len(summary) <= 35


def test_explore_page(client, app):
    """Test explore page loads with categories and stats."""
    response = client.get('/explore')
    assert response.status_code == 200
    assert b'Explore Topics &amp; Categories' in response.data or b'Explore Topics & Categories' in response.data
    assert b'Published Articles' in response.data


def test_category_direct_route(client, app):
    """Test viewing posts by category slug direct route."""
    response = client.get('/category/technology')
    assert response.status_code == 200
    assert b'Category: Technology' in response.data

    # Non-existent category slug
    response_404 = client.get('/category/non-existent-category-slug-123')
    assert response_404.status_code == 404


def test_profile_views(client, auth, test_users):
    """Test viewing user profile."""
    # View public profile of alice
    response = client.get('/auth/profile/alice')
    assert response.status_code == 200
    assert b'alice' in response.data
    assert b'Published Stories' in response.data

    # View own profile when authenticated
    auth.login(email='alice@example.com', password='Password123!')
    response_own = client.get('/auth/profile')
    assert response_own.status_code == 200
    assert b'alice' in response_own.data
    assert b'alice@example.com' in response_own.data

    # View non-existent user profile
    response_404 = client.get('/auth/profile/ghost_user_1234')
    assert response_404.status_code == 404


def test_custom_403_page_content(client, auth, test_users, test_post):
    """Test that custom 403 page renders with proper message and status code."""
    auth.login(email='bob@example.com', password='Password123!')
    response = client.get(f'/posts/{test_post}/edit')
    assert response.status_code == 403
    assert b'403' in response.data
    assert b'Access Forbidden' in response.data
    assert b'Return Home' in response.data
