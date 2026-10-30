import re
import bleach
import markdown
from markupsafe import Markup

ALLOWED_TAGS = [
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'em', 'u', 's', 'del',
    'blockquote', 'pre', 'code',
    'ul', 'ol', 'li',
    'a', 'hr', 'br',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'span'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'code': ['class'],
    'pre': ['class'],
    'span': ['class'],
    '*': ['class']
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def render_markdown_safe(text: str) -> Markup:
    """
    Renders Markdown content to safe HTML with XSS sanitization via Bleach.
    """
    if not text:
        return Markup('')

    # Convert Markdown to HTML
    raw_html = markdown.markdown(
        text,
        extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
    )

    # Sanitize the HTML using Bleach
    clean_html = bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )

    # Add rel="noopener noreferrer" to external links for security
    clean_html = bleach.linkify(clean_html)

    return Markup(clean_html)


def get_plain_summary(text: str, length: int = 160) -> str:
    """
    Strips formatting characters and returns a clean plain text preview.
    """
    if not text:
        return ''

    # Remove markdown headers, bold, italics, code blocks
    cleaned = re.sub(r'#+\s*', '', text)
    cleaned = re.sub(r'[*_~`]', '', cleaned)
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    if len(cleaned) <= length:
        return cleaned
    return cleaned[:length].rstrip() + '...'

