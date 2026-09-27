# ==================================================================================================================== #
#             _____           _ _           __     __            _             _                                       #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ \ \   / /__ _ __ ___(_) ___  _ __ (_)_ __   __ _                           #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` \ \ / / _ \ '__/ __| |/ _ \| '_ \| | '_ \ / _` |                          #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |\ V /  __/ |  \__ \ | (_) | | | | | | | | (_| |                          #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/ \___|_|  |___/_|\___/|_| |_|_|_| |_|\__, |                          #
# |_|    |___/                          |___/                                          |___/                           #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :pep:`440`'s alternative spellings in :meth:`pyTooling.Versioning.PythonVersion.Parse`.

:class:`~pyTooling.Versioning.SemanticVersion` keeps its own meaning of ``-dev`` and ``c``; only
:class:`~pyTooling.Versioning.PythonVersion` follows :pep:`440`.
"""
from unittest             import main as unittest_main

from pyTooling.Versioning import PythonVersion, SemanticVersion, ReleaseLevel
from pyTooling.Testing    import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Spellings(Testcase):
	def test_ReleaseCandidate(self) -> None:
		for spelling in ("10.0.0rc1", "10.0.0-rc1", "10.0.0.rc1", "10.0.0c1", "10.0.0-pre1", "10.0.0-preview1", "10.0.0PRE1"):
			with self.subTest(spelling=spelling):
				version = PythonVersion.Parse(spelling)

				self.assertIs(ReleaseLevel.ReleaseCandidate, version.ReleaseLevel)
				self.assertEqual(1, version.ReleaseNumber)
				self.assertEqual("10.0.0rc1", str(version))

	def test_ReleaseCandidateWithPrefix(self) -> None:
		self.assertEqual(PythonVersion.Parse("10.0.0rc1"), PythonVersion.Parse("v10.0.0-rc1"))

	def test_DevelopmentWithoutNumber(self) -> None:
		for spelling in ("10.0.0-dev", "10.0.0.dev", "10.0.0dev", "10.0.0.dev0"):
			with self.subTest(spelling=spelling):
				version = PythonVersion.Parse(spelling)

				self.assertIs(ReleaseLevel.Final, version.ReleaseLevel)
				self.assertEqual(0, version.Dev)
				self.assertEqual("10.0.0.dev0", str(version))

	def test_DevelopmentWithLocalVersion(self) -> None:
		self.assertEqual("1.0.dev0+local", str(PythonVersion.Parse("1.0-dev+local")))

	def test_PostRelease(self) -> None:
		self.assertEqual("10.0.0.post1", str(PythonVersion.Parse("10.0.0-post1")))

	def test_SemanticVersionKeepsItsMeaning(self) -> None:
		self.assertIs(ReleaseLevel.Development, SemanticVersion.Parse("10.0.0-dev").ReleaseLevel)
		self.assertIs(ReleaseLevel.Gamma, SemanticVersion.Parse("10.0.0c1").ReleaseLevel)

	def test_WordsAreNotReleaseCandidates(self) -> None:
		version = PythonVersion.Parse("10.0.0-precise1")

		self.assertIs(ReleaseLevel.Final, version.ReleaseLevel)
		self.assertEqual("10.0.0+precise1", str(version))
