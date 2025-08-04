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
# Copyright 2025-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for package :mod:`pyTooling.Versioning`."""
from unittest             import TestCase

from pytest               import mark

from pyTooling.Versioning import SemanticVersion, PythonVersion, CalendarVersion, VersionSet

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_None(self) -> None:
		with self.assertRaises(ValueError):
			_ = VersionSet(None)

	def test_SemVer(self) -> None:
		v = SemanticVersion(1, 0, 0)

		vs = VersionSet(v)

		self.assertEqual(v, vs[0])

	def test_MultipleSemVer(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(1, 5, 0)
		v3 = SemanticVersion(2, 0, 0)

		vs = VersionSet((v2, v3, v1))

		self.assertEqual(v1, vs[0])
		self.assertEqual(v2, vs[1])
		self.assertEqual(v3, vs[2])

	def test_SemVer_CalVer(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = CalendarVersion(2, 0, 0)

		with self.assertRaises(TypeError):
			_ = VersionSet((v1, v2))

	def test_SemVer_PyVer(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = PythonVersion(2, 0, 0)

		vs = VersionSet((v1, v2))

		self.assertEqual(v1, vs[0])
		self.assertEqual(v2, vs[1])

	@mark.xfail(reason="An idea is needed how to check for compatible types in set.")
	def test_PyVer_SemVer(self) -> None:
		v1 = PythonVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		vs = VersionSet((v1, v2))

		self.assertEqual(v1, vs[0])
		self.assertEqual(v2, vs[1])


class Ordering(TestCase):
	def test_Index(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(1, 5, 0)
		v3 = SemanticVersion(2, 0, 0)

		vs = VersionSet((v2, v3, v1))

		previousVersion = vs[0]
		for i, nextVersion in enumerate(vs[1:]):
			self.assertLessEqual(previousVersion, vs[i])
			previousVersion = vs[i]

	def test_Iterator(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(1, 5, 0)
		v3 = SemanticVersion(2, 0, 0)

		vs = VersionSet((v2, v3, v1))

		iterator = iter(vs)
		previousVersion = next(iterator)
		for nextVersion in iterator:
			self.assertLessEqual(previousVersion, nextVersion)
			previousVersion = nextVersion

