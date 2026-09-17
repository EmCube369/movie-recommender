import json
import math
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PYTHON_BASE_URL = "http://127.0.0.1:8000"
SPRING_BASE_URL = "http://127.0.0.1:8080"

KNOWN_USER_ID = 1
SPARSE_USER_ID = 7382
UNKNOWN_USER_ID = 999_999_999

TIMEOUT_SECONDS = 20


passed = 0
failed = 0


# =====================================================================
# HELPERS
# =====================================================================

def section(title):
    print()
    print("=" * 90)
    print(title)
    print("=" * 90)


def check(condition, message):
    global passed, failed

    if condition:
        print(f"PASS  - {message}")
        passed += 1
    else:
        print(f"FAIL  - {message}")
        failed += 1


def request_json(
    base_url,
    path,
    method="GET",
    payload=None,
):
    url = f"{base_url}{path}"

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
            timeout=TIMEOUT_SECONDS,
        ) as response:

            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            raw = response.read().decode("utf-8")

            return (
                response.status,
                json.loads(raw),
                elapsed_ms,
            )

    except HTTPError as exc:

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        raw = exc.read().decode("utf-8")

        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = raw

        return (
            exc.code,
            body,
            elapsed_ms,
        )

    except URLError as exc:
        raise RuntimeError(
            f"Could not connect to {url}: {exc}"
        ) from exc


def is_finite_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


# =====================================================================
# START
# =====================================================================

section("PHASE 4.10 - FINAL INTEGRATION VALIDATION")


# =====================================================================
# 1. PYTHON ML SERVICE HEALTH
# =====================================================================

section("1. PYTHON ML SERVICE HEALTH")

status, body, elapsed = request_json(
    PYTHON_BASE_URL,
    "/health",
)

print(f"HTTP status : {status}")
print(f"Time        : {elapsed:.2f} ms")
print(json.dumps(body, indent=2))

check(
    status == 200,
    "Python /health returns HTTP 200",
)

check(
    body.get("status") == "UP",
    "Python ML service reports UP",
)

check(
    body.get("modelLoaded") is True,
    "Hybrid recommender is loaded",
)


# =====================================================================
# 2. DIRECT PYTHON RECOMMENDATION
# =====================================================================

section("2. DIRECT PYTHON RECOMMENDATION")

python_status, python_body, python_ms = request_json(
    PYTHON_BASE_URL,
    "/api/v1/recommendations",
    method="POST",
    payload={
        "mlUserId": KNOWN_USER_ID,
        "limit": 5,
    },
)

print(f"HTTP status : {python_status}")
print(f"Time        : {python_ms:.2f} ms")

check(
    python_status == 200,
    "Python recommendation endpoint returns 200",
)

check(
    python_body.get("mlUserId") == KNOWN_USER_ID,
    "Python response contains correct mlUserId",
)

check(
    python_body.get("count") == 5,
    "Python returns 5 recommendations",
)

python_recommendations = python_body.get(
    "recommendations",
    [],
)

check(
    len(python_recommendations) == 5,
    "Python recommendation list contains 5 movies",
)

if python_recommendations:

    first_python = python_recommendations[0]

    required_internal_fields = {
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

    check(
        required_internal_fields.issubset(
            first_python.keys()
        ),
        "Python response contains internal hybrid fields",
    )


# =====================================================================
# 3. SPRING BOOT PUBLIC RECOMMENDATION API
# =====================================================================

section("3. SPRING BOOT PUBLIC RECOMMENDATION API")

spring_status, spring_body, spring_ms = request_json(
    SPRING_BASE_URL,
    "/api/recommendations/users/1?limit=5",
)

print(f"HTTP status : {spring_status}")
print(f"Time        : {spring_ms:.2f} ms")

check(
    spring_status == 200,
    "Spring recommendation endpoint returns 200",
)

check(
    spring_body.get("userId") == KNOWN_USER_ID,
    "Spring response contains correct userId",
)

check(
    spring_body.get("count") == 5,
    "Spring returns 5 recommendations",
)

spring_recommendations = spring_body.get(
    "recommendations",
    [],
)

check(
    len(spring_recommendations) == 5,
    "Spring recommendation list contains 5 movies",
)


# =====================================================================
# 4. PYTHON -> SPRING DATA CONSISTENCY
# =====================================================================

section("4. PYTHON -> SPRING DATA CONSISTENCY")

python_movie_ids = [
    movie["movieId"]
    for movie in python_recommendations
]

spring_movie_ids = [
    movie["movieId"]
    for movie in spring_recommendations
]

print("Python movie IDs :", python_movie_ids)
print("Spring movie IDs :", spring_movie_ids)

check(
    python_movie_ids == spring_movie_ids,
    "Spring preserves Python recommendation ranking",
)


if (
    len(python_recommendations)
    == len(spring_recommendations)
):

    all_common_fields_match = True
    all_scores_match = True

    for python_movie, spring_movie in zip(
        python_recommendations,
        spring_recommendations,
    ):

        if (
            python_movie["rank"]
            != spring_movie["rank"]
            or python_movie["movieId"]
            != spring_movie["movieId"]
            or python_movie["title"]
            != spring_movie["title"]
            or python_movie["releaseYear"]
            != spring_movie["releaseYear"]
            or python_movie["genres"]
            != spring_movie["genres"]
        ):
            all_common_fields_match = False

        if not math.isclose(
            python_movie["score"],
            spring_movie["score"],
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            all_scores_match = False

    check(
        all_common_fields_match,
        "Movie metadata survives Python -> Spring mapping",
    )

    check(
        all_scores_match,
        "Hybrid scores survive Python -> Spring mapping",
    )


# =====================================================================
# 5. PUBLIC CONTRACT HIDES INTERNAL ML DETAILS
# =====================================================================

section("5. PUBLIC API CONTRACT")

internal_fields = {
    "cfScore",
    "contentScore",
    "sentimentScore",
    "sentimentAvailable",
}

internal_fields_hidden = all(
    internal_fields.isdisjoint(movie.keys())
    for movie in spring_recommendations
)

check(
    internal_fields_hidden,
    "Spring public API hides internal ML component scores",
)

required_public_fields = {
    "rank",
    "movieId",
    "title",
    "releaseYear",
    "genres",
    "score",
}

public_fields_valid = all(
    required_public_fields.issubset(movie.keys())
    for movie in spring_recommendations
)

check(
    public_fields_valid,
    "Spring recommendations contain all public fields",
)


for index, movie in enumerate(
    spring_recommendations,
    start=1,
):
    check(
        movie["rank"] == index,
        f"Recommendation {index} has correct rank",
    )

    check(
        isinstance(movie["movieId"], int),
        f"Recommendation {index} movieId is valid",
    )

    check(
        isinstance(movie["title"], str),
        f"Recommendation {index} title is valid",
    )

    check(
        isinstance(movie["genres"], list),
        f"Recommendation {index} genres are valid",
    )

    check(
        is_finite_number(movie["score"]),
        f"Recommendation {index} score is finite",
    )


# =====================================================================
# 6. EXPECTED KNOWN-USER RANKING
# =====================================================================

section("6. KNOWN-USER RANKING")

expected_movie_ids = [
    922,
    6001,
    6669,
    1244,
    3736,
]

expected_titles = [
    "Sunset Boulevard",
    "The King of Comedy",
    "Ikiru",
    "Manhattan",
    "Ace in the Hole",
]

actual_titles = [
    movie["title"]
    for movie in spring_recommendations
]

check(
    spring_movie_ids == expected_movie_ids,
    "Known user ranking matches validated ML output",
)

check(
    actual_titles == expected_titles,
    "Known user titles match validated ML output",
)

for movie in spring_recommendations:
    print(
        f'{movie["rank"]}. '
        f'{movie["title"]} '
        f'({movie["releaseYear"]}) '
        f'- {movie["score"]:.6f}'
    )


# =====================================================================
# 7. SPARSE KNOWN USER
# =====================================================================

section("7. SPARSE KNOWN USER")

status, body, elapsed = request_json(
    SPRING_BASE_URL,
    "/api/recommendations/users/7382?limit=5",
)

print(f"HTTP status : {status}")
print(f"Time        : {elapsed:.2f} ms")

check(
    status == 200,
    "Sparse known user returns 200 through Spring",
)

check(
    body.get("userId") == SPARSE_USER_ID,
    "Sparse user ID is preserved",
)

check(
    body.get("count") == 5,
    "Sparse user receives 5 recommendations",
)


# =====================================================================
# 8. DEFAULT LIMIT
# =====================================================================

section("8. DEFAULT LIMIT")

status, body, elapsed = request_json(
    SPRING_BASE_URL,
    "/api/recommendations/users/1",
)

check(
    status == 200,
    "Spring request without limit returns 200",
)

check(
    body.get("count") == 10,
    "Spring default recommendation limit is 10",
)


# =====================================================================
# 9. INVALID INPUT HANDLING
# =====================================================================

section("9. INVALID INPUT HANDLING")

invalid_cases = [
    (
        "/api/recommendations/users/0?limit=5",
        400,
        "INVALID_RECOMMENDATION_REQUEST",
        "userId=0",
    ),
    (
        "/api/recommendations/users/1?limit=0",
        400,
        "INVALID_RECOMMENDATION_REQUEST",
        "limit=0",
    ),
    (
        "/api/recommendations/users/1?limit=51",
        400,
        "INVALID_RECOMMENDATION_REQUEST",
        "limit=51",
    ),
    (
        "/api/recommendations/users/abc?limit=5",
        400,
        "INVALID_PARAMETER_TYPE",
        "non-numeric userId",
    ),
]


for path, expected_status, expected_error, name in invalid_cases:

    status, body, elapsed = request_json(
        SPRING_BASE_URL,
        path,
    )

    check(
        status == expected_status,
        f"{name} returns HTTP {expected_status}",
    )

    check(
        isinstance(body, dict)
        and body.get("error") == expected_error,
        f"{name} returns {expected_error}",
    )


# =====================================================================
# 10. UNKNOWN ML USER
# =====================================================================

section("10. UNKNOWN ML USER")

status, body, elapsed = request_json(
    SPRING_BASE_URL,
    (
        "/api/recommendations/users/"
        f"{UNKNOWN_USER_ID}?limit=5"
    ),
)

print(f"HTTP status : {status}")
print(json.dumps(body, indent=2))

check(
    status == 404,
    "Unknown ML user returns HTTP 404",
)

check(
    isinstance(body, dict)
    and body.get("error") == "ML_USER_NOT_FOUND",
    "Unknown ML user returns ML_USER_NOT_FOUND",
)


# =====================================================================
# 11. REPEATED END-TO-END CONSISTENCY
# =====================================================================

section("11. REPEATED END-TO-END CONSISTENCY")

responses = []
timings = []

for iteration in range(3):

    status, body, elapsed = request_json(
        SPRING_BASE_URL,
        "/api/recommendations/users/1?limit=5",
    )

    check(
        status == 200,
        f"Repeated Spring request {iteration + 1} returns 200",
    )

    responses.append(body)
    timings.append(elapsed)

    print(
        f"Request {iteration + 1}: "
        f"{elapsed:.2f} ms"
    )


rankings = [
    [
        movie["movieId"]
        for movie in response["recommendations"]
    ]
    for response in responses
]

check(
    rankings[0] == rankings[1] == rankings[2],
    "Repeated end-to-end rankings are consistent",
)


scores = [
    [
        movie["score"]
        for movie in response["recommendations"]
    ]
    for response in responses
]

scores_consistent = True

for first_scores, other_scores in [
    (scores[0], scores[1]),
    (scores[0], scores[2]),
]:
    for first_score, other_score in zip(
        first_scores,
        other_scores,
    ):
        if not math.isclose(
            first_score,
            other_score,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            scores_consistent = False


check(
    scores_consistent,
    "Repeated end-to-end scores are consistent",
)


# =====================================================================
# 12. TIMING SUMMARY
# =====================================================================

section("12. TIMING SUMMARY")

print(
    f"Direct Python request : "
    f"{python_ms:.2f} ms"
)

print(
    f"Spring end-to-end     : "
    f"{spring_ms:.2f} ms"
)

for index, elapsed in enumerate(
    timings,
    start=1,
):
    print(
        f"Repeated request {index:<2}   : "
        f"{elapsed:.2f} ms"
    )


# =====================================================================
# FINAL RESULT
# =====================================================================

section("FINAL PHASE 4 RESULT")

print(f"Passed checks : {passed}")
print(f"Failed checks : {failed}")

if failed == 0:

    print()
    print("PHASE 4.10 FINAL VALIDATION PASSED")
    print("PHASE 4 COMPLETE")

else:

    print()
    print("PHASE 4.10 FINAL VALIDATION FAILED")

    raise SystemExit(1)