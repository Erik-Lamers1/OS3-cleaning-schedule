from utils.networking import get_webpage_with_auth
from sys import stderr
from bs4 import BeautifulSoup


class Students(object):
    """
    Preform operations on students
    """

    def __init__(self, http_user, http_pass):
        self.year = '2018-2019'
        self.include_unknown_type = True
        self.exclude_playground = True
        self.http_user = http_user
        self.http_pass = http_pass
        self._url = 'https://www.os3.nl/{}/start'.format(self.year)

    def get_all_students(self):
        """
        Get all students listed on os3 webpage of <year>
        :return: list: student names
        """
        students = []
        try:
            webpage = get_webpage_with_auth(self._url, self.http_user, self.http_pass)
        except Exception as e:
            # TODO: Nicer exception handling
            print("Cloudn't get {}\nGot error: {}".format(self._url, e), file=stderr)
            return students

        soup = BeautifulSoup(webpage, "html.parser")
        for a in soup.find_all("a", href=True):
            if '/{}/students'.format(self.year) in a['href']:
                # Dirty hack because the playground link is a "student" link
                if self.exclude_playground and 'playground' in a.text.lower():
                    continue
                students.append(a.text)
        return students
