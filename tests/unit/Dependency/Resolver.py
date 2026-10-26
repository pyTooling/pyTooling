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
from pathlib                       import Path
from tempfile                      import TemporaryDirectory
from time                          import sleep
from typing                        import Any, Optional as Nullable
from unittest.mock                 import patch

from aiohttp                       import ClientConnectionError
from packaging.markers             import default_environment
from packaging.requirements        import Requirement

from pyTooling.Dependency          import BrokenRequirementWarning, DependencyError, ExtraNotFoundError, \
                                          UndeclaredExtraWarning, PackageIndexFailureWarning, ReleaseNotFoundError, \
                                          ResolutionTimeoutWarning, UnresolvedRequirementWarning
from pyTooling.Dependency.Python   import PythonPackageDependencyGraph, PythonPackageIndex, RequirementsFile
from pyTooling.Dependency.Resolver import CurrentEnvironmentResolver, PreReleasePolicy, Resolution, ResolutionStatus, \
                                          ResolutionStrategy, ResolvedRequirement, Resolver
from pyTooling.Timeout             import Timeout
from pyTooling.Warning             import UnhandledCriticalWarningError, WarningCollector
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
# tool 1.0, extra "fast" -> speedup; speedup 1.0 -> accel; empty has no release
# flaky answers 503, offline fails to connect; shaky 1.0 answers 500 for its release
# slow times out; lagging 1.0 times out for its release
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
	"speedup/1.0/json":  _ReleaseDocument(["accel"]),
	"accel/json":        ProjectDocument("accel", "1.0"),
	"accel/1.0/json":    _ReleaseDocument([]),
	"empty/json":        ProjectDocument("empty"),
	"flaky/json":        503,
	"offline/json":      ClientConnectionError("Connection refused"),
	"shaky/json":        ProjectDocument("shaky", "1.0"),
	"shaky/1.0/json":    500,
	"slow/json":         TimeoutError("Timed out."),
	"lagging/json":      ProjectDocument("lagging", "1.0"),
	"lagging/1.0/json":  TimeoutError("Timed out.")
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

	def test_PreReleasePolicy_Parse(self) -> None:
		self.assertIs(PreReleasePolicy.Exclude, PreReleasePolicy.Parse("exclude"))
		self.assertIs(PreReleasePolicy.Include, PreReleasePolicy.Parse("include"))
		self.assertIs(PreReleasePolicy.Exclude, PreReleasePolicy.DEFAULT)

	def test_PreReleasePolicy_Exclude(self) -> None:
		"""A requirement naming a pre-release selects it, also with pre-releases excluded."""
		resolver = Resolver(self._Index(), preReleases=PreReleasePolicy.Exclude)
		resolution = resolver.ResolveRequirements([Requirement("lib")])

		self.assertIs(PreReleasePolicy.Exclude, resolver.PreReleases)
		self.assertEqual("2.0", str(resolution.Requirements[0].Release.Version))

		resolution = resolver.ResolveRequirements([Requirement("lib >= 3.0rc1")])

		self.assertEqual("3.0rc1", str(resolution.Requirements[0].Release.Version))

	def test_PreReleasePolicy_Include(self) -> None:
		resolver = Resolver(self._Index(), preReleases=PreReleasePolicy.Include)
		resolution = resolver.ResolveRequirements([Requirement("lib")])

		self.assertIs(PreReleasePolicy.Include, resolver.PreReleases)
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

	def test_IndexFailure_Project(self) -> None:
		"""A server error for a project is a status and a critical warning carrying the status code."""
		with WarningCollector() as warnings:
			resolution = Resolver(self._Index()).ResolveRequirements([Requirement("flaky")])

		flaky = resolution.Requirements[0]
		self.assertIs(ResolutionStatus.IndexFailure, flaky.Status)
		self.assertIsNone(flaky.Release)

		failures = [warning for warning in warnings.Warnings if isinstance(warning, PackageIndexFailureWarning)]
		self.assertEqual(1, len(failures))
		self.assertEqual("flaky", failures[0].ProjectName)
		self.assertIsNone(failures[0].Version)
		self.assertEqual(503, failures[0].StatusCode)

	def test_IndexFailure_Network(self) -> None:
		"""A failed connection is a status and a critical warning without a status code, caused by the exception."""
		with WarningCollector() as warnings:
			resolution = Resolver(self._Index()).ResolveRequirements([Requirement("offline")])

		self.assertIs(ResolutionStatus.IndexFailure, resolution.Requirements[0].Status)

		failures = [warning for warning in warnings.Warnings if isinstance(warning, PackageIndexFailureWarning)]
		self.assertEqual(1, len(failures))
		self.assertIsNone(failures[0].StatusCode)
		self.assertIsInstance(failures[0].__cause__, ClientConnectionError)

	def test_IndexFailure_Release(self) -> None:
		with WarningCollector() as warnings:
			resolution = Resolver(self._Index()).ResolveRequirements([Requirement("shaky")])

		shaky = resolution.Requirements[0]
		self.assertIs(ResolutionStatus.IndexFailure, shaky.Status)
		self.assertEqual("1.0", str(shaky.Release.Version))

		failures = [warning for warning in warnings.Warnings if isinstance(warning, PackageIndexFailureWarning)]
		self.assertEqual(1, len(failures))
		self.assertEqual("shaky", failures[0].ProjectName)
		self.assertEqual("1.0", str(failures[0].Version))
		self.assertEqual(500, failures[0].StatusCode)

	def test_UnresolvedRequirementWarning_MessageOnly(self) -> None:
		"""The project's name is required: creating the warning with a message only is a 'TypeError'."""
		with self.assertRaises(TypeError) as context:
			_ = UnresolvedRequirementWarning("Package 'ghost' is unknown to the package index.")

		self.assertIn("'projectName'", str(context.exception))

	def test_PackageIndexFailureWarning_MessageOnly(self) -> None:
		"""The project's name and the status code are required: a warning with a message only is a 'TypeError'."""
		with self.assertRaises(TypeError) as context:
			_ = PackageIndexFailureWarning("Package index failed to answer for package 'flaky'.")

		self.assertIn("'projectName'", str(context.exception))
		self.assertIn("'statusCode'", str(context.exception))

	def test_IndexFailure_Uncollected(self) -> None:
		"""Without a collector, the critical warning raises."""
		with self.assertRaises(UnhandledCriticalWarningError):
			Resolver(self._Index()).ResolveRequirements([Requirement("flaky")])

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


class Timeouts(ResolverTestcase):
	"""The current timeout limits a resolution; what it cuts off is a status and one critical warning per level."""

	def test_ExpiredBeforeLevel(self) -> None:
		"""An expired timeout resolves nothing more: no request is sent, every requirement left gets the status."""
		with Timeout(0.01):
			sleep(0.05)
			with WarningCollector() as warnings:
				resolution = Resolver(self._Index()).ResolveRequirements([Requirement("app"), Requirement("lib")])

		for requirement in resolution.Requirements:
			self.assertIs(ResolutionStatus.TimeoutExpired, requirement.Status)
			self.assertIsNone(requirement.Project)

		self.assertListEqual([], DocumentClientSession.Sessions)
		self.assertEqual(1, len(warnings.Warnings))
		self.assertIsInstance(warnings.Warnings[0], ResolutionTimeoutWarning)
		self.assertEqual(0.01, warnings.Warnings[0].Seconds)
		self.assertTupleEqual(("app", "lib"), warnings.Warnings[0].ProjectNames)

	def test_ExpiredKeepsMarkerStatus(self) -> None:
		"""Checks without a download still apply: a marker that doesn't apply keeps its status."""
		environment = dict(default_environment())
		environment["sys_platform"] = "linux"

		with Timeout(0.01):
			sleep(0.05)
			with WarningCollector():
				resolution = Resolver(self._Index(), environment=environment).ResolveRequirements([
					Requirement('winonly; sys_platform == "win32"')
				])

		self.assertIs(ResolutionStatus.MarkerNotApplying, resolution.Requirements[0].Status)

	def test_ProjectTimedOut(self) -> None:
		"""A project download cut off by the timeout is no index failure."""
		resolver = Resolver(self._Index())
		with Timeout(10.0):
			with WarningCollector() as warnings:
				resolution = resolver.ResolveRequirements([Requirement("slow")])

		slow = resolution.Requirements[0]
		self.assertIs(ResolutionStatus.TimeoutExpired, slow.Status)
		self.assertIsNone(slow.Project)
		self.assertSetEqual(set(), resolver._failed)
		self.assertEqual(1, len(warnings.Warnings))
		self.assertIsInstance(warnings.Warnings[0], ResolutionTimeoutWarning)
		self.assertEqual(10.0, warnings.Warnings[0].Seconds)
		self.assertTupleEqual(("slow",), warnings.Warnings[0].ProjectNames)

	def test_ReleaseTimedOut(self) -> None:
		"""A release download cut off by the timeout keeps the project, but selects no release."""
		with Timeout(10.0):
			with WarningCollector() as warnings:
				resolution = Resolver(self._Index()).ResolveRequirements([Requirement("lagging")])

		lagging = resolution.Requirements[0]
		self.assertIs(ResolutionStatus.TimeoutExpired, lagging.Status)
		self.assertEqual("lagging", lagging.Project.Name)
		self.assertIsNone(lagging.Release)
		self.assertTupleEqual(("lagging",), warnings.Warnings[0].ProjectNames)

	def test_TimedOutWithoutTimeout(self) -> None:
		"""Without a current timeout, a request timing out is an index failure, as any other failed request."""
		with WarningCollector() as warnings:
			resolution = Resolver(self._Index()).ResolveRequirements([Requirement("slow")])

		self.assertIs(ResolutionStatus.IndexFailure, resolution.Requirements[0].Status)
		self.assertIsInstance(warnings.Warnings[0], PackageIndexFailureWarning)
		self.assertIsInstance(warnings.Warnings[0].__cause__, TimeoutError)

	def test_SessionTimeout(self) -> None:
		"""The downloads get the time left as the session's total timeout."""
		with Timeout(10.0):
			Resolver(self._Index()).ResolveRequirements([Requirement("util")])

		for session in DocumentClientSession.Sessions:
			self.assertGreater(session.Arguments["timeout"].total, 0.0)
			self.assertLessEqual(session.Arguments["timeout"].total, 10.0)

	def test_SessionWithoutTimeout(self) -> None:
		"""Without a current timeout, the session keeps aiohttp's default timeout."""
		Resolver(self._Index()).ResolveRequirements([Requirement("util")])

		for session in DocumentClientSession.Sessions:
			self.assertNotIn("timeout", session.Arguments)

	def test_Lazy(self) -> None:
		"""A lazily resolved level uses the timeout current when its dependencies are asked for."""
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("app")])

		with Timeout(0.01):
			sleep(0.05)
			with WarningCollector() as warnings:
				dependencies = resolution.Requirements[0].Dependencies

		self.assertIs(ResolutionStatus.Resolved, resolution.Requirements[0].Status)
		for dependency in dependencies:
			self.assertIs(ResolutionStatus.TimeoutExpired, dependency.Status)

		self.assertEqual(1, len(warnings.Warnings))

	def test_Warning_MessageOnly(self) -> None:
		"""The timeout and the projects are required: creating the warning with a message only is a 'TypeError'."""
		with self.assertRaises(TypeError) as context:
			_ = ResolutionTimeoutWarning("Timeout expired.")

		self.assertIn("'seconds'", str(context.exception))
		self.assertIn("'projectNames'", str(context.exception))

	def test_Uncollected(self) -> None:
		"""Without a collector, the critical warning raises."""
		with Timeout(0.01):
			sleep(0.05)
			with self.assertRaises(UnhandledCriticalWarningError):
				Resolver(self._Index()).ResolveRequirements([Requirement("app")])


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


class Markers(ResolverTestcase):
	def _WinOnly(self, resolver: Resolver) -> ResolvedRequirement:
		app = resolver.ResolveRequirements([Requirement("app")]).Requirements[0]
		return next(app.IterateDependencies(lambda requirement: requirement.Requirement.name == "winonly"))

	def test_NotEvaluated(self) -> None:
		self.assertIs(ResolutionStatus.Resolved, self._WinOnly(Resolver(self._Index())).Status)

	def test_NotApplying(self) -> None:
		environment = dict(default_environment())
		environment["sys_platform"] = "linux"

		winonly = self._WinOnly(Resolver(self._Index(), environment=environment))

		self.assertIs(ResolutionStatus.MarkerNotApplying, winonly.Status)
		self.assertIsNone(winonly.Project)

	def test_Applying(self) -> None:
		environment = dict(default_environment())
		environment["sys_platform"] = "win32"

		self.assertIs(ResolutionStatus.Resolved, self._WinOnly(Resolver(self._Index(), environment=environment)).Status)

	def test_CurrentEnvironment(self) -> None:
		resolver = CurrentEnvironmentResolver(self._Index(), preReleases=PreReleasePolicy.Include)
		if default_environment()["sys_platform"] == "win32":
			expected = ResolutionStatus.Resolved
		else:
			expected = ResolutionStatus.MarkerNotApplying

		self.assertDictEqual(dict(default_environment()), resolver.Environment)
		self.assertIs(PreReleasePolicy.Include, resolver.PreReleases)
		self.assertIs(expected, self._WinOnly(resolver).Status)


class Inputs(ResolverTestcase):
	def test_Packages(self) -> None:
		resolution = Resolver(self._Index()).ResolvePackages([("app", None)])

		self.assertListEqual(
			["lib", "util", "winonly"],
			[requirement.Requirement.name for requirement in resolution.Requirements]
		)

	def test_Packages_PreReleaseExcluded(self) -> None:
		"""The newest release the policy admits: lib 2.0 (requires util), not 3.0rc1 (requires nothing)."""
		resolution = Resolver(self._Index()).ResolvePackages([("lib", None)])

		self.assertListEqual(["util"], [requirement.Requirement.name for requirement in resolution.Requirements])

	def test_Packages_PreReleaseIncluded(self) -> None:
		resolution = Resolver(self._Index(), preReleases=PreReleasePolicy.Include).ResolvePackages([("lib", None)])

		self.assertListEqual([], [requirement.Requirement.name for requirement in resolution.Requirements])

	def test_Packages_NoRelease(self) -> None:
		with self.assertRaises(ReleaseNotFoundError) as context:
			Resolver(self._Index()).ResolvePackages([("empty", None)])

		self.assertEqual("Package 'empty' has no release.", str(context.exception))
		self.assertEqual("empty", context.exception.ProjectName)

	def test_Packages_Extra(self) -> None:
		"""An extra's requirements are resolved; their marker names the extra, which is evaluated as given."""
		environment = dict(default_environment())

		resolution = Resolver(self._Index(), environment=environment).ResolvePackages([("app", "test")])
		checker = resolution.Requirements[0]

		self.assertEqual("checker", checker.Requirement.name)
		self.assertEqual("test", checker.Extra)
		self.assertIs(ResolutionStatus.Resolved, checker.Status)

	def test_Packages_ExtraSpelling(self) -> None:
		"""An extra is matched by its canonical name."""
		resolution = Resolver(self._Index()).ResolvePackages([("app", "Test")])

		self.assertEqual("checker", resolution.Requirements[0].Requirement.name)

	def test_Packages_UnknownExtra(self) -> None:
		with self.assertRaises(ExtraNotFoundError) as context:
			Resolver(self._Index()).ResolvePackages([("app", "docs")])

		self.assertEqual("Package 'app' has no extra 'docs'.", str(context.exception))
		self.assertEqual("app", context.exception.ProjectName)
		self.assertEqual("docs", context.exception.Extra)
		self.assertListEqual(["Known are: test."], context.exception.__notes__)

	def test_ExtraNotFoundError_Bases(self) -> None:
		"""Code looking up an extra catches it as a :exc:`LookupError`, code using the package as a ``DependencyError``."""
		self.assertTrue(issubclass(ExtraNotFoundError, LookupError))
		self.assertTrue(issubclass(ExtraNotFoundError, DependencyError))

	def test_ExtraNotFoundError_MessageOnly(self) -> None:
		"""The release and the extra are required: raising the exception with a message only is a 'TypeError'."""
		with self.assertRaises(TypeError) as context:
			raise ExtraNotFoundError("Package 'app' has no extra 'docs'.")

		self.assertIn("'projectName'", str(context.exception))
		self.assertIn("'version'", str(context.exception))
		self.assertIn("'extra'", str(context.exception))

	def test_RequirementExtra(self) -> None:
		"""An extra a requirement names adds that extra's requirements to the dependencies."""
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("tool[fast]")])
		speedup = resolution.Requirements[0].Dependencies[0]

		self.assertEqual("speedup", speedup.Requirement.name)
		self.assertEqual("fast", speedup.Extra)
		self.assertIs(ResolutionStatus.Resolved, speedup.Status)

	def test_RequirementExtra_Subtree(self) -> None:
		"""An extra's dependency is followed further: its own requirements are resolved, too."""
		resolution = Resolver(self._Index()).ResolveRequirements([Requirement("tool[fast]")])
		speedup = resolution.Requirements[0].Dependencies[0]
		accel = speedup.Dependencies[0]

		self.assertEqual("accel", accel.Requirement.name)
		self.assertIs(ResolutionStatus.Resolved, accel.Status)
		self.assertEqual("1.0", str(accel.Release.Version))

	def test_RequirementExtra_Markers(self) -> None:
		"""The extra's marker applies to its own requirements when markers are evaluated."""
		resolver = Resolver(self._Index(), environment=default_environment())
		speedup = resolver.ResolveRequirements([Requirement("tool[fast]")]).Requirements[0].Dependencies[0]

		self.assertIs(ResolutionStatus.Resolved, speedup.Status)

	def test_RequirementExtra_Undeclared(self) -> None:
		with WarningCollector() as warnings:
			resolution = Resolver(self._Index()).ResolveRequirements([Requirement("tool[slow]")])
			dependencies = resolution.Requirements[0].Dependencies

		self.assertTupleEqual((), dependencies)
		broken = [warning for warning in warnings.Warnings if isinstance(warning, BrokenRequirementWarning)]
		self.assertEqual(1, len(broken))
		self.assertIsInstance(broken[0], UndeclaredExtraWarning)
		self.assertIn("names extra 'slow'", str(broken[0]))
		self.assertIs(resolution.Requirements[0], broken[0].Requirement)
		self.assertEqual("slow", broken[0].Extra)
		self.assertIs(resolution.Requirements[0].Release, broken[0].Release)

	def test_RequirementExtra_Undeclared_Uncollected(self) -> None:
		"""Without a collector, the critical warning stops the resolution."""
		with self.assertRaises(UnhandledCriticalWarningError) as context:
			Resolver(self._Index(), strategy=ResolutionStrategy.Eager).ResolveRequirements([Requirement("tool[slow]")])

		self.assertIsInstance(context.exception.__cause__, UndeclaredExtraWarning)

	def test_RequirementsFile(self) -> None:
		with TemporaryDirectory() as directory:
			path = Path(directory) / "requirements.txt"
			path.write_text("lib >= 1.0\nutil\n")

			resolution = Resolver(self._Index()).ResolveRequirementsFile(RequirementsFile.Parse(path))

		self.assertIsInstance(resolution, Resolution)
		self.assertEqual(2, resolution.RequirementCount)
		self.assertTrue(all(requirement.Status is ResolutionStatus.Resolved for requirement in resolution.Requirements))


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

	def test_PreReleases(self) -> None:
		with self.assertRaises(ValueError) as context:
			Resolver(self._Index(), preReleases=None)

		self.assertEqual("Parameter 'preReleases' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			Resolver(self._Index(), preReleases="include")

		self.assertEqual("Parameter 'preReleases' is not of type 'PreReleasePolicy'.", str(context.exception))

	def test_Environment(self) -> None:
		with self.assertRaises(TypeError):
			Resolver(self._Index(), environment=["linux"])

	def test_Requirements(self) -> None:
		resolver = Resolver(self._Index())

		with self.assertRaises(ValueError):
			resolver.ResolveRequirements(None)

		with self.assertRaises(TypeError):
			resolver.ResolveRequirements(5)

		with self.assertRaises(TypeError):
			resolver.ResolveRequirements(["lib"])

	def test_RequirementsFile(self) -> None:
		with self.assertRaises(ValueError):
			Resolver(self._Index()).ResolveRequirementsFile(None)

		with self.assertRaises(TypeError):
			Resolver(self._Index()).ResolveRequirementsFile(Path("requirements.txt"))

	def test_Packages(self) -> None:
		resolver = Resolver(self._Index())

		with self.assertRaises(ValueError):
			resolver.ResolvePackages(None)

		with self.assertRaises(TypeError):
			resolver.ResolvePackages(5)

		with self.assertRaises(TypeError):
			resolver.ResolvePackages(["app"])
