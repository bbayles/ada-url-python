from os.path import dirname, join
from shlex import split
from sys import platform
from sysconfig import get_config_var
from subprocess import check_call

from cffi import FFI

file_dir = dirname(__file__)

# We need to build ada.cpp and link our CFFI module against it.


class AdaFFIBuilder(FFI):
    def __init__(self, *args, **kwargs):
        self.build_ada_cpp()
        super().__init__(*args, **kwargs)

    def build_ada_cpp(self):
        check_call(
            [
                split(get_config_var('CXX'))[0],
                '-c',
                join(file_dir, 'ada.cpp'),
                '-fPIC',
                '-std=c++17',
                '-O2',
                '-o',
                join(file_dir, 'ada.o'),
            ]
        )


# CFFI uses ada_c.h for its function definitions.

ffi_builder = AdaFFIBuilder()
ffi_builder.set_source(
    'ada_url._ada_wrapper',
    '# include "ada_c.h"',
    include_dirs=[file_dir],
    libraries=['stdc++'] if platform == 'linux' else [],
    extra_objects=[join(file_dir, 'ada.o')],
)

cdef_lines = []
with open(join(file_dir, 'ada_c.h'), 'rt') as f:
    for line in f:
        if not line.startswith('#'):
            cdef_lines.append(line)
ffi_builder.cdef(''.join(cdef_lines))


if __name__ == '__main__':
    ffi_builder.compile()
