from os import getenv
from logging import getLogger
from requests import post

logger = getLogger(__name__)

def getenv_defined(key: str) -> str:
    env = getenv(key)
    if not env:
        logger.critical(f'Missing environment variable: {key}')
        exit(1)
    return env

def get_bearer_token(base_url: str) -> str:
    CLIENT_TOKEN = getenv_defined('CLIENT_TOKEN')
    REFRESH_TOKEN = getenv_defined('REFRESH_TOKEN')
    PARAMS = { 'provider': 'refresh_token' }
    headers = { 'clientauthorization': f'Bearer {CLIENT_TOKEN}' }
    payload = { 'refresh_token': REFRESH_TOKEN }

    resp_token = post(f'{base_url}/api/loginextended',
                      params=PARAMS, headers=headers, data=payload)
    if resp_token.status_code != 200:
        logger.critical(resp_token.text)
        exit(1)

    return resp_token.json()['access_token']
