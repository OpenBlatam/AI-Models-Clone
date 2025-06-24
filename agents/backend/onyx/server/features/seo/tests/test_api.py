def test_scrape(client):
    payload = {"url": "https://ejemplo.com"}
    response = client.post("/seo/scrape", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Ejemplo"
    assert "description" in data["data"] 