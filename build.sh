#!/bin/bash

setup_version()
{
    if [ -z "${PYZZ_VERSION}" ]; then
        PYZZ_VERSION=$(hg log -l1 --template='{rev}')
    fi

    if [ -z "${PYZZ_PREFIX}" ]; then
        PYZZ_PREFIX=pyzz_distribution
    fi

    DIR=${PYZZ_PREFIX}
    TGZ=${PYZZ_PREFIX}.${PYZZ_VERSION}${PYZZ_PLATFORM}.tgz
}

setup_python()
{
    if [ -z "${PYZZ_PYTHON}" ]; then
        PYZZ_PYTHON=/usr/bin/python
        SYSTEM=
    else
        SYSTEM=--system
    fi
}

print_versions()
{
    echo =================================================
    cat .hgsubstate
    echo =================================================
}

build_pyzz()
{
    pushd pyzz/api

    ${PYZZ_PYTHON} build.py release
    strip pyzz/_pyzz.so

    popd
}

create_package()
{
    if [ -f ${TGZ} ]; then
        echo "Removing ${TGZ}"
        rm ${TGZ}
    fi

    ${PYZZ_PYTHON} package.py \
        \
        --out=${TGZ} \
        --dir=${PYZZ_PREFIX} \
        \
        --lib=pyzz/api/pyzz \
        \
        --files=abc-zz/LICENSE:licenses/abc-zz_LICENSE \
        --files=abc-zz/README:licenses/abc-zz_README \
        --files=distribution_LICENSE:licenses/LICENSE \
        \
        --files=README.md:README.md \
        \
        ${SYSTEM}
}

open_package()
{
    if [ -d ${DIR} ]; then
    	echo "Removing ${DIR}"
    	\rm -rf ${DIR}
    fi

    tar xvzf ${TGZ}
}

set -e

setup_version
setup_python

print_versions

build_pyzz

create_package
open_package
