import requests.exceptions
from sys import stderr
from bs4 import BeautifulSoup

from utils.logger import configure_logging
from utils.networking import get_webpage_with_auth


class OS3Website(object):
    """
    Preform operations on the OS3 website
    """

    def __init__(self, http_user, http_pass, year='2018-2019', logger=None):
        self.include_unknown_type = True
        self.exclude_playground = True
        self.http_user = http_user
        self.http_pass = http_pass
        self.year = year
        self.logger = logger or configure_logging(__name__)
        self._url = 'https://www.os3.nl/{}/start'.format(self.year)
        self._must_be_os3 = True

    def _is_os3_webpage(self, url):
        """
        Checks if URL is actually an os3.nl URL, only when _must_be_os3 is set to false will it pass on non os3.nl
        :param url: The URL
        :return: True if os3.nl or _must_be_os3 == False else False
        """
        if 'os3.nl' in url.lower():
            return True
        elif not self._must_be_os3:
            self.logger.info('{} is not a OS3 url, But exception is accepted for this instance')
            return True
        else:
            self.logger.critical('{} is not a OS3 url, we do not want to give your credentials to some random site!')
            return False

    def get_all_students(self):
        """
        Get all students listed on os3 webpage of <year>
        :return: list: student names
        """
        students = []
        if not self._is_os3_webpage(self._url):
            return students

        webpage = get_webpage_with_auth(self._url, self.http_user, self.http_pass, self.logger)

        soup = BeautifulSoup(webpage, "html.parser")
        for a in soup.find_all("a", href=True):
            if '/{}/students'.format(self.year) in a['href']:
                # Dirty hack because the playground link is a "student" link
                if self.exclude_playground and 'playground' in a.text.lower():
                    self.logger.debug('Found playground link in student links, skipping...')
                    continue
                students.append(a.text.strip())
        return students

    def get_url(self, url):
        """
        Get a URL from the OS3 website
        :param url: The URL to get
        :return: str: The URLs content
        """
        if not self._is_os3_webpage(url):
            return None
        return get_webpage_with_auth(url, self.http_user, self.http_pass, self.logger)

    def get_elements_from_webpage(self, url, element, **kwargs):
        """
        Uses BS to get all elements of a certain type from a OS3 webpage
        :param url: str: The URL of the OS3 webpage to get
        :param element: str: The element to search for
        :return:
        """
        webpage = get_webpage_with_auth(url, self.http_user, self.http_pass, self.logger)
        if webpage:
            soup = BeautifulSoup(webpage, "html.parser")
            return soup.find_all(element, **kwargs)
        else:
            self.logger.warn('OS3 webpage call returned nothing to search for')
            return None
