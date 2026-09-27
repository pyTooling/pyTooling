# ==================================================================================================================== #
#             _____           _ _               ____ ___                                                               #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|_ _|                                                              #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |    | |                                                               #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |___ | |                                                               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|___|                                                              #
# |_|    |___/                          |___/                                                                          #
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
A service-independent data model of a CI pipeline, with the dependencies between its elements.

.. code-block:: text

   PipelineGroup            the pipelines started for one commit
   +-- Pipeline             a pipeline
       +-- Workflow         a called workflow or a child pipeline, grouping the elements it contains
       |   +-- ...          the same elements a pipeline contains
       +-- Matrix           a matrix, grouping the job instances it produced
       |   +-- MatrixJob    one instance
       +-- Job              a job
           +-- Step         a step of that job

Every element knows its parent and the pipeline it belongs to. The elements one level below a workflow - its jobs,
matrices and called workflows - can **need** each other: :meth:`DependencyMixin.AddNeed` links two siblings and
rejects a dependency that would close a cycle, so a pipeline is always a directed acyclic graph.
:meth:`Workflow.ToGraph` converts it into a :class:`~pyTooling.Graph.Graph`.

A service's model derives from these classes and adds what only that service has: identifiers, URLs, its own status
values, the interface of a reusable workflow.

.. hint::

   See :ref:`high-level help <CI/Pipeline>` for the mapping of GitHub Actions and GitLab CI onto this model.
"""
from __future__            import annotations

from datetime              import datetime
from itertools             import chain
from typing                import ClassVar, Iterable, Iterator, Optional as Nullable

from pyTooling.Common      import getFullyQualifiedName, StringEnum
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import ToolingException
from pyTooling.Graph       import Graph, Subgraph, Vertex
from pyTooling.MetaClasses import ExtendedType, ThisClass, abstractclass


@export
class PipelineError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.CI.Pipeline`."""


@export
class DependencyError(PipelineError):
	"""The exception raised for a dependency two elements of a pipeline can't have."""


@export
class DependencyCycleError(DependencyError):
	"""The exception raised for a dependency which would close a cycle."""


@export
class Outcome(StringEnum):
	"""
	How an element of a pipeline ended, in terms every CI service has.

	The members and values are those of OpenTelemetry's semantic conventions for CI/CD
	(:class:`pyTooling.Tracing.CI.Result`). A service's model maps its own values onto these, e.g. GitHub's
	``startup_failure`` onto :attr:`Error`.
	"""

	Success =      "success"       #: It succeeded.
	Failure =      "failure"       #: It failed.
	Timeout =      "timeout"       #: It was stopped by a timeout.
	Skip =         "skip"          #: It was skipped, because a condition excluded it.
	Cancellation = "cancellation"  #: It was cancelled before it finished.
	Error =        "error"         #: It ended for another reason, e.g. the service couldn't start it.

	@classmethod
	def Combine(cls, outcomes: Iterable[Nullable[Outcome]]) -> Nullable[Outcome]:
		"""
		Combine the outcomes of the elements of a group into the group's outcome.

		The worst outcome wins, so one failed job makes a group's outcome a failure. A group whose elements were all
		skipped is skipped; a skipped element beside a successful one doesn't change the success. The order is:

		#. :attr:`Failure`
		#. :attr:`Timeout`
		#. :attr:`Error`
		#. :attr:`Cancellation`
		#. :attr:`Success`
		#. :attr:`Skip`

		:param outcomes: The elements' outcomes.
		:returns:        The combined outcome, or ``None`` if there is none, or one of them is ``None``.
		"""
		found = set()
		for outcome in outcomes:
			if outcome is None:
				return None

			found.add(outcome)

		for outcome in (cls.Failure, cls.Timeout, cls.Error, cls.Cancellation, cls.Success, cls.Skip):
			if outcome in found:
				return outcome

		return None


def _earliest(times: Iterable[Nullable[datetime]]) -> Nullable[datetime]:
	"""
	Return the earliest of the times that are known.

	:param times: The times, of which some may be unknown.
	:returns:     The earliest time, or ``None`` if none is known.
	"""
	known = [time for time in times if time is not None]

	return min(known) if len(known) > 0 else None


def _latest(times: Iterable[Nullable[datetime]]) -> Nullable[datetime]:
	"""
	Return the latest of the times, once all of them are known.

	:param times: The times, of which some may be unknown.
	:returns:     The latest time, or ``None`` if one of them is unknown, or there is none.
	"""
	known = []
	for time in times:
		if time is None:
			return None

		known.append(time)

	return max(known) if len(known) > 0 else None


@export
@abstractclass
class Base(metaclass=ExtendedType, slots=True):
	"""
	Common behaviour of every element of a pipeline.

	Every element has a name and a position in the tree, and from a run the times a service reports and an
	:class:`Outcome`.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = None  #: Type a parent must have, or ``None`` when it has no parent.

	_name:        str                 #: Name of the element.
	_parent:      Nullable[Base]      #: Reference to the containing element.
	_pipeline:    Nullable[Pipeline]  #: Reference to the pipeline this element belongs to.
	_createdAt:   Nullable[datetime]  #: Time the element was created.
	_startedAt:   Nullable[datetime]  #: Time the element started running.
	_completedAt: Nullable[datetime]  #: Time the element completed.
	_outcome:     Nullable[Outcome]   #: How the element ended.

	def __init__(
		self,
		name:        str,
		*,
		createdAt:   Nullable[datetime] = None,
		startedAt:   Nullable[datetime] = None,
		completedAt: Nullable[datetime] = None,
		outcome:     Nullable[Outcome]  = None,
		parent:      Nullable[Base]     = None
	) -> None:
		"""
		Initializes an element of a pipeline.

		:param name:        Name of the element.
		:param createdAt:   Optional, time the element was created. Default: ``None``.
		:param startedAt:   Optional, time the element started running. Default: ``None``.
		:param completedAt: Optional, time the element completed. Default: ``None``.
		:param outcome:     Optional, how the element ended. Default: ``None``.
		:param parent:      Optional, reference to the containing element. Default: ``None``.
		:raises ValueError: If parameter 'name' is ``None``.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		:raises TypeError:  If parameter 'createdAt' is not of type :class:`~datetime.datetime`.
		:raises TypeError:  If parameter 'startedAt' is not of type :class:`~datetime.datetime`.
		:raises TypeError:  If parameter 'completedAt' is not of type :class:`~datetime.datetime`.
		:raises TypeError:  If parameter 'outcome' is not of type :class:`Outcome`.
		:raises TypeError:  If parameter 'parent' is given for a class declaring no :attr:`_PARENT_TYPE`.
		:raises TypeError:  If parameter 'parent' is not of the type this class declares in :attr:`_PARENT_TYPE`.
		"""
		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		for parameterName, timestamp in (("createdAt", createdAt), ("startedAt", startedAt), ("completedAt", completedAt)):
			if timestamp is not None and not isinstance(timestamp, datetime):
				ex = TypeError(f"Parameter '{parameterName}' is not of type 'datetime'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(timestamp)}'.")
				raise ex

		if outcome is not None and not isinstance(outcome, Outcome):
			ex = TypeError("Parameter 'outcome' is not of type 'Outcome'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(outcome)}'.")
			raise ex

		if parent is not None:
			if self._PARENT_TYPE is None:
				ex = TypeError(f"A '{self.__class__.__name__}' has no parent.")
				ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
				raise ex
			elif not isinstance(parent, self._PARENT_TYPE):
				ex = TypeError(f"Parameter 'parent' is not of type '{self._PARENT_TYPE.__name__}'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
				raise ex

		self._name =        name
		self._parent =      parent
		self._pipeline =    None if parent is None else parent._pipeline
		self._createdAt =   createdAt
		self._startedAt =   startedAt
		self._completedAt = completedAt
		self._outcome =     outcome

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the element's name (:attr:`_name`).

		:returns: Name of the element.
		"""
		return self._name

	@readonly
	def Parent(self) -> Nullable[Base]:
		"""
		Read-only property to access the containing element (:attr:`_parent`).

		:returns: The containing element, or ``None`` for a :class:`PipelineGroup` and an element not yet placed.
		"""
		return self._parent

	@readonly
	def Pipeline(self) -> Nullable[Pipeline]:
		"""
		Read-only property to access the pipeline this element belongs to (:attr:`_pipeline`).

		:returns: The pipeline, or ``None`` for an element outside one.
		"""
		return self._pipeline

	@readonly
	def CreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to access the time the element was created (:attr:`_createdAt`).

		:returns: The time, or ``None`` if none was reported.
		"""
		return self._createdAt

	@readonly
	def StartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to access the time the element started running (:attr:`_startedAt`).

		:returns: The time, or ``None`` while it hasn't started.
		"""
		return self._startedAt

	@readonly
	def CompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to access the time the element completed (:attr:`_completedAt`).

		:returns: The time, or ``None`` while it hasn't completed.
		"""
		return self._completedAt

	@readonly
	def Outcome(self) -> Nullable[Outcome]:
		"""
		Read-only property to access how the element ended (:attr:`_outcome`).

		:returns: The outcome, or ``None`` while the element hasn't ended.
		"""
		return self._outcome

	@readonly
	def Duration(self) -> Nullable[float]:
		"""
		Read-only property to return how long the element ran.

		The times are read through :attr:`StartedAt` and :attr:`CompletedAt`, so a group deriving its times from what
		it holds reports a duration too.

		:returns: Seconds from starting to completing, or ``None`` while either time is unknown.
		"""
		if self.StartedAt is None or self.CompletedAt is None:
			return None

		return (self.CompletedAt - self.StartedAt).total_seconds()

	def __str__(self) -> str:
		"""
		Return a string representation of the element.

		:returns: The element's name.
		"""
		return self._name


@export
class QualifiedNameMixin(metaclass=ExtendedType, mixin=True, expects=("_parent",)):
	"""
	Mixin-class for elements named by the workflows containing them.

	The mixin walks the tree :class:`Base` builds upwards, so the ``expects`` contract requires :attr:`Base._parent`
	from whichever class it ends up in.
	"""

	@readonly
	def QualifiedName(self) -> str:
		"""
		Read-only property to return the element's name, prefixed by the names of the workflows containing it.

		The element itself is named by :func:`str`, so a :class:`MatrixJob` carries the dimension values it was
		produced for. The walk ends at the :class:`Pipeline`, and passes through a :class:`Matrix` without naming it -
		its instances carry its name already. The name is unique among an element's siblings as long as their names
		are, and is the ID of the element's vertex in :meth:`Workflow.ToGraph`.

		:returns: The name, with every calling workflow in front of it, separated by ``' / '``.
		"""
		names =   [str(self)]
		element = self
		while (element := element._parent) is not None and not isinstance(element, Pipeline):
			if isinstance(element, Workflow):
				names.append(element._name)

		return " / ".join(reversed(names))


@export
class ConditionMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for elements a definition can give a condition: workflows, matrices, jobs and steps.

	The condition is kept as written - a GitHub ``if:`` expression or a GitLab ``rules:if`` - and not evaluated.
	"""

	_condition: Nullable[str]  #: Condition under which the element runs, as written.

	def __init__(self, condition: Nullable[str] = None) -> None:
		"""
		Initializes the condition of an element.

		:param condition:  Optional, condition under which the element runs, as written. Default: ``None``.
		:raises TypeError: If parameter 'condition' is not of type :class:`str`.
		"""
		if condition is not None and not isinstance(condition, str):
			ex = TypeError("Parameter 'condition' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(condition)}'.")
			raise ex

		self._condition = condition

	@readonly
	def Condition(self) -> Nullable[str]:
		"""
		Read-only property to access the condition under which the element runs (:attr:`_condition`).

		:returns: The condition, or ``None`` if the element has none, or it isn't known.
		"""
		return self._condition


@export
class DependencyMixin(metaclass=ExtendedType, mixin=True, expects=("_parent",)):
	"""
	Mixin-class for elements that can need their siblings: jobs, matrices and called workflows.

	An element needing another one starts after it. A need is always a **sibling** - an element of the same group -
	and a need that would close a cycle is rejected when it is added, so the dependencies of a group always form a
	directed acyclic graph. A group needing another group needs everything that group contains.

	The mixin compares the elements' parents, so the ``expects`` contract requires :attr:`Base._parent` from whichever
	class it ends up in.
	"""

	_needs:      list[DependencyMixin]  #: Elements this element needs, in the order they were added.
	_dependents: list[DependencyMixin]  #: Elements needing this element, in the order they were added.

	def __init__(self) -> None:
		"""
		Initializes an element without dependencies.
		"""
		self._needs =      []
		self._dependents = []

	@readonly
	def Needs(self) -> list[DependencyMixin]:
		"""
		Read-only property to access the elements this element needs (:attr:`_needs`).

		:returns: The needed elements, in the order they were added.
		"""
		return self._needs

	@readonly
	def Dependents(self) -> list[DependencyMixin]:
		"""
		Read-only property to access the elements needing this element (:attr:`_dependents`).

		:returns: The dependent elements, in the order they were added.
		"""
		return self._dependents

	def AddNeed(self, need: DependencyMixin) -> None:
		"""
		Add an element this element needs, and this element as its dependent.

		:param need:                  The element this element needs.
		:raises ValueError:           If parameter 'need' is ``None``.
		:raises TypeError:            If parameter 'need' is not of type :class:`DependencyMixin`.
		:raises DependencyCycleError: If parameter 'need' is this element.
		:raises DependencyError:      If parameter 'need' isn't contained in the same group as this element.
		:raises DependencyError:      If this element needs parameter 'need' already.
		:raises DependencyCycleError: If parameter 'need' needs this element already, directly or through others. |br|
		                              The note names the cycle.
		"""
		if need is None:
			raise ValueError("Parameter 'need' is None.")
		elif not isinstance(need, DependencyMixin):
			ex = TypeError("Parameter 'need' is not of type 'DependencyMixin'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(need)}'.")
			raise ex
		elif need is self:
			raise DependencyCycleError(f"'{self}' can't need itself.")
		elif self._parent is None or need._parent is not self._parent:
			ex = DependencyError(f"'{self}' can't need '{need}', which isn't contained in the same group.")
			ex.add_note(f"'{self}' is contained in '{self._parent}', '{need}' in '{need._parent}'.")
			raise ex
		elif need in self._needs:
			raise DependencyError(f"'{self}' needs '{need}' already.")

		# Depth-first search from the need along the needs: reaching this element means the new need closes a cycle.
		predecessors: dict[DependencyMixin, DependencyMixin] = {need: need}
		stack = [need]
		while len(stack) > 0:
			element = stack.pop()
			if element is self:
				cycle = [self]
				while element is not need:
					element = predecessors[element]
					cycle.append(element)

				ex = DependencyCycleError(f"'{self}' can't need '{need}', because '{need}' needs '{self}' already.")
				ex.add_note(f"Cycle: {' -> '.join(str(item) for item in [self, *reversed(cycle)])}.")
				raise ex

			for item in element._needs:
				if item not in predecessors:
					predecessors[item] = element
					stack.append(item)

		self._needs.append(need)
		need._dependents.append(self)


@export
class MatrixInstanceMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for a job a matrix produced, carrying the values of the matrix' dimensions it ran with.

	A service's matrix instance derives from that service's job class and mixes this in, as :class:`MatrixJob` does
	with :class:`Job`.
	"""

	_dimensionValues: list[str]  #: Values of the matrix' dimensions this instance ran with.

	def __init__(self, dimensionValues: Nullable[Iterable[str]] = None) -> None:
		"""
		Initializes the dimension values of a matrix instance.

		:param dimensionValues: Optional, values of the matrix' dimensions this instance ran with. Default: ``None``.
		:raises TypeError:      If an element of parameter 'dimensionValues' is not of type :class:`str`.
		"""
		self._dimensionValues = []
		if dimensionValues is None:
			return

		for value in dimensionValues:
			if not isinstance(value, str):
				ex = TypeError("An element of parameter 'dimensionValues' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

			self._dimensionValues.append(value)

	@readonly
	def DimensionValues(self) -> list[str]:
		"""
		Read-only property to access the values this instance's dimensions had (:attr:`_dimensionValues`).

		:returns: The dimension values, in the order the service names them.
		"""
		return self._dimensionValues


@export
class PipelineGroup(Base):
	"""
	The pipelines started for one commit, and the top of the tree.

	The group has no times of its own and derives them from its pipelines.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = None  #: A pipeline group is the top of the tree and has no parent.

	_pipelines: list[Pipeline]  #: Pipelines of the group.

	def __init__(self, name: str, pipelines: Nullable[Iterable[Pipeline]] = None) -> None:
		"""
		Initializes a group of pipelines.

		:param name:       Name of the group, e.g. the commit every pipeline of the group was started on.
		:param pipelines:  Optional, the pipelines, which are attached to the group. Default: ``None``.
		:raises TypeError: If an element of parameter 'pipelines' is not of type :class:`Pipeline`.
		"""
		super().__init__(name)

		self._pipelines = []
		if pipelines is None:
			return

		for pipeline in pipelines:
			if not isinstance(pipeline, Pipeline):
				ex = TypeError("An element of parameter 'pipelines' is not of type 'Pipeline'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(pipeline)}'.")
				raise ex

			self._pipelines.append(pipeline)
			pipeline._parent = self

	@readonly
	def Pipelines(self) -> list[Pipeline]:
		"""
		Read-only property to access the pipelines of the group (:attr:`_pipelines`).

		:returns: The pipelines, in the order they were added.
		"""
		return self._pipelines

	@readonly
	def CreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first pipeline of the group was created.

		:returns: The time, or ``None`` if no pipeline of the group reports one.
		"""
		return _earliest(pipeline.CreatedAt for pipeline in self._pipelines)

	@readonly
	def StartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first pipeline of the group started.

		:returns: The time, or ``None`` if no pipeline of the group has started.
		"""
		return _earliest(pipeline.StartedAt for pipeline in self._pipelines)

	@readonly
	def CompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the last pipeline of the group completed.

		:returns: The time, or ``None`` while a pipeline of the group hasn't completed, or while it holds none.
		"""
		return _latest(pipeline.CompletedAt for pipeline in self._pipelines)

	@readonly
	def Outcome(self) -> Nullable[Outcome]:
		"""
		Read-only property to return how the group's pipelines ended, taken together (see :meth:`Outcome.Combine`).

		:returns: The combined outcome, or ``None`` while a pipeline hasn't ended, or while the group holds none.
		"""
		return Outcome.Combine(pipeline.Outcome for pipeline in self._pipelines)

	def IterateJobs(self) -> Iterator[Job]:
		"""
		Iterate every job of every pipeline of the group.

		:returns: An iterator over the jobs.
		"""
		for pipeline in self._pipelines:
			yield from pipeline.IterateJobs()

	def __len__(self) -> int:
		"""
		Return the number of pipelines of the group.

		:returns: Number of pipelines.
		"""
		return len(self._pipelines)

	def __contains__(self, name: str) -> bool:
		"""
		Check whether a pipeline of that name belongs to the group.

		:param name: Name of the pipeline to check for.
		:returns:    ``True``, if a pipeline of that name belongs to the group.
		"""
		return any(str(pipeline) == name for pipeline in self._pipelines)

	def __iter__(self) -> Iterator[Pipeline]:
		"""
		Iterate the pipelines of the group.

		:returns: An iterator over the pipelines.
		"""
		return iter(self._pipelines)


@export
@abstractclass
class JobGroup(Base):
	"""
	A group of jobs: the shared behaviour of a :class:`Workflow` and a :class:`Matrix`.

	A group the service reports as an element of its own - one that was given a creation time - keeps the times and
	the outcome it was given. A group the service doesn't report, as GitHub doesn't report a called workflow or a
	matrix, derives them from what it holds.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = None  #: Declared by the groups deriving from this class.

	_jobs: list[Job]  #: Jobs of this group.

	def __init__(
		self,
		name:        str,
		*,
		createdAt:   Nullable[datetime] = None,
		startedAt:   Nullable[datetime] = None,
		completedAt: Nullable[datetime] = None,
		outcome:     Nullable[Outcome]  = None,
		parent:      Nullable[Base]     = None
	) -> None:
		"""
		Initializes a group of jobs.

		:param name:        Name of the group.
		:param createdAt:   Optional, time the group was created, if the service reports it. Default: ``None``.
		:param startedAt:   Optional, time the group started, if the service reports it. Default: ``None``.
		:param completedAt: Optional, time the group completed, if the service reports it. Default: ``None``.
		:param outcome:     Optional, how the group ended, if the service reports it. Default: ``None``.
		:param parent:      Optional, reference to the element containing the group. Default: ``None``.
		"""
		super().__init__(
			name, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome, parent=parent
		)

		self._jobs = []

	@readonly
	def Jobs(self) -> list[Job]:
		"""
		Read-only property to access the jobs of this group (:attr:`_jobs`).

		:returns: The jobs, not including those of nested groups.
		"""
		return self._jobs

	@readonly
	def CreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the group was created.

		:returns: The time the service reported, or - for a group it doesn't report - :attr:`ContentsCreatedAt`.
		"""
		return self.ContentsCreatedAt if self._createdAt is None else self._createdAt

	@readonly
	def StartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the group started.

		:returns: The time the service reported, or - for a group it doesn't report - :attr:`ContentsStartedAt`.
		"""
		return self.ContentsStartedAt if self._createdAt is None else self._startedAt

	@readonly
	def CompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the group completed.

		:returns: The time the service reported, or - for a group it doesn't report - :attr:`ContentsCompletedAt`.
		"""
		return self.ContentsCompletedAt if self._createdAt is None else self._completedAt

	@readonly
	def Outcome(self) -> Nullable[Outcome]:
		"""
		Read-only property to return how the group ended.

		:returns: The outcome the service reported, or - for a group it doesn't report - :attr:`ContentsOutcome`.
		"""
		return self.ContentsOutcome if self._createdAt is None else self._outcome

	@readonly
	def ContentsCreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first element below this group was created.

		:returns: The time, or ``None`` if no element below the group reports one.
		"""
		return _earliest(element.CreatedAt for element in self._Contents)

	@readonly
	def ContentsStartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first element below this group started.

		:returns: The time, or ``None`` if no element below the group has started.
		"""
		return _earliest(element.StartedAt for element in self._Contents)

	@readonly
	def ContentsCompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the last element below this group completed.

		:returns: The time, or ``None`` while an element below the group hasn't completed, or while it holds none.
		"""
		return _latest(element.CompletedAt for element in self._Contents)

	@readonly
	def ContentsOutcome(self) -> Nullable[Outcome]:
		"""
		Read-only property to return how the elements below this group ended, taken together.

		:returns: The combined outcome (see :meth:`Outcome.Combine`), or ``None`` while an element below the group
		          hasn't ended, or while it holds none.
		"""
		return Outcome.Combine(element.Outcome for element in self._Contents)

	def __len__(self) -> int:
		"""
		Return the number of jobs of this group.

		:returns: Number of jobs.
		"""
		return len(self._jobs)

	def __contains__(self, name: str) -> bool:
		"""
		Check whether a job of that name belongs to this group.

		A job is named the way :func:`str` names it, so an instance of a :class:`Matrix` is asked for with its
		dimension values: ``"Unit Tests (ubuntu-26.04, 3.14)"``.

		:param name: Name of the job to check for.
		:returns:    ``True``, if a job of that name belongs to this group.
		"""
		return any(str(job) == name for job in self._jobs)

	@readonly
	def _Contents(self) -> Iterable[Base]:
		"""
		Read-only property to access what this group holds, its jobs (:attr:`_jobs`).

		A :class:`Workflow` holds further groups and says so by overriding this.

		:returns: The elements one level below this group.
		"""
		return self._jobs

	def __iter__(self) -> Iterator[Base]:
		"""
		Iterate what this group holds, ordered by the time it was created.

		The order is stable, so elements reporting no time - e.g. the elements of a definition - keep the order they
		were added in.

		:returns: An iterator over the contained elements.
		"""
		def createdAt(element: Base) -> tuple[bool, datetime]:
			"""
			Nested function sorting an element without a creation time behind every element that has one.

			:param element: The element.
			:returns:       The sort key.
			"""
			return (element.CreatedAt is None, element.CreatedAt if element.CreatedAt is not None else datetime.min)

		return iter(sorted(self._Contents, key=createdAt))


@export
class Workflow(JobGroup, QualifiedNameMixin, ConditionMixin, DependencyMixin):
	"""
	A called workflow or a child pipeline, grouping the elements it contains.

	A workflow contains jobs, matrices and further called workflows, which can need each other. It is itself an
	element of the workflow calling it, and can need and be needed by its siblings.

	:attr:`Reference` names what was called, as the service writes it. A workflow whose file isn't read - e.g. one in
	a repository that isn't at hand - is a workflow with a reference and no contents.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = ThisClass  #: A workflow is contained in a workflow.

	_reference: Nullable[str]        #: What the workflow calls, as written.
	_workflows: dict[str, Workflow]  #: Workflows called by this workflow, by name.
	_matrices:  dict[str, Matrix]    #: Matrices of this workflow, by the name their jobs share.

	def __init__(
		self,
		name:        str,
		*,
		reference:   Nullable[str]      = None,
		condition:   Nullable[str]      = None,
		createdAt:   Nullable[datetime] = None,
		startedAt:   Nullable[datetime] = None,
		completedAt: Nullable[datetime] = None,
		outcome:     Nullable[Outcome]  = None,
		parent:      Nullable[Workflow] = None
	) -> None:
		"""
		Initializes a called workflow.

		:param name:           Name of the workflow.
		:param reference:      Optional, what the workflow calls, as written. Default: ``None``.
		:param condition:      Optional, condition under which the workflow is called, as written. Default: ``None``.
		:param createdAt:      Optional, time the workflow was created, if the service reports it. Default: ``None``.
		:param startedAt:      Optional, time the workflow started, if the service reports it. Default: ``None``.
		:param completedAt:    Optional, time the workflow completed, if the service reports it. Default: ``None``.
		:param outcome:        Optional, how the workflow ended, if the service reports it. Default: ``None``.
		:param parent:         Optional, reference to the workflow calling this one. Default: ``None``.
		:raises TypeError:     If parameter 'reference' is not of type :class:`str`.
		:raises PipelineError: If the calling workflow calls a workflow of that name already.
		"""
		if reference is not None and not isinstance(reference, str):
			ex = TypeError("Parameter 'reference' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(reference)}'.")
			raise ex

		ConditionMixin.__init__(self, condition)
		super().__init__(
			name, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome, parent=parent
		)
		DependencyMixin.__init__(self)

		if isinstance(parent, Workflow) and name in parent._workflows:
			raise PipelineError(f"Workflow '{parent._name}' calls a workflow '{name}' already.")

		self._reference = reference
		self._workflows = {}
		self._matrices =  {}

		# A pipeline's parent is a pipeline group, which the pipeline registers at itself.
		if isinstance(parent, Workflow):
			parent._workflows[name] = self

	@readonly
	def Reference(self) -> Nullable[str]:
		"""
		Read-only property to access what the workflow calls, as written (:attr:`_reference`).

		E.g. ``pyTooling/Actions/.github/workflows/Package.yml@r8`` for GitHub, or the file a GitLab trigger includes.

		:returns: The reference, or ``None`` if it isn't known.
		"""
		return self._reference

	@readonly
	def Workflows(self) -> dict[str, Workflow]:
		"""
		Read-only property to access the workflows this workflow calls (:attr:`_workflows`).

		:returns: The called workflows, by name.
		"""
		return self._workflows

	@readonly
	def Matrices(self) -> dict[str, Matrix]:
		"""
		Read-only property to access the matrices of this workflow (:attr:`_matrices`).

		:returns: The matrices, by the name their jobs share.
		"""
		return self._matrices

	def IterateJobs(self) -> Iterator[Job]:
		"""
		Iterate every job below this workflow, including those of its matrices and of the workflows it calls.

		:returns: An iterator over the jobs.
		"""
		yield from self._jobs
		for matrix in self._matrices.values():
			yield from matrix._jobs

		for workflow in self._workflows.values():
			yield from workflow.IterateJobs()

	def ToGraph(self, depth: Nullable[int] = None) -> Graph:
		"""
		Convert the workflow into a graph of the elements it contains and their dependencies.

		Every element one level below the workflow becomes a :class:`~pyTooling.Graph.Vertex` of the graph, with the
		element as its :attr:`~pyTooling.Graph.Vertex.Value` and its :attr:`~QualifiedNameMixin.QualifiedName` as its
		:attr:`~pyTooling.Graph.Vertex.ID`. Every dependency becomes an :class:`~pyTooling.Graph.Edge` from the needed
		element to the one needing it.

		A called workflow or a matrix holding elements is expanded into a :class:`~pyTooling.Graph.Subgraph` named by
		its qualified name, whose vertices and edges are built the same way. The group's vertex has a
		:class:`~pyTooling.Graph.Link` to each vertex of its subgraph. The graph's own vertices and edges don't
		include those of its subgraphs, since :mod:`pyTooling.Graph` registers them on the subgraph.

		:param depth:                 Optional, how many levels of nested groups to expand; ``0`` expands none, ``None``
		                              every level. Default: ``None``.
		:returns:                     The graph, named like the workflow.
		:raises TypeError:            If parameter 'depth' is not of type :class:`int`.
		:raises ValueError:           If parameter 'depth' is negative.
		:raises DuplicateVertexError: If two elements of one group share a name, and therefore a qualified name.

		.. seealso::

		   :meth:`Graph.RemoveTransitiveEdges <pyTooling.Graph.BaseGraph.RemoveTransitiveEdges>`
		      |rarr| Remove the edges a longer path already implies.
		"""
		if depth is not None and (not isinstance(depth, int) or isinstance(depth, bool)):
			ex = TypeError("Parameter 'depth' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
			raise ex
		elif depth is not None and depth < 0:
			ex = ValueError("Parameter 'depth' is negative.")
			ex.add_note(f"Got value '{depth}'.")
			raise ex

		graph = Graph(name=self._name)

		def addContents(
			group:       JobGroup,
			subgraph:    Nullable[Subgraph],
			groupVertex: Nullable[Vertex],
			level:       int
		) -> None:
			"""
			Nested function for recursion.

			:param group:       The group whose contents become vertices.
			:param subgraph:    The subgraph the vertices are placed in, or ``None`` for the graph itself.
			:param groupVertex: The group's own vertex, which links to the new vertices, or ``None`` for the graph itself.
			:param level:       How many levels of nested groups are expanded above this one.
			"""
			vertices: dict[Base, Vertex] = {}
			for element in group:
				vertex = Vertex(vertexID=element.QualifiedName, value=element, graph=graph, subgraph=subgraph)
				vertices[element] = vertex
				if groupVertex is not None:
					groupVertex.LinkToVertex(vertex)

			for element, vertex in vertices.items():
				for need in element._needs:
					vertices[need].EdgeToVertex(vertex)

			if depth is not None and level >= depth:
				return

			for element, vertex in vertices.items():
				if isinstance(element, JobGroup) and len(element) > 0:
					addContents(element, Subgraph(graph, name=element.QualifiedName), vertex, level + 1)

		addContents(self, None, None, 0)

		return graph

	def __len__(self) -> int:
		"""
		Return the number of elements this workflow contains: its jobs, its matrices and the workflows it calls.

		:returns: Number of contained elements.
		"""
		return len(self._jobs) + len(self._matrices) + len(self._workflows)

	def __contains__(self, name: str) -> bool:
		"""
		Check whether an element of that name is contained in this workflow.

		:param name: Name of the called workflow, matrix or job to check for.
		:returns:    ``True``, if an element of that name is contained in this workflow.
		"""
		return name in self._workflows or name in self._matrices or super().__contains__(name)

	@readonly
	def _Contents(self) -> Iterable[Base]:
		"""
		Read-only property to return what this workflow holds: its jobs, its matrices and the workflows it calls.

		:returns: The elements one level below this workflow.
		"""
		return chain(self._jobs, self._matrices.values(), self._workflows.values())


@export
class Pipeline(Workflow):
	"""
	A pipeline: the workflow a service started, holding everything else.

	A pipeline can need another pipeline of its :class:`PipelineGroup`, e.g. one triggered by another's completion.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = PipelineGroup  #: A pipeline is contained in a pipeline group.

	def __init__(
		self,
		name:        str,
		*,
		condition:   Nullable[str]           = None,
		createdAt:   Nullable[datetime]      = None,
		startedAt:   Nullable[datetime]      = None,
		completedAt: Nullable[datetime]      = None,
		outcome:     Nullable[Outcome]       = None,
		parent:      Nullable[PipelineGroup] = None
	) -> None:
		"""
		Initializes a pipeline.

		:param name:        Name of the pipeline.
		:param condition:   Optional, condition under which the pipeline runs, as written. Default: ``None``.
		:param createdAt:   Optional, time the pipeline was created. Default: ``None``.
		:param startedAt:   Optional, time the pipeline started. Default: ``None``.
		:param completedAt: Optional, time the pipeline completed. Default: ``None``.
		:param outcome:     Optional, how the pipeline ended. Default: ``None``.
		:param parent:      Optional, reference to the group of pipelines. Default: ``None``.
		"""
		super().__init__(
			name, condition=condition, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome,
			parent=parent
		)

		self._pipeline = self

		if parent is not None:
			parent._pipelines.append(self)


@export
class Matrix(JobGroup, QualifiedNameMixin, ConditionMixin, DependencyMixin):
	"""
	A matrix, grouping the job instances it produced.

	The matrix is an element of its workflow, so it can need and be needed by its siblings. A service doesn't report a
	matrix as an element of its own, so it has no times of its own and spans its instances.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Workflow  #: A matrix is contained in a workflow.

	def __init__(self, name: str, *, condition: Nullable[str] = None, parent: Nullable[Workflow] = None) -> None:
		"""
		Initializes a matrix.

		:param name:           Name of the matrix, which its instances share.
		:param condition:      Optional, condition under which the matrix' jobs run, as written. Default: ``None``.
		:param parent:         Optional, reference to the workflow containing the matrix. Default: ``None``.
		:raises PipelineError: If the workflow contains a matrix of that name already.
		"""
		ConditionMixin.__init__(self, condition)
		super().__init__(name, parent=parent)
		DependencyMixin.__init__(self)

		if parent is not None:
			if name in parent._matrices:
				raise PipelineError(f"Workflow '{parent._name}' contains a matrix '{name}' already.")

			parent._matrices[name] = self

	@readonly
	def Instances(self) -> list[MatrixJob]:
		"""
		Read-only property to access the job instances this matrix produced (:attr:`_jobs`).

		:returns: The instances, in the order they were added.
		"""
		return self._jobs


@export
class Job(Base, QualifiedNameMixin, ConditionMixin, DependencyMixin):
	"""A job, which runs its steps on a worker."""

	_PARENT_TYPE: ClassVar[Nullable[type]] = JobGroup  #: A job is contained in a job group.

	_steps: list[Step]  #: Steps of the job.

	def __init__(
		self,
		name:        str,
		*,
		condition:   Nullable[str]      = None,
		createdAt:   Nullable[datetime] = None,
		startedAt:   Nullable[datetime] = None,
		completedAt: Nullable[datetime] = None,
		outcome:     Nullable[Outcome]  = None,
		parent:      Nullable[JobGroup] = None
	) -> None:
		"""
		Initializes a job.

		:param name:        Name of the job.
		:param condition:   Optional, condition under which the job runs, as written. Default: ``None``.
		:param createdAt:   Optional, time the job was created, i.e. queued for a worker. Default: ``None``.
		:param startedAt:   Optional, time the job started running on a worker. Default: ``None``.
		:param completedAt: Optional, time the job completed. Default: ``None``.
		:param outcome:     Optional, how the job ended. Default: ``None``.
		:param parent:      Optional, reference to the group containing the job. Default: ``None``.
		"""
		ConditionMixin.__init__(self, condition)
		super().__init__(
			name, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome, parent=parent
		)
		DependencyMixin.__init__(self)

		self._steps = []

		if parent is not None:
			parent._jobs.append(self)

	@readonly
	def Steps(self) -> list[Step]:
		"""
		Read-only property to access the job's steps (:attr:`_steps`).

		:returns: The steps, in the order they were added.
		"""
		return self._steps

	def __len__(self) -> int:
		"""
		Return the number of steps of the job.

		:returns: Number of steps.
		"""
		return len(self._steps)

	def __contains__(self, name: str) -> bool:
		"""
		Check whether a step of that name belongs to the job.

		:param name: Name of the step to check for.
		:returns:    ``True``, if a step of that name belongs to the job.
		"""
		return any(str(step) == name for step in self._steps)

	def __iter__(self) -> Iterator[Step]:
		"""
		Iterate the job's steps.

		:returns: An iterator over the steps.
		"""
		return iter(self._steps)


@export
class MatrixJob(Job, MatrixInstanceMixin):
	"""One instance of a job produced by a matrix."""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Matrix  #: A matrix instance is contained in a matrix.

	def __init__(
		self,
		name:            str,
		dimensionValues: Nullable[Iterable[str]] = None,
		*,
		condition:       Nullable[str]      = None,
		createdAt:       Nullable[datetime] = None,
		startedAt:       Nullable[datetime] = None,
		completedAt:     Nullable[datetime] = None,
		outcome:         Nullable[Outcome]  = None,
		parent:          Nullable[Matrix]   = None
	) -> None:
		"""
		Initializes one instance of a job produced by a matrix.

		:param name:            Name of the job, without the dimension values.
		:param dimensionValues: Optional, values of the matrix' dimensions this instance ran with. Default: ``None``.
		:param condition:       Optional, condition under which the job runs, as written. Default: ``None``.
		:param createdAt:       Optional, time the job was created, i.e. queued for a worker. Default: ``None``.
		:param startedAt:       Optional, time the job started running on a worker. Default: ``None``.
		:param completedAt:     Optional, time the job completed. Default: ``None``.
		:param outcome:         Optional, how the job ended. Default: ``None``.
		:param parent:          Optional, reference to the matrix containing the instance. Default: ``None``.
		"""
		MatrixInstanceMixin.__init__(self, dimensionValues)

		super().__init__(
			name, condition=condition, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome,
			parent=parent
		)

	def __str__(self) -> str:
		"""
		Return a string representation of the matrix instance.

		:returns: The job's name, followed by its dimension values in brackets, if it has any.
		"""
		if len(self._dimensionValues) == 0:
			return self._name

		return f"{self._name} ({', '.join(self._dimensionValues)})"


@export
class Step(Base, ConditionMixin):
	"""A step within a job."""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Job  #: A step is contained in a job.

	def __init__(
		self,
		name:        str,
		*,
		condition:   Nullable[str]      = None,
		startedAt:   Nullable[datetime] = None,
		completedAt: Nullable[datetime] = None,
		outcome:     Nullable[Outcome]  = None,
		parent:      Nullable[Job]      = None
	) -> None:
		"""
		Initializes a step within a job.

		:param name:        Name of the step.
		:param condition:   Optional, condition under which the step runs, as written. Default: ``None``.
		:param startedAt:   Optional, time the step started running. Default: ``None``.
		:param completedAt: Optional, time the step completed. Default: ``None``.
		:param outcome:     Optional, how the step ended. Default: ``None``.
		:param parent:      Optional, reference to the job containing the step. Default: ``None``.
		"""
		ConditionMixin.__init__(self, condition)
		super().__init__(name, startedAt=startedAt, completedAt=completedAt, outcome=outcome, parent=parent)

		if parent is not None:
			parent._steps.append(self)
