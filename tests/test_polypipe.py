"""
TODO:
    - Handle if file already exists
"""
import ctypes
import io
import os
import struct

from contextlib import contextmanager
import ddt
import mock
from unittest2 import TestCase
import tempfile

from polypype import _MAX_C_FLOAT, _MAX_C_UINT32, PolyPype
from polypype.exceptions import (
    PolyPypeArgumentException,
    PolyPypeException,
    PolyPypeFileExistsException,
    PolyPypeOverflowException,
    PolyPypeTypeException,
)


@ddt.ddt
class PolyPypeTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        self.test_filename = 'test_output'
        self.polypype = PolyPype(self.test_filename)
        self.addCleanup(
            self.remove_file_if_exists,
            self.polypype.output_filename
        )

    def remove_file_if_exists(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)

    def assert_next_ctype_equal(self, f, t, expected_value):
        """
        Given an open file, expect that the next 4 bytes are a c_float with the
        expected value.

        Arguments:
            f (file): File to read from
            t (str): `struct` library format string specifying a c type
            expected_value (int, float): Numeric value of the expected c type
        """
        self.assertEqual(
            struct.unpack(t, f.read(4))[0],
            ctypes.c_float(expected_value).value
        )

    @contextmanager
    def open_output_file(self):
        """DRY helper for opening the PolyPype output file."""
        with io.open(self.test_filename, 'rb') as f:
            yield f

    @ddt.data(
        (0.1, [32, 5, 0.7]),
        (0.35, [0]),
        (1, [1, 2, 3]),
        (1, [_MAX_C_FLOAT])
    )
    @ddt.unpack
    def test_write_event(self, time_delta, params):
        self.polypype.write_event(time_delta, params)

        with self.open_output_file() as f:
            self.assert_next_ctype_equal(f, '<f', time_delta)
            self.assert_next_ctype_equal(f, '<I', len(params))
            for param in params:
                self.assert_next_ctype_equal(f, '<f', param)

    @ddt.data(
        (None, [None]),
        ('1', ['1']),
        (list(), [list()]),
        (dict(), [dict()])
    )
    @ddt.unpack
    def test_bad_types(self, time_delta, params):
        with self.assertRaises(PolyPypeTypeException):
            self.polypype.write_event(time_delta, params)

    @ddt.data(list(), dict(), set())
    def test_no_params(self, empty_container):
        time_delta = 1
        self.polypype.write_event(time_delta, empty_container)
        with self.open_output_file() as f:
            self.assert_next_ctype_equal(f, '<f', time_delta)
            self.assert_next_ctype_equal(f, '<I', 0)
            self.assertEqual(f.read(), '')

    def test_too_many_params(self):
        big_list = mock.MagicMock()
        big_list.__len__ = mock.MagicMock(return_value=_MAX_C_UINT32 + 1)
        with self.assertRaises(PolyPypeOverflowException):
            self.polypype.write_event(1, big_list)

    def test_param_too_large(self):
        with self.assertRaises(PolyPypeOverflowException):
            self.polypype.write_event(1, [_MAX_C_FLOAT * 2])

    @mock.patch(
        'polypype.struct.pack',
        mock.Mock(side_effect=PolyPypeException)
    )
    def test_no_event_when_error(self):
        """
        Verify that the event is not written to file if any error occurs.
        """
        try:
            self.polypype.write_event(1, [2])
        except PolyPypeException:
            pass
        self.assertFalse(
            os.path.isfile(self.test_filename),
            'Expected output file not to exist.'
        )

    def test_file_already_exists(self):
        with self.assertRaises(PolyPypeFileExistsException):
            filename = tempfile.mkstemp()[1]
            PolyPype(filename)
        os.remove(filename)

    def test_overwrite_file(self):
        self.polypype.write_event(1, [2])
        new_polypype = PolyPype(self.test_filename, overwrite_file=True)
        new_polypype.write_event(3, [4])
        with self.open_output_file() as f:
            self.assert_next_ctype_equal(f, '<f', 3)
            self.assert_next_ctype_equal(f, '<I', 1)
            self.assert_next_ctype_equal(f, '<f', 4)

    def test_append_to_file(self):
        self.polypype.write_event(1, [2])
        new_polypype = PolyPype(self.test_filename, append_to_file=True)
        new_polypype.write_event(3, [4])
        with self.open_output_file() as f:
            self.assert_next_ctype_equal(f, '<f', 1)
            self.assert_next_ctype_equal(f, '<I', 1)
            self.assert_next_ctype_equal(f, '<f', 2)
            self.assert_next_ctype_equal(f, '<f', 3)
            self.assert_next_ctype_equal(f, '<I', 1)
            self.assert_next_ctype_equal(f, '<f', 4)

    def test_append_and_overwrite(self):
        with self.assertRaises(PolyPypeArgumentException):
            PolyPype(
                self.test_filename,
                append_to_file=True,
                overwrite_file=True
            )
