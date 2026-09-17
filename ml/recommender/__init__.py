"""
Movie Recommender ML runtime package.

Public runtime interface:

    HybridRecommender
    RecommendationResult
    RecommendationResponse

Phase 4 application code should normally interact with
HybridRecommender rather than importing the individual
recommendation components directly.
"""

from recommender.hybrid import HybridRecommender
from recommender.result import (
    RecommendationResult,
    RecommendationResponse,
)


__all__ = [
    "HybridRecommender",
    "RecommendationResult",
    "RecommendationResponse",
]


__version__ = "1.0.0"