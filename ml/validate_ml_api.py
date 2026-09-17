import json
import math
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"

KNOWN_USER_ID = 1
SPARSE_KNOWN_USER_ID = 7382
UNKNOWN_USER_ID = 999_999_999

REQUEST_TIMEOUT_SECONDS = 180


# =====================================================================
# HTTP HELPERS
# =====================================================================

def request_json(path, method="GET", payload=None):
    url = f"{BASE_URL}{path}"

    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        url=url,
        data=data,
        headers=headers,
        method=method,
    )

    start = time.perf_counter()

    try:
        with urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:
            body = response.read().decode("utf-8")
            elapsed_ms = (time.perf_counter() - start) * 1000

            return (
                response.status,
                json.loads(body),
                elapsed_ms,
            )

    except HTTPError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        body = exc.read().decode("utf-8")

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = body

        return (
            exc.code,
            parsed,
            elapsed_ms,
        )

    except URLError as exc:
        raise RuntimeError(
            f"Could not connect to ML API at {BASE_URL}: {exc}"
        ) from exc


# =====================================================================
# TEST HELPERS
# =====================================================================

passed = 0
failed = 0


def check(condition, message):
    global passed, failed

    if condition:
        print(f"PASS  - {message}")
        passed += 1
    else:
        print(f"FAIL  - {message}")
        failed += 1


def section(title):
    print()
    print("=" * 90)
    print(title)
    print("=" * 90)


def is_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


# =====================================================================
# RESPONSE VALIDATION
# =====================================================================

def validate_recommendation_payload(
    payload,
    expected_user_id,
    expected_count=None,
):
    check(
        isinstance(payload, dict),
        "Response is a JSON object",
    )

    if not isinstance(payload, dict):
        return

    required_top_level = {
        "schemaVersion",
        "mlUserId",
        "count",
        "recommendations",
    }

    check(
        required_top_level.issubset(payload.keys()),
        "Top-level recommendation fields are present",
    )

    check(
        payload.get("schemaVersion") == "1.0",
        "schemaVersion is 1.0",
    )

    check(
        payload.get("mlUserId") == expected_user_id,
        f"mlUserId is {expected_user_id}",
    )

    count = payload.get("count")
    recommendations = payload.get("recommendations")

    check(
        isinstance(count, int),
        "count is an integer",
    )

    check(
        isinstance(recommendations, list),
        "recommendations is a list",
    )

    if not isinstance(recommendations, list):
        return

    check(
        count == len(recommendations),
        "count matches recommendations length",
    )

    if expected_count is not None:
        check(
            count == expected_count,
            f"Returned recommendation count is {expected_count}",
        )

    required_movie_fields = {
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

    movie_ids = []

    for expected_rank, movie in enumerate(
        recommendations,
        start=1,
    ):
        check(
            isinstance(movie, dict),
            f"Recommendation {expected_rank} is an object",
        )

        if not isinstance(movie, dict):
            continue

        check(
            required_movie_fields.issubset(movie.keys()),
            f"Recommendation {expected_rank} has all required fields",
        )

        check(
            movie.get("rank") == expected_rank,
            f"Recommendation {expected_rank} rank is correct",
        )

        movie_id = movie.get("movieId")

        check(
            isinstance(movie_id, int)
            and not isinstance(movie_id, bool),
            f"Recommendation {expected_rank} movieId is an integer",
        )

        movie_ids.append(movie_id)

        check(
            isinstance(movie.get("title"), str),
            f"Recommendation {expected_rank} title is a string",
        )

        release_year = movie.get("releaseYear")

        check(
            release_year is None
            or (
                isinstance(release_year, int)
                and not isinstance(release_year, bool)
            ),
            f"Recommendation {expected_rank} releaseYear is valid",
        )

        genres = movie.get("genres")

        check(
            isinstance(genres, list)
            and all(isinstance(x, str) for x in genres),
            f"Recommendation {expected_rank} genres are valid",
        )

        for score_name in (
            "score",
            "cfScore",
            "contentScore",
            "sentimentScore",
        ):
            score = movie.get(score_name)

            check(
                is_number(score),
                (
                    f"Recommendation {expected_rank} "
                    f"{score_name} is numeric and finite"
                ),
            )

        check(
            isinstance(
                movie.get("sentimentAvailable"),
                bool,
            ),
            (
                f"Recommendation {expected_rank} "
                "sentimentAvailable is boolean"
            ),
        )

    check(
        len(movie_ids) == len(set(movie_ids)),
        "No duplicate movie IDs in recommendation response",
    )


# =====================================================================
# TESTS
# =====================================================================

section("PHASE 4.4 - PYTHON ML API VALIDATION")


# ---------------------------------------------------------------------
# 1. HEALTH
# ---------------------------------------------------------------------

section("1. HEALTH ENDPOINT")

status, body, elapsed = request_json("/health")

print(f"HTTP status : {status}")
print(f"Time        : {elapsed:.2f} ms")
print(json.dumps(body, indent=2))

check(
    status == 200,
    "/health returns HTTP 200",
)

check(
    body.get("status") == "UP",
    "ML API status is UP",
)

check(
    body.get("modelLoaded") is True,
    "Hybrid recommender is loaded",
)


# ---------------------------------------------------------------------
# 2. KNOWN USER
# ---------------------------------------------------------------------

section("2. KNOWN USER RECOMMENDATIONS")

status, known_body, first_request_ms = request_json(
    "/api/v1/recommendations",
    method="POST",
    payload={
        "mlUserId": KNOWN_USER_ID,
        "limit": 5,
    },
)

print(f"HTTP status       : {status}")
print(f"Request time      : {first_request_ms:.2f} ms")

check(
    status == 200,
    "Known user request returns HTTP 200",
)

if status == 200:
    validate_recommendation_payload(
        known_body,
        expected_user_id=KNOWN_USER_ID,
        expected_count=5,
    )


# ---------------------------------------------------------------------
# 3. SPARSE KNOWN USER
# ---------------------------------------------------------------------

section("3. SPARSE KNOWN USER")

status, sparse_body, elapsed = request_json(
    "/api/v1/recommendations",
    method="POST",
    payload={
        "mlUserId": SPARSE_KNOWN_USER_ID,
        "limit": 5,
    },
)

print(f"HTTP status : {status}")
print(f"Time        : {elapsed:.2f} ms")

check(
    status == 200,
    "Sparse known user returns HTTP 200",
)

if status == 200:
    validate_recommendation_payload(
        sparse_body,
        expected_user_id=SPARSE_KNOWN_USER_ID,
        expected_count=5,
    )


# ---------------------------------------------------------------------
# 4. DEFAULT LIMIT
# ---------------------------------------------------------------------

section("4. DEFAULT LIMIT")

status, body, elapsed = request_json(
    "/api/v1/recommendations",
    method="POST",
    payload={
        "mlUserId": KNOWN_USER_ID,
    },
)

print(f"HTTP status : {status}")
print(f"Time        : {elapsed:.2f} ms")

check(
    status == 200,
    "Request without limit returns HTTP 200",
)

if status == 200:
    check(
        body["count"] == 10,
        "Default recommendation limit is 10",
    )


# ---------------------------------------------------------------------
# 5. LIMIT BOUNDARIES
# ---------------------------------------------------------------------

section("5. LIMIT BOUNDARIES")

status, body, elapsed = request_json(
    "/api/v1/recommendations",
    method="POST",
    payload={
        "mlUserId": KNOWN_USER_ID,
        "limit": 1,
    },
)

check(
    status == 200,
    "Minimum limit 1 is accepted",
)

if status == 200:
    check(
        body["count"] == 1,
        "Minimum limit returns one recommendation",
    )


status, body, elapsed = request_json(
    "/api/v1/recommendations",
    method="POST",
    payload={
        "mlUserId": KNOWN_USER_ID,
        "limit": 50,
    },
)

check(
    status == 200,
    "Maximum limit 50 is accepted",
)

if status == 200:
    check(
        body["count"] == 50,
        "Maximum limit returns 50 recommendations",
    )


# ---------------------------------------------------------------------
# 6. INVALID LIMITS
# ---------------------------------------------------------------------

section("6. INVALID LIMITS")

for invalid_limit in (0, 51, -1):
    status, body, elapsed = request_json(
        "/api/v1/recommendations",
        method="POST",
        payload={
            "mlUserId": KNOWN_USER_ID,
            "limit": invalid_limit,
        },
    )

    check(
        status == 422,
        f"limit={invalid_limit} returns HTTP 422",
    )


# ---------------------------------------------------------------------
# 7. INVALID USER IDs
# ---------------------------------------------------------------------

section("7. INVALID USER IDs")

for invalid_user in (0, -1):
    status, body, elapsed = request_json(
        "/api/v1/recommendations",
        method="POST",
        payload={
            "mlUserId": invalid_user,
            "limit": 5,
        },
    )

    check(
        status == 422,
        f"mlUserId={invalid_user} returns HTTP 422",
    )


status, body, elapsed = request_json(
    "/api/v1/recommendations",
    method="POST",
    payload={
        "mlUserId": "abc",
        "limit": 5,
    },
)

check(
    status == 422,
    "String mlUserId returns HTTP 422",
)


# ---------------------------------------------------------------------
# 8. UNKNOWN USER
# ---------------------------------------------------------------------

section("8. UNKNOWN ML USER")

status, body, elapsed = request_json(
    "/api/v1/recommendations",
    method="POST",
    payload={
        "mlUserId": UNKNOWN_USER_ID,
        "limit": 5,
    },
)

print(f"HTTP status : {status}")
print(json.dumps(body, indent=2))

check(
    status == 404,
    "Unknown ML user returns HTTP 404",
)


# ---------------------------------------------------------------------
# 9. REPEATED REQUEST CONSISTENCY
# ---------------------------------------------------------------------

section("9. REPEATED REQUEST CONSISTENCY")

responses = []
timings = []

for iteration in range(3):
    status, body, elapsed = request_json(
        "/api/v1/recommendations",
        method="POST",
        payload={
            "mlUserId": KNOWN_USER_ID,
            "limit": 5,
        },
    )

    check(
        status == 200,
        f"Repeated request {iteration + 1} returns HTTP 200",
    )

    responses.append(body)
    timings.append(elapsed)

    print(
        f"Request {iteration + 1}: "
        f"{elapsed:.2f} ms"
    )


if all(isinstance(x, dict) for x in responses):
    movie_id_lists = [
        [
            movie["movieId"]
            for movie in response["recommendations"]
        ]
        for response in responses
    ]

    check(
        movie_id_lists[0]
        == movie_id_lists[1]
        == movie_id_lists[2],
        "Repeated requests return the same movie ranking",
    )

    score_lists = [
        [
            movie["score"]
            for movie in response["recommendations"]
        ]
        for response in responses
    ]

    scores_consistent = True

    for first, other in zip(
        score_lists[0],
        score_lists[1],
    ):
        if not math.isclose(
            first,
            other,
            rel_tol=1e-6,
            abs_tol=1e-6,
        ):
            scores_consistent = False

    for first, other in zip(
        score_lists[0],
        score_lists[2],
    ):
        if not math.isclose(
            first,
            other,
            rel_tol=1e-6,
            abs_tol=1e-6,
        ):
            scores_consistent = False

    check(
        scores_consistent,
        "Repeated recommendation scores are consistent",
    )


# ---------------------------------------------------------------------
# 10. TIMING SUMMARY
# ---------------------------------------------------------------------

section("10. REQUEST TIMING")

print(
    f"First recommendation request : "
    f"{first_request_ms:.2f} ms"
)

for index, elapsed in enumerate(
    timings,
    start=1,
):
    print(
        f"Warm request {index:<2}             : "
        f"{elapsed:.2f} ms"
    )


# =====================================================================
# FINAL RESULT
# =====================================================================

section("FINAL PHASE 4.4 RESULT")

print(f"Passed checks : {passed}")
print(f"Failed checks : {failed}")

if failed == 0:
    print()
    print("PHASE 4.4 VALIDATION PASSED")
else:
    print()
    print("PHASE 4.4 VALIDATION FAILED")
    raise SystemExit(1)