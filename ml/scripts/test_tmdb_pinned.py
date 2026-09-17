import os

import certifi
import urllib3
from dotenv import load_dotenv


load_dotenv()

token = os.getenv("TMDB_ACCESS_TOKEN")

if not token:
    raise ValueError("TMDB_ACCESS_TOKEN not found")


pool = urllib3.HTTPSConnectionPool(
    "3.175.86.50",
    port=443,

    # Still tell TLS that we're connecting to api.themoviedb.org
    server_hostname="api.themoviedb.org",
    assert_hostname="api.themoviedb.org",

    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where(),

    timeout=urllib3.Timeout(
        connect=10,
        read=15
    )
)


headers = {
    "Host": "api.themoviedb.org",
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Connection": "close"
}


try:

    response = pool.request(
        "GET",
        "/3/movie/862",
        headers=headers,
        assert_same_host=False
    )

    print("Status:", response.status)

    data = response.json()

    print("Title:", data.get("title"))
    print("Release Date:", data.get("release_date"))
    print("TMDB ID:", data.get("id"))

except Exception as error:

    print(type(error).__name__)
    print(error)

finally:
    pool.close()