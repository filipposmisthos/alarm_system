import requests
from requests.exceptions import Timeout

def connectedToWeb(timeout):
    try:
        request_response = requests.get('http://clients3.google.com/generate_204',timeout=timeout)
        if request_response.status_code!=204:
            return False
        else:
            return True
    except Exception as exc:
        return False