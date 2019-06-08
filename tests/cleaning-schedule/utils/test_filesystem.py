from tests import HasTempFileTestCaseMixIn, MyTestCase

from cleaning_schedule.utils.filesystem import get_lines_from_file


class TestFilesystem(HasTempFileTestCaseMixIn, MyTestCase):
    def setUp(self):
        self.file_contents = b'banaan\nappel\npeer\nkomkommer'
        self.file_mode = 'wt'
        HasTempFileTestCaseMixIn.setUp(self)
        self.name = 'test_filesystem'
        self.temp_file.write(self.file_contents)
        self.temp_file.flush()

    def test_get_lines_from_file_returns_correct_contents(self):
        ret = get_lines_from_file(self.temp_file.name)
        self.assertEqual(self.file_contents.decode('utf-8').splitlines(), ret)

    def test_get_lines_from_file_throws_IOERROR_on_non_existing_file(self):
        with self.assertRaises(IOError):
            get_lines_from_file('blaaaaaaaaaap')
