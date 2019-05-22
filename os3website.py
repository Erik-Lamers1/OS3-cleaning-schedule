import smtplib
import ssl
from bs4 import BeautifulSoup

from utils.logger import configure_logging
from utils.networking import get_webpage_with_auth

logger = configure_logging(__name__)


class OS3Website(object):
    """
    Preform operations on the OS3 website
    Or send mails from smtp.os3.nl
    """

    def __init__(self, user, password, year='2018-2019'):
        self.include_unknown_type = True
        self.exclude_playground = True
        self.user = user
        self.password = password
        self.year = year
        self.logger = logger
        self._url = 'https://www.os3.nl/{}/start'.format(self.year)
        self._must_be_os3 = True

    def set_log_level(self, level):
        """
        Set the logger leven of this class instance
        :param level: logging.SOMELEVEL
        """
        self.logger.setLevel(level)

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

        webpage = get_webpage_with_auth(self._url, self.user, self.password, self.logger)

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
        self.logger.debug('Getting {}'.format(url))
        return get_webpage_with_auth(url, self.user, self.password, self.logger)

    def get_elements_from_webpage(self, url, element, **kwargs):
        """
        Uses BS to get all elements of a certain type from a OS3 webpage
        :param url: str: The URL of the OS3 webpage to get (without <>)
        :param element: str: The element to search for
        :return:
        """
        webpage = get_webpage_with_auth(url, self.user, self.password, self.logger)
        found_elements = []
        if webpage:
            soup = BeautifulSoup(webpage, "html.parser")
            for element in soup.find_all(element, **kwargs):
                found_elements.append(element.text.strip())
            return found_elements
        else:
            self.logger.warn('OS3 webpage call returned nothing to search for')
            return None

    def send_email(self, sender, to_list, message):
        """
        Tries to send a email message via the OS3 SMTP server
        :param message: The message to send
        :return: True is successful / False is failure
        """
        self.logger.debug('Trying to connect to smtp.os3.nl')
        try:
            server = smtplib.SMTP('smtp.os3.nl', 587)
        #ciphers = 'EECDH+AESGCM:EDH+AESGCM'
        #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        #context.options |= ssl.OP_NO_SSLv2
        #context.options |= ssl.OP_NO_SSLv3
        #context.set_ciphers(ciphers)
        #context.set_default_verify_paths()
        #context.verify_mode = ssl.CERT_REQUIRED
            if server.starttls()[0] != 220:
                self.logger.error('Unable to STARTTLS')
                return False
            server.ehlo()
            server.esmtp_features['auth'] = 'PLAIN LOGIN'
            server.login(self.user, self.password)
            server.sendmail(sender, to_list, message)
            logger.debug('Successfully send email message')
            return True
        except Exception as e:
            logger.error('Unable to send mail, got error: {}'.format(e))
            return False
