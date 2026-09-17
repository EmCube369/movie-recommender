def test_recommendations_success(client):

    response = client.post(
        "/api/v1/recommendations",
        json={
            "mlUserId": 1,
            "limit": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["schemaVersion"] == "1.0"
    assert data["mlUserId"] == 1
    assert data["count"] == 5

    recommendations = data["recommendations"]

    assert len(recommendations) == 5

    assert [
        movie["rank"]
        for movie in recommendations
    ] == [1, 2, 3, 4, 5]


def test_recommendation_fields(client):

    response = client.post(
        "/api/v1/recommendations",
        json={
            "mlUserId": 1,
            "limit": 1,
        },
    )

    assert response.status_code == 200

    movie = response.json()[
        "recommendations"
    ][0]

    expected_fields = {
        "rank",
        "movieId",
        "title",
        "releaseYear",
        "genres",
        "score",
        "cfScore",
        "contentScore",
        "sentimentScore",
        "sentimentAvailable",
    }

    assert set(movie.keys()) == expected_fields


def test_default_recommendation_limit(client):

    response = client.post(
        "/api/v1/recommendations",
        json={
            "mlUserId": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 10
    assert len(data["recommendations"]) == 10