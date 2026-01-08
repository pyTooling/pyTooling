# ==================================================================================================================== #
#             _____           _ _                                                                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _                                                                          #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |                                                                         #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |                                                                         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |                                                                         #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
Package installer for 'pyTooling is a powerful collection of arbitrary useful classes, decorators, meta-classes and
exceptions.'.
"""
# Add package itself to PYTHON_PATH, so it can be used to package itself.
from os.path    import abspath
from sys        import path as sys_path
sys_path.insert(0, abspath('./pyTooling'))

from setuptools import setup

from pathlib    import Path
from Packaging  import DescribePythonPackageHostedOnGitHub

gitHubNamespace =        "pyTooling"
packageName =            "pyTooling.*"
packageDirectory =       packageName[:-2]
packageInformationFile = Path(f"{packageDirectory}/Common/__init__.py")

setup(
	**DescribePythonPackageHostedOnGitHub(
		packageName=packageName,
		description="pyTooling is a powerful collection of arbitrary useful classes, decorators, meta-classes and exceptions.",
		gitHubNamespace=gitHubNamespace,
		unittestRequirementsFile=Path("tests/requirements.txt"),
		additionalRequirements={
			"pypi":      ["aiohttp >= 3.12", "packaging >= 25.0", "requests >= 2.32"],  # aiohttp limited on MSYS2 to 3.12.x
			"packaging": ["setuptools >= 80.0"],
			"terminal":  ["colorama ~= 0.4.6"],
			"yaml":      ["ruamel.yaml ~= 0.18"],
		},
		sourceFileWithVersion=packageInformationFile,
		pythonVersions=("3.11", "3.12", "3.13", "3.14"),
		dataFiles={
			packageName[:-1] + "Common": ["../py.typed"]
		},
		debug=True
	)
)
