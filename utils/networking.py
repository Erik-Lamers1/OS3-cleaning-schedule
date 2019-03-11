import requests
from requests.auth import HTTPBasicAuth


def get_webpage_with_auth(url, username, password):
    """
    HTTP GET's a URL with basic auth
    :param url: str: The URL to GET
    :param username: str: The username for basic auth
    :param password: str: The password for basic auth
    :return: str: The webpage
    """
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.content
