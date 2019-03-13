import requests
import requests.exceptions
from requests.auth import HTTPBasicAuth


def get_webpage_with_auth(url, username, password, logger):
    """
    HTTP GET's a URL with basic auth
    :param url: str: The URL to GET
    :param username: str: The username for basic auth
    :param password: str: The password for basic auth
    :param logger: logger obj: The log errors with
    :return: str: The webpage or empty string on error
    """
    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        return response.content
    except requests.exceptions.SSLError as e:
        logger.error('SSL error occurred while trying to retrieve {}\nGot error: {}'.format(url, e))
    except requests.exceptions.BaseHTTPError as e:
        logger.error('HTTP error occurred while trying to retrieve {}\nGot error: {}'.format(url, e))
    except Exception as e:
        logger.error('Unknown error occurred while trying to retrieve {}\nError msg: {}'.format(url, e))
    finally:
        return ''
