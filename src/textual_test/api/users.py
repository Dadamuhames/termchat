import requests
import logging


BASE_URL = "http://localhost:3000/api"


async def create_user(data: dict) -> dict | None:
    response_json = None

    try:
        response = requests.post(f"{BASE_URL}/users", data)
        response_json = response.json()
    except requests.RequestException as e:
        logging.error(str(e))

    return response_json
