#!/bin/bash -eux

# Simple script for setting up all toolchain dependencies for building Helium on macOS

brew install ninja coreutils ccache --overwrite

# Install httplib2 for Python from PyPI
pip3 install httplib2 --break-system-packages
