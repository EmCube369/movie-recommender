import os
import ssl
import http.client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TMDB_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Connection": "close"
}

context = ssl.create_default_context()

try:
    conn = http.client.HTTPSConnection(
        "api.themoviedb.org",
        443,
        timeout=15,
        context=context
    )

    conn.request(
        "GET",
        "/3/movie/862",
        headers=headers
    )

    response = conn.getresponse()

    print("Status:", response.status)
    print("Reason:", response.reason)

    data = response.read().decode("utf-8")

    print(data[:1000])

    conn.close()

except Exception as error:
    print(type(error).__name__)
    print(error)