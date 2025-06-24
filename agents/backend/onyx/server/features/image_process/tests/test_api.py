def test_analyze_image(client):
    payload = {"image_url": "https://example.com/image.jpg"}
    response = client.post("/api/image_process/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["labels"] == ["example_label"]
    assert data["confidence_scores"]["example_label"] == 0.99
    assert data["ocr_text"] == "Texto de ejemplo extraído por OCR"
    assert data["faces_detected"] == 0
    assert data["objects"] == []
    assert "note" in data["metadata"] 