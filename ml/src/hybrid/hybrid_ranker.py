from pathlib import Path

import numpy as np
import pandas as pd

from cf_candidate_generator import CollaborativeCandidateGenerator
from content_user_scorer import ContentUserScorer
from sentiment_scorer import SentimentScorer
from score_normalizer import ScoreNormalizer
from user_history import UserHistory


# ============================================================
# PATHS
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[2]

MOVIES_PATH = (
    ML_ROOT
    / "data"
    / "processed"
    / "movies_clean_final.csv"
)


# ============================================================
# HYBRID RANKER
# ============================================================

class HybridRanker:

    def __init__(
        self,
        cf_weight=0.50,
        content_weight=0.35,
        sentiment_weight=0.15,
    ):

        # ----------------------------------------------------
        # WEIGHTS
        # ----------------------------------------------------

        total_weight = (
            cf_weight
            + content_weight
            + sentiment_weight
        )

        if not np.isclose(total_weight, 1.0):
            raise ValueError(
                "Hybrid weights must sum to 1.0. "
                f"Current total: {total_weight}"
            )

        self.cf_weight = float(cf_weight)
        self.content_weight = float(content_weight)
        self.sentiment_weight = float(sentiment_weight)

        print("=" * 70)
        print("LOADING HYBRID RECOMMENDATION SYSTEM")
        print("=" * 70)

        print(
            f"CF weight        : {self.cf_weight:.2f}"
        )
        print(
            f"Content weight   : {self.content_weight:.2f}"
        )
        print(
            f"Sentiment weight : {self.sentiment_weight:.2f}"
        )

        # ----------------------------------------------------
        # LOAD COMPONENTS
        # ----------------------------------------------------

        print("\nLoading collaborative component...")
        self.cf = CollaborativeCandidateGenerator()

        print("\nLoading user-history component...")
        self.history = UserHistory()

        print("\nLoading content component...")
        self.content = ContentUserScorer(
            user_history=self.history
        )

        print("\nLoading sentiment component...")
        self.sentiment = SentimentScorer()

        self.normalizer = ScoreNormalizer()

        # ----------------------------------------------------
        # MOVIE CATALOG
        # ----------------------------------------------------

        self.catalog = pd.read_csv(
            MOVIES_PATH,
            low_memory=False,
        )

        self.title_column = (
            "title_x"
            if "title_x" in self.catalog.columns
            else "title"
        )

        print("\nHybrid system loaded.")

    # ========================================================
    # COLLABORATIVE SCORES
    # ========================================================

    def get_cf_scores(
        self,
        user_id,
    ):

        print("\nGenerating collaborative scores...")

        cf_scores = self.cf.score_movies_for_user(
            user_id
        )

        cf_scores = cf_scores[
            [
                "movieId",
                "cf_score",
            ]
        ].copy()

        cf_scores[
            "cf_normalized"
        ] = self.normalizer.normalize_cf(
            cf_scores["cf_score"]
        )

        print(
            f"CF scored movies: {len(cf_scores):,}"
        )

        return cf_scores

    # ========================================================
    # CONTENT SCORES
    # ========================================================

    def get_content_scores(
        self,
        user_id,
        minimum_rating=4.0,
    ):

        print("\nGenerating personalized content scores...")

        user_ratings = self.content.load_user_ratings(
            user_id=user_id,
            minimum_rating=minimum_rating,
        )

        profiles = self.content.build_user_profiles(
            user_ratings
        )

        content_scores, _ = (
            self.content.score_all_movies(
                profiles
            )
        )

        content_scores[
            "content_normalized"
        ] = self.normalizer.normalize_content(
            content_scores["content_score"]
        )

        print(
            f"Content scored movies: "
            f"{len(content_scores):,}"
        )

        return content_scores

    # ========================================================
    # COMBINE SCORES
    # ========================================================

    def build_hybrid_scores(
        self,
        user_id,
        minimum_rating=4.0,
    ):

        print("\n" + "=" * 70)
        print(
            f"BUILDING HYBRID SCORES FOR USER {user_id}"
        )
        print("=" * 70)

        # ----------------------------------------------------
        # 1. CONTENT
        #
        # Content covers the complete movie catalog, so use it
        # as the base candidate universe.
        # ----------------------------------------------------

        result = self.get_content_scores(
            user_id=user_id,
            minimum_rating=minimum_rating,
        )

        # ----------------------------------------------------
        # 2. COLLABORATIVE
        # ----------------------------------------------------

        cf_scores = self.get_cf_scores(
            user_id
        )

        result = result.merge(
            cf_scores,
            on="movieId",
            how="left",
        )

        result["has_cf"] = (
            result["cf_normalized"].notna()
        )

        # ----------------------------------------------------
        # 3. SENTIMENT
        # ----------------------------------------------------

        sentiment_scores = (
            self.sentiment.score_movies(
                result["movieId"]
            )
        )

        result = result.merge(
            sentiment_scores,
            on="movieId",
            how="left",
        )

        result[
            "sentiment_normalized"
        ] = (
            self.normalizer
            .normalize_sentiment(
                result["sentiment_score"]
            )
        )

        # ----------------------------------------------------
        # 4. CORE RECOMMENDATION SCORE
        #
        # When CF exists:
        #
        #    weighted CF + Content
        #
        # When CF does not exist:
        #
        #    Content becomes the complete core score.
        # ----------------------------------------------------

        result["core_score"] = (
            result["content_normalized"]
        )

        cf_mask = result["has_cf"]

        core_weight_total = (
            self.cf_weight
            + self.content_weight
        )

        result.loc[
            cf_mask,
            "core_score",
        ] = (
            (
                self.cf_weight
                * result.loc[
                    cf_mask,
                    "cf_normalized",
                ]
            )
            +
            (
                self.content_weight
                * result.loc[
                    cf_mask,
                    "content_normalized",
                ]
            )
        ) / core_weight_total

        # ----------------------------------------------------
        # 5. FINAL HYBRID SCORE
        #
        # For movies with CF:
        #
        # 0.50 CF
        # + 0.35 Content
        # + 0.15 Sentiment
        #
        # For movies without CF:
        #
        # 0.85 Content
        # + 0.15 Sentiment
        # ----------------------------------------------------

        core_contribution = (
            1.0 - self.sentiment_weight
        )

        result["hybrid_score"] = (
            core_contribution
            * result["core_score"]
            +
            self.sentiment_weight
            * result["sentiment_normalized"]
        )

        result["hybrid_score"] = (
            result["hybrid_score"]
            .clip(
                lower=0.0,
                upper=1.0,
            )
        )

        # ----------------------------------------------------
        # SOURCE LABEL
        # ----------------------------------------------------

        result["recommendation_source"] = (
            np.where(
                result["has_cf"],
                "CF+Content",
                "Content-only",
            )
        )

        # ----------------------------------------------------
        # TITLES
        # ----------------------------------------------------

        result = result.merge(
            self.catalog[
                [
                    "movieId",
                    self.title_column,
                ]
            ],
            on="movieId",
            how="left",
        )

        return result

    # ========================================================
    # TOP HYBRID CANDIDATES
    # ========================================================

    def get_top_candidates(
        self,
        user_id,
        top_n=20,
        minimum_rating=4.0,
    ):

        scores = self.build_hybrid_scores(
            user_id=user_id,
            minimum_rating=minimum_rating,
        )

        # --------------------------------------------------------
        # REMOVE MOVIES ALREADY RATED
        # --------------------------------------------------------

        scores, history_count, removed_count = (
            self.history.filter_rated_movies(
                dataframe=scores,
                user_id=user_id,
            )
        )

        print("\n" + "=" * 70)
        print("USER HISTORY FILTER")
        print("=" * 70)

        print(
            f"User history movies: "
            f"{history_count:,}"
        )

        print(
            f"Rated movies removed from candidate universe: "
            f"{removed_count:,}"
        )

        # --------------------------------------------------------
        # REQUIRE TRAINED CF SUPPORT FOR KNOWN USERS
        # --------------------------------------------------------

        before_cf_filter = len(scores)

        scores = scores[
            scores["has_cf"]
        ].copy()

        print(
            f"CF-supported candidates: "
            f"{len(scores):,}"
        )

        print(
            f"Content-only candidates excluded: "
            f"{before_cf_filter - len(scores):,}"
        )

        # --------------------------------------------------------
        # FINAL RANKING
        # --------------------------------------------------------

        scores = scores.sort_values(
            "hybrid_score",
            ascending=False,
        )

        return (
            scores
            .head(top_n)
            .reset_index(drop=True)
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    hybrid = HybridRanker(
        cf_weight=0.50,
        content_weight=0.35,
        sentiment_weight=0.15,
    )

    test_user_id = 1

    results = hybrid.get_top_candidates(
        user_id=test_user_id,
        top_n=30,
        minimum_rating=4.0,
    )

    print("\n" + "=" * 120)
    print(
        f"TOP HYBRID CANDIDATES FOR USER "
        f"{test_user_id}"
    )
    print("=" * 120)

    display_columns = [
        "movieId",
        hybrid.title_column,
        "cf_normalized",
        "content_normalized",
        "sentiment_normalized",
        "has_sentiment",
        "recommendation_source",
        "hybrid_score",
    ]

    print(
        results[
            display_columns
        ].to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # COVERAGE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("HYBRID COVERAGE")
    print("=" * 70)

    print(
        "Top candidates with CF:",
        int(results["has_cf"].sum()),
    )

    print(
        "Top candidates without CF:",
        int((~results["has_cf"]).sum()),
    )

    print(
        "Top candidates with sentiment:",
        int(results["has_sentiment"].sum()),
    )

    print(
        "Top candidates without sentiment:",
        int((~results["has_sentiment"]).sum()),
    )
