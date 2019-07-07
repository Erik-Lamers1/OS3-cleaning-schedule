"""
unittests for cleaning-schedule
"""

import sys
from io import StringIO
from mock import Mock, patch
import unittest
from tempfile import NamedTemporaryFile
import os

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


class SysStreamCapturingTestCase(CaptureSysStreamsMixin, MyTestCase):
    def capture_sys_streams(self, auto_restore=True):
        CaptureSysStreamsMixin.capture_sys_streams(self)
        if auto_restore:
            self.addCleanup(self.restore_sys_streams)

    def assertPrintRegex(self, message):
        self.assertRegex(self.stdout.getvalue(), message)

    def assertPrintRegexAndExitOK(self, pattern, func, args):
        with self.assertRaises(SystemExit) as exp:
            func(args)
        self.assertEqual(exp.exception.code, os.EX_OK)
        self.assertPrintRegex(pattern)
        self.assertNoPrintError()

    def assertNoPrint(self):
        self.assertEqual(self.stdout.getvalue(), '')

    def assertPrintErrorRegex(self, message):
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
