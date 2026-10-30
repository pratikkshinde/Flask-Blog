def test_404_error_page(client):
    """Test custom 404 Not Found error page."""
    response = client.get('/non-existent-page-url-xyz')
    assert response.status_code == 404
    assert b'404' in response.data
    assert b'Page Not Found' in response.data
    assert b'Return Home' in response.data
