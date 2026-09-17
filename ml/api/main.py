from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request

from scalar_fastapi import get_scalar_api_reference

from recommender import HybridRecommender

from api.schemas import (
    HealthResponse,
    RecommendationRequest,
    RecommendationResponse,
    PersonalizedRecommendationRequest,
    PersonalizedRecommendationResponse,
    MovieCatalogItem,
    MovieCatalogSearchResponse,
)


# ---------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 70)
    print("STARTING MOVIE RECOMMENDER ML API")
    print("=" * 70)

    try:
        print("Initializing HybridRecommender...")

        app.state.recommender = HybridRecommender()

        print("HybridRecommender loaded successfully.")
        print("ML API is ready.")

    except Exception as exc:
        print(f"Failed to initialize HybridRecommender: {exc}")

        app.state.recommender = None

        raise

    yield

    print("=" * 70)
    print("SHUTTING DOWN MOVIE RECOMMENDER ML API")
    print("=" * 70)


# ---------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------

app = FastAPI(
    title="Movie Recommender ML API",
    description="HTTP interface for the hybrid movie recommendation system",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Movie Recommender ML API",
    )

# ---------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "Movie Recommender ML API",
        "version": "1.0.0",
        "status": "running",
    }


# ---------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
)
def health(request: Request):
    recommender: Optional[HybridRecommender] = getattr(
        request.app.state,
        "recommender",
        None,
    )

    return HealthResponse(
        status="UP" if recommender is not None else "DOWN",
        modelLoaded=recommender is not None,
    )


# ---------------------------------------------------------------------
# Movie catalog
# ---------------------------------------------------------------------

@app.get(
    "/api/v1/movies/{movie_id}",
    response_model=MovieCatalogItem,
)
def get_movie(
    movie_id: int,
    request: Request,
):
    recommender: Optional[HybridRecommender] = getattr(
        request.app.state,
        "recommender",
        None,
    )

    if recommender is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation model is not available.",
        )

    try:
        return recommender.get_movie_catalog_entry(
            movie_id
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(
                exc.args[0]
            ),
        ) from exc

# ---------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------

@app.post(
    "/api/v1/recommendations",
    response_model=RecommendationResponse,
)
def get_recommendations(
    body: RecommendationRequest,
    request: Request,
):
    recommender: Optional[HybridRecommender] = getattr(
        request.app.state,
        "recommender",
        None,
    )

    if recommender is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation model is not available.",
        )

    try:
        result = recommender.recommend_payload(
            user_id=body.mlUserId,
            top_n=body.limit,
            
        )
        # print("\nRAW RECOMMENDATION RESULT")
        # print("=" * 70)
        # print(type(result))
        # print(result.keys())

        # if result.get("recommendations"):
        #     print("\nFIRST RECOMMENDATION")
        #     print(result["recommendations"][0])

        # print("=" * 70)

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    # Existing ML runtime uses "userId".
    # External ML API deliberately calls it "mlUserId".
    response = {
        "schemaVersion": result["schemaVersion"],
        "mlUserId": result["userId"],
        "count": result["count"],
        "recommendations": result["recommendations"],
    }

    return response

@app.post(
    "/api/v1/recommendations/personalized",
    response_model=PersonalizedRecommendationResponse,
)
def get_personalized_recommendations(
    body: PersonalizedRecommendationRequest,
    request: Request,
):
    recommender: Optional[HybridRecommender] = getattr(
        request.app.state,
        "recommender",
        None,
    )

    if recommender is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation model is not available.",
        )

    ratings = [
        (
            item.movieId,
            item.rating,
        )
        for item in body.ratings
    ]

    try:
        result = (
            recommender
            .recommend_personalized_payload(
                ratings=ratings,
                top_n=body.limit,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except KeyError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return result

@app.get(
    "/api/v1/movie-catalog/search",
    response_model=MovieCatalogSearchResponse,
)
def search_movies(
    query: str,
    request: Request,
    limit: int = 20,
):
    recommender: Optional[HybridRecommender] = getattr(
        request.app.state,
        "recommender",
        None,
    )

    if recommender is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation model is not available.",
        )

    try:
        movies = recommender.search_supported_movies(
            query=query,
            limit=limit,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "count": len(movies),
        "movies": movies,
    }