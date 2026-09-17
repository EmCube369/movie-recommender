from typing import Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    mlUserId: int = Field(
        ...,
        gt=0,
        description="MovieLens/ML user ID known to the recommendation model",
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of recommendations to return",
    )

class UserRating(BaseModel):
    movieId: int = Field(
        ...,
        gt=0,
        description="MovieLens/ML movie ID",
    )

    rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Rating given by the website user",
    )


class PersonalizedRecommendationRequest(BaseModel):
    ratings: list[UserRating]

    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of recommendations to return",
    )


class RecommendedMovie(BaseModel):
    rank: int
    movieId: int
    title: str
    releaseYear: Optional[int] = None
    genres: list[str]

    score: float
    cfScore: float
    contentScore: float
    sentimentScore: float
    sentimentAvailable: bool


class RecommendationResponse(BaseModel):
    schemaVersion: str
    mlUserId: int
    count: int
    recommendations: list[RecommendedMovie]

class PersonalizedRecommendationResponse(BaseModel):
    schemaVersion: str
    count: int
    recommendations: list[RecommendedMovie]

class MovieCatalogItem(BaseModel):
    movieId: int
    title: str
    releaseYear: int | None = None
    genres: list[str]

    tmdbRating: float | None = None
    tmdbVoteCount: int | None = None

    recommendationSupported: bool

class HealthResponse(BaseModel):
    status: str
    modelLoaded: bool


class MovieCatalogSearchResponse(BaseModel):
    count: int
    movies: list[MovieCatalogItem]