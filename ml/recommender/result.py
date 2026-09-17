from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd


# ============================================================
# HELPERS
# ============================================================


def _optional_int(
    value: Any,
) -> int | None:
    """
    Convert a value to a normal Python int.

    Missing/NaN values become None so the result remains
    valid JSON.
    """

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return int(value)


def _optional_string(
    value: Any,
) -> str | None:
    """
    Convert a value to a normal Python string.

    Missing/NaN values become None.
    """

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    text = str(value).strip()

    return text if text else None


def _parse_genres(
    value: Any,
) -> list[str]:
    """
    Convert the MovieLens/TMDB pipe-separated genre field into
    a JSON-friendly list.

    Example:

        "Drama|Thriller"

    becomes:

        ["Drama", "Thriller"]
    """

    if value is None:
        return []

    try:
        if pd.isna(value):
            return []
    except (TypeError, ValueError):
        pass

    if isinstance(
        value,
        (list, tuple, set),
    ):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    return [
        part.strip()
        for part in str(value).split("|")
        if part.strip()
    ]


# ============================================================
# SINGLE RECOMMENDATION
# ============================================================


@dataclass(
    frozen=True,
    slots=True,
)
class RecommendationResult:
    """
    Stable external representation of one recommendation.

    All values are plain Python types suitable for JSON
    serialization.
    """

    rank: int

    movie_id: int

    title: str

    release_year: int | None

    genres: tuple[str, ...]

    score: float

    cf_score: float

    content_score: float

    sentiment_score: float

    sentiment_available: bool

    # ========================================================
    # BUILD FROM INTERNAL HYBRID ROW
    # ========================================================

    @classmethod
    def from_row(
        cls,
        rank: int,
        row: Mapping[str, Any],
    ) -> "RecommendationResult":

        movie_id = int(
            row["movieId"]
        )

        title = _optional_string(
            row.get("title")
        )

        if title is None:
            title = f"Movie {movie_id}"

        genres = _parse_genres(
            row.get("genres")
        )

        return cls(
            rank=int(rank),

            movie_id=movie_id,

            title=title,

            release_year=_optional_int(
                row.get(
                    "release_year"
                )
            ),

            genres=tuple(
                genres
            ),

            score=float(
                row["hybrid_score"]
            ),

            # External component scores are normalized.
            cf_score=float(
                row["cf_norm"]
            ),

            content_score=float(
                row["content_norm"]
            ),

            sentiment_score=float(
                row["sentiment_norm"]
            ),

            sentiment_available=bool(
                row.get(
                    "has_sentiment",
                    False,
                )
            ),
        )

    # ========================================================
    # JSON DICTIONARY
    # ========================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Return the public JSON representation.

        CamelCase is used because this object will eventually
        cross the ML -> Spring Boot -> React boundary.
        """

        return {
            "rank": int(
                self.rank
            ),

            "movieId": int(
                self.movie_id
            ),

            "title": self.title,

            "releaseYear": (
                int(
                    self.release_year
                )
                if self.release_year
                is not None
                else None
            ),

            "genres": list(
                self.genres
            ),

            "score": round(
                float(self.score),
                6,
            ),

            "cfScore": round(
                float(self.cf_score),
                6,
            ),

            "contentScore": round(
                float(self.content_score),
                6,
            ),

            "sentimentScore": round(
                float(self.sentiment_score),
                6,
            ),

            "sentimentAvailable": bool(
                self.sentiment_available
            ),
        }


# ============================================================
# FULL RECOMMENDATION RESPONSE
# ============================================================


@dataclass(
    frozen=True,
    slots=True,
)
class RecommendationResponse:
    """
    Stable result envelope returned to Phase 4.
    """

    user_id: int

    recommendations: tuple[
        RecommendationResult,
        ...
    ]

    schema_version: str = "1.0"

    # ========================================================
    # PROPERTIES
    # ========================================================

    @property
    def count(
        self,
    ) -> int:

        return len(
            self.recommendations
        )

    # ========================================================
    # JSON DICTIONARY
    # ========================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schemaVersion": (
                self.schema_version
            ),

            "userId": int(
                self.user_id
            ),

            "count": int(
                self.count
            ),

            "recommendations": [
                recommendation.to_dict()
                for recommendation
                in self.recommendations
            ],
        }