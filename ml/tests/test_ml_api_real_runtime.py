import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.mark.integration
def test_real_ml_runtime_recommendation():

    with TestClient(app) as client:

        # --------------------------------------------------
        # Health
        # --------------------------------------------------

        health_response = client.get("/health")

        assert health_response.status_code == 200

        assert health_response.json() == {
            "status": "UP",
            "modelLoaded": True,
        }

        # --------------------------------------------------
        # Real recommendation
        # --------------------------------------------------

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

        # Rankings must be sequential.
        assert [
            movie["rank"]
            for movie in recommendations
        ] == [1, 2, 3, 4, 5]

        # No duplicate movies.
        movie_ids = [
            movie["movieId"]
            for movie in recommendations
        ]

        assert len(movie_ids) == len(set(movie_ids))

        # Hybrid scores must be valid.
        for movie in recommendations:

            assert 0.0 <= movie["score"] <= 1.0
            assert 0.0 <= movie["contentScore"] <= 1.0
            assert 0.0 <= movie["sentimentScore"] <= 1.0

            assert isinstance(
                movie["sentimentAvailable"],
                bool,
            )

        # Current Phase 4 / ML-runtime regression result.
        top_movie = recommendations[0]

        assert top_movie["movieId"] == 922
        assert top_movie["title"] == "Sunset Boulevard"