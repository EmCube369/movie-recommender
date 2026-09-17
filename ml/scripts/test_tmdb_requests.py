import os

import requests
from dotenv import load_dotenv


load_dotenv()

token = os.getenv("TMDB_ACCESS_TOKEN")

session = requests.Session()

# Ignore proxy settings inherited from Windows/environment
session.trust_env = False

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Connection": "close"
}

url = "https://api.themoviedb.org/3/movie/862"

try:
    response = session.get(
        url,
        headers=headers,
        timeout=15
    )

    print("Status:", response.status_code)
    print(response.text[:1000])

except Exception as error:
    print(type(error).__name__)
    print(error)