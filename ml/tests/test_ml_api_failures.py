import pytest
from fastapi.testclient import TestClient

import api.main as api_main


class RuntimeFailingRecommender:
    def recommend_payload(
        self,
        user_id: int,
        top_n: int = 10,
        positive_threshold: float = 4.0,
    ):
        raise RuntimeError(
            "Unexpected recommendation failure"
        )


class StartupFailingRecommender:
    def __init__(self):
        raise RuntimeError(
            "Model initialization failed"
        )


class InvalidPayloadRecommender:
    def recommend_payload(
        self,
        user_id: int,
        top_n: int = 10,
        positive_threshold: float = 4.0,
    ):
        # Deliberately malformed internal result.
        return {
            "userId": user_id,
            "count": 0,
            "recommendations": [],
        }


def test_unexpected_recommender_failure_returns_500(
    monkeypatch,
):

    monkeypatch.setattr(
        api_main,
        "HybridRecommender",
        RuntimeFailingRecommender,
    )

    with TestClient(
        api_main.app,
        raise_server_exceptions=False,
    ) as client:

        response = client.post(
            "/api/v1/recommendations",
            json={
                "mlUserId": 1,
                "limit": 5,
            },
        )

    assert response.status_code == 500


def test_startup_failure_prevents_api_start(
    monkeypatch,
):

    monkeypatch.setattr(
        api_main,
        "HybridRecommender",
        StartupFailingRecommender,
    )

    with pytest.raises(
        RuntimeError,
        match="Model initialization failed",
    ):

        with TestClient(api_main.app):
            pass


def test_invalid_internal_payload_returns_500(
    monkeypatch,
):

    monkeypatch.setattr(
        api_main,
        "HybridRecommender",
        InvalidPayloadRecommender,
    )

    with TestClient(
        api_main.app,
        raise_server_exceptions=False,
    ) as client:

        response = client.post(
            "/api/v1/recommendations",
            json={
                "mlUserId": 1,
                "limit": 5,
            },
        )

    assert response.status_code == 500