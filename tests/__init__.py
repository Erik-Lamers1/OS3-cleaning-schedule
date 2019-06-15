"""
unittests for cleaning-schedule
"""

import sys
from io import StringIO
from mock import Mock, patch
import unittest
from tempfile import NamedTemporaryFile
import os


class CaptureSysStreamsMixin(object):
    sys_stdout = None
    sys_stderr = None
    stdout = None
    stderr = None

    def capture_sys_streams(self):
        self.sys_stdout = sys.stdout
        self.sys_stderr = sys.stderr

        self.stdout = StringIO()
        self.stderr = StringIO()

        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def restore_sys_streams(self):
        sys.stdout = self.sys_stdout
        sys.stderr = self.sys_stderr


class SysStreamTestCaseMixin(CaptureSysStreamsMixin):
    def capture_auto_restore_sys_streams(self):
        self.capture_sys_streams()
        self.addCleanup(self.restore_sys_streams)

    def setUp(self):
        super(SysStreamTestCaseMixin, self).setUp()
        self.capture_auto_restore_sys_streams()

    def tearDown(self):
        super(SysStreamTestCaseMixin, self).tearDown()
        self.stdout.close()
        self.stderr.close()

    def assertPrintRegexp(self, message):
        self.assertRegex(self.stdout.getvalue(), message)

    def assertPrintRegexpAndExitOK(self, pattern, func, *args, **kwargs):
        with self.assertRaises(SystemExit) as exp:
            func(*args, **kwargs)
        self.assertEqual(exp.exception.code, EX_OK)
        self.assertPrintRegexp(pattern)
        self.assertNoPrintError()

    def assertNoPrint(self):
        self.assertEqual(self.stdout.getvalue(), '')

    def assertPrintErrorRegexp(self, message):
        self.assertRegex(self.stderr.getvalue(), message)

    def assertNoPrintError(self):
        self.assertEqual(self.stderr.getvalue(), '')


class HasTempFileTestCaseMixIn(object):
    temp_file = None
    temp_file_path = ''
    temp_file_mode = 'wb'
    temp_file_prefix = 'cleaning-schedule'

    def _create_temp_file(self):
        # The delete option here is needed to make this work on Windows #oneshouldneverdeveloponwindows
        # https://github.com/deepchem/deepchem/issues/707
        self.temp_file = NamedTemporaryFile(mode=self.temp_file_mode, prefix=self.temp_file_prefix, delete=False)
        self.temp_file_path = self.temp_file.name

    def _clear_temp_file(self):
        try:
            if self.temp_file:
                self.temp_file.close()
            if os.path.exists(self.temp_file_path):
                os.remove(self.temp_file_path)
        except:
            pass

    def setUp(self):
        self._create_temp_file()

    def tearDown(self):
        self._clear_temp_file()


class MyTestCase(unittest.TestCase):
    def set_up_patch(self, topatch, themock=None, **kwargs):
        """Patch a function or class

        :param topatch: string The class to patch
        :param themock: optional object to use as mock
        :return: mocked object
        """
        if themock is None:
            themock = Mock()

        if "return_value" in kwargs:
            themock.return_value = kwargs["return_value"]

        patcher = patch(topatch, themock)
        self.addCleanup(patcher.stop)
        return patcher.start()
