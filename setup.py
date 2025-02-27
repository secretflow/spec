# Copyright 2024 Ant Group Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import shutil
import subprocess
import time
from datetime import date

import setuptools
from setuptools import find_packages, setup

this_directory = os.path.abspath(os.path.dirname(__file__))


def long_description():
    with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
        return f.read()


def get_commit_id() -> str:
    commit_id = (
        subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
    )
    dirty = subprocess.check_output(["git", "diff", "--stat"]).decode("ascii").strip()

    if dirty:
        commit_id = f"{commit_id}-dirty"

    return commit_id


def complete_version_file(*filepath):
    today = date.today()
    dstr = today.strftime("%Y%m%d")
    with open(os.path.join(".", *filepath), "r") as fp:
        content = fp.read()

    content = content.replace("$$DATE$$", dstr)
    content = content.replace("$$BUILD_TIME$$", time.strftime("%b %d %Y, %X"))
    try:
        content = content.replace("$$COMMIT_ID$$", get_commit_id())
    except:
        pass

    with open(os.path.join(".", *filepath), "w+") as fp:
        fp.write(content)


def find_version(*filepath):
    complete_version_file(*filepath)
    # Extract version information from filepath
    with open(os.path.join(".", *filepath)) as fp:
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", fp.read(), re.M
        )
        if version_match:
            return version_match.group(1)
        print("Unable to find version string.")
        exit(-1)


def read_requirements():
    with open("requirements.txt") as req_file:
        return req_file.read().splitlines()


# [ref](https://github.com/perwin/pyimfit/blob/master/setup.py)
# Modified cleanup command to remove dist subdirectory
# Based on: https://stackoverflow.com/questions/1710839/custom-distutils-commands
class CleanCommand(setuptools.Command):
    description = "custom clean command that forcefully removes dist directories"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        directories_to_clean = ["./build"]

        for dir in directories_to_clean:
            if os.path.exists(dir):
                shutil.rmtree(dir)


if __name__ == "__main__":
    setup(
        name="secretflow_spec",
        version=find_version("secretflow_spec", "version.py"),
        license="Apache 2.0",
        description="Secretflow spec",
        long_description=long_description(),
        long_description_content_type="text/markdown",
        author="SCI Center",
        author_email="secretflow-contact@service.alipay.com",
        url="https://github.com/secretflow/spec",
        packages=find_packages(exclude=["secretflow_spec.tests"]),
        install_requires=read_requirements(),
        extras_require={"dev": ["pylint"]},
        cmdclass=dict(clean=CleanCommand, cleanall=CleanCommand),
    )
