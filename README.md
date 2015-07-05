This repository combines all the various tools and libraries needed for building pyzz https://bitbucket.org/sterin/pyzz.

# How to build this tool #

The instructions work on Ubuntu 14.04, minor modifications are required for Ubuntu 12.04.

## Requirements ##

Install the required packages:

    sudo apt-get install -y gcc g++ mercurial make zlib1g-dev python-setuptools python-dev

## Checking out the code ##

This repository uses Mercurial subrepositories to collect a few repositories with the code required to build this tool

    hg clone https://bitbucket.org/sterin/pyzz_build

This will checkout all the relevant subrepositories

## Building the code ##

Change into the newly created `pyzz_build` directory and run the build.sh script

    ./build.sh

This will compile the code and build a gzipped tar with the distribution.

## Building on Ubuntu 12.04

The only change requires is to modify the file `pyzz_build/pyzz/api/MODULE.conf`. Replace `-std=c++11` with `-std=c++0x`.
