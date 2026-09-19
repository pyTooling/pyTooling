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
A data model of a GitHub Actions workflow run.

The GitHub REST API answers with nested JSON objects whose fields are strings - ``"status": "completed"``,
``"conclusion": "timed_out"``, timestamps as ISO 8601 text. This model reads those payloads once into objects:

.. code-block:: text

   PipelineGroup            every run started for one commit
   +-- Pipeline             a workflow run
       +-- Workflow         a called (reusable) workflow, grouping the jobs it contains
       |   +-- Workflow     a workflow called by that workflow
       |   +-- Matrix       a matrix, grouping the job instances it produced
       |   |   +-- MatrixJob
       |   +-- Job
       +-- Matrix
       +-- Job              a job that ran on a runner
           +-- Step         a step of that job

Every element knows its parent and the pipeline it belongs to, and the string fields become :class:`Status`,
:class:`Conclusion` and :class:`Event` members, so an undocumented value is an error rather than a comparison that
never matches.

The model carries no dependency on what is done with it. Converting a :class:`Pipeline` into a software execution
trace, a graph or a report is a consumer of this model.
"""
from __future__            import annotations

from datetime              import datetime, timezone
from enum                  import Enum
from typing                import Optional as Nullable, Any, ClassVar, Iterable, Iterator, Self, Union

from pyTooling.CI          import JSONObject
from pyTooling.Common      import __version__, getFullyQualifiedName, parseISO8601Timestamp
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import ToolingException
from pyTooling.GenericPath.URL import URL
from pyTooling.MetaClasses import ExtendedType, ThisClass, abstractclass


@export
class GitHubError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.CI.GitHub`."""


@export
class Status(Enum):
	"""The state a workflow run, job or step is in."""

	Queued =     "queued"       #: Waiting to be picked up.
	InProgress = "in_progress"  #: Running.
	Completed =  "completed"    #: Finished, with a :class:`Conclusion`.
	Waiting =    "waiting"      #: Held, e.g. for an environment's approval.
	Requested =  "requested"    #: Requested, but not yet queued.
	Pending =    "pending"      #: Blocked by a concurrency group.

	@classmethod
	def Parse(cls, value: Nullable[str]) -> Nullable[Status]:
		"""
		Convert GitHub's ``status`` field to a member of this enumeration.

		:param value:        Optional, the field's value. Default: ``None``.
		:returns:            The matching member, or ``None`` if the field was absent or empty.
		:raises GitHubError: If the value is not a status GitHub documents. |br|
		                     The note lists the documented values.
		"""
		if value is None or value == "":
			return None

		try:
			return cls(value)
		except ValueError as ex:
			error = GitHubError(f"'{value}' is not a GitHub status.")
			error.add_note(f"Known: {', '.join(member.value for member in cls)}.")
			raise error from ex


@export
class Conclusion(Enum):
	"""How a completed workflow run, job or step ended."""

	Success =        "success"          #: Succeeded.
	Failure =        "failure"          #: Failed.
	Cancelled =      "cancelled"        #: Cancelled before it finished.
	Skipped =        "skipped"          #: Not run, because a condition excluded it.
	TimedOut =       "timed_out"        #: Stopped by a timeout.
	ActionRequired = "action_required"  #: Waiting for a manual action.
	Neutral =        "neutral"          #: Finished without a verdict.
	Stale =          "stale"            #: Never ran, because the run was superseded.
	StartupFailure = "startup_failure"  #: The workflow file itself couldn't be started.

	@classmethod
	def Parse(cls, value: Nullable[str]) -> Nullable[Conclusion]:
		"""
		Convert GitHub's ``conclusion`` field to a member of this enumeration.

		:param value:        Optional, the field's value. Default: ``None``.
		:returns:            The matching member, or ``None`` while it hasn't concluded.
		:raises GitHubError: If the value is not a conclusion GitHub documents. |br|
		                     The note lists the documented values.
		"""
		if value is None or value == "":
			return None

		try:
			return cls(value)
		except ValueError as ex:
			error = GitHubError(f"'{value}' is not a GitHub conclusion.")
			error.add_note(f"Known: {', '.join(member.value for member in cls)}.")
			raise error from ex


@export
class Event(Enum):
	"""The event that triggered a workflow run."""

	CheckRun                 = "check_run"                    #: A check run was created or completed.
	CheckSuite               = "check_suite"                  #: A check suite was created or completed.
	Create                   = "create"                       #: A branch or tag was created.
	Delete                   = "delete"                       #: A branch or tag was deleted.
	Deployment               = "deployment"                   #: A deployment was created.
	DeploymentStatus         = "deployment_status"            #: A deployment's status changed.
	Discussion               = "discussion"                   #: A discussion was touched.
	DiscussionComment        = "discussion_comment"           #: A discussion was commented on.
	Fork                     = "fork"                         #: The repository was forked.
	Gollum                   = "gollum"                       #: A wiki page was created or updated.
	IssueComment             = "issue_comment"                #: An issue or pull-request was commented on.
	Issues                   = "issues"                       #: An issue was touched.
	Label                    = "label"                        #: A label was touched.
	MergeGroup               = "merge_group"                  #: A merge group entered the merge queue.
	Milestone                = "milestone"                    #: A milestone was touched.
	PageBuild                = "page_build"                   #: GitHub Pages was built.
	Public                   = "public"                       #: The repository was made public.
	PullRequest              = "pull_request"                 #: A pull-request was touched.
	PullRequestComment       = "pull_request_comment"         #: A pull-request was commented on.
	PullRequestReview        = "pull_request_review"          #: A pull-request was reviewed.
	PullRequestReviewComment = "pull_request_review_comment"  #: A review was commented on.
	PullRequestTarget        = "pull_request_target"          #: A pull-request, run against its base.
	Push                     = "push"                         #: A commit or tag was pushed.
	RegistryPackage          = "registry_package"             #: A package was published or updated.
	Release                  = "release"                      #: A release was touched.
	RepositoryDispatch       = "repository_dispatch"          #: An external event was dispatched.
	Schedule                 = "schedule"                     #: A cron schedule fired.
	Status                   = "status"                       #: A commit's status changed.
	Watch                    = "watch"                        #: The repository was starred.
	WorkflowCall             = "workflow_call"                #: The workflow was called by another one.
	WorkflowDispatch         = "workflow_dispatch"            #: The workflow was started by hand or by a token.
	WorkflowRun              = "workflow_run"                 #: Another workflow run completed.
	Dynamic                  = "dynamic"                      #: GitHub started the run without a workflow file.

	@classmethod
	def Parse(cls, value: Nullable[str]) -> Nullable[Event]:
		"""
		Convert GitHub's ``event`` field to a member of this enumeration.

		:param value:        Optional, the field's value. Default: ``None``.
		:returns:            The matching member, or ``None`` if the field was absent or empty.
		:raises GitHubError: If the value is not an event GitHub documents. |br|
		                     The note lists the documented values.
		"""
		if value is None or value == "":
			return None

		try:
			return cls(value)
		except ValueError as ex:
			error = GitHubError(f"'{value}' is not a GitHub event.")
			error.add_note(f"Known: {', '.join(member.value for member in cls)}.")
			raise error from ex


def _parseISO8601Timestamp(value: Nullable[str], field: str) -> Nullable[datetime]:
	"""
	Parse an ISO 8601 timestamp, as the GitHub REST API reports them.

	A timestamp without a time zone is read as UTC, so every timestamp of a run can be compared with every other.

	:param value:        Optional, the field's value. Default: ``None``.
	:param field:        Name of the field, for the exception's message.
	:returns:            The timestamp, or ``None`` if the field was absent or empty.
	:raises GitHubError: If the value isn't an ISO 8601 timestamp. |br|
	                     The note reports the value that was read.
	"""
	try:
		return parseISO8601Timestamp(value, timezone.utc)
	except ValueError as ex:
		error = GitHubError(f"Field '{field}' isn't an ISO 8601 timestamp.")
		error.add_note(f"Got '{value}'.")
		raise error from ex


def _parseURL(value: Nullable[str], field: str) -> Nullable[URL]:
	"""
	Parse a URL, as the GitHub REST API reports them.

	:param value: Optional, the field's value. Default: ``None``.
	:param field: Name of the field, kept for symmetry with :func:`_parseISO8601Timestamp` and for the message this
	              will report once :meth:`~pyTooling.GenericPath.URL.URL.Parse` rejects what isn't a URL.
	:returns:     The URL, or ``None`` if the field was absent or empty.
	"""
	if value is None or value == "":
		return None

	return URL.Parse(value)


def _splitMatrixJobName(name: str) -> tuple[str, Nullable[list[str]]]:
	"""
	Split a job's name into the matrix' name and the dimension values, if it carries any.

	GitHub appends the dimension values of a matrix instance to the job's name, as ``Unit Tests (ubuntu-26.04, 3.14)``.
	That bracketed suffix is a naming convention of GitHub's own interface, not a field of the payload, so a job
	genuinely named ``Build (fast)`` and produced by no matrix is indistinguishable from one that was. A job whose
	workflow sets its own ``name:`` carries no values at all, and its matrix stays invisible.

	:param name: The job's name, without any calling workflows' prefixes.
	:returns:    The name without the suffix and the dimension values, or the name and ``None`` if it carries none.
	"""
	if not name.endswith(")") or "(" not in name:
		return name, None

	base, _, values = name[:-1].rpartition("(")
	base = base.rstrip()
	if base == "":
		return name, None

	return base, [value.strip() for value in values.split(",")]


@export
@abstractclass
class Base(metaclass=ExtendedType, slots=True):
	"""
	Common behaviour of every element of a workflow run.

	Every element has a name, a position in the tree, a :class:`Status` and - once completed - a :class:`Conclusion`,
	and the timestamps GitHub reports for it.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = None  #: Type a parent must have, or ``None`` when it has no parent.

	_name:        str                   #: Name of the element.
	_parent:      Nullable[Base]        #: Reference to the containing element.
	_pipeline:    Nullable[Pipeline]    #: Reference to the workflow run this element belongs to.
	_status:      Nullable[Status]      #: State the element is in.
	_conclusion:  Nullable[Conclusion]  #: How the element ended.
	_createdAt:   Nullable[datetime]    #: Time the element was created.
	_startedAt:   Nullable[datetime]    #: Time the element started running.
	_completedAt: Nullable[datetime]    #: Time the element completed.
	_url:         Nullable[URL]         #: URL of the element on github.com.

	def __init__(
		self,
		name:        str,
		status:      Nullable[Status]     = None,
		conclusion:  Nullable[Conclusion] = None,
		createdAt:   Nullable[datetime]   = None,
		startedAt:   Nullable[datetime]   = None,
		completedAt: Nullable[datetime]   = None,
		url:         Nullable[URL]        = None,
		*,
		parent:      Nullable[Base] = None
	) -> None:
		"""
		Initializes an element of a workflow run.

		:param name:        Name of the element.
		:param status:      Optional, state the element is in. Default: ``None``.
		:param conclusion:  Optional, how the element ended. Default: ``None``.
		:param createdAt:   Optional, time the element was created. Default: ``None``.
		:param startedAt:   Optional, time the element started running. Default: ``None``.
		:param completedAt: Optional, time the element completed. Default: ``None``.
		:param url:         Optional, URL of the element on github.com. Default: ``None``.
		:param parent:      Optional, reference to the containing element. Default: ``None``.
		:raises ValueError: If parameter 'name' is ``None``.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		:raises TypeError:  If parameter 'status' is not of type :class:`Status`.
		:raises TypeError:  If parameter 'conclusion' is not of type :class:`Conclusion`.
		:raises TypeError:  If parameter 'createdAt' is not of type :class:`~datetime.datetime`.
		:raises TypeError:  If parameter 'startedAt' is not of type :class:`~datetime.datetime`.
		:raises TypeError:  If parameter 'completedAt' is not of type :class:`~datetime.datetime`.
		:raises TypeError:  If parameter 'url' is not of type :class:`~pyTooling.GenericPath.URL.URL`.
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

		if status is not None and not isinstance(status, Status):
			ex = TypeError("Parameter 'status' is not of type 'Status'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(status)}'.")
			raise ex

		if conclusion is not None and not isinstance(conclusion, Conclusion):
			ex = TypeError("Parameter 'conclusion' is not of type 'Conclusion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(conclusion)}'.")
			raise ex

		for parameterName, timestamp in (("createdAt", createdAt), ("startedAt", startedAt), ("completedAt", completedAt)):
			if timestamp is not None and not isinstance(timestamp, datetime):
				ex = TypeError(f"Parameter '{parameterName}' is not of type 'datetime'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(timestamp)}'.")
				raise ex

		if url is not None and not isinstance(url, URL):
			ex = TypeError("Parameter 'url' is not of type 'URL'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(url)}'.")
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
		self._status =      status
		self._conclusion =  conclusion
		self._createdAt =   createdAt
		self._startedAt =   startedAt
		self._completedAt = completedAt
		self._url =         url

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

		:returns: The containing element, or ``None`` for a :class:`PipelineGroup`.
		"""
		return self._parent

	@readonly
	def Pipeline(self) -> Nullable[Pipeline]:
		"""
		Read-only property to access the workflow run this element belongs to (:attr:`_pipeline`).

		:returns: The workflow run, or ``None`` for an element outside one.
		"""
		return self._pipeline

	@readonly
	def Status(self) -> Nullable[Status]:
		"""
		Read-only property to access the state the element is in (:attr:`_status`).

		:returns: The state, or ``None`` if GitHub reported none.
		"""
		return self._status

	@readonly
	def Conclusion(self) -> Nullable[Conclusion]:
		"""
		Read-only property to access how the element ended (:attr:`_conclusion`).

		:returns: The conclusion, or ``None`` while the element hasn't concluded.
		"""
		return self._conclusion

	@readonly
	def CreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to access the time the element was created (:attr:`_createdAt`).

		:returns: The time, or ``None`` if GitHub reported none.
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
	def URL(self) -> Nullable[URL]:
		"""
		Read-only property to access the element's URL on github.com (:attr:`_url`).

		:returns: The URL, or ``None`` if GitHub reported none.
		"""
		return self._url

	@readonly
	def Duration(self) -> Nullable[float]:
		"""
		Read-only property to return how long the element ran.

		The times are read through :attr:`StartedAt` and :attr:`CompletedAt`, so a :class:`JobGroup` - which has no
		times of its own and derives them from its jobs - reports a duration too.

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
	Mixin-class for elements GitHub names by the workflows containing them.

	:meth:`Pipeline.FromJSON` takes such a name apart - ``Caller / Build (ubuntu-26.04)`` becomes a job ``Build``
	below a :class:`Workflow` ``Caller``, with the dimension values on a :class:`MatrixJob` - and this mixin puts it
	back together, so a report can name an element the way the service does.

	It is mixed into elements of the tree :class:`Base` builds and walks it upwards, so the ``expects`` contract
	requires :attr:`Base._parent` from whichever class it ends up in. The element itself is named by :func:`str`,
	which every class has; a containing workflow is read as a :class:`Workflow`, which this module declares.
	"""

	@readonly
	def QualifiedName(self) -> str:
		"""
		Read-only property to return the element's name, prefixed by the names of the workflows containing it.

		The element itself is named by :func:`str`, so a :class:`MatrixJob` carries the dimension values it was
		produced for. The walk ends at the :class:`Pipeline`, which is a run rather than a called workflow, and passes
		through a :class:`Matrix` without naming it - a matrix shares its name with the jobs it produced.

		:returns: The name, with every calling workflow in front of it, separated by ``' / '``.
		"""
		names =   [str(self)]
		element = self
		while (element := element._parent) is not None and not isinstance(element, Pipeline):
			if isinstance(element, Workflow):
				names.append(element._name)

		return " / ".join(reversed(names))


@export
class PipelineGroup(Base):
	"""
	Every workflow run GitHub started for one commit, and the top of the tree.

	A push starts one run per workflow file whose triggers match, so a commit has as many pipelines as the repository
	has matching workflows - `pyTooling/Actions` answers a push with six.

	**A run at a tag is in the group as well, and is not the same thing.** It carries the same commit, so the API
	cannot separate it, but it was started later and for a different reason: a release pipeline tags its own commit,
	and the run at that tag publishes the release. For `pyTooling/MiKTeX` v1.6.0 the two runs of commit ``2c36ead``
	were

	.. code-block:: text

	   event=push               head_branch=main     run_started_at=07:53:39   tags the commit
	   event=workflow_dispatch  head_branch=v1.6.0   run_started_at=08:09:37   publishes the release

	:meth:`ByGitReference` separates them, since :attr:`Pipeline.GitReference` holds the tag's name for the second.

	The group has no times of its own and derives them from its pipelines - so its span covers the tag's run too, and
	is wider than the time the commit's checks took.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = None  #: A pipeline group is the top of the tree and has no parent.

	_pipelines: list[Pipeline]  #: Pipelines started for the commit.

	def __init__(self, sha: str, pipelines: Nullable[Iterable[Pipeline]] = None) -> None:
		"""
		Initializes a group of pipelines started for one commit.

		:param sha:         Commit every pipeline of the group was started on.
		:param pipelines:   Optional, the pipelines. Default: ``None``.
		:raises TypeError:  If parameter 'sha' is not of type :class:`str`.
		:raises ValueError: If parameter 'sha' is empty.
		:raises TypeError:  If an element of parameter 'pipelines' is not of type :class:`Pipeline`.
		"""
		super().__init__(sha)

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
	def SHA(self) -> str:
		"""
		Read-only property to access the commit every pipeline of the group was started on (:attr:`_name`).

		:returns: The commit's hash.
		"""
		return self._name

	@readonly
	def Pipelines(self) -> list[Pipeline]:
		"""
		Read-only property to access the pipelines started for the commit (:attr:`_pipelines`).

		:returns: The pipelines, in the order they were reported.
		"""
		return self._pipelines

	@readonly
	def CreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first pipeline of the group was created.

		:returns: The time, or ``None`` if no pipeline of the group reports one.
		"""
		times = [pipeline.CreatedAt for pipeline in self._pipelines if pipeline.CreatedAt is not None]

		return min(times) if len(times) > 0 else None

	@readonly
	def StartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first pipeline of the group started.

		:returns: The time, or ``None`` if no pipeline of the group has started.
		"""
		times = [pipeline.StartedAt for pipeline in self._pipelines if pipeline.StartedAt is not None]

		return min(times) if len(times) > 0 else None

	@readonly
	def CompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the last pipeline of the group completed.

		:returns: The time, or ``None`` while a pipeline of the group hasn't completed.
		"""
		if len(self._pipelines) == 0:
			return None

		times = []
		for pipeline in self._pipelines:
			if pipeline.CompletedAt is None:
				return None

			times.append(pipeline.CompletedAt)

		return max(times)

	@readonly
	def Conclusion(self) -> Nullable[Conclusion]:
		"""
		Read-only property to return how the commit's pipelines ended, taken together.

		The worst conclusion wins, so one failed pipeline makes the commit's verdict a failure, as a branch protection
		rule would. The order is:

		#. :attr:`~Conclusion.Failure`
		#. :attr:`~Conclusion.TimedOut`
		#. :attr:`~Conclusion.StartupFailure`
		#. :attr:`~Conclusion.ActionRequired`
		#. :attr:`~Conclusion.Cancelled`
		#. :attr:`~Conclusion.Stale`
		#. :attr:`~Conclusion.Neutral`
		#. :attr:`~Conclusion.Skipped`
		#. :attr:`~Conclusion.Success`

		:returns: The worst conclusion of the group's pipelines, or ``None`` while one hasn't concluded.
		"""
		if len(self._pipelines) == 0:
			return None

		conclusions = set()
		for pipeline in self._pipelines:
			if pipeline.Conclusion is None:
				return None

			conclusions.add(pipeline.Conclusion)

		for conclusion in (
			Conclusion.Failure, Conclusion.TimedOut, Conclusion.StartupFailure, Conclusion.ActionRequired,
			Conclusion.Cancelled, Conclusion.Stale, Conclusion.Neutral, Conclusion.Skipped, Conclusion.Success
		):
			if conclusion in conclusions:
				return conclusion

		return None

	def ByGitReference(self) -> dict[Nullable[str], list[Pipeline]]:
		"""
		Group the commit's pipelines by the branch or tag they were started on.

		A commit pushed to a branch and later tagged has its pipelines under two keys - the branch's name and the
		tag's - which is what separates the checks of a commit from the run that published its release.

		:returns: Dictionary of a reference's name to the pipelines started on it, in the order they were reported.
		"""
		byReference: dict[Nullable[str], list[Pipeline]] = {}
		for pipeline in self._pipelines:
			if (pipelines := byReference.get(pipeline.GitReference, None)) is None:
				pipelines = []
				byReference[pipeline.GitReference] = pipelines

			pipelines.append(pipeline)

		return byReference

	def IterateJobs(self) -> Iterator[Job]:
		"""
		Iterate every job of every pipeline of the group.

		:returns: An iterator over the jobs.
		"""
		for pipeline in self._pipelines:
			yield from pipeline.IterateJobs()

	def __len__(self) -> int:
		"""
		Return the number of pipelines started for the commit.

		:returns: Number of pipelines.
		"""
		return len(self._pipelines)

	def __contains__(self, name: str) -> bool:
		"""
		Check whether a pipeline of that name was started for the commit.

		:param name: Name of the pipeline to check for.
		:returns:    ``True``, if a pipeline of that name belongs to the group.
		"""
		return any(str(pipeline) == name for pipeline in self._pipelines)

	def __iter__(self) -> Iterator[Pipeline]:
		"""
		Iterate the pipelines started for the commit.

		:returns: An iterator over the pipelines.
		"""
		return iter(self._pipelines)

	@classmethod
	def FromJSON(
		cls,
		runs: Union[JSONObject, Iterable[JSONObject]],
		jobs: Nullable[dict[int, Iterable[JSONObject]]] = None,
		sha:  Nullable[str] = None
	) -> Self:
		"""
		Build a group of pipelines from the JSON objects the GitHub REST API answers with.

		:param runs:         The runs, as returned by ``GET /repos/{owner}/{repo}/actions/runs?head_sha=...`` - either
		                     the answer itself or its ``workflow_runs`` array.
		:param jobs:         Optional, the jobs of each run, by the run's identifier. Default: ``None``.
		:param sha:          Optional, the commit. Default: the ``head_sha`` the runs report.
		:returns:            The group, with its pipelines attached.
		:raises GitHubError: If the runs report different commits.
		:raises GitHubError: If no run reports a commit and parameter 'sha' wasn't given.
		"""
		if not isinstance(runs, dict):
			workflowRuns = runs
		elif (workflowRuns := runs.get("workflow_runs", None)) is None:
			workflowRuns = []

		pipelines = []
		shas = set()
		for run in workflowRuns:
			runJobs = None
			if jobs is not None:
				runJobs = jobs.get(run.get("id", None), None)

			pipeline = Pipeline.FromJSON(run, runJobs)
			pipelines.append(pipeline)
			if pipeline.SHA is not None:
				shas.add(pipeline.SHA)

		if sha is None:
			if (commits := len(shas)) == 0:
				raise GitHubError("None of the runs reports a 'head_sha', and parameter 'sha' wasn't given.")
			elif commits > 1:
				error = GitHubError("The runs report different commits.")
				error.add_note(f"Got {', '.join(sorted(shas))}.")
				raise error

			sha = shas.pop()

		return cls(sha, pipelines)


@export
@abstractclass
class JobGroup(Base):
	"""
	A group of jobs, which has no times of its own and derives them from the jobs it contains.

	It is the shared behaviour of a :class:`Matrix` and a :class:`Workflow` - GitHub reports neither as an element, so
	neither has a status, a conclusion or timestamps of its own.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = None  #: Declared by the groups deriving from this class.

	_jobs: list[Job]  #: Jobs of this group.

	def __init__(self, name: str, *, parent: Nullable[Base] = None) -> None:
		"""
		Initializes a group of jobs.

		:param name:   Name of the group.
		:param parent: Optional, reference to the element containing the group. Default: ``None``.
		"""
		super().__init__(name, parent=parent)

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
		Read-only property to return when the first job of this group was created.

		:returns: The time, or ``None`` if no job of the group reports one.
		"""
		times = [job.CreatedAt for job in self._jobs if job.CreatedAt is not None]

		return min(times) if len(times) > 0 else None

	@readonly
	def StartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first job of this group started.

		:returns: The time, or ``None`` if no job of the group has started.
		"""
		times = [job.StartedAt for job in self._jobs if job.StartedAt is not None]

		return min(times) if len(times) > 0 else None

	@readonly
	def CompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the last job of this group completed.

		:returns: The time, or ``None`` while a job of the group hasn't completed.
		"""
		if len(self._jobs) == 0 or any(job.CompletedAt is None for job in self._jobs):
			return None

		return max(job.CompletedAt for job in self._jobs)

	def __len__(self) -> int:
		"""
		Return the number of jobs of this group.

		:returns: Number of jobs.
		"""
		return len(self._jobs)

	def __contains__(self, name: str) -> bool:
		"""
		Check whether a job of that name belongs to this group.

		A job is named the way :func:`str` names it, so an instance of a :class:`Matrix` - which carries the matrix'
		name - is asked for with its dimension values: ``"Unit Tests (ubuntu-26.04, 3.14)"``.

		:param name: Name of the job to check for.
		:returns:    ``True``, if a job of that name belongs to this group.
		"""
		return any(str(job) == name for job in self._jobs)

	def __iter__(self) -> Iterator[Job]:
		"""
		Iterate the jobs of this group.

		:returns: An iterator over the jobs.
		"""
		return iter(self._jobs)


@export
class Workflow(JobGroup, QualifiedNameMixin):
	"""
	A called (reusable) workflow, grouping the jobs it contains.

	GitHub doesn't report a called workflow as an element of its own - it prefixes the names of the jobs it contains,
	as ``Caller / Job``. :meth:`Pipeline.FromJSON` reads those prefixes back into this level, so the tree shows which
	workflow a job came from. A workflow may call another, and the tree nests as deeply as the caller chain is long.

	.. caution::

	   **A called workflow carries less information than a run.** Its name is the only thing GitHub reports about it,
	   recovered from the prefix of a job's name, so this class has no counterpart to
	   :attr:`Pipeline.Path` (the workflow's YAML file), :attr:`Pipeline.WorkflowID`, or the ``@ref`` the caller
	   pinned it at - and it has no status, conclusion or timestamps of its own either, which is why
	   :class:`JobGroup` derives them from the jobs below it.

	   Neither the runs nor the jobs payload holds any of it. Filling these in means reading the caller's workflow
	   file and resolving its ``uses:`` entries, which is a different source than this model reads. See
	   `issue #408 <https://github.com/pyTooling/pyTooling/issues/408>`__.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = ThisClass  #: A workflow is contained in a workflow.

	_workflows: dict[str, Workflow]  #: Workflows called by this workflow, by name.
	_matrices:  dict[str, Matrix]    #: Matrices of this workflow, by the name their jobs share.

	def __init__(self, name: str, *, parent: Nullable[Workflow] = None) -> None:
		"""
		Initializes a called workflow.

		:param name:   Name of the workflow, as it prefixes its jobs' names.
		:param parent: Optional, reference to the workflow calling this one. Default: ``None``.
		"""
		super().__init__(name, parent=parent)

		self._workflows = {}
		self._matrices =  {}

		if parent is not None:
			parent._workflows[name] = self

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

	@readonly
	def CreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first job below this workflow was created.

		Unlike a :class:`Matrix`, a workflow contains further groups, so the time covers the jobs of its matrices and
		of the workflows it calls as well.

		:returns: The time, or ``None`` if no job below the workflow reports one.
		"""
		times = [job.CreatedAt for job in self._jobs if job.CreatedAt is not None]
		for matrix in self._matrices.values():
			if matrix.CreatedAt is not None:
				times.append(matrix.CreatedAt)

		for workflow in self._workflows.values():
			if workflow.CreatedAt is not None:
				times.append(workflow.CreatedAt)

		return min(times) if len(times) > 0 else None

	@readonly
	def StartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the first job below this workflow started.

		:returns: The time, or ``None`` if no job below the workflow has started.
		"""
		times = [job.StartedAt for job in self._jobs if job.StartedAt is not None]
		for matrix in self._matrices.values():
			if matrix.StartedAt is not None:
				times.append(matrix.StartedAt)

		for workflow in self._workflows.values():
			if workflow.StartedAt is not None:
				times.append(workflow.StartedAt)

		return min(times) if len(times) > 0 else None

	@readonly
	def CompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to return when the last job below this workflow completed.

		:returns: The time, or ``None`` while a job below the workflow hasn't completed, or while it holds none.
		"""
		times = []
		for job in self._jobs:
			if job.CompletedAt is None:
				return None

			times.append(job.CompletedAt)

		for matrix in self._matrices.values():
			if matrix.CompletedAt is None:
				return None

			times.append(matrix.CompletedAt)

		for workflow in self._workflows.values():
			if workflow.CompletedAt is None:
				return None

			times.append(workflow.CompletedAt)

		return max(times) if len(times) > 0 else None

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

	def __len__(self) -> int:
		"""
		Return the number of elements this workflow contains: its jobs, its matrices and the workflows it calls.

		Unlike :meth:`IterateJobs`, this counts the elements one level below the workflow, not the jobs below all of
		them.

		:returns: Number of contained elements.
		"""
		return len(self._jobs) + len(self._matrices) + len(self._workflows)

	def __contains__(self, name: str) -> bool:
		"""
		Check whether an element of that name is contained in this workflow.

		The name is looked for among the workflows this one calls, its matrices and its jobs - the elements one level
		below it, the same :meth:`__iter__` yields.

		:param name: Name of the called workflow, matrix or job to check for.
		:returns:    ``True``, if an element of that name is contained in this workflow.
		"""
		return name in self._workflows or name in self._matrices or super().__contains__(name)

	def __iter__(self) -> Iterator[Base]:
		"""
		Iterate the elements this workflow contains: its jobs, then its matrices, then the workflows it calls.

		A :class:`JobGroup` iterates its jobs, but a workflow contains further groups, so it iterates everything one
		level below it. Use :meth:`IterateJobs` to reach the jobs below those groups as well.

		:returns: An iterator over the contained elements.
		"""
		yield from self._jobs
		yield from self._matrices.values()
		yield from self._workflows.values()


@export
class Pipeline(Workflow):
	"""
	A workflow run.

	A run contains its own jobs, a :class:`Matrix` for every matrix, and a :class:`Workflow` for every workflow it
	called. Unlike a called workflow, a run reports its own status, conclusion and times. Several runs of one commit
	are held by a :class:`PipelineGroup`, which is the top of the tree.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = PipelineGroup  #: A pipeline is contained in a pipeline group.

	_id:           Nullable[int]    #: GitHub's identifier of the run.
	_workflowID:   Nullable[int]    #: GitHub's identifier of the workflow the run belongs to.
	_path:         Nullable[str]    #: Path of the workflow's YAML file in the repository.
	_runNumber:    Nullable[int]    #: Number of the run within its workflow.
	_runAttempt:   Nullable[int]    #: Attempt of the run, starting at 1.
	_event:        Nullable[Event]  #: Event that triggered the run.
	_gitReference: Nullable[str]    #: Branch or tag the run was started on.
	_sha:          Nullable[str]    #: Commit the run was started on.

	def __init__(
		self,
		name:         str,
		identifier:   Nullable[int]        = None,
		status:       Nullable[Status]     = None,
		conclusion:   Nullable[Conclusion] = None,
		createdAt:    Nullable[datetime]   = None,
		startedAt:    Nullable[datetime]   = None,
		completedAt:  Nullable[datetime]   = None,
		url:          Nullable[URL]        = None,
		workflowID:   Nullable[int]        = None,
		path:         Nullable[str]        = None,
		runNumber:    Nullable[int]        = None,
		runAttempt:   Nullable[int]        = None,
		event:        Nullable[Event]      = None,
		gitReference: Nullable[str]        = None,
		sha:          Nullable[str]        = None,
		*,
		parent:       Nullable[PipelineGroup] = None
	) -> None:
		"""
		Initializes a workflow run.

		:param name:         Name of the workflow.
		:param identifier:   Optional, GitHub's identifier of the run. Default: ``None``.
		:param status:       Optional, state the run is in. Default: ``None``.
		:param conclusion:   Optional, how the run ended. Default: ``None``.
		:param createdAt:    Optional, time the run was created. Default: ``None``.
		:param startedAt:    Optional, time the run started. Default: ``None``.
		:param completedAt:  Optional, time the run was last updated, once completed. Default: ``None``.
		:param url:          Optional, URL of the run on github.com. Default: ``None``.
		:param workflowID:   Optional, GitHub's identifier of the workflow the run belongs to. Default: ``None``.
		:param path:         Optional, path of the workflow's YAML file in the repository. Default: ``None``.
		:param runNumber:    Optional, number of the run within its workflow. Default: ``None``.
		:param runAttempt:   Optional, attempt of the run, starting at 1. Default: ``None``.
		:param event:        Optional, event that triggered the run. Default: ``None``.
		:param gitReference: Optional, branch or tag the run was started on. Default: ``None``.
		:param sha:          Optional, commit the run was started on. Default: ``None``.
		:param parent:       Optional, reference to the group of the commit's runs. Default: ``None``.
		:raises TypeError:   If parameter 'identifier' is not of type :class:`int`.
		:raises TypeError:   If parameter 'workflowID' is not of type :class:`int`.
		:raises TypeError:   If parameter 'path' is not of type :class:`str`.
		:raises TypeError:   If parameter 'runNumber' is not of type :class:`int`.
		:raises TypeError:   If parameter 'runAttempt' is not of type :class:`int`.
		:raises TypeError:   If parameter 'event' is not of type :class:`Event`.
		:raises TypeError:   If parameter 'gitReference' is not of type :class:`str`.
		:raises TypeError:   If parameter 'sha' is not of type :class:`str`.
		:raises TypeError:   If parameter 'parent' is not of the type this class declares in :attr:`_PARENT_TYPE`.
		"""
		super().__init__(name)

		for parameterName, number in (
			("identifier", identifier), ("workflowID", workflowID), ("runNumber", runNumber), ("runAttempt", runAttempt)
		):
			if number is not None and not isinstance(number, int):
				ex = TypeError(f"Parameter '{parameterName}' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(number)}'.")
				raise ex

		if event is not None and not isinstance(event, Event):
			ex = TypeError("Parameter 'event' is not of type 'Event'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(event)}'.")
			raise ex

		for parameterName, text in (("path", path), ("gitReference", gitReference), ("sha", sha)):
			if text is not None and not isinstance(text, str):
				ex = TypeError(f"Parameter '{parameterName}' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(text)}'.")
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

		self._parent =      parent
		self._pipeline =    self
		self._status =      status
		self._conclusion =  conclusion
		self._createdAt =   createdAt
		self._startedAt =   startedAt
		self._completedAt = completedAt
		self._url =         url

		self._id =           identifier
		self._workflowID =   workflowID
		self._path =         path
		self._runNumber =    runNumber
		self._runAttempt =   runAttempt
		self._event =        event
		self._gitReference = gitReference
		self._sha =          sha

		if parent is not None:
			parent._pipelines.append(self)

	@readonly
	def ID(self) -> Nullable[int]:
		"""
		Read-only property to access GitHub's identifier of the run (:attr:`_id`).

		:returns: The identifier, or ``None`` if GitHub reported none.
		"""
		return self._id

	@readonly
	def WorkflowID(self) -> Nullable[int]:
		"""
		Read-only property to access GitHub's identifier of the workflow the run belongs to (:attr:`_workflowID`).

		Every run of the same workflow file reports the same identifier, so it groups a workflow's runs over time,
		where :attr:`ID` identifies the single run.

		:returns: The identifier, or ``None`` if GitHub reported none.
		"""
		return self._workflowID

	@readonly
	def Path(self) -> Nullable[str]:
		"""
		Read-only property to access the path of the workflow's YAML file (:attr:`_path`).

		GitHub reports it relative to the repository's root, e.g. ``.github/workflows/Pipeline.yml``.

		:returns: The path, or ``None`` if GitHub reported none.
		"""
		return self._path

	@readonly
	def RunNumber(self) -> Nullable[int]:
		"""
		Read-only property to access the run's number within its workflow (:attr:`_runNumber`).

		:returns: The number, or ``None`` if GitHub reported none.
		"""
		return self._runNumber

	@readonly
	def RunAttempt(self) -> Nullable[int]:
		"""
		Read-only property to access which attempt of the run this is (:attr:`_runAttempt`).

		:returns: The attempt, starting at 1, or ``None`` if GitHub reported none.
		"""
		return self._runAttempt

	@readonly
	def Event(self) -> Nullable[Event]:
		"""
		Read-only property to access the event that triggered the run (:attr:`_event`).

		:returns: The event, or ``None`` if GitHub reported none.
		"""
		return self._event

	@readonly
	def GitReference(self) -> Nullable[str]:
		"""
		Read-only property to access the branch or tag the run was started on (:attr:`_gitReference`).

		GitHub reports this as ``head_branch`` and puts the **tag's** name there for a run started at a tag, with no
		field saying which it is - a run of `pyTooling/MiKTeX` v1.6.0 reports ``main``, and the run at the tag of the
		very same commit reports ``v1.6.0``. :attr:`Event` is the other half of telling them apart.

		:returns: The branch's or tag's name, or ``None`` if GitHub reported none.
		"""
		return self._gitReference

	@readonly
	def SHA(self) -> Nullable[str]:
		"""
		Read-only property to access the commit the run was started on (:attr:`_sha`).

		:returns: The commit's hash, or ``None`` if GitHub reported none.
		"""
		return self._sha

	@readonly
	def CreatedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to access the time the run was created (:attr:`_createdAt`).

		Unlike a :class:`JobGroup`, a run reports its own times.

		:returns: The time, or ``None`` if GitHub reported none.
		"""
		return self._createdAt

	@readonly
	def StartedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to access the time the run started (:attr:`_startedAt`).

		:returns: The time, or ``None`` if GitHub reported none.
		"""
		return self._startedAt

	@readonly
	def CompletedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to access the time the run was last updated, once completed (:attr:`_completedAt`).

		:returns: The time, or ``None`` while the run isn't completed.
		"""
		return self._completedAt

	@classmethod
	def FromJSON(
		cls,
		run:  JSONObject,
		jobs: Nullable[Iterable[JSONObject]] = None,
		*,
		parent: Nullable[PipelineGroup] = None
	) -> Self:
		"""
		Build a workflow run and its tree from the JSON objects the GitHub REST API answers with.

		A job's name says where it sits, and is read back into the tree: ``Docs / Sphinx / HTML`` nests below a
		:class:`Workflow` per prefix, and ``Unit Tests (ubuntu-26.04, 3.14)`` becomes a :class:`MatrixJob` below a
		:class:`Matrix` named ``Unit Tests``.

		:param run:          The workflow run, as returned by ``GET /repos/{owner}/{repo}/actions/runs/{run_id}``.
		:param jobs:         Optional, the run's jobs, as listed by ``GET .../actions/runs/{run_id}/jobs``.
		:param parent:       Optional, reference to the group of the commit's runs. Default: ``None``.
		:returns:            The workflow run, with its workflows, matrices, jobs and steps attached.
		:raises TypeError:   If parameter 'run' is not of type :class:`dict`.
		:raises TypeError:   If an element of parameter 'jobs' is not of type :class:`dict`.
		:raises GitHubError: If field ``name`` is missing.
		:raises GitHubError: If a field holds a value GitHub doesn't document.
		"""
		if not isinstance(run, dict):
			ex = TypeError("Parameter 'run' is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(run)}'.")
			raise ex

		if (name := run.get("name", None)) is None:
			raise GitHubError("Field 'run.name' is missing.")

		identifier =   run.get("id", None)
		status =       Status.Parse(run.get("status", None))
		conclusion =   Conclusion.Parse(run.get("conclusion", None))
		createdAt =    _parseISO8601Timestamp(run.get("created_at", None), "run.created_at")
		startedAt =    _parseISO8601Timestamp(run.get("run_started_at", None), "run.run_started_at")
		completedAt =  _parseISO8601Timestamp(run.get("updated_at", None), "run.updated_at") \
		               if status is Status.Completed else None
		url =          _parseURL(run.get("html_url", None), "run.html_url")
		workflowID =   run.get("workflow_id", None)
		path =         run.get("path", None)
		runNumber =    run.get("run_number", None)
		runAttempt =   run.get("run_attempt", None)
		event =        Event.Parse(run.get("event", None))
		gitReference = run.get("head_branch", None)
		sha =          run.get("head_sha", None)

		pipeline = cls(
			name, identifier, status, conclusion, createdAt, startedAt, completedAt, url, workflowID, path, runNumber,
			runAttempt, event, gitReference, sha, parent=parent
		)

		if jobs is None:
			return pipeline

		for position, job in enumerate(jobs):
			if not isinstance(job, dict):
				ex = TypeError(f"Job {position} is not of type 'dict'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(job)}'.")
				raise ex

			path = f"jobs[{position}]"
			if (fullName := job.get("name", None)) is None:
				raise GitHubError(f"Field '{path}.name' is missing.")

			*callers, leaf = fullName.split(" / ")

			group: Workflow = pipeline
			for caller in callers:
				if (calledWorkflow := group._workflows.get(caller, None)) is None:
					calledWorkflow = Workflow(caller, parent=group)

				group = calledWorkflow

			jobName, dimensionValues = _splitMatrixJobName(leaf)
			if dimensionValues is None:
				Job.FromJSON(job, path, parent=group)
			else:
				if (matrix := group._matrices.get(jobName, None)) is None:
					matrix = Matrix(jobName, parent=group)
					group._matrices[jobName] = matrix

				MatrixJob.FromJSON(job, path, jobName, dimensionValues, parent=matrix)

		return pipeline


@export
class Matrix(JobGroup):
	"""
	A matrix, grouping the job instances it produced.

	GitHub doesn't report a matrix as an element of its own - it appends the dimension values to the names of the jobs
	it produced, as ``Unit Tests (ubuntu-26.04, 3.14)``. :meth:`Pipeline.FromJSON` reads those back into this level, so
	the tree shows the jobs of one matrix together, and the matrix' times span all of them.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Workflow  #: A matrix is contained in a workflow.

	@readonly
	def Instances(self) -> list[MatrixJob]:
		"""
		Read-only property to access the job instances this matrix produced (:attr:`_jobs`).

		:returns: The instances, in the order GitHub reported them.
		"""
		return self._jobs


@export
class Job(Base, QualifiedNameMixin):
	"""A job of a workflow run, which ran on a runner and contains steps."""

	_PARENT_TYPE: ClassVar[Nullable[type]] = JobGroup  #: A job is contained in a job group.

	_id:              Nullable[int]    #: GitHub's identifier of the job.
	_labels:          list[str]        #: Labels the job requested its runner by, i.e. its ``runs-on``.
	_runnerName:      Nullable[str]    #: Name of the runner the job ran on.
	_runnerGroupName: Nullable[str]    #: Name of the runner group the runner belongs to.
	_steps:           list[Step]       #: Steps of the job.

	def __init__(
		self,
		name:            str,
		identifier:      Nullable[int]           = None,
		status:          Nullable[Status]        = None,
		conclusion:      Nullable[Conclusion]    = None,
		createdAt:       Nullable[datetime]      = None,
		startedAt:       Nullable[datetime]      = None,
		completedAt:     Nullable[datetime]      = None,
		url:             Nullable[URL]           = None,
		labels:          Nullable[Iterable[str]] = None,
		runnerName:      Nullable[str]           = None,
		runnerGroupName: Nullable[str]           = None,
		steps:           Nullable[Iterable[Step]] = None,
		*,
		parent:          Nullable[Base] = None
	) -> None:
		"""
		Initializes a job of a workflow run.

		:param name:            Name of the job, without the calling workflows' prefixes.
		:param identifier:      Optional, GitHub's identifier of the job. Default: ``None``.
		:param status:          Optional, state the job is in. Default: ``None``.
		:param conclusion:      Optional, how the job ended. Default: ``None``.
		:param createdAt:       Optional, time the job was created, i.e. queued for a runner. Default: ``None``.
		:param startedAt:       Optional, time the job started running on a runner. Default: ``None``.
		:param completedAt:     Optional, time the job completed. Default: ``None``.
		:param url:             Optional, URL of the job on github.com. Default: ``None``.
		:param labels:          Optional, labels the job requested its runner by. Default: ``None``.
		:param runnerName:      Optional, name of the runner the job ran on. Default: ``None``.
		:param runnerGroupName: Optional, name of the runner group the runner belongs to. Default: ``None``.
		:param steps:           Optional, the job's steps, which are attached to it. Default: ``None``.
		:param parent:          Optional, reference to the group containing the job. Default: ``None``.
		:raises TypeError:      If parameter 'identifier' is not of type :class:`int`.
		:raises TypeError:      If an element of parameter 'steps' is not of type :class:`Step`.
		:raises TypeError:      If an element of parameter 'labels' is not of type :class:`str`.
		:raises TypeError:      If parameter 'runnerName' is not of type :class:`str`.
		:raises TypeError:      If parameter 'runnerGroupName' is not of type :class:`str`.
		"""
		if identifier is not None and not isinstance(identifier, int):
			ex = TypeError("Parameter 'identifier' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex

		for parameterName, value in (("runnerName", runnerName), ("runnerGroupName", runnerGroupName)):
			if value is not None and not isinstance(value, str):
				ex = TypeError(f"Parameter '{parameterName}' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

		super().__init__(name, status, conclusion, createdAt, startedAt, completedAt, url, parent=parent)

		self._id =     identifier
		self._labels = []
		if labels is not None:
			for label in labels:
				if not isinstance(label, str):
					ex = TypeError("An element of parameter 'labels' is not of type 'str'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(label)}'.")
					raise ex

				self._labels.append(label)

		self._runnerName =      runnerName
		self._runnerGroupName = runnerGroupName
		self._steps =           []
		if steps is not None:
			for step in steps:
				if not isinstance(step, Step):
					ex = TypeError("An element of parameter 'steps' is not of type 'Step'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(step)}'.")
					raise ex

				step._parent =   self
				step._pipeline = self._pipeline
				self._steps.append(step)

		if parent is not None:
			parent._jobs.append(self)

	@readonly
	def ID(self) -> Nullable[int]:
		"""
		Read-only property to access GitHub's identifier of the job (:attr:`_id`).

		:returns: The identifier, or ``None`` if GitHub reported none.
		"""
		return self._id

	@readonly
	def Labels(self) -> list[str]:
		"""
		Read-only property to access the labels the job requested its runner by (:attr:`_labels`).

		These are the values of the workflow's ``runs-on``. For a hosted runner a label doubles as the image's name
		(``ubuntu-26.04``); for a self-hosted runner they are the tags the runner was registered with.

		:returns: The labels, empty if GitHub reported none.
		"""
		return self._labels

	@readonly
	def RunnerName(self) -> Nullable[str]:
		"""
		Read-only property to access the name of the runner the job ran on (:attr:`_runnerName`).

		:returns: The runner's name, or ``None`` while the job hasn't started.
		"""
		return self._runnerName

	@readonly
	def RunnerGroupName(self) -> Nullable[str]:
		"""
		Read-only property to access the name of the runner group the runner belongs to (:attr:`_runnerGroupName`).

		:returns: The group's name, or ``None`` if GitHub reported none.
		"""
		return self._runnerGroupName

	@readonly
	def Steps(self) -> list[Step]:
		"""
		Read-only property to access the job's steps (:attr:`_steps`).

		:returns: The steps, in the order GitHub reported them.
		"""
		return self._steps

	@readonly
	def QueuedDuration(self) -> Nullable[float]:
		"""
		Read-only property to return how long the job waited for a runner.

		:returns: Seconds from being created to starting, or ``None`` while either time is unknown.
		"""
		if self._createdAt is None or self._startedAt is None:
			return None

		return (self._startedAt - self._createdAt).total_seconds()

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

	@classmethod
	def FromJSON(cls, json: JSONObject, path: str = "job", *, parent: Nullable[Base] = None) -> Self:
		"""
		Build a job and its steps from the JSON object the GitHub REST API answers with.

		The job's name is taken without the calling workflows' prefixes: a job reported as ``Caller / Build`` is named
		``Build``, because the prefix describes where it sits, which the tree already says.

		:param json:         The job, as listed by ``GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs``.
		:param path:         Optional, position of the job, for an exception's message. Default: ``'job'``.
		:param parent:       Optional, reference to the group containing the job. Default: ``None``.
		:returns:            The job, with its steps attached.
		:raises TypeError:   If parameter 'json' is not of type :class:`dict`.
		:raises GitHubError: If field ``name`` is missing.
		:raises GitHubError: If a field holds a value GitHub doesn't document.
		"""
		if not isinstance(json, dict):
			ex = TypeError("Parameter 'json' is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(json)}'.")
			raise ex

		if (fullName := json.get("name", None)) is None:
			raise GitHubError(f"Field '{path}.name' is missing.")

		name =            fullName.rsplit(" / ", 1)[-1]
		identifier =      json.get("id", None)
		status =          Status.Parse(json.get("status", None))
		conclusion =      Conclusion.Parse(json.get("conclusion", None))
		createdAt =       _parseISO8601Timestamp(json.get("created_at", None), f"{path}.created_at")
		startedAt =       _parseISO8601Timestamp(json.get("started_at", None), f"{path}.started_at")
		completedAt =     _parseISO8601Timestamp(json.get("completed_at", None), f"{path}.completed_at")
		url =             _parseURL(json.get("html_url", None), f"{path}.html_url")
		labels =          json.get("labels", None)
		runnerName =      json.get("runner_name", None)
		runnerGroupName = json.get("runner_group_name", None)

		if (jsonSteps := json.get("steps", None)) is None:
			steps = None
		else:
			steps = [Step.FromJSON(step, f"{path}.steps[{pos}]") for pos, step in enumerate(jsonSteps)]

		return cls(
			name, identifier, status, conclusion, createdAt, startedAt, completedAt, url, labels, runnerName,
			runnerGroupName, steps, parent=parent
		)


@export
class MatrixJob(Job):
	"""
	One instance of a job produced by a matrix.

	GitHub reports a matrix instance as an ordinary job whose name carries the dimension values in brackets, e.g.
	``Unit Tests (ubuntu-26.04, 3.14)``. :meth:`Pipeline.FromJSON` reads those back into :attr:`DimensionValues` and
	groups the instances below a :class:`Matrix`.
	"""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Matrix  #: A matrix instance is contained in a matrix.

	_dimensionValues: list[str]  #: Values of the matrix' dimensions this instance ran with.

	def __init__(
		self,
		name:            str,
		dimensionValues: Nullable[Iterable[str]] = None,
		identifier:      Nullable[int]           = None,
		status:          Nullable[Status]        = None,
		conclusion:      Nullable[Conclusion]    = None,
		createdAt:       Nullable[datetime]      = None,
		startedAt:       Nullable[datetime]      = None,
		completedAt:     Nullable[datetime]      = None,
		url:             Nullable[URL]           = None,
		labels:          Nullable[Iterable[str]] = None,
		runnerName:      Nullable[str]           = None,
		runnerGroupName: Nullable[str]           = None,
		steps:           Nullable[Iterable[Step]] = None,
		*,
		parent:          Nullable[Matrix] = None
	) -> None:
		"""
		Initializes one instance of a job produced by a matrix.

		:param name:            Name of the job, without the dimension values.
		:param dimensionValues: Optional, values of the matrix' dimensions this instance ran with. Default: ``None``.
		:param identifier:      Optional, GitHub's identifier of the job. Default: ``None``.
		:param status:          Optional, state the job is in. Default: ``None``.
		:param conclusion:      Optional, how the job ended. Default: ``None``.
		:param createdAt:       Optional, time the job was created, i.e. queued for a runner. Default: ``None``.
		:param startedAt:       Optional, time the job started running on a runner. Default: ``None``.
		:param completedAt:     Optional, time the job completed. Default: ``None``.
		:param url:             Optional, URL of the job on github.com. Default: ``None``.
		:param labels:          Optional, labels the job requested its runner by. Default: ``None``.
		:param runnerName:      Optional, name of the runner the job ran on. Default: ``None``.
		:param runnerGroupName: Optional, name of the runner group the runner belongs to. Default: ``None``.
		:param steps:           Optional, the job's steps, which are attached to it. Default: ``None``.
		:param parent:          Optional, reference to the matrix containing the instance. Default: ``None``.
		:raises TypeError:      If an element of parameter 'dimensionValues' is not of type :class:`str`.
		"""
		super().__init__(
			name, identifier, status, conclusion, createdAt, startedAt, completedAt, url, labels, runnerName,
			runnerGroupName, steps, parent=parent
		)

		self._dimensionValues = []
		if dimensionValues is not None:
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

		The values are in the order GitHub prints them and carry no dimension names: ``['ubuntu-26.04', '3.14']`` says
		nothing about which is the operating system and which the Python version, because the job's payload doesn't
		either - only the workflow file names the dimensions.

		:returns: The dimension values.
		"""
		return self._dimensionValues

	def __str__(self) -> str:
		"""
		Return a string representation of the matrix instance.

		:returns: The job's name with its dimension values, as GitHub prints it.
		"""
		if len(self._dimensionValues) == 0:
			return self._name

		return f"{self._name} ({', '.join(self._dimensionValues)})"

	@classmethod
	def FromJSON(
		cls,
		json:            JSONObject,
		path:            str                     = "job",
		name:            Nullable[str]           = None,
		dimensionValues: Nullable[Iterable[str]] = None,
		*,
		parent:          Nullable[Matrix] = None
	) -> Self:
		"""
		Build a matrix instance and its steps from the JSON object the GitHub REST API answers with.

		:param json:            The job, as listed by ``GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs``.
		:param path:            Optional, position of the job, for an exception's message. Default: ``'job'``.
		:param name:            Optional, the job's name without the dimension values. Default: read from the payload.
		:param dimensionValues: Optional, the dimension values. Default: read from the payload.
		:param parent:          Optional, reference to the matrix containing the instance. Default: ``None``.
		:returns:               The matrix instance, with its steps attached.
		:raises TypeError:      If parameter 'json' is not of type :class:`dict`.
		:raises GitHubError:    If field ``name`` is missing.
		:raises GitHubError:    If a field holds a value GitHub doesn't document.
		"""
		if not isinstance(json, dict):
			ex = TypeError("Parameter 'json' is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(json)}'.")
			raise ex

		if (fullName := json.get("name", None)) is None:
			raise GitHubError(f"Field '{path}.name' is missing.")

		if name is None:
			name, dimensionValues = _splitMatrixJobName(fullName.rsplit(" / ", 1)[-1])

		identifier =      json.get("id", None)
		status =          Status.Parse(json.get("status", None))
		conclusion =      Conclusion.Parse(json.get("conclusion", None))
		createdAt =       _parseISO8601Timestamp(json.get("created_at", None), f"{path}.created_at")
		startedAt =       _parseISO8601Timestamp(json.get("started_at", None), f"{path}.started_at")
		completedAt =     _parseISO8601Timestamp(json.get("completed_at", None), f"{path}.completed_at")
		url =             _parseURL(json.get("html_url", None), f"{path}.html_url")
		labels =          json.get("labels", None)
		runnerName =      json.get("runner_name", None)
		runnerGroupName = json.get("runner_group_name", None)

		if (jsonSteps := json.get("steps", None)) is None:
			steps = None
		else:
			steps = [Step.FromJSON(step, f"{path}.steps[{pos}]") for pos, step in enumerate(jsonSteps)]

		return cls(
			name, dimensionValues, identifier, status, conclusion, createdAt, startedAt, completedAt, url, labels,
			runnerName, runnerGroupName, steps, parent=parent
		)


@export
class Step(Base):
	"""A step within a job."""

	_PARENT_TYPE: ClassVar[Nullable[type]] = Job  #: A step is contained in a job.

	_number: Nullable[int]  #: Position of the step within its job, starting at 1.

	def __init__(
		self,
		name:        str,
		number:      Nullable[int]        = None,
		status:      Nullable[Status]     = None,
		conclusion:  Nullable[Conclusion] = None,
		startedAt:   Nullable[datetime]   = None,
		completedAt: Nullable[datetime]   = None,
		*,
		parent:      Nullable[Job] = None
	) -> None:
		"""
		Initializes a step within a job.

		:param name:        Name of the step.
		:param number:      Optional, position of the step within its job, starting at 1. Default: ``None``.
		:param status:      Optional, state the step is in. Default: ``None``.
		:param conclusion:  Optional, how the step ended. Default: ``None``.
		:param startedAt:   Optional, time the step started running. Default: ``None``.
		:param completedAt: Optional, time the step completed. Default: ``None``.
		:param parent:      Optional, reference to the job containing the step. Default: ``None``.
		:raises TypeError:  If parameter 'number' is not of type :class:`int`.
		:raises ValueError: If parameter 'number' is not positive.
		"""
		super().__init__(name, status, conclusion, None, startedAt, completedAt, parent=parent)

		if number is not None and not isinstance(number, int):
			ex = TypeError("Parameter 'number' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(number)}'.")
			raise ex
		elif number is not None and number < 1:
			ex = ValueError("Parameter 'number' is not positive.")
			ex.add_note(f"Got value '{number}'.")
			raise ex

		self._number = number

		if parent is not None:
			parent._steps.append(self)

	@readonly
	def Number(self) -> Nullable[int]:
		"""
		Read-only property to access the step's position within its job (:attr:`_number`).

		:returns: The position, starting at 1, or ``None`` if GitHub reported none.
		"""
		return self._number

	@classmethod
	def FromJSON(cls, json: JSONObject, path: str = "step", *, parent: Nullable[Job] = None) -> Self:
		"""
		Build a step from the JSON object the GitHub REST API answers with.

		:param json:         The step, as it appears in a job's ``steps`` array.
		:param path:         Optional, position of the step, for an exception's message. Default: ``'step'``.
		:param parent:       Optional, reference to the job containing the step. Default: ``None``.
		:returns:            The step.
		:raises TypeError:   If parameter 'json' is not of type :class:`dict`.
		:raises GitHubError: If field ``name`` is missing.
		:raises GitHubError: If a field holds a value GitHub doesn't document.
		"""
		if not isinstance(json, dict):
			ex = TypeError("Parameter 'json' is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(json)}'.")
			raise ex

		if (name := json.get("name", None)) is None:
			raise GitHubError(f"Field '{path}.name' is missing.")

		number =      json.get("number", None)
		status =      Status.Parse(json.get("status", None))
		conclusion =  Conclusion.Parse(json.get("conclusion", None))
		startedAt =   _parseISO8601Timestamp(json.get("started_at", None), f"{path}.started_at")
		completedAt = _parseISO8601Timestamp(json.get("completed_at", None), f"{path}.completed_at")

		return cls(name, number, status, conclusion, startedAt, completedAt, parent=parent)

