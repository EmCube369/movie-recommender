def test_health_when_model_loaded(client):

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "UP",
        "modelLoaded": True,
    }


def test_health_when_model_not_loaded(client):

    client.app.state.recommender = None

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "DOWN",
        "modelLoaded": False,
    }