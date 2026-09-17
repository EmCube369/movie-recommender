# Movie Recommender

A full-stack movie recommendation web application built with **React**, **Spring Boot**, **MySQL**, and **Python/FastAPI**.

The application combines **collaborative filtering**, **content-based filtering**, and **sentiment analysis** to generate personalized movie recommendations. It also includes user authentication, ratings and watch history, a personal library, and an admin dashboard for managing the application catalog.

---

## Features

### User features

- Register, log in, and log out
- Session-based authentication using Spring Security
- Password hashing with BCrypt
- Browse and search movies
- Filter movies by genre
- View movie details
- Mark movies as watched
- Rate watched movies from 1 to 5
- View and manage a personal movie library
- Receive personalized movie recommendations
- Responsive UI for desktop, tablet, and mobile

### Admin features

- ADMIN-only dashboard
- Search recommendation-supported movies from the ML catalog
- Add supported movies to the application catalog
- Remove movies when allowed by catalog rules
- View and manage users
- Role-based route and API protection

### Recommendation features

- Collaborative Filtering for user preference modeling
- Content-Based Filtering for movie similarity
- Sentiment Analysis as an additional ranking signal
- Hybrid recommendation ranking
- Personalized recommendations based on logged-in user ratings
- Recommendation-supported catalog validation
- Graceful handling of unknown users, unavailable ML service, and invalid recommendation requests

---

## Architecture

```text
                          ┌─────────────────────┐
                          │    React Frontend   │
                          │      Vite + CSS     │
                          └──────────┬──────────┘
                                     │
                                     │ HTTP / JSON
                                     ▼
                          ┌─────────────────────┐
                          │ Spring Boot Backend │
                          │  REST API + Auth    │
                          └───────┬─────┬───────┘
                                  │     │
                         JPA      │     │ HTTP
                                  │     │
                                  ▼     ▼
                         ┌───────────┐  ┌──────────────────┐
                         │   MySQL   │  │ FastAPI ML API   │
                         │ Database  │  │ Hybrid Recommender│
                         └───────────┘  └────────┬─────────┘
                                               │
                        ┌──────────────────────┼──────────────────────┐
                        ▼                      ▼                      ▼
              Collaborative Filtering   Content-Based         Sentiment
                    50%                      35%                  15%
                        └──────────────────────┼──────────────────────┘
                                               ▼
                                      Hybrid Ranking
                                               ▼
                                      Recommended Movies
```

Sentiment is used as an additional ranking signal rather than being directly responsible for deciding whether a movie should be recommended.

---

## Tech Stack

### Frontend

- React
- Vite
- React Router
- Axios
- CSS
- Vitest
- React Testing Library
- Playwright

### Backend

- Java 21
- Spring Boot
- Spring Web
- Spring Data JPA
- Spring Security
- BCrypt
- MySQL
- Maven
- JUnit
- Mockito

### Machine Learning

- Python 3.10
- FastAPI
- PyTorch
- NumPy
- Pandas
- SciPy
- scikit-learn
- pytest

### Data

- MovieLens
- TMDB metadata
- Movie review sentiment data

---

## Hybrid Recommendation System

The recommendation engine combines three signals.

| Component | Main Responsibility |
|---|---|
| Collaborative Filtering | Learns user preferences from rating behavior |
| Content-Based Filtering | Finds movies with similar characteristics |
| Sentiment Analysis | Adds an audience-reception signal |

The current hybrid weighting is:

```text
Collaborative Filtering : 0.50
Content-Based Filtering : 0.35
Sentiment Analysis       : 0.15
```

### Collaborative Filtering

The collaborative model uses matrix factorization with user and movie embeddings, bias terms, and a learned global rating signal.

### Content-Based Filtering

The content recommender uses movie metadata such as:

- Genres
- Keywords
- Director
- Cast
- Overview
- Tagline

TF-IDF and sparse feature matrices are used to calculate content similarity.

### Sentiment Analysis

Review sentiment is normalized and reliability-adjusted before being added to the final hybrid score. Movies without sufficient review sentiment can fall back to a neutral sentiment value.

---

## Project Structure

```text
Movie-Recommender/
│
├── backend/
│   ├── src/main/java/com/marshal/movierecommender/
│   │   ├── admin/
│   │   ├── config/
│   │   ├── controller/
│   │   ├── dto/
│   │   ├── entity/
│   │   ├── exception/
│   │   ├── recommendation/
│   │   ├── repository/
│   │   └── service/
│   │
│   ├── src/test/
│   ├── pom.xml
│   └── performance-test.ps1
│
├── frontend/
│   ├── e2e/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── services/
│   │   └── test/
│   │
│   ├── package.json
│   └── playwright.config.js
│
├── ml/
│   ├── api/
│   ├── data/
│   ├── models/
│   ├── recommender/
│   ├── scripts/
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
│
├── .gitattributes
├── .gitignore
└── README.md
```

---

## Authentication and Roles

Authentication is intentionally kept straightforward and learning-oriented.

The application uses:

- Spring Security
- Server-side HTTP sessions
- HttpOnly session cookies
- BCrypt password hashing
- `USER` and `ADMIN` roles
- Protected frontend routes
- Protected backend endpoints

No OAuth or refresh-token architecture is required for the current version.

---

## Catalog Rules

The application catalog and ML recommendation catalog are connected deliberately.

An admin can only add a movie to the application catalog if that movie is supported by the recommendation system.

This keeps user ratings aligned with movies that the ML service can understand and use for personalization.

---

## Local Setup

### Prerequisites

Install:

- Java 21
- Maven or use the included Maven Wrapper
- Node.js
- npm
- Python 3.10
- MySQL 8
- Git
- Git LFS

---

## 1. Clone the Repository

```bash
git clone https://github.com/EmCube369/movie-recommender.git
cd Movie-Recommender
```

Make sure Git LFS files are downloaded:

```bash
git lfs pull
```

---

## 2. Configure MySQL

Create a database:

```sql
CREATE DATABASE movie_recommender;
```

Set the database credentials as environment variables.

### Windows PowerShell

```powershell
$env:DB_USERNAME="root"
$env:DB_PASSWORD="your-password"
```

The backend defaults to:

```text
jdbc:mysql://localhost:3306/movie_recommender
```

You can override it using:

```powershell
$env:DB_URL="jdbc:mysql://localhost:3306/movie_recommender"
```

---

## 3. Start the ML Service

Open a terminal:

```powershell
cd ml
```

Create and activate a virtual environment if needed:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start FastAPI:

```powershell
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

The API should be available at:

```text
http://127.0.0.1:8000
```

---

## 4. Start the Spring Boot Backend

Open another terminal:

```powershell
cd backend
```

Run:

```powershell
.\mvnw spring-boot:run
```

The backend defaults to:

```text
http://localhost:8080
```

The ML service URL can be overridden with:

```powershell
$env:ML_SERVICE_BASE_URL="http://127.0.0.1:8000"
```

---

## 5. Start the React Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `DB_URL` | MySQL JDBC connection URL |
| `DB_USERNAME` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `ML_SERVICE_BASE_URL` | FastAPI ML service URL |
| `PORT` | Spring Boot server port when deployed |
| `TMDB_ACCESS_TOKEN` | Used by optional TMDB metadata scripts |

Never commit real passwords, access tokens, or other secrets to the repository.

---

## Running Tests

### Backend

```powershell
cd backend
.\mvnw test
```

The backend test suite covers areas including:

- Authentication
- USER and ADMIN authorization
- Movie CRUD
- User movie activity
- Repository behavior
- Recommendation service
- Recommendation controller
- ML client behavior
- Personalized recommendations

### ML

```powershell
cd ml
pytest
```

The ML tests cover areas including:

- API health
- API validation
- Recommendation behavior
- Error handling
- Runtime loading
- Collaborative filtering
- Content-based recommendations
- Hybrid recommendations
- Sentiment signal
- Edge cases

### Frontend

```powershell
cd frontend
npm test
```

### Lint

```powershell
npm run lint
```

### Production Build

```powershell
npm run build
```

### End-to-End Tests

```powershell
npx playwright test
```

---

## Final Validation Status

The completed project has been validated across the full stack.

```text
Backend Tests : PASS
ML Tests      : PASS
Frontend Tests: PASS
Lint          : PASS
Build         : PASS
E2E Tests     : PASS
```

---

## ML Data and Git LFS

Large raw and training datasets are intentionally excluded from normal Git tracking.

Runtime ML artifacts required by the recommender are stored using **Git LFS**, including model checkpoints and binary feature artifacts.

Examples include:

```text
*.pt
*.npy
*.npz
*.pkl
```

After cloning the repository, run:

```bash
git lfs pull
```

to download the required runtime artifacts.

---

## Screenshots

Add screenshots of the finished application here.

Suggested screenshots:

- Home page
- Movies page
- Movie details page
- Recommendations page
- User profile/library
- Admin dashboard
- Mobile responsive layout

Example structure:

```text
docs/
└── screenshots/
    ├── home.png
    ├── movies.png
    ├── movie-details.png
    ├── recommendations.png
    ├── profile.png
    └── admin-dashboard.png
```

Then reference them in this README:

```markdown
![Home Page](docs/screenshots/home.png)
```

---

## Future Improvements

Possible future additions include:

- Deployment with a public production URL
- Custom domain
- Movie posters and richer metadata
- Recommendation explanations
- Password reset flow
- Email verification
- Improved caching
- More advanced recommendation evaluation
- CI/CD with GitHub Actions

These are intentionally outside the current scope so the project remains understandable and appropriate for a learning-focused full-stack implementation.

---

## Author

**M. Marshal Murmu**

Computer Science graduate focused on Java full-stack development, Spring Boot, React, MySQL, and practical machine learning integration.

---

## Project Status

**Core development complete.**

The current version includes the frontend, backend, authentication, user activity, admin functionality, hybrid recommendation service, automated tests, and end-to-end validation.

Deployment is the next step.
