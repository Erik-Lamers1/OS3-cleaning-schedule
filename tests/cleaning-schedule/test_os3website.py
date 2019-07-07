from tests import MyTestCase
from logging import WARNING

from cleaning_schedule.os3website import OS3Website


class TestOS3WebsiteLogLevel(MyTestCase):
    def setUp(self):
        self.year = '2019-2020'
        self.os3website = OS3Website('henk', 'henkpw', self.year)

    def test_that_logger_set_level_sets_level(self):
        self.os3website.set_log_level(WARNING)
        self.assertEqual(self.os3website.logger.level, WARNING)


class TestOS3Website(MyTestCase):
    def setUp(self):
        self.year = '2019-2020'
        self.get_call = self.set_up_patch('cleaning_schedule.os3website.get_webpage_with_auth')
        self.logger = self.set_up_patch('cleaning_schedule.os3website.logger')
        self.os3website = OS3Website('henk', 'henkpw', self.year)

    def test_that_class_user_gets_set_to_passed_user_var(self):
        self.assertEqual(self.os3website.user, 'henk')

    def test_that_class_password_gets_set_to_passed_password_var(self):
        self.assertEqual(self.os3website.password, 'henkpw')

    def test_that_class_year_gets_set_to_passed_year_var(self):
        self.assertEqual(self.os3website.year, '2019-2020')

    def test_that_exclude_playground_is_set_to_true_by_default(self):
        self.assertTrue(self.os3website.exclude_playground)

    def test_that_url_formats_year_into_url(self):
        self.assertEqual(self.os3website._url, 'https://www.os3.nl/{}/start'.format(self.year))

    def test_that__must_be_os3_is_set_to_true_by_default(self):
        self.assertTrue(self.os3website._must_be_os3)

    def test_that_is_os3_website_return_true_if_os3_nl_in_url(self):
        self.assertTrue(self.os3website.is_os3_webpage('https://blaap.os3.nl/blaap'))

    def test_that_is_os3_website_return_true_if_os3_nl_in_url_even_when_no_slash_present(self):
        self.assertTrue(self.os3website.is_os3_webpage('https://blaap.os3.nl'))

    def test_that_is_os3_website_return_false_if_os3_nl_not_in_url(self):
        self.assertFalse(self.os3website.is_os3_webpage('https://blaap.blaap.nl/blaap'))

    def test_that_is_os3_website_return_false_if_os3_nl_in_url_even_when_no_slash_present(self):
        self.assertFalse(self.os3website.is_os3_webpage('https://blaap.nl'))

    def test_that_critical_message_is_logged_when_is_os3_nl_webpage_fails(self):
        self.os3website.is_os3_webpage('https://blaap.nl')
        self.logger.critical.assert_called_once_with('https://blaap.nl is not a OS3 url, '
                                                     'we do not want to give your credentials to some random site!')

    def test_that_critical_message_is_logged_when_is_os3_nl_webpage_fails_to_parse(self):
        self.https_checks = self.set_up_patch('cleaning_schedule.os3website.https_in_url')
        self.https_checks.return_value = True
        self.assertFalse(self.os3website.is_os3_webpage('blaaaap'))
        self.logger.error.assert_called_once_with('Could not parse blaaaap, are you using https://?')

    def test_that_if__must_be_os3_is_set_to_false_other_valid_url_passes(self):
        self.os3website._must_be_os3 = False
        self.assertTrue(self.os3website.is_os3_webpage('https://blaap.nl'))
        self.logger.info.assert_called_once_with('https://blaap.nl is not a OS3 url, '
                                                 'But exception is accepted for this instance')
