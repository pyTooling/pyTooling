# =============================================================================
#             _____           _ _
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |
# | |_) | |_| || | (_) | (_) | | | | | | (_| |
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |
# |_|    |___/                          |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Package installer:  A collection of MetaClasses for Python.
#
# License:
# ============================================================================
# Copyright 2017-2021 Patrick Lehmann - Bötzingen, Germany
# Copyright 2007-2016 Technische Universität Dresden - Germany
#                     Chair of VLSI-Design, Diagnostics and Architecture
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#		http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
from ast        import parse as ast_parse, iter_child_nodes, Assign, Constant, Name
from pathlib    import Path
from setuptools import (
	setup as setuptools_setup,
	find_namespace_packages as setuptools_find_namespace_packages
)

gitHubNamespace =       "pyTooling"
projectName =           "pyTooling"
projectNameWithPrefix = f"{projectName}"
__author =              None
__email =               None
__version =             None

# Read __version__ from source file
versionFile = Path(f"{projectName}/Common/__init__.py")
with versionFile.open("r") as file:
	for item in iter_child_nodes(ast_parse(file.read())):
		if isinstance(item, Assign) and len(item.targets) == 1:
			target = item.targets[0]
			value =  item.value
			if isinstance(target, Name) and target.id == "__author__" and isinstance(value, Constant) and isinstance(value.value, str):
				__author = value.value
			if isinstance(target, Name) and target.id == "__email__" and isinstance(value, Constant) and isinstance(value.value, str):
				__email = value.value
			if isinstance(target, Name) and target.id == "__version__" and isinstance(value, Constant) and isinstance(value.value, str):
				__version = value.value
if __version is None:
	raise AssertionError(f"Could not extract '__version__' from '{versionFile}'.")

# Read README for upload to PyPI
readmeFile = Path("README.md")
with readmeFile.open("r") as file:
	long_description = file.read()

# Read requirements file and add them to package dependency list
requirementsFile = Path("requirements.txt")
with requirementsFile.open("r") as file:
	requirements = [line for line in file.readlines()]

# Derive URLs
sourceCodeURL =     f"https://GitHub.com/{gitHubNamespace}/{projectNameWithPrefix}"
documentationURL =  f"https://{gitHubNamespace}.GitHub.io/{projectNameWithPrefix}"

# Assemble all package information
setuptools_setup(
	name=projectNameWithPrefix,
	version=__version,
	author=__author,
	author_email=__email,
	# maintainer="Patrick Lehmann",
	# maintainer_email="Paebbels@gmail.com",
	license='Apache 2.0',

	description="pyTooling is a powerful collection of arbitrary useful classes, decorators, meta-classes and exceptions.",
	long_description=long_description,
	long_description_content_type="text/markdown",

	url=sourceCodeURL,
	project_urls={
		'Documentation': f"{documentationURL}",
		'Source Code':   f"{sourceCodeURL}",
		'Issue Tracker': f"{sourceCodeURL}/issues"
	},

	packages=setuptools_find_namespace_packages(exclude=["doc", "doc.*", "tests", "tests.*",]),
	classifiers=[
		"License :: OSI Approved :: Apache Software License",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Topic :: Utilities"
	],
	keywords="Python3 Exceptions Decorators MetaClasses Versioning Collection",

	python_requires='>=3.6',
	install_requires=requirements,
)
