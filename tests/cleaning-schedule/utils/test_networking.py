from tests import MyTestCase

from cleaning_schedule.utils.networking import https_in_url


class TestNetworking(MyTestCase):
    def test_that_https_in_url_returns_true_if_url_startswith_https(self):
        self.assertTrue(https_in_url('https://blaap.nl'))

    def test_that_https_in_url_returns_false_if_url_does_not_start_with_https(self):
        self.assertFalse(https_in_url('http://blaap.nl'))
