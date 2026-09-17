from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from recommender.artifact_loader import ArtifactLoader
from recommender.config import NEUTRAL_SENTIMENT_SCORE


class SentimentRecommender:
    """
    Runtime sentiment component.

    Sentiment is an additional ranking signal, not the primary
    recommendation engine.

    adjustedSentimentScore is expected to be approximately in
    the range [-1, 1].

    Normalization:

        normalized = (adjusted + 1) / 2

    Movies without sentiment data receive the neutral fallback
    score defined in config.py.
    """

    def __init__(
        self,
        loader: ArtifactLoader | None = None,
        neutral_score: float = NEUTRAL_SENTIMENT_SCORE,
    ) -> None:

        self.loader = (
            loader
            if loader is not None
            else ArtifactLoader()
        )

        self.neutral_score = float(
            neutral_score
        )

        if not 0.0 <= self.neutral_score <= 1.0:
            raise ValueError(
                "neutral_score must be between 0 and 1."
            )

        self.sentiment = (
            self.loader.movie_sentiment.copy()
        )

        self._validate()

        self._prepare_runtime_data()

    # ========================================================
    # VALIDATION
    # ========================================================

    def _validate(self) -> None:

        required_columns = {
            "movieId",
            "reviewCount",
            "sentimentReliability",
            "adjustedSentimentScore",
        }

        missing = (
            required_columns
            - set(self.sentiment.columns)
        )

        if missing:
            raise ValueError(
                "Sentiment artifact is missing columns: "
                f"{sorted(missing)}"
            )

        if self.sentiment["movieId"].isna().any():
            raise ValueError(
                "Sentiment artifact contains missing movieIds."
            )

        if self.sentiment["movieId"].duplicated().any():
            raise ValueError(
                "Sentiment artifact contains duplicate movieIds."
            )

        if (
            self.sentiment[
                "adjustedSentimentScore"
            ]
            .isna()
            .any()
        ):
            raise ValueError(
                "Sentiment artifact contains missing "
                "adjustedSentimentScore values."
            )

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def normalize_adjusted_score(
        adjusted_score: float | np.ndarray,
    ):
        """
        Convert adjusted sentiment from approximately [-1, 1]
        into [0, 1].
        """

        normalized = (
            np.asarray(
                adjusted_score,
                dtype=np.float32,
            )
            + 1.0
        ) / 2.0

        normalized = np.clip(
            normalized,
            0.0,
            1.0,
        )

        if np.ndim(adjusted_score) == 0:
            return float(normalized)

        return normalized.astype(
            np.float32
        )

    # ========================================================
    # PREPARE RUNTIME LOOKUPS
    # ========================================================

    def _prepare_runtime_data(self) -> None:

        self.sentiment[
            "sentiment_score"
        ] = self.normalize_adjusted_score(
            self.sentiment[
                "adjustedSentimentScore"
            ].to_numpy()
        )

        self.sentiment["movieId"] = (
            self.sentiment[
                "movieId"
            ].astype(int)
        )

        self._score_lookup = dict(
            zip(
                self.sentiment["movieId"],
                self.sentiment[
                    "sentiment_score"
                ].astype(float),
            )
        )

        self._adjusted_lookup = dict(
            zip(
                self.sentiment["movieId"],
                self.sentiment[
                    "adjustedSentimentScore"
                ].astype(float),
            )
        )

        self._review_count_lookup = dict(
            zip(
                self.sentiment["movieId"],
                self.sentiment[
                    "reviewCount"
                ].astype(int),
            )
        )

        self._reliability_lookup = dict(
            zip(
                self.sentiment["movieId"],
                self.sentiment[
                    "sentimentReliability"
                ].astype(float),
            )
        )

    # ========================================================
    # BASIC LOOKUPS
    # ========================================================

    def has_sentiment(
        self,
        movie_id: int,
    ) -> bool:

        return (
            int(movie_id)
            in self._score_lookup
        )

    def get_score(
        self,
        movie_id: int,
        fallback: bool = True,
    ) -> float | None:
        """
        Return normalized sentiment score in [0, 1].

        If sentiment does not exist:

            fallback=True  -> neutral score
            fallback=False -> None
        """

        movie_id = int(movie_id)

        score = self._score_lookup.get(
            movie_id
        )

        if score is not None:
            return float(score)

        if fallback:
            return self.neutral_score

        return None

    def get_adjusted_score(
        self,
        movie_id: int,
    ) -> float | None:

        return self._adjusted_lookup.get(
            int(movie_id)
        )

    def get_review_count(
        self,
        movie_id: int,
    ) -> int:

        return self._review_count_lookup.get(
            int(movie_id),
            0,
        )

    def get_reliability(
        self,
        movie_id: int,
    ) -> float:

        return self._reliability_lookup.get(
            int(movie_id),
            0.0,
        )

    # ========================================================
    # SINGLE MOVIE DETAILS
    # ========================================================

    def get_movie_sentiment(
        self,
        movie_id: int,
    ) -> dict:

        movie_id = int(movie_id)

        has_data = self.has_sentiment(
            movie_id
        )

        return {
            "movieId": movie_id,
            "hasSentiment": has_data,
            "sentiment_score": self.get_score(
                movie_id,
                fallback=True,
            ),
            "adjustedSentimentScore": (
                self.get_adjusted_score(
                    movie_id
                )
                if has_data
                else None
            ),
            "reviewCount": (
                self.get_review_count(
                    movie_id
                )
                if has_data
                else 0
            ),
            "sentimentReliability": (
                self.get_reliability(
                    movie_id
                )
                if has_data
                else 0.0
            ),
        }

    # ========================================================
    # BATCH SCORING
    # ========================================================

    def score_movies(
        self,
        movie_ids: Iterable[int],
    ) -> pd.DataFrame:
        """
        Score a collection of movieIds.

        Movies without sentiment receive the neutral fallback.
        """

        rows = []

        for movie_id in movie_ids:

            movie_id = int(movie_id)

            has_data = self.has_sentiment(
                movie_id
            )

            rows.append(
                {
                    "movieId": movie_id,
                    "sentiment_score": (
                        self.get_score(
                            movie_id,
                            fallback=True,
                        )
                    ),
                    "has_sentiment": has_data,
                    "adjusted_sentiment_score": (
                        self.get_adjusted_score(
                            movie_id
                        )
                        if has_data
                        else np.nan
                    ),
                    "sentiment_reliability": (
                        self.get_reliability(
                            movie_id
                        )
                        if has_data
                        else 0.0
                    ),
                    "review_count": (
                        self.get_review_count(
                            movie_id
                        )
                        if has_data
                        else 0
                    ),
                }
            )

        return pd.DataFrame(
            rows,
            columns=[
                "movieId",
                "sentiment_score",
                "has_sentiment",
                "adjusted_sentiment_score",
                "sentiment_reliability",
                "review_count",
            ],
        )

    # ========================================================
    # DATASET STATISTICS
    # ========================================================

    @property
    def num_movies(self) -> int:

        return len(
            self.sentiment
        )

    @property
    def minimum_score(self) -> float:

        return float(
            self.sentiment[
                "sentiment_score"
            ].min()
        )

    @property
    def maximum_score(self) -> float:

        return float(
            self.sentiment[
                "sentiment_score"
            ].max()
        )