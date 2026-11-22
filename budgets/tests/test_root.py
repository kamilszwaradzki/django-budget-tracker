def test_root_redirects_to_api_root(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.url == "/api/"


def test_api_root_lists_endpoints_without_login(api_client):
    response = api_client.get("/api/")
    assert response.status_code == 200
    assert response.data["transactions"].endswith("/api/transactions/")
    assert response.data["categories"].endswith("/api/categories/")
