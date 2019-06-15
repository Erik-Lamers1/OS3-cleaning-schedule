from tests import MyTestCase, SysStreamTestCaseMixin
from logging import WARNING

from cleaning_schedule.os3website import OS3Website


class TestOS3Website(SysStreamTestCaseMixin, MyTestCase):
    def setUp(self):
        super(TestOS3Website, self).setUp()
        self.year = '2019-2020'
        self.get_call = self.set_up_patch('cleaning_schedule.os3website.get_webpage_with_auth')
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

    def test_that_logger_set_level_sets_level(self):
        self.os3website.set_log_level(WARNING)
        self.assertEqual(self.os3website.logger.level, WARNING)

    def test_that_is_os3_website_return_true_if_os3_nl_in_url(self):
        self.assertTrue(self.os3website.is_os3_webpage('blaap.os3.nl/blaap'))

    def test_that_is_os3_website_return_true_if_os3_nl_in_url_even_when_no_slash_present(self):
        self.assertTrue(self.os3website.is_os3_webpage('blaap.os3.nl'))

    def test_that_is_os3_website_return_false_if_os3_nl_not_in_url(self):
        self.assertFalse(self.os3website.is_os3_webpage('blaap.blaap.nl/blaap'))

    def test_that_is_os3_website_return_false_if_os3_nl_in_url_even_when_no_slash_present(self):
        self.assertFalse(self.os3website.is_os3_webpage('blaap.nl'))

    # TODO: Fix stdout capture
    #def test_that_critical_message_is_logged_when_is_os3_nl_webpage_fails(self):
    #    self.os3website.is_os3_webpage('blaap.nl')
    #    self.assertPrintErrorRegexp('cleaning_schedule.os3website CRITICAL {} is not a OS3 url, '
    #                           'we do not want to give your credentials to some random site!'.format('blaap.nl'))
