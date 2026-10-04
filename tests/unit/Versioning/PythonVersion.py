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
Unit tests for :pep:`440`'s alternative spellings in :class:`pyTooling.Versioning.PythonVersion`.

A version keeps the spelling it was parsed from and compares equal to its normalized form;
:meth:`~pyTooling.Versioning.PythonVersion.Normalize` returns the normalized form.
"""
from unittest             import main as unittest_main

from pyTooling.Versioning import PythonVersion, SemanticVersion, ReleaseLevel, VersionValidatorError
from pyTooling.Testing    import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Spellings(Testcase):
	def test_ReleaseCandidate(self) -> None:
		releaseCandidate = PythonVersion.Parse("10.0.0rc1")

		for spelling, expected in (
			("10.0.0rc1",       "10.0.0rc1"),
			("10.0.0-rc1",      "10.0.0rc1"),
			("10.0.0.rc1",      "10.0.0rc1"),
			("10.0.0c1",        "10.0.0c1"),
			("10.0.0-pre1",     "10.0.0pre1"),
			("10.0.0-preview1", "10.0.0preview1")
		):
			with self.subTest(spelling=spelling):
				version = PythonVersion.Parse(spelling)

				self.assertEqual(expected, str(version))
				self.assertEqual(1, version.ReleaseNumber)
				self.assertEqual(releaseCandidate, version)
				self.assertEqual(hash(releaseCandidate), hash(version))
				self.assertEqual("10.0.0rc1", str(version.Normalize()))
				self.assertEqual("10.0.0rc1", str(PythonVersion.Parse(spelling, normalize=True)))

	def test_ReleaseLevelIsKept(self) -> None:
		gamma = PythonVersion.Parse("10.0.0c1")
		preview = PythonVersion.Parse("10.0.0-preview1")

		self.assertIs(ReleaseLevel.Gamma, gamma.ReleaseLevel)
		self.assertIs(ReleaseLevel.ReleaseCandidate, gamma.Normalize().ReleaseLevel)
		self.assertIs(ReleaseLevel.ReleaseCandidate, preview.ReleaseLevel)
		self.assertEqual("preview", preview.ReleaseLevelSpelling)
		self.assertEqual("", preview.Normalize().ReleaseLevelSpelling)

	def test_DevelopmentWithoutNumber(self) -> None:
		for spelling in ("10.0.0-dev", "10.0.0.dev", "10.0.0dev"):
			with self.subTest(spelling=spelling):
				version = PythonVersion.Parse(spelling)

				self.assertEqual("10.0.0-dev", str(version))
				self.assertIs(ReleaseLevel.Development, version.ReleaseLevel)
				self.assertEqual(PythonVersion.Parse("10.0.0.dev0"), version)
				self.assertEqual(hash(PythonVersion.Parse("10.0.0.dev0")), hash(version))
				self.assertNotEqual(PythonVersion.Parse("10.0.0"), version)

				normalized = version.Normalize()
				self.assertEqual("10.0.0.dev0", str(normalized))
				self.assertIs(ReleaseLevel.Final, normalized.ReleaseLevel)
				self.assertEqual(0, normalized.Dev)

	def test_UpperCaseIsNoReleaseLevel(self) -> None:
		for spelling in ("10.0.0-PRE1", "10.0.0-DEV"):
			with self.subTest(spelling=spelling):
				version = PythonVersion.Parse(spelling)

				self.assertIs(ReleaseLevel.Final, version.ReleaseLevel)
				self.assertEqual(spelling[7:], version.Postfix)

	def test_DevelopmentWithLocalVersion(self) -> None:
		version = PythonVersion.Parse("1.0-dev+local")

		self.assertEqual("1.0-dev+local", str(version))
		self.assertEqual("1.0.dev0+local", str(version.Normalize()))

	def test_Ordering(self) -> None:
		versions = [PythonVersion.Parse(v) for v in (
			"1.0.dev0", "1.0a1.dev0", "1.0a1", "1.0b1", "1.0-pre1", "1.0rc2", "1.0", "1.0.post1.dev0", "1.0.post1"
		)]

		for smaller, greater in zip(versions, versions[1:]):
			with self.subTest(smaller=str(smaller), greater=str(greater)):
				self.assertLess(smaller, greater)
				self.assertGreater(greater, smaller)

		self.assertLess(PythonVersion.Parse("1.0-dev"), PythonVersion.Parse("1.0a1"))
		self.assertLessEqual(PythonVersion.Parse("1.0c1"), PythonVersion.Parse("1.0rc1"))
		self.assertGreaterEqual(PythonVersion.Parse("1.0c1"), PythonVersion.Parse("1.0rc1"))

	def test_NormalizeDropsPrefix(self) -> None:
		self.assertEqual("v10.0.0rc1", str(PythonVersion.Parse("v10.0.0-rc1")))
		self.assertEqual("10.0.0rc1", str(PythonVersion.Parse("v10.0.0-rc1", normalize=True)))
		self.assertEqual(PythonVersion.Parse("10.0.0rc1"), PythonVersion.Parse("v10.0.0-rc1"))

	def test_NormalizeKeepsParts(self) -> None:
		self.assertEqual("1!2.0rc1.post3.dev4+local", str(PythonVersion.Parse("1!2.0-pre1.post3.dev4+local").Normalize()))

	def test_ValidatorSeesNormalizedVersion(self) -> None:
		def validator(version: PythonVersion) -> bool:
			return str(version) == "10.0.0rc1"

		self.assertEqual("10.0.0rc1", str(PythonVersion.Parse("10.0.0-pre1", validator, normalize=True)))
		with self.assertRaises(VersionValidatorError):
			PythonVersion.Parse("10.0.0-pre1", validator)

	def test_PostRelease(self) -> None:
		self.assertEqual("10.0.0.post1", str(PythonVersion.Parse("10.0.0-post1")))

	def test_WordsAreNotReleaseCandidates(self) -> None:
		version = PythonVersion.Parse("10.0.0-precise1")

		self.assertIs(ReleaseLevel.Final, version.ReleaseLevel)
		self.assertEqual("10.0.0+precise1", str(version))


class SemanticVersionSpellings(Testcase):
	def test_Preview(self) -> None:
		for spelling, expected in (("10.0.0-pre1", "10.0.0.pre1"), ("10.0.0-preview1", "10.0.0.preview1")):
			with self.subTest(spelling=spelling):
				version = SemanticVersion.Parse(spelling)

				self.assertIs(ReleaseLevel.ReleaseCandidate, version.ReleaseLevel)
				self.assertEqual(expected, str(version))
				self.assertEqual(SemanticVersion.Parse("10.0.0-rc1"), version)

	def test_KeepsItsMeaning(self) -> None:
		self.assertIs(ReleaseLevel.Development, SemanticVersion.Parse("10.0.0-dev").ReleaseLevel)
		self.assertIs(ReleaseLevel.Gamma, SemanticVersion.Parse("10.0.0c1").ReleaseLevel)
		self.assertNotEqual(SemanticVersion.Parse("10.0.0rc1"), SemanticVersion.Parse("10.0.0c1"))

	def test_SpellingIsKept(self) -> None:
		self.assertEqual("1.0.a1", str(SemanticVersion.Parse("1.0a1")))
		self.assertEqual("1.0.alpha1", str(SemanticVersion(1, 0, level=ReleaseLevel.Alpha, number=1)))

	def test_SpellingParameter(self) -> None:
		version = SemanticVersion(1, 0, 0, level=ReleaseLevel.ReleaseCandidate, number=1, spelling="pre")

		self.assertEqual("pre", version.ReleaseLevelSpelling)
		self.assertEqual("1.0.0.pre1", str(version))

		with self.assertRaises(ValueError):
			SemanticVersion(1, 0, 0, level=ReleaseLevel.ReleaseCandidate, number=1, spelling="a")

		with self.assertRaises(ValueError):
			SemanticVersion(1, 0, 0, spelling="rc")

		with self.assertRaises(TypeError):
			SemanticVersion(1, 0, 0, level=ReleaseLevel.ReleaseCandidate, number=1, spelling=1)
