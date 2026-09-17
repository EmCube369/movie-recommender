import pytest
from fastapi.testclient import TestClient

import api.main as api_main


class FakeHybridRecommender:
    """
    Lightweight replacement for HybridRecommender.

    API tests should test the FastAPI HTTP layer without
    loading the real PyTorch model, sparse content matrices,
    sentiment data, and user-history artifacts.
    """

    def recommend_payload(
        self,
        user_id: int,
        top_n: int = 10,
        positive_threshold: float = 4.0,
    ) -> dict:

        # Used later for unknown-user tests.
        if user_id == 999999:
            raise KeyError(
                f"Unknown hybrid userId: {user_id}"
            )

        # Used later for recommender ValueError tests.
        if user_id == 888888:
            raise ValueError(
                f"User {user_id} has no ratings >= "
                f"{positive_threshold} for building "
                "a content profile."
            )

        recommendations = []

        for rank in range(1, top_n + 1):

            recommendations.append(
                {
                    "rank": rank,
                    "movieId": 1000 + rank,
                    "title": f"Test Movie {rank}",
                    "releaseYear": 2000 + rank,
                    "genres": ["Drama"],
                    "score": round(
                        0.90 - rank * 0.01,
                        6,
                    ),
                    "cfScore": round(
                        0.80 - rank * 0.01,
                        6,
                    ),
                    "contentScore": round(
                        0.70 - rank * 0.01,
                        6,
                    ),
                    "sentimentScore": 0.50,
                    "sentimentAvailable": False,
                }
            )

        return {
            "schemaVersion": "1.0",
            "userId": int(user_id),
            "count": len(recommendations),
            "recommendations": recommendations,
        }


@pytest.fixture
def client(monkeypatch):
    """
    FastAPI TestClient using a fake recommender.

    The real HybridRecommender is replaced before the
    application's lifespan starts.
    """

    monkeypatch.setattr(
        api_main,
        "HybridRecommender",
        FakeHybridRecommender,
    )

    with TestClient(api_main.app) as test_client:
        yield test_client