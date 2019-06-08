import jinja2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr
from utils.logger import configure_logging

from settings import EMAIL_TEMPLATE

logger = configure_logging(__name__)


class Mail:
    """
    Preform email actions
    """
    def __init__(self, from_address='cleaning-schedule@os3.nl'):
        """
        :param from_address: The email address to send from
        """
        self.logger = logger
        self.template = EMAIL_TEMPLATE
        self.from_address = from_address

    def set_log_level(self, level):
        """
        Set the logger leven of this class instance
        :param level: logging.SOMELEVEL
        """
        self.logger.setLevel(level)

    def render_template(self, **kwargs):
        """
        Render a file template with given args
        :param kwargs: The arguments to pass to the jinja template
        :return: blob: The rendered template (UTF-8 encoded)
        """
        self.logger.debug('Rendering email template from {}'.format(self.template))
        template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        template_env = jinja2.Environment(loader=template_loader)
        template_file = self.template
        template = template_env.get_template(template_file)
        return template.render(**kwargs).encode('utf-8')

    def verify_email_addresses(self, addresses):
        """
        Verify an email address
        TODO: Make this a regex, current method just tries to parse and find a @ sign
        :param addresses: str: The email to verify
        :return: bool: True is valid email, False is not a valid email
        """
        for email in addresses:
            if '@' not in parseaddr(email)[1]:
                self.logger.warning('{} is not a valid email'.format(addresses))
                return False
        return True

    def make_email(self, to, subject, body, cc=None):
        """
        Construct a MIME email message
        :param to: str: The primary email to send to
        :param subject: str: The email subject
        :param body: str(encoded): The email body (html)
        :param cc: list: The email addresses to included as CC's
        :return: str: The formatted MIME email message
        """
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_address
        msg['Subject'] = subject
        msg['To'] = to
        if cc:
            self.logger.info('Sending CC to {}'.format(', '.join(cc)))
            msg['Cc'] = ', '.join(cc)
        msg.attach(MIMEText(body, 'html'))
        return msg.as_string()
