from pathlib import Path

import numpy as np
import pandas as pd


# ======================================================================
# PATHS
# ======================================================================

ML_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ML_ROOT / "data" / "processed"
SENTIMENT_DIR = PROCESSED_DIR / "sentiment"
OUTPUT_DIR = PROCESSED_DIR / "testing"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SENTIMENT_PATH = (
    SENTIMENT_DIR / "movie_sentiment_final.csv"
)

MOVIES_PATH = (
    PROCESSED_DIR / "movies_clean_final.csv"
)


# ======================================================================
# EXPECTED FINAL ARTIFACT VALUES
# ======================================================================

EXPECTED_SENTIMENT_MOVIES = 3769

EXPECTED_MIN_ADJUSTED = -0.5329
EXPECTED_MAX_ADJUSTED = 0.8095

EXPECTED_MIN_RELIABILITY = 0.1667
EXPECTED_MAX_RELIABILITY = 0.9219


# ======================================================================
# HYBRID WEIGHTS
# ======================================================================

CF_WEIGHT = 0.50
CONTENT_WEIGHT = 0.35
SENTIMENT_WEIGHT = 0.15

NEUTRAL_SENTIMENT = 0.50


# ======================================================================
# HELPERS
# ======================================================================

def find_column(df, candidates, required=True):
    """
    Find a column using several possible names.
    """

    for candidate in candidates:
        if candidate in df.columns:
            return candidate

    if required:
        raise ValueError(
            f"Could not find required column.\n"
            f"Tried: {candidates}\n"
            f"Available: {df.columns.tolist()}"
        )

    return None


def normalize_sentiment(adjusted_sentiment):
    """
    Convert sentiment from [-1, 1] to [0, 1].

    -1 -> 0.0
     0 -> 0.5
    +1 -> 1.0
    """

    normalized = (
        np.asarray(adjusted_sentiment, dtype=float) + 1.0
    ) / 2.0

    return np.clip(normalized, 0.0, 1.0)


# ======================================================================
# START
# ======================================================================

print("=" * 100)
print("3.9.4 SENTIMENT SIGNAL TEST")
print("=" * 100)


# ======================================================================
# FILE VALIDATION
# ======================================================================

required_files = [
    SENTIMENT_PATH,
    MOVIES_PATH,
]

missing_files = [
    path
    for path in required_files
    if not path.exists()
]

if missing_files:

    print("\nMissing files:")

    for path in missing_files:
        print(path)

    raise FileNotFoundError(
        "One or more sentiment test artifacts are missing."
    )


# ======================================================================
# LOAD DATA
# ======================================================================

sentiment = pd.read_csv(
    SENTIMENT_PATH,
    low_memory=False,
)

movies = pd.read_csv(
    MOVIES_PATH,
    low_memory=False,
)


print("\n" + "=" * 100)
print("ARTIFACT INFORMATION")
print("=" * 100)

print(
    f"Sentiment movies: {len(sentiment):,}"
)

print(
    f"Catalog movies:   {len(movies):,}"
)

print("\nSentiment columns:")
print(sentiment.columns.tolist())


# ======================================================================
# RESOLVE COLUMNS
# ======================================================================

movie_id_col = find_column(
    sentiment,
    [
        "movieId",
        "movie_id",
    ],
)

adjusted_col = find_column(
    sentiment,
    [
        "adjustedSentimentScore",
        "adjustedSentiment",
        "adjusted_sentiment",
        "adjusted_sentiment_score",
    ],
)

reliability_col = find_column(
    sentiment,
    [
        "sentimentReliability",
        "reliability",
        "sentiment_reliability",
        "reliabilityScore",
        "reliability_score",
    ],
)

review_count_col = find_column(
    sentiment,
    [
        "reviewCount",
        "review_count",
        "numReviews",
        "num_reviews",
    ],
)

mean_sentiment_col = find_column(
    sentiment,
    [
        "meanSentimentScore",
        "meanSentiment",
        "mean_sentiment",
        "averageSentiment",
        "average_sentiment",
        "avgSentiment",
        "avg_sentiment",
    ],
    required=False,
)


catalog_title_col = find_column(
    movies,
    [
        "title",
        "title_x",
    ],
)


# ======================================================================
# BASIC ARTIFACT VALIDATION
# ======================================================================

print("\n" + "=" * 100)
print("CORE ARTIFACT VALIDATION")
print("=" * 100)


failures = []


if len(sentiment) != EXPECTED_SENTIMENT_MOVIES:

    failures.append(
        f"Expected {EXPECTED_SENTIMENT_MOVIES:,} sentiment movies, "
        f"found {len(sentiment):,}."
    )

else:

    print(
        f"PASS - sentiment movie count = "
        f"{len(sentiment):,}"
    )


if sentiment[movie_id_col].duplicated().any():

    failures.append(
        "Duplicate movie IDs found."
    )

else:

    print(
        "PASS - no duplicate movie IDs"
    )


if sentiment[movie_id_col].isna().any():

    failures.append(
        "Missing movie IDs found."
    )

else:

    print(
        "PASS - no missing movie IDs"
    )


if sentiment[adjusted_col].isna().any():

    failures.append(
        "Missing adjusted sentiment values found."
    )

else:

    print(
        "PASS - no missing adjusted sentiment values"
    )


if sentiment[reliability_col].isna().any():

    failures.append(
        "Missing reliability values found."
    )

else:

    print(
        "PASS - no missing reliability values"
    )


if sentiment[review_count_col].isna().any():

    failures.append(
        "Missing review counts found."
    )

else:

    print(
        "PASS - no missing review counts"
    )


# ======================================================================
# RANGE VALIDATION
# ======================================================================

print("\n" + "=" * 100)
print("SENTIMENT RANGE VALIDATION")
print("=" * 100)


adjusted = sentiment[
    adjusted_col
].astype(float)


reliability = sentiment[
    reliability_col
].astype(float)


review_count = sentiment[
    review_count_col
].astype(float)


adjusted_min = adjusted.min()
adjusted_max = adjusted.max()

reliability_min = reliability.min()
reliability_max = reliability.max()


print(
    f"Adjusted sentiment range: "
    f"{adjusted_min:.6f} to {adjusted_max:.6f}"
)

print(
    f"Reliability range:        "
    f"{reliability_min:.6f} to {reliability_max:.6f}"
)

print(
    f"Review count range:       "
    f"{review_count.min():.0f} to "
    f"{review_count.max():.0f}"
)


if (
    adjusted_min < -1.0
    or adjusted_max > 1.0
):

    failures.append(
        "Adjusted sentiment outside [-1, 1]."
    )

else:

    print(
        "PASS - adjusted sentiment within [-1, 1]"
    )


if (
    reliability_min < 0.0
    or reliability_max > 1.0
):

    failures.append(
        "Reliability outside [0, 1]."
    )

else:

    print(
        "PASS - reliability within [0, 1]"
    )


if (review_count <= 0).any():

    failures.append(
        "Movies with zero or negative review counts found."
    )

else:

    print(
        "PASS - all sentiment movies have reviews"
    )


# ======================================================================
# REGRESSION RANGE CHECK
# ======================================================================

print("\n" + "=" * 100)
print("PHASE 3.7 REGRESSION CHECK")
print("=" * 100)


if np.isclose(
    adjusted_min,
    EXPECTED_MIN_ADJUSTED,
    atol=1e-3,
):

    print(
        "PASS - minimum adjusted sentiment "
        "matches Phase 3.7."
    )

else:

    print(
        "WARNING - minimum adjusted sentiment differs."
    )


if np.isclose(
    adjusted_max,
    EXPECTED_MAX_ADJUSTED,
    atol=1e-3,
):

    print(
        "PASS - maximum adjusted sentiment "
        "matches Phase 3.7."
    )

else:

    print(
        "WARNING - maximum adjusted sentiment differs."
    )


if np.isclose(
    reliability_min,
    EXPECTED_MIN_RELIABILITY,
    atol=1e-3,
):

    print(
        "PASS - minimum reliability "
        "matches Phase 3.7."
    )

else:

    print(
        "WARNING - minimum reliability differs."
    )


if np.isclose(
    reliability_max,
    EXPECTED_MAX_RELIABILITY,
    atol=1e-3,
):

    print(
        "PASS - maximum reliability "
        "matches Phase 3.7."
    )

else:

    print(
        "WARNING - maximum reliability differs."
    )


# ======================================================================
# NORMALIZATION TEST
# ======================================================================

print("\n" + "=" * 100)
print("NORMALIZATION TEST")
print("=" * 100)


normalization_examples = [
    -1.0,
    -0.5,
    0.0,
    0.5,
    1.0,
]


expected_normalized = [
    0.0,
    0.25,
    0.5,
    0.75,
    1.0,
]


for raw, expected in zip(
    normalization_examples,
    expected_normalized,
):

    result = float(
        normalize_sentiment(raw)
    )

    print(
        f"{raw:+.2f} -> {result:.4f}"
    )

    if not np.isclose(
        result,
        expected,
        atol=1e-8,
    ):

        failures.append(
            f"Normalization failed for {raw}"
        )


normalized = normalize_sentiment(
    adjusted.to_numpy()
)


if (
    normalized.min() < 0
    or normalized.max() > 1
):

    failures.append(
        "Normalized sentiment outside [0, 1]."
    )

else:

    print(
        "\nPASS - all normalized sentiment "
        "values within [0, 1]"
    )


sentiment["sentimentNormalized"] = (
    normalized
)


# ======================================================================
# KNOWN MAXIMUM SENTIMENT REGRESSION
# ======================================================================

print("\n" + "=" * 100)
print("MAXIMUM SENTIMENT NORMALIZATION CHECK")
print("=" * 100)


max_index = adjusted.idxmax()

max_adjusted = float(
    sentiment.loc[
        max_index,
        adjusted_col,
    ]
)

max_normalized = float(
    sentiment.loc[
        max_index,
        "sentimentNormalized",
    ]
)


expected_max_normalized = (
    EXPECTED_MAX_ADJUSTED + 1.0
) / 2.0


print(
    f"Adjusted:   {max_adjusted:.6f}"
)

print(
    f"Normalized: {max_normalized:.6f}"
)

print(
    f"Expected:   {expected_max_normalized:.6f}"
)


if np.isclose(
    max_normalized,
    expected_max_normalized,
    atol=1e-3,
):

    print(
        "PASS - maximum sentiment normalization "
        "matches expected value."
    )

else:

    failures.append(
        "Maximum sentiment normalization "
        "does not match expected value."
    )


# ======================================================================
# ATTACH MOVIE TITLES
# ======================================================================

title_lookup = (
    movies[
        [
            "movieId",
            catalog_title_col,
        ]
    ]
    .drop_duplicates("movieId")
    .set_index("movieId")[
        catalog_title_col
    ]
    .to_dict()
)


sentiment["title"] = (
    sentiment[movie_id_col]
    .map(title_lookup)
    .fillna("<title unavailable>")
)


# ======================================================================
# TOP / BOTTOM SENTIMENT MOVIES
# ======================================================================

print("\n" + "=" * 100)
print("HIGHEST ADJUSTED SENTIMENT")
print("=" * 100)


top_sentiment = (
    sentiment
    .sort_values(
        adjusted_col,
        ascending=False,
    )
    .head(10)
)


display_columns = [
    movie_id_col,
    "title",
    review_count_col,
    adjusted_col,
    reliability_col,
    "sentimentNormalized",
]


print(
    top_sentiment[
        display_columns
    ].to_string(
        index=False,
        formatters={
            adjusted_col:
                lambda x: f"{x:.4f}",
            reliability_col:
                lambda x: f"{x:.4f}",
            "sentimentNormalized":
                lambda x: f"{x:.4f}",
        },
    )
)


print("\n" + "=" * 100)
print("LOWEST ADJUSTED SENTIMENT")
print("=" * 100)


bottom_sentiment = (
    sentiment
    .sort_values(
        adjusted_col,
        ascending=True,
    )
    .head(10)
)


print(
    bottom_sentiment[
        display_columns
    ].to_string(
        index=False,
        formatters={
            adjusted_col:
                lambda x: f"{x:.4f}",
            reliability_col:
                lambda x: f"{x:.4f}",
            "sentimentNormalized":
                lambda x: f"{x:.4f}",
        },
    )
)


# ======================================================================
# RELIABILITY TEST
# ======================================================================

print("\n" + "=" * 100)
print("RELIABILITY BEHAVIOR")
print("=" * 100)


correlation = np.corrcoef(
    review_count,
    reliability,
)[0, 1]


print(
    "Correlation between review count "
    f"and reliability: {correlation:.4f}"
)


review_quantiles = pd.qcut(
    sentiment[review_count_col],
    q=4,
    duplicates="drop",
)


reliability_summary = (
    sentiment
    .assign(
        reviewGroup=review_quantiles
    )
    .groupby(
        "reviewGroup",
        observed=True,
    )
    .agg(
        movies=(movie_id_col, "count"),
        avgReviews=(review_count_col, "mean"),
        avgReliability=(reliability_col, "mean"),
    )
)


print("\nReliability by review-count group:")

print(
    reliability_summary.to_string()
)


if correlation >= 0:

    print(
        "\nPASS - reliability generally increases "
        "with review evidence."
    )

else:

    print(
        "\nWARNING - reliability is negatively "
        "correlated with review count."
    )


# ======================================================================
# ADJUSTMENT / SHRINKAGE CHECK
# ======================================================================

if mean_sentiment_col is not None:

    print("\n" + "=" * 100)
    print("SENTIMENT SHRINKAGE CHECK")
    print("=" * 100)


    raw_mean = sentiment[
        mean_sentiment_col
    ].astype(float)


    absolute_raw = np.abs(
        raw_mean
    )

    absolute_adjusted = np.abs(
        adjusted
    )


    shrinkage_valid = (
        absolute_adjusted
        <= absolute_raw + 1e-6
    )


    shrinkage_rate = (
        shrinkage_valid.mean()
    )


    print(
        "Rows where adjusted sentiment is "
        "not more extreme than raw sentiment: "
        f"{shrinkage_rate:.2%}"
    )


    if shrinkage_rate >= 0.99:

        print(
            "PASS - reliability adjustment "
            "shrinks sentiment appropriately."
        )

    else:

        print(
            "WARNING - adjustment behavior "
            "requires inspection."
        )


# ======================================================================
# CATALOG COVERAGE / NEUTRAL FALLBACK
# ======================================================================

print("\n" + "=" * 100)
print("NEUTRAL FALLBACK TEST")
print("=" * 100)


sentiment_movie_ids = set(
    sentiment[
        movie_id_col
    ]
    .astype(int)
    .tolist()
)


catalog_movie_ids = (
    movies["movieId"]
    .astype(int)
)


coverage_count = (
    catalog_movie_ids
    .isin(sentiment_movie_ids)
    .sum()
)

missing_count = (
    len(movies)
    - coverage_count
)

coverage_percent = (
    coverage_count
    / len(movies)
    * 100
)


print(
    f"Catalog movies:           {len(movies):,}"
)

print(
    f"With sentiment:           {coverage_count:,}"
)

print(
    f"Using neutral fallback:   {missing_count:,}"
)

print(
    f"Sentiment coverage:       {coverage_percent:.2f}%"
)


sentiment_lookup = dict(
    zip(
        sentiment[
            movie_id_col
        ].astype(int),
        sentiment[
            "sentimentNormalized"
        ].astype(float),
    )
)


def get_sentiment_score(movie_id):

    return sentiment_lookup.get(
        int(movie_id),
        NEUTRAL_SENTIMENT,
    )


missing_example = movies.loc[
    ~catalog_movie_ids.isin(
        sentiment_movie_ids
    )
].iloc[0]


missing_movie_id = int(
    missing_example["movieId"]
)

missing_title = (
    missing_example[catalog_title_col]
)

fallback_score = get_sentiment_score(
    missing_movie_id
)


print(
    "\nMissing-sentiment example:"
)

print(
    f"movieId: {missing_movie_id}"
)

print(
    f"title:   {missing_title}"
)

print(
    f"score:   {fallback_score:.4f}"
)


if np.isclose(
    fallback_score,
    0.5,
):

    print(
        "PASS - missing sentiment uses "
        "neutral score 0.5."
    )

else:

    failures.append(
        "Neutral sentiment fallback is incorrect."
    )


# ======================================================================
# HYBRID WEIGHT VALIDATION
# ======================================================================

print("\n" + "=" * 100)
print("HYBRID SENTIMENT INFLUENCE TEST")
print("=" * 100)


weight_sum = (
    CF_WEIGHT
    + CONTENT_WEIGHT
    + SENTIMENT_WEIGHT
)


print(
    f"CF weight:        {CF_WEIGHT:.2f}"
)

print(
    f"Content weight:   {CONTENT_WEIGHT:.2f}"
)

print(
    f"Sentiment weight: {SENTIMENT_WEIGHT:.2f}"
)

print(
    f"Total:            {weight_sum:.2f}"
)


if not np.isclose(
    weight_sum,
    1.0,
):

    failures.append(
        "Hybrid weights do not sum to 1."
    )

else:

    print(
        "PASS - hybrid weights sum to 1.0"
    )


# ======================================================================
# MAXIMUM POSSIBLE SENTIMENT EFFECT
# ======================================================================

cf_score = 0.80
content_score = 0.80


low_sentiment_score = (
    CF_WEIGHT * cf_score
    + CONTENT_WEIGHT * content_score
    + SENTIMENT_WEIGHT * 0.0
)


neutral_sentiment_score = (
    CF_WEIGHT * cf_score
    + CONTENT_WEIGHT * content_score
    + SENTIMENT_WEIGHT * 0.5
)


high_sentiment_score = (
    CF_WEIGHT * cf_score
    + CONTENT_WEIGHT * content_score
    + SENTIMENT_WEIGHT * 1.0
)


print("\nEqual CF/content candidate:")

print(
    f"Sentiment 0.0 -> Hybrid "
    f"{low_sentiment_score:.4f}"
)

print(
    f"Sentiment 0.5 -> Hybrid "
    f"{neutral_sentiment_score:.4f}"
)

print(
    f"Sentiment 1.0 -> Hybrid "
    f"{high_sentiment_score:.4f}"
)


maximum_sentiment_effect = (
    high_sentiment_score
    - low_sentiment_score
)


print(
    "\nMaximum possible sentiment-only "
    f"score difference: "
    f"{maximum_sentiment_effect:.4f}"
)


if np.isclose(
    maximum_sentiment_effect,
    SENTIMENT_WEIGHT,
):

    print(
        "PASS - sentiment can contribute "
        "at most 15% of hybrid score."
    )

else:

    failures.append(
        "Unexpected sentiment influence."
    )


# ======================================================================
# CORE RECOMMENDATION DOMINANCE TEST
# ======================================================================

print("\nCore recommendation dominance test:")


# Candidate A has significantly better CF + content
candidate_a_cf = 0.90
candidate_a_content = 0.90
candidate_a_sentiment = 0.00


# Candidate B has worse core recommendation signals,
# but perfect sentiment
candidate_b_cf = 0.65
candidate_b_content = 0.65
candidate_b_sentiment = 1.00


candidate_a_hybrid = (
    CF_WEIGHT * candidate_a_cf
    + CONTENT_WEIGHT * candidate_a_content
    + SENTIMENT_WEIGHT * candidate_a_sentiment
)


candidate_b_hybrid = (
    CF_WEIGHT * candidate_b_cf
    + CONTENT_WEIGHT * candidate_b_content
    + SENTIMENT_WEIGHT * candidate_b_sentiment
)


print(
    f"Candidate A "
    f"(strong core, negative sentiment): "
    f"{candidate_a_hybrid:.4f}"
)

print(
    f"Candidate B "
    f"(weaker core, perfect sentiment):  "
    f"{candidate_b_hybrid:.4f}"
)


if candidate_a_hybrid > candidate_b_hybrid:

    print(
        "PASS - sentiment does not overpower "
        "strong CF/content evidence."
    )

else:

    failures.append(
        "Sentiment is overpowering "
        "core recommendation signals."
    )


# ======================================================================
# SAVE TEST OUTPUT
# ======================================================================

output_path = (
    OUTPUT_DIR
    / "sentiment_signal_test_results.csv"
)


sentiment[
    [
        movie_id_col,
        "title",
        review_count_col,
        adjusted_col,
        reliability_col,
        "sentimentNormalized",
    ]
].to_csv(
    output_path,
    index=False,
)


print("\nSaved:")
print(output_path)


# ======================================================================
# FINAL RESULT
# ======================================================================

print("\n" + "=" * 100)
print("3.9.4 AUTOMATED TEST RESULT")
print("=" * 100)


if failures:

    print(
        "FAIL - One or more sentiment "
        "signal tests failed."
    )

    print("\nFailures:")

    for failure in failures:
        print(
            f"  - {failure}"
        )

else:

    print(
        "PASS - All sentiment signal tests passed."
    )


print(
    "\nThis test confirms that sentiment behaves "
    "as a bounded ranking signal."
)

print(
    "Actual hybrid recommendation ranking will "
    "be tested separately in 3.9.5."
)