from tests import MyTestCase
from os.path import isfile

from cleaning_schedule.settings.base import MAX_WEBSITE_RETRIES, CLEANING_TASK_LIST_URL, EMAIL_TEMPLATE


class TestSettings(MyTestCase):
    def test_that_max_website_retries_is_an_int(self):
        self.assertIs(type(MAX_WEBSITE_RETRIES), int)

    def test_that_max_website_retries_does_not_exceed_10(self):
        self.assertLessEqual(MAX_WEBSITE_RETRIES, 10)

    def test_that_cleaning_task_list_url_contains_os3(self):
        self.assertIn('os3.nl', CLEANING_TASK_LIST_URL)

    def test_that_cleaning_task_list_url_is_a_string(self):
        self.assertIs(type(CLEANING_TASK_LIST_URL), str)

    def test_that_email_template_is_a_string(self):
        self.assertIs(type(EMAIL_TEMPLATE), str)

    def test_that_email_template_is_located_in_template_dir(self):
        self.assertTrue(isfile('cleaning_schedule/templates/{}'.format(EMAIL_TEMPLATE)))
