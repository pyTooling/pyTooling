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
Data models of continuous integration services, and the service-independent model of a pipeline they derive from.

A model reads a service's REST payloads or files into objects with a parent-child relation, so a consumer works with
named attributes and typed enumerations instead of nested dictionaries and magic strings. The models carry no
dependency on what is done with them - rendering, tracing or reporting are consumers of a model, not part of it.

The service-independent pipeline:

.. code-block:: text

   PipelineGroup            the pipelines started for one commit
   +-- Pipeline             a pipeline
       +-- Workflow         a called workflow or a child pipeline, grouping the elements it contains
       |   +-- ...          the same elements a pipeline contains
       +-- Matrix           a matrix, grouping the instances it produced
       |   +-- MatrixJob        one job instance
       |   +-- MatrixWorkflow   one instance of a called workflow
       +-- Job              a job
           +-- Step         a step of that job

Every element knows its parent and the pipeline it belongs to. The elements one level below a workflow - its jobs,
matrices and called workflows - can **need** each other: :meth:`DependencyMixin.AddNeed` links two siblings, and
:meth:`JobGroup.Validate` checks a completed pipeline for cycles. :meth:`Workflow.ToGraph` converts it into a
:class:`~pyTooling.Graph.Graph`.

A service's model derives from these classes and adds what only that service has: identifiers, URLs, its own status
values, the interface of a reusable workflow.

.. hint::

   See :ref:`high-level help <CI/Pipeline>` for the mapping of GitHub Actions and GitLab CI onto this model.

.. seealso::

   `pyTooling.GitHub <https://pyTooling.github.io/pyTooling.GitHub/>`__
      |rarr| The models of a GitHub Actions workflow run and workflow file, built on this model.
   :mod:`pyTooling.REST`
      |rarr| The client a model's payloads are read with.
"""
from __future__            import annotations

from datetime              import datetime
from typing                import Any, ClassVar, Hashable, Iterable, Iterator, Mapping, Optional as Nullable

from pyTooling.Common      import getFullyQualifiedName, StringEnum
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import ToolingException
from pyTooling.Graph       import Graph, Subgraph, Vertex
from pyTooling.MetaClasses import ExtendedType, ThisClass, abstractclass
from pyTooling.REST        import JSONObject


@export
class CIError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.CI` and the models of the CI services."""


@export
class PipelineError(CIError):
	"""Base-exception of all exceptions raised by the service-independent pipeline model."""


@export
class NeedDependencyError(PipelineError):
	"""The exception raised for a need - a dependency - two elements of a pipeline can't have."""


@export
class NeedDependencyCycleError(NeedDependencyError):
	"""The exception raised for a need which would close a cycle of dependencies."""


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
		found = set(outcomes)
		for outcome in (None, cls.Failure, cls.Timeout, cls.Error, cls.Cancellation, cls.Success, cls.Skip):
			if outcome in found:
				return outcome

		return None


@export
@abstractclass
class Base(metaclass=ExtendedType, slots=True):
	"""
	Common behaviour of every element of a pipeline.

	Every element has a name and a position in the tree, and from a run the times a service reports and an
	:class:`Outcome`. Every element carries a dictionary of arbitrary key-value-pairs as well, which a consumer
	attaches its own information to, like the elements of :mod:`pyTooling.Graph`. It is accessed like a dictionary:
	:pycode:`job["runner.os"] = "Linux"`.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = None  #: Type a parent must have, or ``None`` when it has no parent.

	_name:        str                  #: Name of the element.
	_parent:      Nullable[Base]       #: Reference to the containing element.
	_pipeline:    Nullable[Pipeline]   #: Reference to the pipeline this element belongs to.
	_createdAt:   Nullable[datetime]   #: Time the element was created.
	_startedAt:   Nullable[datetime]   #: Time the element started running.
	_completedAt: Nullable[datetime]   #: Time the element completed.
	_outcome:     Nullable[Outcome]    #: How the element ended.
	_dict:        dict[Hashable, Any]  #: A dictionary to store arbitrary key-value-pairs.

	def __init__(
		self,
		name:          str,
		*,
		createdAt:     Nullable[datetime]               = None,
		startedAt:     Nullable[datetime]               = None,
		completedAt:   Nullable[datetime]               = None,
		outcome:       Nullable[Outcome]                = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Base]                   = None
	) -> None:
		"""
		Initializes an element of a pipeline.

		The element is added to its parent's elements last, so a class deriving from this one checks its own parameters
		before it calls this initializer.

		:param name:          Name of the element.
		:param createdAt:     Optional, time the element was created. Default: ``None``.
		:param startedAt:     Optional, time the element started running. Default: ``None``.
		:param completedAt:   Optional, time the element completed. Default: ``None``.
		:param outcome:       Optional, how the element ended. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the containing element. Default: ``None``.
		:raises ValueError:   If parameter 'name' is ``None``.
		:raises TypeError:    If parameter 'name' is not of type :class:`str`.
		:raises ValueError:   If parameter 'name' is empty.
		:raises TypeError:    If parameter 'createdAt' is not of type :class:`~datetime.datetime`.
		:raises TypeError:    If parameter 'startedAt' is not of type :class:`~datetime.datetime`.
		:raises TypeError:    If parameter 'completedAt' is not of type :class:`~datetime.datetime`.
		:raises TypeError:    If parameter 'outcome' is not of type :class:`Outcome`.
		:raises TypeError:    If parameter 'parent' is not of the type this class declares in :attr:`_PARENT_TYPE`.
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

		if parent is not None and not isinstance(parent, self._PARENT_TYPE):
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
		self._dict =        {} if keyValuePairs is None else {key: value for key, value in keyValuePairs.items()}

		if parent is not None:
			parent._AddElement(self)

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

	@staticmethod
	def _Earliest(times: Iterable[Nullable[datetime]]) -> Nullable[datetime]:
		"""
		Return the earliest of the times that are known.

		:param times: The times, of which some may be unknown.
		:returns:     The earliest time, or ``None`` if none is known.
		"""
		known = [time for time in times if time is not None]

		return min(known) if len(known) > 0 else None

	@staticmethod
	def _Latest(times: Iterable[Nullable[datetime]]) -> Nullable[datetime]:
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

	def __getitem__(self, key: Hashable) -> Any:
		"""
		Read an element's attached attributes (key-value-pairs) by key.

		:param key:       The key to look for.
		:returns:         The value associated to the given key.
		:raises KeyError: If key doesn't exist in the element's attributes.
		"""
		return self._dict[key]

	def __setitem__(self, key: Hashable, value: Any) -> None:
		"""
		Create or update an element's attached attributes (key-value-pairs) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key:   The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: Hashable) -> None:
		"""
		Remove an entry from an element's attached attributes (key-value-pairs) by key.

		:param key:       The key to remove.
		:raises KeyError: If key doesn't exist in the element's attributes.
		"""
		del self._dict[key]

	def __contains__(self, key: Hashable) -> bool:
		"""
		Check if the key is an attached attribute (key-value-pairs) on this element.

		:param key: The key to check.
		:returns:   ``True``, if the key is an attached attribute.
		"""
		return key in self._dict

	def __len__(self) -> int:
		"""
		Return the number of attached attributes (key-value-pairs) on this element.

		:returns: Number of attached attributes.
		"""
		return len(self._dict)

	def __iter__(self) -> Iterator[Hashable]:
		"""
		Iterate the keys of the attached attributes (key-value-pairs) on this element.

		:returns: An iterator over the keys, in the order they were added.
		"""
		return iter(self._dict)

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
	"""

	@readonly
	def QualifiedName(self) -> str:
		"""
		Read-only property to return the element's name, prefixed by the names of the workflows containing it.

		Every element is named by :func:`str`, so a :class:`MatrixJob` or a :class:`MatrixWorkflow` carries the
		values of the dimensions it was produced for. The walk ends at the :class:`Pipeline`, and passes through a
		:class:`Matrix` without naming it - its instances carry its name already.

		:returns: The name, with every calling workflow in front of it, separated by ``' / '``.
		"""
		names =   [str(self)]
		element = self
		while (element := element._parent) is not None and not isinstance(element, Pipeline):
			if isinstance(element, Workflow):
				names.append(str(element))

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

	An element needing another one starts after it. A need is always a **sibling** - an element of the same group. A
	group needing another group needs everything that group contains. Whether the needs of a pipeline form cycles is
	checked once it is completely built, by :meth:`JobGroup.Validate` or :meth:`PipelineGroup.Validate`.

	The mixin compares the elements' parents, so the ``expects`` contract requires :attr:`Base._parent` from whichever
	class it ends up in.
	"""

	_needs:      list[DependencyMixin]  #: Elements this element needs, in the order they were added.
	_dependents: list[DependencyMixin]  #: Elements needing this element, in the order they were added.

	def __init__(
		self,
		needs:      Nullable[Iterable[DependencyMixin]] = None,
		dependents: Nullable[Iterable[DependencyMixin]] = None
	) -> None:
		"""
		Initializes an element's dependencies.

		The element must be contained in its group already, as a need is a sibling.

		:param needs:                Optional, siblings this element needs. Default: ``None``.
		:param dependents:           Optional, siblings needing this element. Default: ``None``.
		:raises TypeError:           If parameter 'needs' or 'dependents' is not iterable.
		:raises ValueError:          If an element of parameter 'needs' or 'dependents' is ``None``.
		:raises TypeError:           If an element of parameter 'needs' or 'dependents' is not of type
		                             :class:`DependencyMixin`.
		:raises NeedDependencyError: If an element of parameter 'needs' or 'dependents' isn't contained in the same
		                             group.
		"""
		for name, elements in (("needs", needs), ("dependents", dependents)):
			if elements is not None and not isinstance(elements, Iterable):
				ex = TypeError(f"Parameter '{name}' is not iterable.")
				ex.add_note(f"Got type '{getFullyQualifiedName(elements)}'.")
				raise ex

		self._needs =      []
		self._dependents = []

		if needs is not None:
			for need in needs:
				self.AddNeed(need)

		if dependents is not None:
			for dependent in dependents:
				if dependent is None:
					raise ValueError("An element of parameter 'dependents' is None.")
				elif not isinstance(dependent, DependencyMixin):
					ex = TypeError("An element of parameter 'dependents' is not of type 'DependencyMixin'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(dependent)}'.")
					raise ex

				dependent.AddNeed(self)

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

		:param need:                      The element this element needs.
		:raises ValueError:               If parameter 'need' is ``None``.
		:raises TypeError:                If parameter 'need' is not of type :class:`DependencyMixin`.
		:raises NeedDependencyCycleError: If parameter 'need' is this element.
		:raises NeedDependencyError:      If parameter 'need' isn't contained in the same group as this element.
		:raises NeedDependencyError:      If this element needs parameter 'need' already.
		"""
		if need is None:
			raise ValueError("Parameter 'need' is None.")
		elif not isinstance(need, DependencyMixin):
			ex = TypeError("Parameter 'need' is not of type 'DependencyMixin'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(need)}'.")
			raise ex
		elif need is self:
			raise NeedDependencyCycleError(f"'{self}' can't need itself.")
		elif self._parent is None or need._parent is not self._parent:
			ex = NeedDependencyError(f"'{self}' can't need '{need}', which isn't contained in the same group.")
			ex.add_note(f"'{self}' is contained in '{self._parent}', '{need}' in '{need._parent}'.")
			raise ex
		elif need in self._needs:
			raise NeedDependencyError(f"'{self}' needs '{need}' already.")

		self._needs.append(need)
		need._dependents.append(self)

	@staticmethod
	def _FindCycle(elements: Iterable[DependencyMixin]) -> Nullable[list[DependencyMixin]]:
		"""
		Find a cycle in the needs of sibling elements.

		The elements are searched depth-first along their needs; an element reached again while it is on the current
		path closes a cycle. Every element and need is visited once.

		:param elements: The elements of one group.
		:returns:        The cycle from its first element back to it, e.g. ``[A, D, C, A]``, or ``None``.
		"""
		onPath =   set()
		finished = set()
		for start in elements:
			if start in finished:
				continue

			path =  [start]
			stack = [iter(start._needs)]
			onPath.add(start)
			while len(stack) > 0:
				need = next(stack[-1], None)
				if need is None:
					element = path.pop()
					stack.pop()
					onPath.discard(element)
					finished.add(element)
				elif need in onPath:
					return path[path.index(need):] + [need]
				elif need not in finished:
					path.append(need)
					stack.append(iter(need._needs))
					onPath.add(need)

		return None


@export
class MatrixInstanceMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for a job a matrix produced, carrying the matrix' dimensions it ran with.

	A dimension is a variable of the matrix; the instance carries its name and the value it had for this instance. A
	service's matrix instance derives from that service's job class and mixes this in, as :class:`MatrixJob` does with
	:class:`Job`.
	"""

	_dimensions: dict[str, Any]  #: The matrix' dimensions this instance ran with, as name and value.

	def __init__(self, dimensions: Nullable[Mapping[str, Any]] = None) -> None:
		"""
		Initializes the dimensions of a matrix instance.

		:param dimensions: Optional, the dimensions' names and values this instance ran with. Default: ``None``.
		:raises TypeError: If parameter 'dimensions' is not a mapping.
		:raises TypeError: If a key of parameter 'dimensions' is not of type :class:`str`.
		"""
		self._dimensions = {}
		if dimensions is None:
			return
		elif not isinstance(dimensions, Mapping):
			ex = TypeError("Parameter 'dimensions' is not a mapping ('dict', ...).")
			ex.add_note(f"Got type '{getFullyQualifiedName(dimensions)}'.")
			raise ex

		for name, value in dimensions.items():
			if not isinstance(name, str):
				ex = TypeError("A key of parameter 'dimensions' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
				raise ex

			self._dimensions[name] = value

	@readonly
	def Dimensions(self) -> dict[str, Any]:
		"""
		Read-only property to access the dimensions this instance ran with (:attr:`_dimensions`).

		:returns: The dimensions' names and values, in the matrix' order.
		"""
		return self._dimensions


@export
class PipelineGroup(Base):
	"""
	The pipelines started for one commit, and the top of the tree.

	The group has no times of its own and derives them from its pipelines.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = None  #: A pipeline group is the top of the tree and has no parent.

	_pipelines: list[Pipeline]  #: Pipelines of the group.

	def __init__(
		self,
		name:          str,
		pipelines:     Nullable[Iterable[Pipeline]]     = None,
		*,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None
	) -> None:
		"""
		Initializes a group of pipelines.

		:param name:          Name of the group, e.g. the commit every pipeline of the group was started on.
		:param pipelines:     Optional, the pipelines, which are attached to the group. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:raises TypeError:    If an element of parameter 'pipelines' is not of type :class:`Pipeline`.
		"""
		super().__init__(name, keyValuePairs=keyValuePairs)

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

	def _AddElement(self, pipeline: Pipeline) -> None:
		"""
		Add a pipeline, which names the group as its parent.

		:param pipeline: The pipeline.
		"""
		self._pipelines.append(pipeline)

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
		return self._Earliest(pipeline.CreatedAt for pipeline in self._pipelines)

	@readonly
	def StartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first pipeline of the group started.

		:returns: The time, or ``None`` if no pipeline of the group has started.
		"""
		return self._Earliest(pipeline.StartedAt for pipeline in self._pipelines)

	@readonly
	def CompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the last pipeline of the group completed.

		:returns: The time, or ``None`` while a pipeline of the group hasn't completed, or while it holds none.
		"""
		return self._Latest(pipeline.CompletedAt for pipeline in self._pipelines)

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

	def Validate(self) -> None:
		"""
		Check that the needs of the group's pipelines, and of every group they contain, form no cycle.

		:raises NeedDependencyCycleError: If the needs of the pipelines or of a group form a cycle. |br|
		                                  The note names the cycle.
		"""
		if (cycle := DependencyMixin._FindCycle(self._pipelines)) is not None:
			ex = NeedDependencyCycleError(f"The needs of the pipelines of '{self}' form a cycle.")
			ex.add_note(f"Cycle: {' -> '.join(str(pipeline) for pipeline in cycle)}.")
			raise ex

		for pipeline in self._pipelines:
			pipeline.Validate()

	@readonly
	def PipelineCount(self) -> int:
		"""
		Read-only property to return the number of pipelines of the group.

		:returns: Number of pipelines.
		"""
		return len(self._pipelines)

	def ContainsPipeline(self, name: str) -> bool:
		"""
		Check whether a pipeline of that name belongs to the group.

		:param name: Name of the pipeline to check for.
		:returns:    ``True``, if a pipeline of that name belongs to the group.
		"""
		return any(str(pipeline) == name for pipeline in self._pipelines)

	def IteratePipelines(self) -> Iterator[Pipeline]:
		"""
		Iterate the pipelines of the group.

		:returns: An iterator over the pipelines, in the order they were added.
		"""
		return iter(self._pipelines)


@export
@abstractclass
class JobGroup(Base):
	"""
	A group of jobs: the shared behaviour of a :class:`Workflow` and a :class:`Matrix`.

	A group the service reports as an element of its own - one that was given a time or an outcome - keeps the times
	and the outcome it was given. A group the service doesn't report, as GitHub doesn't report a called workflow or a
	matrix, derives them from what it holds.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = None  #: Declared by the groups deriving from this class.

	_elements: list[Base]  #: Elements of this group - jobs, matrices, workflows - in the order they were added.

	def __init__(
		self,
		name:          str,
		*,
		createdAt:     Nullable[datetime]               = None,
		startedAt:     Nullable[datetime]               = None,
		completedAt:   Nullable[datetime]               = None,
		outcome:       Nullable[Outcome]                = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Base]                   = None
	) -> None:
		"""
		Initializes a group of jobs.

		:param name:          Name of the group.
		:param createdAt:     Optional, time the group was created, if the service reports it. Default: ``None``.
		:param startedAt:     Optional, time the group started, if the service reports it. Default: ``None``.
		:param completedAt:   Optional, time the group completed, if the service reports it. Default: ``None``.
		:param outcome:       Optional, how the group ended, if the service reports it. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the element containing the group. Default: ``None``.
		"""
		super().__init__(
			name, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome,
			keyValuePairs=keyValuePairs, parent=parent
		)

		self._elements = []

	def _AddElement(self, element: Base) -> None:
		"""
		Add an element, which names the group as its parent.

		:param element: The element.
		"""
		self._elements.append(element)

	@readonly
	def Elements(self) -> list[Base]:
		"""
		Read-only property to access the elements of this group (:attr:`_elements`).

		:returns: The jobs, matrices and workflows one level below the group, in the order they were added.
		"""
		return self._elements

	@readonly
	def Jobs(self) -> list[Job]:
		"""
		Read-only property to return the jobs of this group.

		:returns: The jobs one level below the group, in the order they were added.
		"""
		return [element for element in self._elements if isinstance(element, Job)]

	def IterateJobs(self) -> Iterator[Job]:
		"""
		Iterate every job below this group, including those of the groups it contains.

		:returns: An iterator over the jobs, in the order their elements were added.
		"""
		for element in self._elements:
			if isinstance(element, Job):
				yield element
			else:
				yield from element.IterateJobs()

	def Validate(self) -> None:
		"""
		Check that the needs of this group and of every group it contains form no cycle.

		A pipeline is validated once it is completely built: each group is searched once, along every need.

		:raises NeedDependencyCycleError: If the needs of a group form a cycle. |br|
		                                  The note names the cycle.
		"""
		groups = [self]
		while len(groups) > 0:
			group = groups.pop()
			elements = (element for element in group._elements if isinstance(element, DependencyMixin))
			if (cycle := DependencyMixin._FindCycle(elements)) is not None:
				ex = NeedDependencyCycleError(f"The needs of the elements of '{group}' form a cycle.")
				ex.add_note(f"Cycle: {' -> '.join(str(element) for element in cycle)}.")
				raise ex

			groups.extend(element for element in group._elements if isinstance(element, JobGroup))

	@readonly
	def IsReported(self) -> bool:
		"""
		Check if the service reported the group as an element of its own.

		A reported group keeps its own times and outcome; otherwise they span its contents.

		:returns: ``True``, if the group was given a time or an outcome.
		"""
		return any(fact is not None for fact in (self._createdAt, self._startedAt, self._completedAt, self._outcome))

	@readonly
	def CreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the group was created.

		:returns: The time the service reported, or - for a group it doesn't report - :attr:`ContentsCreatedAt`.
		"""
		return self._createdAt if self.IsReported else self.ContentsCreatedAt

	@readonly
	def StartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the group started.

		:returns: The time the service reported, or - for a group it doesn't report - :attr:`ContentsStartedAt`.
		"""
		return self._startedAt if self.IsReported else self.ContentsStartedAt

	@readonly
	def CompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the group completed.

		:returns: The time the service reported, or - for a group it doesn't report - :attr:`ContentsCompletedAt`.
		"""
		return self._completedAt if self.IsReported else self.ContentsCompletedAt

	@readonly
	def Outcome(self) -> Nullable[Outcome]:
		"""
		Read-only property to return how the group ended.

		:returns: The outcome the service reported, or - for a group it doesn't report - :attr:`ContentsOutcome`.
		"""
		return self._outcome if self.IsReported else self.ContentsOutcome

	@readonly
	def ContentsCreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first element below this group was created.

		:returns: The time, or ``None`` if no element below the group reports one.
		"""
		return self._Earliest(element.CreatedAt for element in self._elements)

	@readonly
	def ContentsStartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first element below this group started.

		:returns: The time, or ``None`` if no element below the group has started.
		"""
		return self._Earliest(element.StartedAt for element in self._elements)

	@readonly
	def ContentsCompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the last element below this group completed.

		:returns: The time, or ``None`` while an element below the group hasn't completed, or while it holds none.
		"""
		return self._Latest(element.CompletedAt for element in self._elements)

	@readonly
	def ContentsOutcome(self) -> Nullable[Outcome]:
		"""
		Read-only property to return how the elements below this group ended, taken together.

		:returns: The combined outcome (see :meth:`Outcome.Combine`), or ``None`` while an element below the group
		          hasn't ended, or while it holds none.
		"""
		return Outcome.Combine(element.Outcome for element in self._elements)

	@readonly
	def ElementCount(self) -> int:
		"""
		Read-only property to return the number of elements of this group.

		:returns: Number of elements one level below the group.
		"""
		return len(self._elements)

	def ContainsElement(self, name: str) -> bool:
		"""
		Check whether an element of that name belongs to this group.

		An element is named the way :func:`str` names it, so an instance of a :class:`Matrix` is asked for with its
		dimensions' values: ``"Unit Tests (ubuntu-26.04, 3.14)"``.

		:param name: Name of the job, matrix or workflow to check for.
		:returns:    ``True``, if an element of that name belongs to this group.
		"""
		return any(str(element) == name for element in self._elements)

	def GetElement(self, name: str) -> Base:
		"""
		Return the element of that name.

		An element is named the way :func:`str` names it, as for :meth:`ContainsElement`.

		:param name:      Name of the job, matrix or workflow to return.
		:returns:         The first element of that name, in the order they were added.
		:raises KeyError: If no element of that name belongs to this group.
		"""
		for element in self._elements:
			if str(element) == name:
				return element

		raise KeyError(f"Group '{self._name}' contains no element '{name}'.")

	def IterateElements(self) -> Iterator[Base]:
		"""
		Iterate what this group holds, ordered by the time it was created.

		The order is stable, so elements reporting no time - e.g. the elements of a definition - keep the order they
		were added in, which for a definition is the order of its file.

		:returns: An iterator over the contained elements.
		"""
		def createdAt(element: Base) -> tuple[bool, datetime]:
			"""
			Nested function sorting an element without a creation time behind every element that has one.

			:param element: The element.
			:returns:       The sort key.
			"""
			return (element.CreatedAt is None, element.CreatedAt if element.CreatedAt is not None else datetime.min)

		return iter(sorted(self._elements, key=createdAt))


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
		name:          str,
		*,
		reference:     Nullable[str]                       = None,
		condition:     Nullable[str]                       = None,
		createdAt:     Nullable[datetime]                  = None,
		startedAt:     Nullable[datetime]                  = None,
		completedAt:   Nullable[datetime]                  = None,
		outcome:       Nullable[Outcome]                   = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]]    = None,
		parent:        Nullable[Workflow]                  = None,
		needs:         Nullable[Iterable[DependencyMixin]] = None,
		dependents:    Nullable[Iterable[DependencyMixin]] = None
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
		:param keyValuePairs:  Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:         Optional, reference to the workflow calling this one. Default: ``None``.
		:param needs:          Optional, siblings this workflow needs. Default: ``None``.
		:param dependents:     Optional, siblings needing this workflow. Default: ``None``.
		:raises TypeError:     If parameter 'reference' is not of type :class:`str`.
		:raises PipelineError: If the calling workflow calls a workflow of that name already.
		"""
		if reference is not None and not isinstance(reference, str):
			ex = TypeError("Parameter 'reference' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(reference)}'.")
			raise ex

		super().__init__(
			name, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome,
			keyValuePairs=keyValuePairs, parent=parent
		)
		ConditionMixin.__init__(self, condition)
		DependencyMixin.__init__(self, needs, dependents)

		self._reference = reference
		self._workflows = {}
		self._matrices =  {}

	def _AddElement(self, element: Base) -> None:
		"""
		Add an element, which names the workflow as its parent, and index a called workflow or a matrix by its name.

		:param element:        The element.
		:raises PipelineError: If the workflow calls a workflow of that name already.
		:raises PipelineError: If the workflow contains a matrix of that name already.
		"""
		if isinstance(element, Workflow):
			if element._name in self._workflows:
				raise PipelineError(f"Workflow '{self._name}' calls a workflow '{element._name}' already.")

			self._workflows[element._name] = element
		elif isinstance(element, Matrix):
			if element._name in self._matrices:
				raise PipelineError(f"Workflow '{self._name}' contains a matrix '{element._name}' already.")

			self._matrices[element._name] = element

		super()._AddElement(element)

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
		Read-only property to access the workflows this workflow calls, by name (:attr:`_workflows`).

		:returns: The called workflows, in the order they were added.
		"""
		return self._workflows

	@readonly
	def Matrices(self) -> dict[str, Matrix]:
		"""
		Read-only property to access the matrices of this workflow, by the name their instances share (:attr:`_matrices`).

		:returns: The matrices, in the order they were added.
		"""
		return self._matrices

	def ToGraph(self, depth: Nullable[int] = None, reduce: bool = True) -> Graph:
		"""
		Convert the workflow into a graph of the elements it contains and their dependencies.

		Every element one level below the workflow becomes a :class:`~pyTooling.Graph.Vertex` of the graph, with the
		element as its :attr:`~pyTooling.Graph.Vertex.ID` and its :attr:`~pyTooling.Graph.Vertex.Value`, so
		:meth:`Graph.GetVertexByID <pyTooling.Graph.Graph.GetVertexByID>` finds an element's vertex. A vertex has no
		name; a consumer labels it by :pycode:`vertex.Value.QualifiedName`. Every dependency becomes an
		:class:`~pyTooling.Graph.Edge` from the element needing to the element it needs, so an edge reads *needs*, and
		:meth:`Graph.IterateTopologically <pyTooling.Graph.BaseGraph.IterateTopologically>` yields the elements in an order
		they can run in.

		A called workflow or a matrix holding elements is expanded into a :class:`~pyTooling.Graph.Subgraph` named by
		its qualified name, whose vertices and edges are built the same way. The group's vertex has a
		:class:`~pyTooling.Graph.Link` to each vertex of its subgraph. The graph's own vertices and edges don't
		include those of its subgraphs, since :mod:`pyTooling.Graph` registers them on the subgraph.

		By default, the graph and every subgraph are reduced to their transitive reduction: a dependency a longer path
		already implies - ``C`` needing ``A`` although it needs ``B``, which needs ``A`` - has no edge. With ``reduce``
		set to ``False``, every dependency has one.

		:param depth:       Optional, how many levels of nested groups to expand; ``0`` expands none, ``None`` every
		                    level. Default: ``None``.
		:param reduce:      Optional, ``True``, if the edges a longer path already implies are removed. Default:
		                    ``True``.
		:returns:           The graph, named like the workflow.
		:raises TypeError:  If parameter 'depth' is not of type :class:`int`.
		:raises ValueError: If parameter 'depth' is negative.
		:raises ValueError: If parameter 'reduce' is None.
		:raises TypeError:  If parameter 'reduce' is not of type :class:`bool`.

		.. seealso::

		   :meth:`Graph.RemoveTransitiveEdges <pyTooling.Graph.BaseGraph.RemoveTransitiveEdges>`
		      |rarr| Remove the edges a longer path already implies.
		"""
		if depth is not None:
			if not isinstance(depth, int) or isinstance(depth, bool):
				ex = TypeError("Parameter 'depth' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
				raise ex
			elif depth < 0:
				ex = ValueError("Parameter 'depth' is negative.")
				ex.add_note(f"Got value '{depth}'.")
				raise ex

		if reduce is None:
			raise ValueError("Parameter 'reduce' is None.")
		elif not isinstance(reduce, bool):
			ex = TypeError("Parameter 'reduce' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(reduce)}'.")
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
			for element in group.IterateElements():
				vertex = Vertex(vertexID=element, value=element, graph=graph, subgraph=subgraph)
				vertices[element] = vertex
				if groupVertex is not None:
					groupVertex.LinkToVertex(vertex)

			for element, vertex in vertices.items():
				for need in element._needs:
					vertex.EdgeToVertex(vertices[need])

			if depth is not None and level >= depth:
				return

			for element, vertex in vertices.items():
				if isinstance(element, JobGroup) and element.ElementCount > 0:
					addContents(element, Subgraph(graph, name=element.QualifiedName), vertex, level + 1)

		addContents(self, None, None, 0)

		if reduce:
			graph.RemoveTransitiveEdges()
			for subgraph in graph.Subgraphs:
				subgraph.RemoveTransitiveEdges()

		return graph


@export
class Pipeline(Workflow):
	"""
	A pipeline: the workflow a service started, holding everything else.

	A pipeline can need another pipeline of its :class:`PipelineGroup`, e.g. one triggered by another's completion.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = PipelineGroup  #: A pipeline is contained in a pipeline group.

	def __init__(
		self,
		name:          str,
		*,
		condition:     Nullable[str]                       = None,
		createdAt:     Nullable[datetime]                  = None,
		startedAt:     Nullable[datetime]                  = None,
		completedAt:   Nullable[datetime]                  = None,
		outcome:       Nullable[Outcome]                   = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]]    = None,
		parent:        Nullable[PipelineGroup]             = None,
		needs:         Nullable[Iterable[DependencyMixin]] = None,
		dependents:    Nullable[Iterable[DependencyMixin]] = None
	) -> None:
		"""
		Initializes a pipeline.

		:param name:          Name of the pipeline.
		:param condition:     Optional, condition under which the pipeline runs, as written. Default: ``None``.
		:param createdAt:     Optional, time the pipeline was created. Default: ``None``.
		:param startedAt:     Optional, time the pipeline started. Default: ``None``.
		:param completedAt:   Optional, time the pipeline completed. Default: ``None``.
		:param outcome:       Optional, how the pipeline ended. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the group of pipelines. Default: ``None``.
		:param needs:         Optional, siblings this pipeline needs. Default: ``None``.
		:param dependents:    Optional, siblings needing this pipeline. Default: ``None``.
		"""
		super().__init__(
			name, condition=condition, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome,
			keyValuePairs=keyValuePairs, parent=parent, needs=needs, dependents=dependents
		)

		self._pipeline = self



@export
class Matrix(JobGroup, QualifiedNameMixin, ConditionMixin, DependencyMixin):
	"""
	A matrix, grouping the instances it produced: jobs, or called workflows.

	The matrix is an element of its workflow, so it can need and be needed by its siblings. A service doesn't report a
	matrix as an element of its own, so it has no times of its own and spans its instances.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Workflow  #: A matrix is contained in a workflow.

	def __init__(
		self,
		name:          str,
		*,
		condition:     Nullable[str]                       = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]]    = None,
		parent:        Nullable[Workflow]                  = None,
		needs:         Nullable[Iterable[DependencyMixin]] = None,
		dependents:    Nullable[Iterable[DependencyMixin]] = None
	) -> None:
		"""
		Initializes a matrix.

		:param name:           Name of the matrix, which its instances share.
		:param condition:      Optional, condition under which the instances run, as written. Default: ``None``.
		:param keyValuePairs:  Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:         Optional, reference to the workflow containing the matrix. Default: ``None``.
		:param needs:          Optional, siblings this matrix needs. Default: ``None``.
		:param dependents:     Optional, siblings needing this matrix. Default: ``None``.
		:raises PipelineError: If the workflow contains a matrix of that name already.
		"""
		super().__init__(name, keyValuePairs=keyValuePairs, parent=parent)
		ConditionMixin.__init__(self, condition)
		DependencyMixin.__init__(self, needs, dependents)

	@readonly
	def Instances(self) -> list[Base]:
		"""
		Read-only property to access the instances this matrix produced (:attr:`_elements`).

		:returns: The :class:`MatrixJob` or :class:`MatrixWorkflow` instances, in the order they were added.
		"""
		return self._elements


@export
class MatrixWorkflow(Workflow, MatrixInstanceMixin):
	"""
	One instance of a called workflow produced by a matrix.

	A GitHub job with ``strategy.matrix`` and ``uses:`` produces such instances.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Matrix  #: A matrix instance is contained in a matrix.

	def __init__(
		self,
		name:          str,
		dimensions:    Nullable[Mapping[str, Any]]         = None,
		*,
		reference:     Nullable[str]                       = None,
		condition:     Nullable[str]                       = None,
		createdAt:     Nullable[datetime]                  = None,
		startedAt:     Nullable[datetime]                  = None,
		completedAt:   Nullable[datetime]                  = None,
		outcome:       Nullable[Outcome]                   = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]]    = None,
		parent:        Nullable[Matrix]                    = None,
		needs:         Nullable[Iterable[DependencyMixin]] = None,
		dependents:    Nullable[Iterable[DependencyMixin]] = None
	) -> None:
		"""
		Initializes one instance of a called workflow produced by a matrix.

		:param name:          Name of the workflow, without the dimensions' values.
		:param dimensions:    Optional, the dimensions' names and values this instance ran with. Default: ``None``.
		:param reference:     Optional, what the workflow calls, as written. Default: ``None``.
		:param condition:     Optional, condition under which the workflow is called, as written. Default: ``None``.
		:param createdAt:     Optional, time the workflow was created, if the service reports it. Default: ``None``.
		:param startedAt:     Optional, time the workflow started, if the service reports it. Default: ``None``.
		:param completedAt:   Optional, time the workflow completed, if the service reports it. Default: ``None``.
		:param outcome:       Optional, how the workflow ended, if the service reports it. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the matrix containing the instance. Default: ``None``.
		:param needs:         Optional, siblings this instance needs. Default: ``None``.
		:param dependents:    Optional, siblings needing this instance. Default: ``None``.
		"""
		super().__init__(
			name, reference=reference, condition=condition, createdAt=createdAt, startedAt=startedAt,
			completedAt=completedAt, outcome=outcome, keyValuePairs=keyValuePairs, parent=parent
		)
		MatrixInstanceMixin.__init__(self, dimensions)
		DependencyMixin.__init__(self, needs, dependents)

	def __str__(self) -> str:
		"""
		Return a string representation of the matrix instance.

		:returns: The workflow's name, followed by its dimensions' values in brackets, if it has any.
		"""
		if len(self._dimensions) == 0:
			return self._name

		return f"{self._name} ({', '.join(str(value) for value in self._dimensions.values())})"


@export
class Job(Base, QualifiedNameMixin, ConditionMixin, DependencyMixin):
	"""A job, which runs its steps on a worker."""

	_PARENT_TYPE: ClassVar[Nullable[type]] = JobGroup  #: A job is contained in a job group.

	_steps: list[Step]  #: Steps of the job.

	def __init__(
		self,
		name:          str,
		*,
		condition:     Nullable[str]                       = None,
		createdAt:     Nullable[datetime]                  = None,
		startedAt:     Nullable[datetime]                  = None,
		completedAt:   Nullable[datetime]                  = None,
		outcome:       Nullable[Outcome]                   = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]]    = None,
		parent:        Nullable[JobGroup]                  = None,
		needs:         Nullable[Iterable[DependencyMixin]] = None,
		dependents:    Nullable[Iterable[DependencyMixin]] = None
	) -> None:
		"""
		Initializes a job.

		:param name:          Name of the job.
		:param condition:     Optional, condition under which the job runs, as written. Default: ``None``.
		:param createdAt:     Optional, time the job was created, i.e. queued for a worker. Default: ``None``.
		:param startedAt:     Optional, time the job started running on a worker. Default: ``None``.
		:param completedAt:   Optional, time the job completed. Default: ``None``.
		:param outcome:       Optional, how the job ended. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the group containing the job. Default: ``None``.
		:param needs:         Optional, siblings this job needs. Default: ``None``.
		:param dependents:    Optional, siblings needing this job. Default: ``None``.
		"""
		super().__init__(
			name, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome,
			keyValuePairs=keyValuePairs, parent=parent
		)
		ConditionMixin.__init__(self, condition)
		DependencyMixin.__init__(self, needs, dependents)

		self._steps = []

	def _AddElement(self, step: Step) -> None:
		"""
		Add a step, which names the job as its parent.

		:param step: The step.
		"""
		self._steps.append(step)

	@readonly
	def Steps(self) -> list[Step]:
		"""
		Read-only property to access the job's steps (:attr:`_steps`).

		:returns: The steps, in the order they were added.
		"""
		return self._steps

	@readonly
	def StepCount(self) -> int:
		"""
		Read-only property to return the number of steps of the job.

		:returns: Number of steps.
		"""
		return len(self._steps)

	def ContainsStep(self, name: str) -> bool:
		"""
		Check whether a step of that name belongs to the job.

		:param name: Name of the step to check for.
		:returns:    ``True``, if a step of that name belongs to the job.
		"""
		return any(str(step) == name for step in self._steps)

	def IterateSteps(self) -> Iterator[Step]:
		"""
		Iterate the job's steps.

		:returns: An iterator over the steps, in the order they were added.
		"""
		return iter(self._steps)


@export
class MatrixJob(Job, MatrixInstanceMixin):
	"""One instance of a job produced by a matrix."""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Matrix  #: A matrix instance is contained in a matrix.

	def __init__(
		self,
		name:          str,
		dimensions:    Nullable[Mapping[str, Any]]         = None,
		*,
		condition:     Nullable[str]                       = None,
		createdAt:     Nullable[datetime]                  = None,
		startedAt:     Nullable[datetime]                  = None,
		completedAt:   Nullable[datetime]                  = None,
		outcome:       Nullable[Outcome]                   = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]]    = None,
		parent:        Nullable[Matrix]                    = None,
		needs:         Nullable[Iterable[DependencyMixin]] = None,
		dependents:    Nullable[Iterable[DependencyMixin]] = None
	) -> None:
		"""
		Initializes one instance of a job produced by a matrix.

		:param name:          Name of the job, without the dimensions' values.
		:param dimensions:    Optional, the dimensions' names and values this instance ran with. Default: ``None``.
		:param condition:     Optional, condition under which the job runs, as written. Default: ``None``.
		:param createdAt:     Optional, time the job was created, i.e. queued for a worker. Default: ``None``.
		:param startedAt:     Optional, time the job started running on a worker. Default: ``None``.
		:param completedAt:   Optional, time the job completed. Default: ``None``.
		:param outcome:       Optional, how the job ended. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the matrix containing the instance. Default: ``None``.
		:param needs:         Optional, siblings this instance needs. Default: ``None``.
		:param dependents:    Optional, siblings needing this instance. Default: ``None``.
		"""
		super().__init__(
			name, condition=condition, createdAt=createdAt, startedAt=startedAt, completedAt=completedAt, outcome=outcome,
			keyValuePairs=keyValuePairs, parent=parent
		)
		MatrixInstanceMixin.__init__(self, dimensions)
		DependencyMixin.__init__(self, needs, dependents)

	def __str__(self) -> str:
		"""
		Return a string representation of the matrix instance.

		:returns: The job's name, followed by its dimensions' values in brackets, if it has any.
		"""
		if len(self._dimensions) == 0:
			return self._name

		return f"{self._name} ({', '.join(str(value) for value in self._dimensions.values())})"


@export
class Step(Base, ConditionMixin):
	"""A step within a job."""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Job  #: A step is contained in a job.

	def __init__(
		self,
		name:          str,
		*,
		condition:     Nullable[str]                    = None,
		startedAt:     Nullable[datetime]               = None,
		completedAt:   Nullable[datetime]               = None,
		outcome:       Nullable[Outcome]                = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Job]                    = None
	) -> None:
		"""
		Initializes a step within a job.

		:param name:          Name of the step.
		:param condition:     Optional, condition under which the step runs, as written. Default: ``None``.
		:param startedAt:     Optional, time the step started running. Default: ``None``.
		:param completedAt:   Optional, time the step completed. Default: ``None``.
		:param outcome:       Optional, how the step ended. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the job containing the step. Default: ``None``.
		"""
		super().__init__(
			name, startedAt=startedAt, completedAt=completedAt, outcome=outcome, keyValuePairs=keyValuePairs, parent=parent
		)
		ConditionMixin.__init__(self, condition)
