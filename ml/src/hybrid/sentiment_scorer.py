from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[2]

SENTIMENT_PATH = (
    ML_ROOT
    / "data"
    / "processed"
    / "sentiment"
    / "movie_sentiment_final.csv"
)

MOVIES_PATH = (
    ML_ROOT
    / "data"
    / "processed"
    / "movies_clean_final.csv"
)


# ============================================================
# SENTIMENT SCORER
# ============================================================

class SentimentScorer:

    def __init__(
        self,
        neutral_score=0.5,
    ):

        print("Loading sentiment artifacts...")

        self.neutral_score = float(
            neutral_score
        )

        self.sentiment = pd.read_csv(
            SENTIMENT_PATH
        )

        required_columns = {
            "movieId",
            "reviewCount",
            "meanSentimentScore",
            "sentimentReliability",
            "adjustedSentimentScore",
        }

        missing = required_columns - set(
            self.sentiment.columns
        )

        if missing:
            raise ValueError(
                f"Missing sentiment columns: {missing}"
            )

        if self.sentiment[
            "movieId"
        ].duplicated().any():

            raise ValueError(
                "Duplicate movieId values found "
                "in sentiment data."
            )

        # ----------------------------------------------------
        # Convert adjusted sentiment from roughly [-1, 1]
        # into [0, 1].
        # ----------------------------------------------------

        adjusted = self.sentiment[
            "adjustedSentimentScore"
        ].astype(np.float32)

        self.sentiment[
            "sentiment_score"
        ] = (
            adjusted + 1.0
        ) / 2.0

        self.sentiment[
            "sentiment_score"
        ] = self.sentiment[
            "sentiment_score"
        ].clip(
            lower=0.0,
            upper=1.0,
        )

        print(
            f"Sentiment movies: "
            f"{len(self.sentiment):,}"
        )

        print(
            "Normalized sentiment range:",
            f"{self.sentiment['sentiment_score'].min():.4f}",
            "to",
            f"{self.sentiment['sentiment_score'].max():.4f}",
        )

    # ========================================================
    # SCORE A LIST OF MOVIES
    # ========================================================

    def score_movies(
        self,
        movie_ids,
    ):

        candidates = pd.DataFrame(
            {
                "movieId": list(movie_ids)
            }
        )

        result = candidates.merge(
            self.sentiment[
                [
                    "movieId",
                    "reviewCount",
                    "meanSentimentScore",
                    "sentimentReliability",
                    "adjustedSentimentScore",
                    "sentiment_score",
                ]
            ],
            on="movieId",
            how="left",
        )

        # ----------------------------------------------------
        # Movies with no review sentiment get NEUTRAL score.
        # ----------------------------------------------------

        result[
            "has_sentiment"
        ] = result[
            "sentiment_score"
        ].notna()

        result[
            "sentiment_score"
        ] = result[
            "sentiment_score"
        ].fillna(
            self.neutral_score
        )

        result[
            "reviewCount"
        ] = result[
            "reviewCount"
        ].fillna(0).astype(int)

        return result

    # ========================================================
    # SCORE WHOLE CATALOG
    # ========================================================

    def score_catalog(
        self,
        catalog,
    ):

        result = catalog[
            ["movieId"]
        ].merge(
            self.sentiment[
                [
                    "movieId",
                    "reviewCount",
                    "adjustedSentimentScore",
                    "sentiment_score",
                ]
            ],
            on="movieId",
            how="left",
        )

        result[
            "has_sentiment"
        ] = result[
            "sentiment_score"
        ].notna()

        result[
            "sentiment_score"
        ] = result[
            "sentiment_score"
        ].fillna(
            self.neutral_score
        )

        result[
            "reviewCount"
        ] = result[
            "reviewCount"
        ].fillna(0).astype(int)

        return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    scorer = SentimentScorer()

    catalog = pd.read_csv(
        MOVIES_PATH,
        low_memory=False,
    )

    title_column = (
        "title_x"
        if "title_x" in catalog.columns
        else "title"
    )

    scored = scorer.score_catalog(
        catalog
    )

    scored = scored.merge(
        catalog[
            [
                "movieId",
                title_column,
            ]
        ],
        on="movieId",
        how="left",
    )

    # --------------------------------------------------------
    # Sentiment coverage
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("SENTIMENT COVERAGE")
    print("=" * 80)

    print(
        "Catalog movies:",
        f"{len(scored):,}",
    )

    print(
        "Movies with sentiment:",
        f"{scored['has_sentiment'].sum():,}",
    )

    print(
        "Movies using neutral fallback:",
        f"{(~scored['has_sentiment']).sum():,}",
    )

    # --------------------------------------------------------
    # Highest sentiment movies
    # --------------------------------------------------------

    with_sentiment = scored[
        scored["has_sentiment"]
    ].copy()

    top = with_sentiment.sort_values(
        [
            "sentiment_score",
            "reviewCount",
        ],
        ascending=[
            False,
            False,
        ],
    ).head(20)

    print("\n" + "=" * 80)
    print("TOP SENTIMENT SCORES")
    print("=" * 80)

    print(
        top[
            [
                "movieId",
                title_column,
                "reviewCount",
                "adjustedSentimentScore",
                "sentiment_score",
            ]
        ].to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Lowest sentiment movies
    # --------------------------------------------------------

    bottom = with_sentiment.sort_values(
        [
            "sentiment_score",
            "reviewCount",
        ],
        ascending=[
            True,
            False,
        ],
    ).head(20)

    print("\n" + "=" * 80)
    print("LOWEST SENTIMENT SCORES")
    print("=" * 80)

    print(
        bottom[
            [
                "movieId",
                title_column,
                "reviewCount",
                "adjustedSentimentScore",
                "sentiment_score",
            ]
        ].to_string(
            index=False
        )
    )