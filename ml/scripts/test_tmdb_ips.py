import os
import socket
import ssl

from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TMDB_ACCESS_TOKEN")

ips = [
    "3.175.86.50",
    "3.175.86.103",
    "3.175.86.37",
    "3.175.86.67"
]

for ip in ips:
    print(f"\nTesting {ip}")

    try:
        sock = socket.create_connection((ip, 443), timeout=10)

        context = ssl.create_default_context()

        secure_sock = context.wrap_socket(
            sock,
            server_hostname="api.themoviedb.org"
        )

        request = (
            "GET /3/movie/862 HTTP/1.1\r\n"
            "Host: api.themoviedb.org\r\n"
            f"Authorization: Bearer {token}\r\n"
            "Accept: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        secure_sock.sendall(request.encode())

        response = secure_sock.recv(1024).decode(
            "utf-8",
            errors="replace"
        )

        print(response.split("\r\n")[0])

        secure_sock.close()

    except Exception as error:
        print(type(error).__name__, error)