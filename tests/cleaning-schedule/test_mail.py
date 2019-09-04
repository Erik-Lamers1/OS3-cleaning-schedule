from logging import WARNING
from tests import MyTestCase
from os.path import join

from cleaning_schedule.mail import Mail
from cleaning_schedule.settings.base import EMAIL_TEMPLATE, PROJECT_DIR


class TestMailLogLevel(MyTestCase):
    def  setUp(self):
        self.mail = Mail()

    def test_that_logger_set_level_sets_level(self):
        self.mail.set_log_level(WARNING)
        self.assertEqual(self.mail.logger.level, WARNING)


class TestMail(MyTestCase):
    def setUp(self):
        self.jinja = self.set_up_patch('cleaning_schedule.mail.jinja2')
        self.logger = self.set_up_patch('cleaning_schedule.mail.logger')
        self.mail = Mail(from_address='test')

    def test_render_template_calls_correct_functions(self):
        self.mail.render_template()
        self.logger.debug.assert_called_once_with('Rendering email template from {}'.format(EMAIL_TEMPLATE))
        self.jinja.FileSystemLoader.assert_called_once_with(searchpath=join(PROJECT_DIR, "templates"))
        self.jinja.Environment.assert_called_once_with(loader=self.jinja.FileSystemLoader())
        self.jinja.Environment().get_template.assert_called_once_with(EMAIL_TEMPLATE)

    def test_verify_email_addresses_verifies_correct_email_address(self):
        self.assertTrue(self.mail.verify_email_addresses(['test@test.com']))

    def test_verify_email_addresses_does_not_verify_invalid_email_address(self):
        self.assertFalse(self.mail.verify_email_addresses(['test.nl']))

    def test_verify_email_addresses_verifies_multiple_correct_addresses(self):
        self.assertTrue(self.mail.verify_email_addresses(['test@test.com', 'blaap@blaap.com', 'blaap2@blaap.com']))

    def test_verify_email_addresses_does_not_verify_single_faulty_address_in_address_list(self):
        self.assertFalse(self.mail.verify_email_addresses(['test@test.com', 'test2@test.com', 'blaap']))
