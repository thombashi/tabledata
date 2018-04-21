# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import io
import os.path
import sys

import setuptools


MODULE_NAME = "tabledata"
REQUIREMENT_DIR = "requirements"
ENCODING = "utf8"

pkg_info = {}


with open(os.path.join(MODULE_NAME, "__version__.py")) as f:
    exec(f.read(), pkg_info)

with io.open("README.rst", encoding=ENCODING) as f:
    LONG_DESCRIPTION = f.read()

with io.open(os.path.join("docs", "pages", "introduction", "summary.txt"), encoding=ENCODING) as f:
    SUMMARY = f.read()

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    INSTALL_REQUIRES = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    TESTS_REQUIRES = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "docs_requirements.txt")) as f:
    DOCS_REQUIRES = [line.strip() for line in f if line.strip()]

SETUPTOOLS_REQUIRES = ["setuptools>=20.2.2"]
NEEDS_PYTEST = set(["pytest", "test", "ptr"]).intersection(sys.argv)
PYTEST_RUNNER_REQUIRES = ["pytest-runner"] if NEEDS_PYTEST else []

setuptools.setup(
    name=MODULE_NAME,
    version=pkg_info["__version__"],
    url="https://github.com/thombashi/{:s}".format(MODULE_NAME),

    author=pkg_info["__author__"],
    author_email=pkg_info["__email__"],
    description=SUMMARY,
    include_package_data=True,
    keywords=[""],
    license=pkg_info["__license__"],
    long_description=LONG_DESCRIPTION,
    packages=setuptools.find_packages(exclude=["test*"]),

    install_requires=SETUPTOOLS_REQUIRES + INSTALL_REQUIRES,
    setup_requires=SETUPTOOLS_REQUIRES + PYTEST_RUNNER_REQUIRES,
    tests_require=TESTS_REQUIRES,
    extras_require={
        "test": TESTS_REQUIRES,
        "build": "wheel",
        "docs": DOCS_REQUIRES,
    },

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ])
