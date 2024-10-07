import httpx
import logging
from termchat.config import BASE_URL


assert BASE_URL != None



def get_auth_header(chat_id: str):
    HEADERS = {
        "Authorization": f"Device {chat_id}"
    }

    return HEADERS



def get(url: str, params: dict = {}, headers: dict = {}) -> dict:
    URL = BASE_URL + url

    response_json = {}
    
    try:
        with httpx.Client() as client:
            response = client.get(URL, params=params, headers=headers)

            logging.info(response.text)

            response_json = response.json()

    except Exception as error:
        logging.error(str(error))

    return response_json



async def post(url: str, json: dict = {}, headers: dict = {}) -> dict | None:
    URL = BASE_URL + url

    response_json = None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=json, headers=headers)
            
            response.raise_for_status() 

            response_json = response.json()

    except httpx.HTTPStatusError as error:        
        logging.error(str(error))
        return None

    return response_json

