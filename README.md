![.github/workflows/build.yml](https://github.com/sterin/pyzz-build/workflows/.github/workflows/build.yml/badge.svg)


# PyZZ

This repository combines the various tools and libraries needed for building [pyzz](https://bitbucket.org/sterin/pyzz)

# Requirements

* CMake 3.3 or above
* Ninja build tool
* g++ 4.8 or above (or clang with similar levels of C++11 support)
* Python 2.7 with development headers and libraries
* setuptools
* Zlib header files and libraries
* Git

For example, in Ubuntu 16.04, run the following command to satisfy all the requirements:

    sudo apt-get install cmake ninja-build g++ python-dev python-setuptools git zlib1g-dev

Note that the version of CMake included in previous releases of Ubuntu is too old. This requires CMake 3.3 or above to be manually installed.

# How to build this tool #

    python setup.py build

# How to install this tool

    python setup.py install

or (only for the current user)

    python setup.py install --user


## Windows

Building on Windows is more complicated. The simplest way is to use `vcpkg` to gather the dependencies.

### Vcpkg

Clone the repository

    git clone https://github.com/Microsoft/vcpkg

Change into the `vcpkg` directory, and bootstrap

    cd vcpkg
    ./bootstrap-vcpkg.bat

Install the relevant pacakges

    ./vcpkg.exe install dirent:x64-windows-static-md zlib:x64-windows-static-md

Build the extension

    python setup.py \
        build_ext \
            --cmake-platform=x64 \
            --vcpkg-path=vcpkg \
            --vcpkg-triplet=x64-windows-static-md \
        build \
        install
