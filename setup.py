#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree
from typing import Any, List

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = "kameleoon-openfeature"
FOLDER_NAME = "kameleoon_openfeature"
DESCRIPTION = "OpenFeature Kameleoon Provider."
URL = "https://developers.kameleoon.com/python-sdk.html"
EMAIL = "sdk@kameleoon.com"
AUTHOR = "Kameleoon"
REQUIRES_PYTHON = ">=3.8.0"

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt")) as _file:
    REQUIREMENTS = _file.read().splitlines()

with open(os.path.join(here, "requirements_test.txt")) as _file:
    TEST_REQUIREMENTS = _file.read().splitlines()
    TEST_REQUIREMENTS = list(set(REQUIREMENTS + TEST_REQUIREMENTS))

with open(os.path.join(here, "README.md")) as _file:
    README = _file.read()

try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

__openfeature_version__ = None

project_slug = FOLDER_NAME
with open(os.path.join(here, project_slug, "sdk_version.py")) as _file:
    exec(_file.read())


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options: List[Any] = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        os.environ["TWINE_USERNAME"] = os.getenv("PYPI_USERNAME")
        os.environ["TWINE_PASSWORD"] = os.getenv("PYPI_PASSWORD")

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(__openfeature_version__))
        os.system("git push --tags")

        sys.exit()


setup(
    name=NAME,
    version=__openfeature_version__,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["integration"]),
    install_requires=REQUIREMENTS,
    extras_require={"test": TEST_REQUIREMENTS},
    include_package_data=True,
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    cmdclass={
        "upload": UploadCommand,
    },
)
