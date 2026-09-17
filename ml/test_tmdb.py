import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TMDB_ACCESS_TOKEN")

if not token:
    print("TMDB_ACCESS_TOKEN not found.")
    exit()

url = "https://api.themoviedb.org/3/movie/862"

headers = {
    "Authorization": f"Bearer {token}",
    "accept": "application/json"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("Title:", data.get("title"))
    print("Overview:", data.get("overview"))
    print("Release Date:", data.get("release_date"))
else:
    print("Error:", response.text)