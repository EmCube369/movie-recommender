def test_root_endpoint(client):

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "service": "Movie Recommender ML API",
        "version": "1.0.0",
        "status": "running",
    }