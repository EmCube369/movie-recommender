import pytest


@pytest.mark.parametrize(
    "payload",
    [
        # Missing required mlUserId
        {},

        # Invalid mlUserId values
        {
            "mlUserId": 0,
        },
        {
            "mlUserId": -1,
        },
        {
            "mlUserId": None,
        },
        {
            "mlUserId": "not-a-user",
        },

        # Invalid limit values
        {
            "mlUserId": 1,
            "limit": 0,
        },
        {
            "mlUserId": 1,
            "limit": -1,
        },
        {
            "mlUserId": 1,
            "limit": 51,
        },
        {
            "mlUserId": 1,
            "limit": None,
        },
        {
            "mlUserId": 1,
            "limit": "not-a-limit",
        },
    ],
)
def test_invalid_recommendation_requests(
    client,
    payload,
):

    response = client.post(
        "/api/v1/recommendations",
        json=payload,
    )

    assert response.status_code == 422


def test_empty_request_body(client):

    response = client.post(
        "/api/v1/recommendations",
    )

    assert response.status_code == 422


def test_wrong_request_body_type(client):

    response = client.post(
        "/api/v1/recommendations",
        json=[
            {
                "mlUserId": 1,
            }
        ],
    )

    assert response.status_code == 422


def test_minimum_valid_limit(client):

    response = client.post(
        "/api/v1/recommendations",
        json={
            "mlUserId": 1,
            "limit": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_maximum_valid_limit(client):

    response = client.post(
        "/api/v1/recommendations",
        json={
            "mlUserId": 1,
            "limit": 50,
        },
    )

    assert response.status_code == 200
    assert response.json()["count"] == 50