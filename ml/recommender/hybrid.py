from __future__ import annotations

import numpy as np
import pandas as pd

from recommender.artifact_loader import ArtifactLoader
from recommender.collaborative import CollaborativeRecommender
from recommender.content_based import ContentBasedRecommender
from recommender.sentiment import SentimentRecommender
from recommender.user_history import UserHistory

from recommender.config import (
    CF_WEIGHT,
    CONTENT_WEIGHT,
    SENTIMENT_WEIGHT,
    CF_MIN_SCORE,
    CF_MAX_SCORE,
    CONTENT_NORMALIZATION_MAX,
    DEFAULT_TOP_N,
    POSITIVE_RATING_THRESHOLD,
)

from recommender.result import (
    RecommendationResult,
    RecommendationResponse,
)


class HybridRecommender:
    """
    Final hybrid recommendation system.

    Core recommendation:
        Collaborative Filtering + Content-Based Filtering

    Additional ranking signal:
        Sentiment

    Final score:

        hybrid =
            CF_WEIGHT        * cf_norm
          + CONTENT_WEIGHT   * content_norm
          + SENTIMENT_WEIGHT * sentiment_score
    """

    def __init__(
        self,
        device=None,
    ) -> None:

        # ----------------------------------------------------
        # Shared artifact loader
        # ----------------------------------------------------

        self.loader = ArtifactLoader()

        # ----------------------------------------------------
        # Components
        # ----------------------------------------------------

        self.cf = CollaborativeRecommender(
            loader=self.loader,
            device=device,
        )

        self.content = ContentBasedRecommender(
            loader=self.loader,
        )

        self.sentiment = SentimentRecommender(
            loader=self.loader,
        )

        self.history = UserHistory(
            loader=self.loader,
        )

        # ----------------------------------------------------
        # Weights
        # ----------------------------------------------------

        self.cf_weight = float(
            CF_WEIGHT
        )

        self.content_weight = float(
            CONTENT_WEIGHT
        )

        self.sentiment_weight = float(
            SENTIMENT_WEIGHT
        )

        self._validate_weights()

    # ========================================================
    # VALIDATION
    # ========================================================

    def _validate_weights(self) -> None:

        total = (
            self.cf_weight
            + self.content_weight
            + self.sentiment_weight
        )

        if not np.isclose(
            total,
            1.0,
        ):
            raise ValueError(
                "Hybrid weights must sum to 1.0. "
                f"Current total: {total}"
            )

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def normalize_cf(
        scores,
    ) -> np.ndarray:
        """
        Normalize predicted MovieLens ratings:

            0.5 -> 0
            5.0 -> 1
        """

        values = np.asarray(
            scores,
            dtype=np.float32,
        )

        normalized = (
            values - CF_MIN_SCORE
        ) / (
            CF_MAX_SCORE - CF_MIN_SCORE
        )

        return np.clip(
            normalized,
            0.0,
            1.0,
        ).astype(
            np.float32
        )

    @staticmethod
    def normalize_content(
        scores,
    ) -> np.ndarray:
        """
        Normalize content-profile similarity.

            0.00 -> 0
            0.28 -> 1

        Scores above 0.28 are clipped to 1.
        """

        values = np.asarray(
            scores,
            dtype=np.float32,
        )

        normalized = (
            values
            / CONTENT_NORMALIZATION_MAX
        )

        return np.clip(
            normalized,
            0.0,
            1.0,
        ).astype(
            np.float32
        )

    # ========================================================
    # USER VALIDATION
    # ========================================================

    def has_user(
        self,
        user_id: int,
    ) -> bool:

        return (
            self.cf.has_user(user_id)
            and self.history.has_user(user_id)
        )

    def _require_user(
        self,
        user_id: int,
    ) -> None:

        if not self.has_user(
            user_id
        ):
            raise KeyError(
                f"Unknown hybrid userId: {user_id}"
            )

    # ========================================================
    # COMPONENT SCORES
    # ========================================================

    def _get_cf_scores(
        self,
        user_id: int,
        rated_movie_ids: np.ndarray,
    ) -> pd.DataFrame:

        return self.cf.score_candidates(
            user_id=user_id,
            exclude_movie_ids=rated_movie_ids,
        )

    def _get_content_scores(
        self,
        positive_movie_ids: np.ndarray,
        rated_movie_ids: np.ndarray,
    ) -> pd.DataFrame:

        return self.content.score_profile(
            positive_movie_ids=positive_movie_ids,
            exclude_movie_ids=rated_movie_ids,
        )

    # ========================================================
    # SCORE USER
    # ========================================================

    def score_user(
        self,
        user_id: int,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> pd.DataFrame:
        """
        Calculate full hybrid scores for all valid candidates
        for one existing collaborative-filtering user.
        """

        user_id = int(
            user_id
        )

        self._require_user(
            user_id
        )

        # ----------------------------------------------------
        # 1. User history
        # ----------------------------------------------------

        rated_movie_ids = (
            self.history
            .get_rated_movie_ids(
                user_id
            )
        )

        positive_movie_ids = (
            self.history
            .get_positive_movie_ids(
                user_id=user_id,
                min_rating=positive_threshold,
            )
        )

        if len(
            positive_movie_ids
        ) == 0:
            raise ValueError(
                f"User {user_id} has no ratings >= "
                f"{positive_threshold} for building "
                "a content profile."
            )

        # ----------------------------------------------------
        # 2. Collaborative candidates
        # ----------------------------------------------------

        cf_scores = (
            self._get_cf_scores(
                user_id=user_id,
                rated_movie_ids=rated_movie_ids,
            )
        )

        # Candidate universe is intentionally CF-supported.
        #
        # We do NOT add content-only movies here because the
        # current hybrid design uses CF + Content as the core
        # recommender.
        # ----------------------------------------------------

        # ----------------------------------------------------
        # 3. Personalized content scores
        # ----------------------------------------------------

        content_scores = (
            self._get_content_scores(
                positive_movie_ids=positive_movie_ids,
                rated_movie_ids=rated_movie_ids,
            )
        )

        content_scores = (
            content_scores[
                [
                    "movieId",
                    "content_score",
                ]
            ]
        )

        # ----------------------------------------------------
        # 4. Merge CF candidates with content
        # ----------------------------------------------------

        result = cf_scores.merge(
            content_scores,
            on="movieId",
            how="left",
            validate="one_to_one",
        )

        # All CF movies should exist in the content catalog.
        # Still use zero as a safe runtime fallback.
        result[
            "content_score"
        ] = (
            result[
                "content_score"
            ]
            .fillna(0.0)
            .astype(np.float32)
        )

        # ----------------------------------------------------
        # 5. Sentiment
        # ----------------------------------------------------

        sentiment_scores = (
            self.sentiment
            .score_movies(
                result[
                    "movieId"
                ].to_numpy()
            )
        )

        result = result.merge(
            sentiment_scores,
            on="movieId",
            how="left",
            validate="one_to_one",
        )

        # ----------------------------------------------------
        # 6. Normalize
        # ----------------------------------------------------

        result[
            "cf_norm"
        ] = self.normalize_cf(
            result[
                "cf_score"
            ].to_numpy()
        )

        result[
            "content_norm"
        ] = self.normalize_content(
            result[
                "content_score"
            ].to_numpy()
        )

        # sentiment_score is already normalized 0–1
        result[
            "sentiment_norm"
        ] = (
            result[
                "sentiment_score"
            ]
            .astype(np.float32)
        )

        # ----------------------------------------------------
        # 7. Hybrid score
        # ----------------------------------------------------

        result[
            "hybrid_score"
        ] = (
            self.cf_weight
            * result["cf_norm"]
            +
            self.content_weight
            * result["content_norm"]
            +
            self.sentiment_weight
            * result["sentiment_norm"]
        ).astype(
            np.float32
        )

        # ----------------------------------------------------
        # 8. Diagnostic metadata
        # ----------------------------------------------------

        result[
            "recommendation_source"
        ] = "CF+Content"

        result[
            "user_positive_count"
        ] = len(
            positive_movie_ids
        )

        result[
            "user_rated_count"
        ] = len(
            rated_movie_ids
        )

        return result

    def score_personalized(
        self,
        ratings,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> pd.DataFrame:
        """
        Calculate hybrid scores for a new website user whose
        preferences are supplied as explicit movie ratings.

        ratings:
            Iterable of (movieId, rating) pairs.
        """

        ratings = [
            (
                int(movie_id),
                float(rating),
            )
            for movie_id, rating
            in ratings
        ]

        if not ratings:
            raise ValueError(
                "At least one rating is required."
            )

        # ----------------------------------------------------
        # 1. Validate duplicates and rating range
        # ----------------------------------------------------

        seen_movie_ids = set()

        for movie_id, rating in ratings:

            if movie_id in seen_movie_ids:
                raise ValueError(
                    f"Duplicate movieId in ratings: {movie_id}"
                )

            seen_movie_ids.add(
                movie_id
            )

            if rating < 1.0 or rating > 5.0:
                raise ValueError(
                    f"Rating for movieId {movie_id} must be "
                    "between 1.0 and 5.0."
                )

        rated_movie_ids = np.asarray(
            [
                movie_id
                for movie_id, _
                in ratings
            ],
            dtype=np.int64,
        )

        positive_movie_ids = np.asarray(
            [
                movie_id
                for movie_id, rating
                in ratings
                if rating >= positive_threshold
            ],
            dtype=np.int64,
        )

        if len(positive_movie_ids) == 0:
            raise ValueError(
                "At least one positive rating is required "
                f"(rating >= {positive_threshold})."
            )

        # ----------------------------------------------------
        # 2. Temporary collaborative-filtering profile
        # ----------------------------------------------------

        cf_scores = (
            self.cf
            .score_new_user_candidates(
                ratings=ratings
            )
        )

        # ----------------------------------------------------
        # 3. Content profile from positively-rated movies
        # ----------------------------------------------------

        content_scores = (
            self._get_content_scores(
                positive_movie_ids=positive_movie_ids,
                rated_movie_ids=rated_movie_ids,
            )
        )

        content_scores = (
            content_scores[
                [
                    "movieId",
                    "content_score",
                ]
            ]
        )

        # ----------------------------------------------------
        # 4. Merge content scores into CF candidate universe
        # ----------------------------------------------------

        result = cf_scores.merge(
            content_scores,
            on="movieId",
            how="left",
            validate="one_to_one",
        )

        result[
            "content_score"
        ] = (
            result[
                "content_score"
            ]
            .fillna(0.0)
            .astype(np.float32)
        )

        # ----------------------------------------------------
        # 5. Sentiment
        # ----------------------------------------------------

        sentiment_scores = (
            self.sentiment
            .score_movies(
                result[
                    "movieId"
                ].to_numpy()
            )
        )

        result = result.merge(
            sentiment_scores,
            on="movieId",
            how="left",
            validate="one_to_one",
        )

        # ----------------------------------------------------
        # 6. Normalize component scores
        # ----------------------------------------------------

        result[
            "cf_norm"
        ] = self.normalize_cf(
            result[
                "cf_score"
            ].to_numpy()
        )

        result[
            "content_norm"
        ] = self.normalize_content(
            result[
                "content_score"
            ].to_numpy()
        )

        result[
            "sentiment_norm"
        ] = (
            result[
                "sentiment_score"
            ]
            .astype(np.float32)
        )

        # ----------------------------------------------------
        # 7. Final hybrid score
        # ----------------------------------------------------

        result[
            "hybrid_score"
        ] = (
            self.cf_weight
            * result["cf_norm"]
            +
            self.content_weight
            * result["content_norm"]
            +
            self.sentiment_weight
            * result["sentiment_norm"]
        ).astype(
            np.float32
        )

        # ----------------------------------------------------
        # 8. Diagnostic information
        # ----------------------------------------------------

        result[
            "recommendation_source"
        ] = "NewUserCF+Content"

        result[
            "user_positive_count"
        ] = len(
            positive_movie_ids
        )

        result[
            "user_rated_count"
        ] = len(
            rated_movie_ids
        )

        return result
    #####

    def recommend_personalized(
        self,
        ratings,
        top_n: int = DEFAULT_TOP_N,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> pd.DataFrame:

        if top_n <= 0:
            raise ValueError(
                "top_n must be greater than 0."
            )

        scores = self.score_personalized(
            ratings=ratings,
            positive_threshold=positive_threshold,
        )

        top = (
            scores
            .nlargest(
                top_n,
                "hybrid_score",
            )
            .reset_index(
                drop=True
            )
        )

        metadata_columns = [
            column
            for column in [
                "movieId",
                "title",
                "release_year",
                "genres",
                "poster_path",
                "overview",
            ]
            if column
            in self.loader.movies.columns
        ]

        top = top.merge(
            self.loader.movies[
                metadata_columns
            ],
            on="movieId",
            how="left",
            validate="one_to_one",
        )

        return top

    # ========================================================
    # TOP-N RECOMMENDATIONS
    # ========================================================

    def recommend(
        self,
        user_id: int,
        top_n: int = DEFAULT_TOP_N,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> pd.DataFrame:

        if top_n <= 0:
            raise ValueError(
                "top_n must be greater than 0."
            )

        scores = self.score_user(
            user_id=user_id,
            positive_threshold=positive_threshold,
        )

        top = (
            scores
            .nlargest(
                top_n,
                "hybrid_score",
            )
            .reset_index(
                drop=True
            )
        )

        # ----------------------------------------------------
        # Attach movie metadata
        # ----------------------------------------------------

        metadata_columns = [
            column
            for column in [
                "movieId",
                "title",
                "release_year",
                "genres",
                "poster_path",
                "overview",
            ]
            if column
            in self.loader.movies.columns
        ]

        top = top.merge(
            self.loader.movies[
                metadata_columns
            ],
            on="movieId",
            how="left",
            validate="one_to_one",
        )

        return top

    # ========================================================
    # USER SUMMARY
    # ========================================================

    def user_summary(
        self,
        user_id: int,
    ) -> dict:

        summary = (
            self.history.summary(
                user_id=user_id,
                positive_threshold=(
                    POSITIVE_RATING_THRESHOLD
                ),
            )
        )

        summary.update(
            {
                "cfWeight": self.cf_weight,
                "contentWeight": self.content_weight,
                "sentimentWeight": self.sentiment_weight,
            }
        )

        return summary
    
    # ========================================================
    # MOVIE CATALOG
    # ========================================================

    def get_movie_catalog_entry(
        self,
        movie_id: int,
    ) -> dict:

        movie_id = int(movie_id)

        movies = self.loader.movies

        match = movies[
            movies["movieId"] == movie_id
        ]

        if match.empty:
            raise KeyError(
                f"Unknown movieId: {movie_id}"
            )

        row = match.iloc[0]

        release_year = row.get(
            "release_year"
        )

        if pd.isna(release_year):
            release_year = None
        else:
            release_year = int(
                release_year
            )

        tmdb_rating = row.get(
            "vote_average"
        )

        if pd.isna(tmdb_rating):
            tmdb_rating = None
        else:
            tmdb_rating = float(
                tmdb_rating
            )


        tmdb_vote_count = row.get(
            "vote_count"
        )

        if pd.isna(tmdb_vote_count):
            tmdb_vote_count = None
        else:
            tmdb_vote_count = int(
                tmdb_vote_count
            )

        genres_value = row.get(
            "genres"
        )

        if pd.isna(genres_value):
            genres = []

        elif isinstance(
            genres_value,
            str,
        ):
            genres = [
                genre.strip()
                for genre
                in genres_value.split("|")
                if genre.strip()
            ]

        else:
            genres = [
                str(genres_value)
            ]

        return {
            "movieId": movie_id,
            "title": str(
                row["title"]
            ),
            "releaseYear": release_year,
            "genres": genres,
            "tmdbRating": tmdb_rating,
            "tmdbVoteCount": tmdb_vote_count,
            "recommendationSupported":
                self.cf
                .is_recommendation_supported_movie(
                    movie_id
                ),
        }
    

    def search_supported_movies(
        self,
        query: str,
        limit: int = 20,
    ) -> list[dict]:

        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be blank."
            )

        if limit < 1 or limit > 50:
            raise ValueError(
                "limit must be between 1 and 50."
            )

        movies = self.loader.movies

        matches = movies[
            movies["title"]
            .fillna("")
            .str.contains(
                query,
                case=False,
                regex=False,
            )
        ]

        matches = matches[
            matches["movieId"].isin(
                self.loader.cf_supported_movie_ids
            )
        ]

        matches = matches.head(limit)

        results = []

        for _, row in matches.iterrows():

            movie_id = int(
                row["movieId"]
            )

            results.append(
                self.get_movie_catalog_entry(
                    movie_id
                )
            )

        return results

    # ========================================================
    # STABLE RESULT FORMAT
    # ========================================================

    def recommend_results(
        self,
        user_id: int,
        top_n: int = DEFAULT_TOP_N,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> list[RecommendationResult]:
        """
        Return recommendations as strongly-typed runtime objects.

        Unlike recommend(), this method does not expose a pandas
        DataFrame to application code.
        """

        recommendations = self.recommend(
            user_id=user_id,
            top_n=top_n,
            positive_threshold=positive_threshold,
        )

        results = []

        for rank, (_, row) in enumerate(
            recommendations.iterrows(),
            start=1,
        ):

            results.append(
                RecommendationResult.from_row(
                    rank=rank,
                    row=row,
                )
            )

        return results


    def recommend_personalized_results(
        self,
        ratings,
        top_n: int = DEFAULT_TOP_N,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> list[RecommendationResult]:

        recommendations = (
            self.recommend_personalized(
                ratings=ratings,
                top_n=top_n,
                positive_threshold=positive_threshold,
            )
        )

        results = []

        for rank, (_, row) in enumerate(
            recommendations.iterrows(),
            start=1,
        ):

            results.append(
                RecommendationResult.from_row(
                    rank=rank,
                    row=row,
                )
            )

        return results


    def recommend_response(
        self,
        user_id: int,
        top_n: int = DEFAULT_TOP_N,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> RecommendationResponse:
        """
        Return the complete typed recommendation response.
        """

        results = self.recommend_results(
            user_id=user_id,
            top_n=top_n,
            positive_threshold=positive_threshold,
        )

        return RecommendationResponse(
            user_id=int(user_id),
            recommendations=tuple(results),
        )


    def recommend_payload(
        self,
        user_id: int,
        top_n: int = DEFAULT_TOP_N,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> dict:
        """
        Public JSON-safe recommendation payload.

        This is the method Phase 4 should use.
        """

        response = self.recommend_response(
            user_id=user_id,
            top_n=top_n,
            positive_threshold=positive_threshold,
        )

        return response.to_dict()
    
    def recommend_personalized_payload(
        self,
        ratings,
        top_n: int = DEFAULT_TOP_N,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> dict:
        """
        Public JSON-safe recommendation payload for website users.
        """

        results = (
            self.recommend_personalized_results(
                ratings=ratings,
                top_n=top_n,
                positive_threshold=positive_threshold,
            )
        )

        return {
            "schemaVersion": "1.0",
            "count": len(results),
            "recommendations": [
                recommendation.to_dict()
                for recommendation
                in results
            ],
        }