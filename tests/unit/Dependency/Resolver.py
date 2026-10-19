# ==================================================================================================================== #
#             _____           _ _               ____                            _                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  ___ _ __   ___ _ __   __| | ___ _ __   ___ _   _                #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _ \ '_ \ / _ \ '_ \ / _` |/ _ \ '_ \ / __| | | |               #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| |  __/ |_) |  __/ | | | (_| |  __/ | | | (__| |_| |               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \___| .__/ \___|_| |_|\__,_|\___|_| |_|\___|\__, |               #
# |_|    |___/                          |___/             |_|                                     |___/                #
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
"""
Unit tests for :mod:`pyTooling.Dependency.Resolver`, against a package index answering from documents in memory.
"""
from typing                        import Any, Optional as Nullable
from unittest.mock                 import patch

from packaging.requirements        import Requirement

from pyTooling.Dependency          import UnresolvedRequirementWarning
from pyTooling.Dependency.Python   import PythonPackageDependencyGraph, PythonPackageIndex
from pyTooling.Dependency.Resolver import ResolutionStatus, ResolutionStrategy, ResolvedRequirement, Resolver
from pyTooling.Warning             import WarningCollector
from pyTooling.Testing             import Testcase

from tests.unit.Dependency.FakeIndex import DocumentClientSession, DocumentSession, ProjectDocument


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


API = "https://api.index.org/v4/"


def _ReleaseDocument(requirements: list[str], extras: Nullable[list[str]] = None) -> dict:
	"""
	Return the JSON document a package index answers for a release.

	:param requirements: The release's requirements, as in ``requires_dist``.
	:param extras:       Optional, the extras it declares.
	:returns:            The document.
	"""
	return {"info": {"provides_extra": extras, "requires_dist": requirements}}


# app 1.0 -> lib >= 1.0, util, winonly (Windows only); extra "test" -> checker
# lib 1.0, 2.0, 3.0rc1; lib 2.0 -> util >= 1.0; util 1.0 -> nothing
# ping 1.0 -> pong; pong 1.0 -> ping (cycle); old 1.0 only; broken 1.0 can't be described; ghost is unknown
# tool 1.0, extra "fast" -> speedup
DOCUMENTS = {
	"app/json":          ProjectDocument("app", "1.0"),
	"app/1.0/json":      _ReleaseDocument(
		["lib >= 1.0", "util", 'winonly; sys_platform == "win32"', 'checker; extra == "test"'], ["test"]
	),
	"lib/json":          ProjectDocument("lib", "1.0", "2.0", "3.0rc1"),
	"lib/2.0/json":      _ReleaseDocument(["util >= 1.0"]),
	"lib/3.0rc1/json":   _ReleaseDocument([]),
	"util/json":         ProjectDocument("util", "1.0"),
	"util/1.0/json":     _ReleaseDocument([]),
	"winonly/json":      ProjectDocument("winonly", "1.0"),
	"winonly/1.0/json":  _ReleaseDocument([]),
	"checker/json":      ProjectDocument("checker", "1.0"),
	"checker/1.0/json":  _ReleaseDocument([]),
	"ping/json":         ProjectDocument("ping", "1.0"),
	"ping/1.0/json":     _ReleaseDocument(["pong"]),
	"pong/json":         ProjectDocument("pong", "1.0"),
	"pong/1.0/json":     _ReleaseDocument(["ping"]),
	"old/json":          ProjectDocument("old", "1.0"),
	"old/1.0/json":      _ReleaseDocument([]),
	"broken/json":       ProjectDocument("broken", "1.0"),
	"tool/json":         ProjectDocument("tool", "1.0"),
	"tool/1.0/json":     _ReleaseDocument(['speedup; extra == "fast"'], ["fast"]),
	"speedup/json":      ProjectDocument("speedup", "1.0"),
	"speedup/1.0/json":  _ReleaseDocument([])
}


class ResolverTestcase(Testcase):
	"""Base of the resolver tests: an index answering :data:`DOCUMENTS`, asynchronous requests included."""

	def setUp(self) -> None:
		DocumentClientSession.Documents = DOCUMENTS
		DocumentClientSession.Sessions =  []
		self._patch = patch("pyTooling.Dependency.Resolver.ClientSession", DocumentClientSession)
		self._patch.start()

	def tearDown(self) -> None:
		self._patch.stop()

	@staticmethod
	def _Index() -> PythonPackageIndex:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", API, graph=graph)
		index._session = DocumentSession(API, DOCUMENTS)
		return index

	@staticmethod
	def _Tree(requirements: tuple[ResolvedRequirement, ...]) -> list[tuple[Any, ...]]:
		"""Name, status, selected version and dependencies of each requirement, walked depth-first."""
		return [
			(
				requirement.Requirement.name,
				requirement.Status,
				None if requirement.Release is None else str(requirement.Release.Version),
				ResolverTestcase._Tree(requirement.Dependencies) if requirement.Status is ResolutionStatus.Resolved else []
			)
			for requirement in requirements
		]


class Strategy(ResolverTestcase):
	def test_Parse(self) -> None:
		self.assertIs(ResolutionStrategy.Lazy, ResolutionStrategy.Parse(None))
		self.assertIs(ResolutionStrategy.Eager, ResolutionStrategy.Parse("eager"))

	def test_Lazy(self) -> None:
		"""Only the given requirements are resolved; a release's requirements when first asked for."""
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("lib >= 1.0")])
		lib = resolution.Requirements[0]

		self.assertIs(ResolutionStatus.Resolved, lib.Status)
		self.assertIsNone(lib._dependencies)

		util = lib.Dependencies[0]

		self.assertEqual("util", util.Requirement.name)
		self.assertIs(ResolutionStatus.Resolved, util.Status)
		self.assertIs(lib, util.Parent)
		self.assertEqual(1, util.Level)

	def test_Eager(self) -> None:
		"""Every level is resolved up front; the downloads of a level share one session."""
		resolution = Resolver(self._Index(), strategy=ResolutionStrategy.Eager).ResolveRequirements([Requirement("lib")])

		self.assertIsNotNone(resolution.Requirements[0]._dependencies)
		sessions = [session.Requests for session in DocumentClientSession.Sessions]
		self.assertIn(["util/json"], sessions)
		self.assertIn(["util/1.0/json"], sessions)

	def test_EagerEqualsLazy(self) -> None:
		requirements = [Requirement("app"), Requirement("ping")]

		lazy =  Resolver(self._Index(), strategy=ResolutionStrategy.Lazy).ResolveRequirements(requirements)
		eager = Resolver(self._Index(), strategy=ResolutionStrategy.Eager).ResolveRequirements(requirements)

		self.assertListEqual(self._Tree(eager.Requirements), self._Tree(lazy.Requirements))

	def test_ParallelLevel(self) -> None:
		"""The projects of one level are downloaded over one session, then the releases over another."""
		Resolver(self._Index()).ResolveRequirements([Requirement("lib"), Requirement("util"), Requirement("old")])

		self.assertEqual(2, len(DocumentClientSession.Sessions))
		self.assertListEqual(["lib/json", "util/json", "old/json"], DocumentClientSession.Sessions[0].Requests)
		self.assertListEqual(["lib/2.0/json", "util/1.0/json", "old/1.0/json"], DocumentClientSession.Sessions[1].Requests)


class Selection(ResolverTestcase):
	def test_NewestMatching(self) -> None:
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("lib < 2.0")])

		self.assertEqual("1.0", str(resolution.Requirements[0].Release.Version))

	def test_PreReleaseSkipped(self) -> None:
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("lib")])

		self.assertEqual("2.0", str(resolution.Requirements[0].Release.Version))

	def test_PreReleaseAskedFor(self) -> None:
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("lib >= 3.0rc1")])

		self.assertEqual("3.0rc1", str(resolution.Requirements[0].Release.Version))

	def test_PreReleaseOnly(self) -> None:
		"""If only a pre-release matches, it's selected."""
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("lib > 2.0")])

		self.assertEqual("3.0rc1", str(resolution.Requirements[0].Release.Version))

	def test_NoMatchingRelease(self) -> None:
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("old >= 2.0")])
		old = resolution.Requirements[0]

		self.assertIs(ResolutionStatus.NoMatchingRelease, old.Status)
		self.assertEqual("old", old.Project.Name)
		self.assertIsNone(old.Release)

	def test_SameProjectTwice(self) -> None:
		"""A later requirement of a project replaces the earlier one, in its position."""
		resolution = Resolver(self._Index()).ResolveRequirements(
			[Requirement("lib"), Requirement("util"), Requirement("Lib < 2.0")]
		)

		self.assertListEqual(["Lib", "util"], [requirement.Requirement.name for requirement in resolution.Requirements])
		self.assertEqual("1.0", str(resolution.Requirements[0].Release.Version))

	def test_Graph(self) -> None:
		"""The selected releases are connected in the index's dependency graph."""
		index = self._Index()
		resolution = Resolver(index, strategy=ResolutionStrategy.Eager).ResolveRequirements([Requirement("lib")])
		lib =  resolution.Requirements[0]
		util = lib.Dependencies[0]

		self.assertIn(util.Release, lib.Release._dependsOn[util.Project].values())


class Unresolved(ResolverTestcase):
	def test_UnknownProject(self) -> None:
		index = self._Index()

		with WarningCollector() as warnings:
			resolution = Resolver(index).ResolveRequirements([Requirement("ghost")])

		ghost = resolution.Requirements[0]
		self.assertIs(ResolutionStatus.UnknownProject, ghost.Status)
		self.assertIsNone(ghost.Project)
		self.assertTupleEqual(("ghost", ), index.UnknownProjects)

		unresolved = [warning for warning in warnings.Warnings if isinstance(warning, UnresolvedRequirementWarning)]
		self.assertEqual(1, len(unresolved))
		self.assertEqual("ghost", unresolved[0].ProjectName)
		self.assertIsNone(unresolved[0].Version)

	def test_UndescribedRelease(self) -> None:
		with WarningCollector() as warnings:
			resolution = Resolver(self._Index()).ResolveRequirements([Requirement("broken")])

		broken = resolution.Requirements[0]
		self.assertIs(ResolutionStatus.UndescribedRelease, broken.Status)
		self.assertEqual("1.0", str(broken.Release.Version))
		self.assertTupleEqual((), broken.Dependencies)

		unresolved = [warning for warning in warnings.Warnings if isinstance(warning, UnresolvedRequirementWarning)]
		self.assertEqual(1, len(unresolved))
		self.assertEqual("broken", unresolved[0].ProjectName)
		self.assertEqual("1.0", str(unresolved[0].Version))

	def test_Cycle(self) -> None:
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("ping")])
		ping = resolution.Requirements[0]
		pong = ping.Dependencies[0]
		cycle = pong.Dependencies[0]

		self.assertIs(ResolutionStatus.Resolved, pong.Status)
		self.assertIs(ResolutionStatus.Cycle, cycle.Status)
		self.assertIs(ping.Release, cycle.Release)
		self.assertTupleEqual((), cycle.Dependencies)
		self.assertIn(ping.Release, pong.Release._dependsOn[ping.Project].values())


class Limit(ResolverTestcase):
	"""The limit counts the levels resolved below the given requirements: app (0), lib (1), util (2)."""

	def _App(self, limit: Nullable[int]) -> ResolvedRequirement:
		return Resolver(self._Index(), limit=limit).ResolveRequirements([Requirement("app")]).Requirements[0]

	@staticmethod
	def _Lib(app: ResolvedRequirement) -> ResolvedRequirement:
		return next(app.IterateDependencies(lambda requirement: requirement.Requirement.name == "lib"))

	def test_Unlimited(self) -> None:
		app = self._App(None)
		lib = self._Lib(app)

		self.assertIs(ResolutionStatus.Resolved, app.Status)
		self.assertIs(ResolutionStatus.Resolved, lib.Status)
		self.assertIs(ResolutionStatus.Resolved, lib.Dependencies[0].Status)

	def test_Zero(self) -> None:
		"""Only the given requirements are resolved; their dependencies are listed, but not looked up."""
		app = self._App(0)
		lib = self._Lib(app)

		self.assertIs(ResolutionStatus.Resolved, app.Status)
		self.assertIs(ResolutionStatus.LimitReached, lib.Status)
		self.assertIsNone(lib.Project)
		self.assertTupleEqual((), lib.Dependencies)

	def test_One(self) -> None:
		lib = self._Lib(self._App(1))

		self.assertIs(ResolutionStatus.Resolved, lib.Status)
		self.assertIs(ResolutionStatus.LimitReached, lib.Dependencies[0].Status)

	def test_Two(self) -> None:
		lib = self._Lib(self._App(2))

		self.assertIs(ResolutionStatus.Resolved, lib.Dependencies[0].Status)


class ParameterChecks(ResolverTestcase):
	def test_Index(self) -> None:
		with self.assertRaises(ValueError) as context:
			Resolver(None)

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			Resolver("index")

		self.assertEqual("Parameter 'index' is not of type 'PythonPackageIndex'.", str(context.exception))

	def test_Strategy(self) -> None:
		with self.assertRaises(ValueError):
			Resolver(self._Index(), strategy=None)

		with self.assertRaises(TypeError):
			Resolver(self._Index(), strategy="lazy")

	def test_Limit(self) -> None:
		with self.assertRaises(TypeError):
			Resolver(self._Index(), limit="1")

		with self.assertRaises(TypeError):
			Resolver(self._Index(), limit=True)

		with self.assertRaises(ValueError) as context:
			Resolver(self._Index(), limit=-1)

		self.assertEqual("Parameter 'limit' is negative.", str(context.exception))

	def test_Requirements(self) -> None:
		resolver = Resolver(self._Index())

		with self.assertRaises(ValueError):
			resolver.ResolveRequirements(None)

		with self.assertRaises(TypeError):
			resolver.ResolveRequirements(5)

		with self.assertRaises(TypeError):
			resolver.ResolveRequirements(["lib"])
