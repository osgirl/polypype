"""Provides utilities for dealing with polypipe events."""

from cStringIO import StringIO
import ctypes
import io
import os
import struct

from polypype.exceptions import (
    PolyPypeArgumentException,
    PolyPypeFileExistsException,
    PolyPypeOverflowException,
    PolyPypeTypeException,
)

_MAX_C_FLOAT = (2 - 2 ** -23) * 2 ** 127
_MAX_C_UINT32 = 2 ** 32 - 1


class PolyPype(object):
    """Writes polypipe events to a file."""
    def __init__(
            self,
            output_filename,
            append_to_file=False,
            overwrite_file=False
    ):
        file_exists = os.path.isfile(output_filename)
        if (not overwrite_file and file_exists) and \
                (not append_to_file and file_exists):
            raise PolyPypeFileExistsException()
        if append_to_file and overwrite_file:
            raise PolyPypeArgumentException(
                '`append_to_file` and `overwrite_file` cannot both be True.'
            )
        if overwrite_file:
            with io.open(output_filename, 'w'):
                pass
        self.output_filename = output_filename

    def write_event(self, time_delta, params):
        """
        Write a PolyPipe event to the file.

        Arguments:
            time_delta (int): Time delta, in seconds, for the event
            params (list[float]): Parameters for the event
        """
        buf = StringIO()
        try:
            buf.write(struct.pack('<f', ctypes.c_float(time_delta).value))
            if len(params) > _MAX_C_UINT32:
                raise PolyPypeOverflowException('Too many parameters')
            buf.write(struct.pack('<I', ctypes.c_uint32(len(params)).value))
            for param in params:
                if param > _MAX_C_FLOAT:
                    raise PolyPypeOverflowException(
                        'Parameter value too large: {}'.format(param)
                    )
                buf.write(struct.pack('<f', ctypes.c_float(param).value))
        except TypeError as e:
            raise PolyPypeTypeException(e)

        buf.seek(0)
        with io.open(self.output_filename, 'ab') as output_file:
            output_file.write(buf.read())
