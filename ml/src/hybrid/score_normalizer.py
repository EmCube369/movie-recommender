import numpy as np
import pandas as pd


# ============================================================
# SCORE NORMALIZER
# ============================================================

class ScoreNormalizer:

    # ========================================================
    # COLLABORATIVE
    # ========================================================

    @staticmethod
    def normalize_cf(
        scores,
        minimum_rating=0.5,
        maximum_rating=5.0,
    ):
        """
        Convert MovieLens predicted ratings from [0.5, 5.0]
        into [0, 1].
        """

        scores = np.asarray(
            scores,
            dtype=np.float32,
        )

        normalized = (
            scores - minimum_rating
        ) / (
            maximum_rating - minimum_rating
        )

        return np.clip(
            normalized,
            0.0,
            1.0,
        )

    # ========================================================
    # CONTENT
    # ========================================================

    @staticmethod
    def normalize_content(scores):
        """
        Normalize one user's content scores relative to their
        strongest content match.

        Content similarities are non-negative.
        """

        scores = np.asarray(
            scores,
            dtype=np.float32,
        )

        if len(scores) == 0:
            return scores

        maximum = float(
            np.max(scores)
        )

        if maximum <= 0:
            return np.zeros_like(
                scores,
                dtype=np.float32,
            )

        normalized = scores / maximum

        return np.clip(
            normalized,
            0.0,
            1.0,
        )

    # ========================================================
    # SENTIMENT
    # ========================================================

    @staticmethod
    def normalize_sentiment(scores):
        """
        Sentiment scorer already produces [0,1].
        This method only validates/clips it.
        """

        scores = np.asarray(
            scores,
            dtype=np.float32,
        )

        return np.clip(
            scores,
            0.0,
            1.0,
        )

    # ========================================================
    # DATAFRAME HELPERS
    # ========================================================

    @classmethod
    def normalize_cf_dataframe(cls, df):

        result = df.copy()

        result["cf_normalized"] = (
            cls.normalize_cf(
                result["cf_score"]
            )
        )

        return result

    @classmethod
    def normalize_content_dataframe(cls, df):

        result = df.copy()

        result["content_normalized"] = (
            cls.normalize_content(
                result["content_score"]
            )
        )

        return result

    @classmethod
    def normalize_sentiment_dataframe(cls, df):

        result = df.copy()

        result["sentiment_normalized"] = (
            cls.normalize_sentiment(
                result["sentiment_score"]
            )
        )

        return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    normalizer = ScoreNormalizer()

    print("=" * 70)
    print("CF NORMALIZATION TEST")
    print("=" * 70)

    cf = pd.DataFrame(
        {
            "cf_score": [
                0.5,
                1.0,
                2.5,
                3.5,
                4.0,
                4.5,
                5.0,
            ]
        }
    )

    cf = normalizer.normalize_cf_dataframe(
        cf
    )

    print(
        cf.to_string(
            index=False
        )
    )

    print("\n" + "=" * 70)
    print("CONTENT NORMALIZATION TEST")
    print("=" * 70)

    content = pd.DataFrame(
        {
            "content_score": [
                0.0,
                0.05,
                0.10,
                0.20,
                0.28,
            ]
        }
    )

    content = (
        normalizer
        .normalize_content_dataframe(
            content
        )
    )

    print(
        content.to_string(
            index=False
        )
    )

    print("\n" + "=" * 70)
    print("SENTIMENT NORMALIZATION TEST")
    print("=" * 70)

    sentiment = pd.DataFrame(
        {
            "sentiment_score": [
                0.23,
                0.50,
                0.75,
                0.90,
            ]
        }
    )

    sentiment = (
        normalizer
        .normalize_sentiment_dataframe(
            sentiment
        )
    )

    print(
        sentiment.to_string(
            index=False
        )
    )