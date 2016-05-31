
import os
import sys
import sysconfig
import subprocess
import shutil

from setuptools import setup, Extension
from distutils.command.build_ext import build_ext as _build_ext

source_dir = os.path.dirname(os.path.abspath(__file__))

# build extensions using CMake/Ninja

class build_ext(_build_ext):

    def __init__(self, *args, **kwargs):
        _build_ext.__init__(self, *args, **kwargs)

    def initialize_options(self):
        self.cmake_dir = None
        self.install_dir = None
        _build_ext.initialize_options(self)

    def finalize_options(self):
        _build_ext.finalize_options(self)
        self.cmake_dir = os.path.abspath(os.path.join(self.build_temp, 'cmake'))
        self.install_dir =  os.path.join(self.cmake_dir, 'install_dir')
        if not os.path.isdir(self.cmake_dir):
            os.makedirs(self.cmake_dir)

    def run(self):

        cmake_options = [
            'cmake',
            '-G', 'Ninja',
            '-DCMAKE_INSTALL_PREFIX=%s'%self.install_dir,
            '-DCMAKE_C_COMPILER=%s'%sysconfig.get_config_var('CC'),
            '-DCMAKE_CXX_COMPILER=%s'%sysconfig.get_config_var('CXX'),
            '-DPYTHON_EXECUTABLE=%s'%sys.executable,
        ]

        # ugly workaround
        if sys.platform=='darwin':
            python_library = '%s/libpython%d.%d.dylib'%(
                sysconfig.get_config_var('LIBDIR'),
                sys.version_info.major,
                sys.version_info.minor
            )
            cmake_options.append('-DPYTHON_LIBRARY=%s'%python_library)

        if self.debug:
            cmake_options.append('-DCMAKE_BUILD_TYPE=Debug')
        else:
            cmake_options.append('-DCMAKE_BUILD_TYPE=Release')

        cmake_options.append(source_dir)

        subprocess.check_call(cmake_options, cwd=self.cmake_dir)
        subprocess.check_call(['ninja'], cwd=self.cmake_dir)
        subprocess.check_call(['ninja', 'install'], cwd=self.cmake_dir)

        for ext in self.extensions:
            src = "%s.so"%os.path.join(self.install_dir, 'lib', *ext.name.split('.'))
            dst = self.get_ext_fullpath(ext.name)
            if not os.path.isdir(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
            shutil.copyfile(src, dst)

setup(
    name = "PyZZ",
    version = "0.0.1",
    description = "",
    url="https://bitbucket.org/sterin/pyzz_build",
    author='Baruch Sterin',
    author_email='pyzz@bsterin.com',
    license="MIT/BSD-like",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'License :: Freely Distributable',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
    keywords = '',
    packages = [
        'pyzz',
    ],
    package_dir={
        'pyzz':'pyzz/pyzz',
    },
    include_package_data = True,
    zip_safe = False,
    cmdclass = dict(build_ext=build_ext),
    ext_modules = [Extension('pyzz._pyzz', [])],
)
