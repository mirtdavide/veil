def test_security_headers_present_on_normal_endpoint(client):
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "content-security-policy" in response.headers


def test_docs_page_excluded_from_restrictive_csp(client):
    response = client.get("/docs")
    assert "content-security-policy" not in response.headers
