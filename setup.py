# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import io
import os.path
import sys

import setuptools


REQUIREMENT_DIR = "requirements"
ENCODING = "utf8"

with io.open("README.rst", encoding=ENCODING) as f:
    LONG_DESCRIPTION = f.read()

with io.open(
        os.path.join("docs", "pages", "introduction", "summary.txt"),
        encoding=ENCODING) as f:
    SUMMARY = f.read()

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    INSTALL_REQUIRES = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    TESTS_REQUIRES = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "docs_requirements.txt")) as f:
    DOCS_REQUIRES = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "build_requirements.txt")) as f:
    BUILD_REQUIRES = [line.strip() for line in f if line.strip()]

MODULE_NAME = "tabledata"
SETUPTOOLS_REQUIRES = ["setuptools>=20.2.2"]
NEEDS_PYTEST = set(["pytest", "test", "ptr"]).intersection(sys.argv)
PYTEST_RUNNER_REQUIRES = ["pytest-runner"] if NEEDS_PYTEST else []

setuptools.setup(
    name=MODULE_NAME,
    version="0.0.2",
    url="https://github.com/thombashi/{:s}".format(MODULE_NAME),

    author="Tsuyoshi Hombashi",
    author_email="tsuyoshi.hombashi@gmail.com",
    description=SUMMARY,
    include_package_data=True,
    keywords=[""],
    license="MIT License",
    long_description=LONG_DESCRIPTION,
    packages=setuptools.find_packages(exclude=["test*"]),

    install_requires=SETUPTOOLS_REQUIRES + INSTALL_REQUIRES,
    setup_requires=SETUPTOOLS_REQUIRES + PYTEST_RUNNER_REQUIRES,
    tests_require=TESTS_REQUIRES,
    extras_require={
        "test": TESTS_REQUIRES,
        "docs": DOCS_REQUIRES,
        "build": BUILD_REQUIRES,
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
