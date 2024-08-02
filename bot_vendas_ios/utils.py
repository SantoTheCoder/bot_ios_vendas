#utils.py
import requests
import logging
import random
import string

logger = logging.getLogger(__name__)

def make_request(data, url='https://poisonbrasil.atlasssh.com/core/apiatlas.php'):
    try:
        response = requests.post(url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)}

def generate_random_string(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))