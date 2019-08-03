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
