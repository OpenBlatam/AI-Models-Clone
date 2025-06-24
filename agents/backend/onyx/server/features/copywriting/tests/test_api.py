def test_generate_copywriting(client):
    payload = {
        "product_description": "Zapatos deportivos de alta gama",
        "target_platform": "Instagram",
        "tone": "Inspirador",
        "target_audience": "Jóvenes activos",
        "key_points": ["Comodidad", "Estilo", "Durabilidad"]
    }
    response = client.post("/copywriting/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["headline"].startswith("Copy para")
    assert "Texto generado" in data["primary_text"]
    assert "#ejemplo" in data["hashtags"]
    assert "llamativas" in data["platform_tips"] 