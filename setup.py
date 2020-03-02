
import os
import imp
import sys
import platform
import sysconfig
import subprocess
import shutil

from setuptools import setup, Extension
from distutils.command.build_ext import build_ext as _build_ext

source_dir = os.path.dirname(os.path.abspath(__file__))

# build extensions using CMake/Ninja

class build_ext(_build_ext):

    user_options = _build_ext.user_options + [
        ('cmake-generator=', None, "CMake generator"),
        ('cmake-platform=', None, "CMake platform"),
        ('vcpkg-path=', None, "path to vcpkg directory"),
        ('vcpkg-triplet=', None, "vcpkg triplet")
    ]

    def __init__(self, *args, **kwargs):
        _build_ext.__init__(self, *args, **kwargs)

    def initialize_options(self):
        self.cmake_dir = None
        self.install_dir = None
        self.cmake_generator = None
        self.cmake_platform = None
        self.vcpkg_path = None
        self.vcpkg_triplet = None
        _build_ext.initialize_options(self)

    def finalize_options(self):
        _build_ext.finalize_options(self)
        if not self.cmake_generator and platform.system() != 'Windows':
            self.cmake_generator = 'Ninja'
        self.cmake_dir = os.path.abspath(os.path.join(self.build_temp, 'cmake'))
        self.install_dir =  os.path.join(self.cmake_dir, 'install_dir')
        if not os.path.isdir(self.cmake_dir):
            os.makedirs(self.cmake_dir)

    def run(self):

        cmake_options = [
            'cmake'
        ]

        if self.cmake_generator:
            cmake_options.append('-G')
            cmake_options.append(self.cmake_generator)

        if self.cmake_platform:
            cmake_options.append('-A')
            cmake_options.append(self.cmake_platform)

        cmake_options.append('-DCMAKE_INSTALL_PREFIX=%s'%self.install_dir)
        cmake_options.append('-DPYTHON_EXECUTABLE=%s'%sys.executable)

        # ugly workaround
        if sys.platform=='darwin':
            python_library = '%s/libpython%d.%d.dylib'%(
                sysconfig.get_config_var('LIBDIR'),
                sys.version_info.major,
                sys.version_info.minor
            )
            cmake_options.append('-DPYTHON_LIBRARY=%s'%python_library)
            cmake_options.append('-DCMAKE_C_COMPILER=%s'%sysconfig.get_config_var('CC').split(' ')[0])
            cmake_options.append('-DCMAKE_CXX_COMPILER=%s'%sysconfig.get_config_var('CXX').split(' ')[0])

        build_type = 'Debug' if self.debug else 'Release'

        cmake_options.append('-DCMAKE_BUILD_TYPE=%s'%build_type)

        if self.vcpkg_path:
            cmake_options.append('-DCMAKE_TOOLCHAIN_FILE=%s/scripts/buildsystems/vcpkg.cmake'%os.path.abspath(self.vcpkg_path))
            if self.vcpkg_triplet:
                cmake_options.append('-DVCPKG_TARGET_TRIPLET=%s'%self.vcpkg_triplet)

        cmake_options.append(source_dir)

        subprocess.check_call(cmake_options, cwd=self.cmake_dir)
        subprocess.check_call(['cmake', '--build', '.', '--config', build_type], cwd=self.cmake_dir)
        subprocess.check_call(['cmake', '--build', '.', '--config', build_type, '--target', 'install'], cwd=self.cmake_dir)

        suffixes = [ suffix for suffix, mode, type in imp.get_suffixes() if type == imp.C_EXTENSION ]

        for ext in self.extensions:
            dst = self.get_ext_fullpath(ext.name)
            if not os.path.isdir(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
            for suffix in suffixes:
                src = "%s%s"%(os.path.join(self.install_dir, 'lib', *ext.name.split('.')), suffix)
                if os.path.exists(src):
                    shutil.copyfile(src, dst)

setup(
    name = "pyzz",
    version = "0.0.12",
    description = "",
    url="https://github.com/sterin/pyzz-build",
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
