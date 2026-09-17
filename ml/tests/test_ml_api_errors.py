def test_unknown_user_returns_404(client):

    response = client.post(
        "/api/v1/recommendations",
        json={
            "mlUserId": 999999,
            "limit": 5,
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data
    assert "Unknown hybrid userId" in data["detail"]


def test_recommender_value_error_returns_404(client):

    response = client.post(
        "/api/v1/recommendations",
        json={
            "mlUserId": 888888,
            "limit": 5,
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data
    assert "no ratings" in data["detail"]


def test_model_unavailable_returns_503(client):

    client.app.state.recommender = None

    response = client.post(
        "/api/v1/recommendations",
        json={
            "mlUserId": 1,
            "limit": 5,
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": "Recommendation model is not available."
    }