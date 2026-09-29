# ==================================================================================================================== #
#             _____           _ _               ____                                        _        _   _             #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  ___   ___ _   _ _ __ ___   ___ _ __ | |_ __ _| |_(_) ___  _ __  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _ \ / __| | | | '_ ` _ \ / _ \ '_ \| __/ _` | __| |/ _ \| '_ \ #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| | (_) | (__| |_| | | | | | |  __/ | | | || (_| | |_| | (_) | | | |#
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \___/ \___|\__,_|_| |_| |_|\___|_| |_|\__\__,_|\__|_|\___/|_| |_|#
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
A Sphinx domain ``gha`` documenting GitHub Actions workflows from their YAML files.

The facts of a reusable workflow - an input's type, whether it is required, its default - are read from the workflow
file by :mod:`pyTooling.CI.GitHub.Workflow`, so a page states them without copying them. What the file can't say stays
hand-written, as the content of a directive:

.. code-block:: rst

   .. gha:workflow:: Parameters

   Parameters
   ##########

   .. gha:input:: package_name

      :Possible Values: Any valid Python package name.
      :Example:         ``myPackage``

.. rubric:: What it registers

* the directives ``gha:workflow``, ``gha:input``, ``gha:output`` and ``gha:secret``;
* the roles ``:gha:workflow:``, ``:gha:input:``, ``:gha:output:`` and ``:gha:secret:``;
* the configuration values in :data:`CONFIG_VALUES`.

The workflow files are read with ``ruamel.yaml`` when a directive runs, not when this module is imported.

.. seealso::

   :mod:`pyTooling.CI.GitHub.Workflow`
      |rarr| The model of a workflow file the domain reads.
"""
from __future__                                import annotations

from pathlib                                   import Path
from typing                                    import TYPE_CHECKING, Any, ClassVar, Iterable, Optional as Nullable

from docutils                                  import nodes
from docutils.nodes                            import Element, Node, fully_normalize_name
from docutils.parsers.rst                      import directives
from sphinx                                    import addnodes
from sphinx.builders                           import Builder
from sphinx.domains                            import Domain, ObjType
from sphinx.environment                        import BuildEnvironment
from sphinx.roles                              import XRefRole
from sphinx.util.docutils                      import SphinxDirective
from sphinx.util.logging                       import getLogger
from sphinx.util.nodes                         import make_id, make_refnode

from pyTooling.Common                          import getFullyQualifiedName
from pyTooling.Decorators                      import export, readonly

if TYPE_CHECKING:  # pragma: no cover
	from pyTooling.CI.GitHub.Workflow            import Input, Output, Parameter, Secret, ValueT, Workflow
	from pyTooling.CI.GitHub.Workflow            import WorkflowResolver


__all__ = ["CONFIG_VALUES", "NO_DEFAULT", "WARNING_TYPE", "LEADING_FIELDS"]

#: The configuration values this domain adds to :file:`conf.py`, as ``name: (default, rebuild, types)``.
#:
#: ``gha_repository``
#:    The documented repository, as ``owner/repo``. A ``uses`` naming it is read from ``gha_workflow_directory``,
#:    whatever its ref.
#: ``gha_workflow_directory``
#:    The directory holding the workflow files, relative to the Sphinx source directory, as
#:    ``../.github/workflows``. A ``gha:workflow`` without ``:file:`` reads ``<name>.yml`` from it.
#: ``gha_ref``
#:    The ref - a branch or tag - of the documented repository the documentation describes, as ``r8``, or ``None``.
#:    A directive may warn about a ``uses`` of the documented repository at another ref.
#: ``gha_label_prefix``
#:    The root of the ``:ref:`` labels the directives register besides their domain targets, as
#:    ``JOBTMPL/Parameters/Input/package_name``, or ``None`` for none.
CONFIG_VALUES = {
	"gha_repository":         (None,      "env", (str, type(None))),
	"gha_workflow_directory": (None,      "env", (str, type(None))),
	"gha_ref":                (None,      "env", (str, type(None))),
	"gha_label_prefix":       ("JOBTMPL", "env", (str, type(None))),
}

#: The text of the field *Default Value* when an input has no default.
NO_DEFAULT = "— — — —"

#: The type of the warnings this domain emits; the drift warnings have the subtype ``drift``, so
#: ``suppress_warnings = ["gha.drift"]`` silences them.
WARNING_TYPE = "gha"

#: The fields a *Description* taken from the workflow file follows.
LEADING_FIELDS = ("Type", "Required", "Default Value", "Possible Values")

_logger = getLogger(__name__)


@export
def formatValue(value: ValueT) -> str:
	"""
	Format a value read from a workflow file the way the file writes it.

	A string is quoted as YAML quotes it - ``'3.14'`` -, a boolean is ``true`` or ``false``, and a number is written as
	it is.

	:param value: The value, as :attr:`Input.Default <pyTooling.CI.GitHub.Workflow.Input.Default>`.
	:returns:     The value as text, or :data:`NO_DEFAULT` for ``None``.
	"""
	if value is None:
		return NO_DEFAULT
	elif isinstance(value, bool):
		return "true" if value else "false"
	elif isinstance(value, str):
		escaped = value.replace("'", "''")
		return f"'{escaped}'"

	return str(value)


@export
class WorkflowDirective(SphinxDirective):
	"""
	The directive ``gha:workflow``: a workflow's target, its index entry, and the current workflow of the document.

	.. code-block:: rst

	   .. gha:workflow:: Parameters
	      :file: ../../.github/workflows/Parameters.yml

	The argument is the workflow's name, its file's stem. Without ``:file:``, the file is ``<name>.yml`` in
	``gha_workflow_directory``. Every ``gha:input``, ``gha:output`` and ``gha:secret`` following it in the document
	belongs to this workflow.

	The directive writes no visible output. Placed above a page's title, its target is the title, as a label is.
	"""

	has_content =        False                                   #: The directive has no content.
	required_arguments = 1                                       #: The workflow's name.
	option_spec =        {"file": directives.unchanged_required}  #: Path to the workflow file, relative to the document.

	def run(self) -> list[Node]:
		"""
		Register the workflow, read its file, and make it the current workflow.

		:returns: An index node and the workflow's target.
		"""
		name = self.arguments[0].strip()
		domain: GitHubActionsDomain = self.env.get_domain("gha")

		if "file" in self.options:
			path = Path(self.env.relfn2path(self.options["file"], self.env.docname)[1])
		elif domain.WorkflowDirectory is not None:
			path = domain.WorkflowDirectory / f"{name}.yml"
			if not path.exists() and (alternative := path.with_suffix(".yaml")).exists():
				path = alternative
		else:
			path = None

		if path is None:
			_logger.warning(
				f"gha:workflow '{name}' has no file: give option ':file:' or set 'gha_workflow_directory'.",
				location=self.get_location(), type=WARNING_TYPE, subtype="workflow"
			)
		elif not path.exists():
			_logger.warning(
				f"gha:workflow '{name}': file '{path}' doesn't exist.",
				location=self.get_location(), type=WARNING_TYPE, subtype="workflow"
			)
		else:
			self.env.note_dependency(str(path))
			self._Load(domain, name, path)

		self.env.ref_context["gha:workflow"] = name

		nodeID = make_id(self.env, self.state.document, "gha-workflow", name)
		target = nodes.target("", "", ids=[nodeID])
		if (prefix := self.config.gha_label_prefix) is not None:
			label = f"{prefix}/{name}"
			target["ids"].append(nodes.make_id(label))
			target["names"].append(fully_normalize_name(label))

		self.set_source_info(target)
		self.state.document.note_explicit_target(target)
		domain.NoteObject("workflow", name, nodeID, target)

		return [addnodes.index(entries=[("single", f"GitHub Actions workflow; {name}", nodeID, "", None)]), target]

	def _Load(self, domain: GitHubActionsDomain, name: str, path: Path) -> None:
		"""
		Read the workflow file, make it the current one, and warn about inputs that are required and have a default.

		A file that isn't a well-formed workflow is reported as a warning at the place in the file, and the document
		has no current workflow model then.

		:param domain: The domain.
		:param name:   The workflow's name, as given as argument.
		:param path:   Path to the workflow file.
		"""
		from pyTooling.CI.GitHub.Workflow import WorkflowError

		try:
			workflow = domain.Resolver.Load(path)
		except WorkflowError as ex:
			if ex.Path is None:
				location = self.get_location()
			elif ex.Line is None:
				location = str(ex.Path)
			else:
				location = f"{ex.Path}:{ex.Line}"

			_logger.warning(f"gha:workflow '{name}': {ex}", location=location, type=WARNING_TYPE, subtype="workflow")
			return

		if workflow.Name != name:
			_logger.warning(
				f"gha:workflow '{name}' reads file '{path.name}', which names workflow '{workflow.Name}'.",
				location=self.get_location(), type=WARNING_TYPE, subtype="workflow"
			)

		self.env.current_document["gha:workflow-file"] = path

		for parameter in workflow.Inputs.values():
			if parameter.Required and parameter.Default is not None:
				_logger.warning(
					f"Input '{parameter.Name}' of workflow '{workflow.Name}' is required and has a default, which is never used.",
					location=f"{workflow.Path}:{parameter.Line}", type=WARNING_TYPE, subtype="drift"
				)


@export
class ParameterDirective(SphinxDirective):
	"""
	Base-class of the directives documenting one parameter of the current workflow.

	The entry is a section titled by the parameter's name, holding a field list: first the fields read from the
	workflow file (:attr:`FACT_FIELDS`), then the fields of the directive's content, in the order written. Without a
	hand-written *Description*, the workflow file's ``description`` is used, placed behind the :data:`LEADING_FIELDS`.
	Content after the field list follows it.

	A hand-written field repeating a fact of the file is a warning, and the file's value is shown.

	Besides its anchor ``gha-<type>-<Workflow>.<name>``, the section carries the anchor of its label and - unless the
	document uses it already - the anchor docutils derives from a title, as a hand-written section has.
	"""

	OBJECT_TYPE: ClassVar[str]              #: The domain's object type, as ``input``.
	LABEL_KIND:  ClassVar[str]              #: The kind in a label, as ``Input`` in ``JOBTMPL/Parameters/Input/name``.
	COLLECTION:  ClassVar[str]              #: The workflow's property holding the parameters, as ``Inputs``.
	FACT_FIELDS: ClassVar[tuple[str, ...]]  #: The fields taken from the workflow file.

	has_content =        True  #: The hand-written fields and text.
	required_arguments = 1     #: The parameter's name.

	def run(self) -> list[Node]:
		"""
		Create the parameter's entry and register it.

		:returns: An index node and the entry's section, or nothing outside a ``gha:workflow``.
		"""
		name = self.arguments[0].strip()
		if (workflowName := self.env.ref_context.get("gha:workflow", None)) is None:
			_logger.warning(
				f"gha:{self.OBJECT_TYPE} '{name}' is not preceded by a gha:workflow.",
				location=self.get_location(), type=WARNING_TYPE, subtype="workflow"
			)
			return []

		domain: GitHubActionsDomain = self.env.get_domain("gha")
		parameter = None
		if (workflow := domain.GetCurrentWorkflow()) is not None:
			if (parameter := getattr(workflow, self.COLLECTION).get(name, None)) is None:
				_logger.warning(
					f"Workflow '{workflowName}' has no {self.OBJECT_TYPE} '{name}' ({workflow.Path.name}).",
					location=self.get_location(), type=WARNING_TYPE, subtype="drift"
				)

		fullName = f"{workflowName}.{name}"
		nodeID = make_id(self.env, self.state.document, f"gha-{self.OBJECT_TYPE}", fullName)
		section = nodes.section("", nodes.title(name, name), ids=[nodeID])
		if (titleID := nodes.make_id(name)) not in self.state.document.ids:
			section["ids"].append(titleID)

		# The label's anchor comes last: docutils links a name to a node's last anchor, so a link keeps its target.
		if (prefix := self.config.gha_label_prefix) is not None:
			label = f"{prefix}/{workflowName}/{self.LABEL_KIND}/{name}"
			section["ids"].append(nodes.make_id(label))
			section["names"].append(fully_normalize_name(label))

		self.set_source_info(section)
		self.state.document.note_explicit_target(section)

		content = self.parse_content_to_nodes()
		handwritten = []
		if len(content) > 0 and isinstance(content[0], nodes.field_list):
			handwritten = list(content[0].children)
			content = content[1:]

		fields = [] if parameter is None else self._FactFields(parameter)
		for field in handwritten:
			fieldName = field[0].astext().strip()
			if fieldName in self.FACT_FIELDS:
				_logger.warning(
					f"gha:{self.OBJECT_TYPE} '{fullName}': field '{fieldName}' is taken from the workflow file; remove it.",
					location=field, type=WARNING_TYPE, subtype="drift"
				)
				if parameter is not None:
					continue

			fields.append(field)

		fieldNames = [field[0].astext().strip() for field in fields]
		if "Description" not in fieldNames and parameter is not None and parameter.Description:
			leading = [index + 1 for index, fieldName in enumerate(fieldNames) if fieldName in LEADING_FIELDS]
			position = max(leading, default=0)
			fields.insert(position, self._TextField("Description", parameter.Description.strip()))

		if len(fields) > 0:
			section += nodes.field_list("", *fields)
		section.extend(content)

		domain.NoteObject(self.OBJECT_TYPE, fullName, nodeID, section)
		index = addnodes.index(
			entries=[("single", f"{name} ({self.OBJECT_TYPE} of {workflowName})", nodeID, "", None)]
		)

		return [index, section]

	@staticmethod
	def _Field(name: str, *body: Node) -> nodes.field:
		"""
		Create a field of a field list.

		:param name: Name of the field, as ``Type``.
		:param body: The nodes of the field's body.
		:returns:    The field.
		"""
		return nodes.field("", nodes.field_name(name, name), nodes.field_body("", *body))

	@classmethod
	def _TextField(cls, name: str, text: str) -> nodes.field:
		"""
		Create a field of a field list, whose body is a line of text.

		:param name: Name of the field, as ``Required``.
		:param text: Text of the field's body.
		:returns:    The field.
		"""
		return cls._Field(name, nodes.paragraph(text, text))

	@classmethod
	def _DefaultField(cls, value: ValueT) -> nodes.field:
		"""
		Create the field *Default Value*.

		A multi-line string becomes a literal block, keeping its line breaks; no default becomes :data:`NO_DEFAULT`.

		:param value: The default value.
		:returns:     The field.
		"""
		if value is None:
			return cls._TextField("Default Value", NO_DEFAULT)
		elif isinstance(value, str) and "\n" in value:
			return cls._Field("Default Value", nodes.literal_block(value, value, language="text"))

		text = formatValue(value)
		return cls._Field("Default Value", nodes.paragraph("", "", nodes.literal(text, text)))

	def _FactFields(self, parameter: Parameter) -> list[nodes.field]:
		"""
		Create the fields taken from the workflow file.

		:param parameter: The parameter, as read from the workflow file.
		:returns:         The fields named in :attr:`FACT_FIELDS`, in that order.
		"""
		return []


@export
class InputDirective(ParameterDirective):
	"""
	The directive ``gha:input``: an input of the current workflow.

	The fields *Type*, *Required* and *Default Value* are taken from the workflow file.
	"""

	OBJECT_TYPE = "input"                                #: The domain's object type.
	LABEL_KIND =  "Input"                                #: The kind in a label.
	COLLECTION =  "Inputs"                               #: The workflow's property holding the parameters.
	FACT_FIELDS = ("Type", "Required", "Default Value")  #: The fields taken from the workflow file.

	def _FactFields(self, parameter: Input) -> list[nodes.field]:
		"""
		Create the fields *Type*, *Required* and *Default Value*.

		:param parameter: The input, as read from the workflow file.
		:returns:         The fields.
		"""
		return [
			self._TextField("Type", parameter.Type.value),
			self._TextField("Required", "yes" if parameter.Required else "no"),
			self._DefaultField(parameter.Default)
		]


@export
class SecretDirective(ParameterDirective):
	"""
	The directive ``gha:secret``: a secret of the current workflow.

	The fields *Type* - a secret is a string -, *Required* and *Default Value* - a secret has none - are taken from the
	workflow file.
	"""

	OBJECT_TYPE = "secret"                               #: The domain's object type.
	LABEL_KIND =  "Secret"                               #: The kind in a label.
	COLLECTION =  "Secrets"                              #: The workflow's property holding the parameters.
	FACT_FIELDS = ("Type", "Required", "Default Value")  #: The fields taken from the workflow file.

	def _FactFields(self, parameter: Secret) -> list[nodes.field]:
		"""
		Create the fields *Type*, *Required* and *Default Value*.

		:param parameter: The secret, as read from the workflow file.
		:returns:         The fields.
		"""
		return [
			self._TextField("Type", "string"),
			self._TextField("Required", "yes" if parameter.Required else "no"),
			self._DefaultField(None)
		]


@export
class OutputDirective(ParameterDirective):
	"""
	The directive ``gha:output``: an output of the current workflow.

	A workflow file states no type and no default for an output, so every field is hand-written; only the
	*Description* falls back to the file's ``description``.
	"""

	OBJECT_TYPE = "output"   #: The domain's object type.
	LABEL_KIND =  "Output"   #: The kind in a label.
	COLLECTION =  "Outputs"  #: The workflow's property holding the parameters.
	FACT_FIELDS = ()         #: The fields taken from the workflow file.


@export
class GitHubActionsXRefRole(XRefRole):
	"""
	The roles ``:gha:workflow:``, ``:gha:input:``, ``:gha:output:`` and ``:gha:secret:``.

	A parameter is named as ``<Workflow>.<name>``; inside a ``gha:workflow``, the name alone refers to the current
	workflow's parameter. A leading ``~`` shows only the part behind the last dot.
	"""

	def process_link(
		self,
		env:                BuildEnvironment,
		refnode:            Element,
		has_explicit_title: bool,
		title:              str,
		target:             str
	) -> tuple[str, str]:
		"""
		Remember the current workflow on the reference, and shorten the title for a leading ``~``.

		:param env:                The build environment.
		:param refnode:            The reference node.
		:param has_explicit_title: ``True``, if the role was written with a title, as ``text <target>``.
		:param title:              The title.
		:param target:             The target.
		:returns:                  The title and the target.
		"""
		refnode["gha:workflow"] = env.ref_context.get("gha:workflow", None)
		if not has_explicit_title and target.startswith("~"):
			target = target[1:]
			title = target.rpartition(".")[2]

		return title, target


@export
class GitHubActionsDomain(Domain):
	"""
	The Sphinx domain ``gha``, documenting GitHub Actions workflows.

	Its objects are keyed by type and name - ``("workflow", "Parameters")``, ``("input", "Parameters.package_name")``
	- and located by document and anchor. Directives of other modules reach the domain by
	``self.env.get_domain("gha")``, and use :meth:`GetCurrentWorkflow`, :attr:`Resolver` and :meth:`ResolveWorkflow`.
	"""

	name =         "gha"             #: Name of the domain, the prefix of its directives and roles.
	label =        "GitHub Actions"  #: Name of the domain, as displayed.
	data_version = 1                 #: Version of the data layout; a change discards pickled environments.

	object_types: ClassVar[dict[str, ObjType]] = {  # type: ignore[misc]
		"workflow": ObjType("workflow", "workflow"),
		"input":    ObjType("input",    "input"),
		"output":   ObjType("output",   "output"),
		"secret":   ObjType("secret",   "secret"),
	}  #: The object types, each referenced by the role of the same name.

	directives: ClassVar[dict[str, type]] = {  # type: ignore[misc]
		"workflow": WorkflowDirective,
		"input":    InputDirective,
		"output":   OutputDirective,
		"secret":   SecretDirective,
	}  #: The directives, by name.

	roles: ClassVar[dict[str, XRefRole]] = {  # type: ignore[misc]
		"workflow": GitHubActionsXRefRole(innernodeclass=nodes.literal, warn_dangling=True),
		"input":    GitHubActionsXRefRole(innernodeclass=nodes.literal, warn_dangling=True),
		"output":   GitHubActionsXRefRole(innernodeclass=nodes.literal, warn_dangling=True),
		"secret":   GitHubActionsXRefRole(innernodeclass=nodes.literal, warn_dangling=True),
	}  #: The roles, by name.

	initial_data: ClassVar[dict[str, Any]] = {  # type: ignore[misc]
		"objects": {},
	}  #: The domain's data: ``objects`` maps (type, name) to (document, anchor).

	_resolver: Nullable[WorkflowResolver]  #: Resolver reading the workflow files, created when first needed.

	def __init__(self, env: BuildEnvironment) -> None:
		"""
		Initializes the domain.

		:param env: The build environment.
		"""
		super().__init__(env)

		self._resolver = None

	@readonly
	def Objects(self) -> dict[tuple[str, str], tuple[str, str]]:
		"""
		Read-only property to return the documented objects.

		:returns: A mapping of (object type, name) to (document, anchor).
		"""
		return self.data["objects"]

	@readonly
	def WorkflowDirectory(self) -> Nullable[Path]:
		"""
		Read-only property to return the directory holding the workflow files.

		:returns: ``gha_workflow_directory`` resolved against the Sphinx source directory, or ``None`` if it isn't set.
		"""
		if (directory := self.env.config.gha_workflow_directory) is None:
			return None

		return (Path(self.env.srcdir) / directory).resolve()

	@readonly
	def Resolver(self) -> WorkflowResolver:
		"""
		Read-only property to access the resolver reading the workflow files (:attr:`_resolver`), created when first
		needed.

		It maps ``gha_repository`` to :attr:`WorkflowDirectory`, and reads every file once per build and process - a
		parallel build reads a file once in every process that needs it.

		:returns:                       The resolver.
		:raises MissingDependencyError: If the ``yaml`` extra isn't installed.
		"""
		if self._resolver is None:
			from pyTooling.CI.GitHub.Workflow import WorkflowResolver

			repositories = {}
			repository = self.env.config.gha_repository
			if repository is not None and (directory := self.WorkflowDirectory) is not None:
				repositories[repository] = directory

			self._resolver = WorkflowResolver(repositories)

		return self._resolver

	def GetCurrentWorkflow(self) -> Nullable[Workflow]:
		"""
		Return the model of the current document's workflow, as set by the last ``gha:workflow``.

		:returns: The workflow, or ``None`` if the document has no ``gha:workflow``, or its file couldn't be read -
		          which the ``gha:workflow`` directive reported already.
		"""
		if (path := self.env.current_document.get("gha:workflow-file", None)) is None:
			return None

		return self.Resolver.Load(path)

	def ResolveWorkflow(self, name: str) -> Nullable[tuple[str, str]]:
		"""
		Return where a workflow is documented.

		:param name:        The workflow's name, its file's stem.
		:returns:           The document and the anchor of its ``gha:workflow``, or ``None`` if it isn't documented.
		:raises ValueError: If parameter 'name' is ``None``.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		"""
		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		return self.data["objects"].get(("workflow", name), None)

	def NoteObject(self, objectType: str, name: str, nodeID: str, location: Nullable[Node] = None) -> None:
		"""
		Register a documented object.

		:param objectType:  The object type, as ``input``.
		:param name:        The object's name, as ``Parameters.package_name``.
		:param nodeID:      The anchor of the object's node.
		:param location:    Optional, the node a duplicate is reported at. Default: ``None``.
		:raises ValueError: If parameter 'objectType' is ``None``.
		:raises TypeError:  If parameter 'objectType' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is ``None``.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'nodeID' is ``None``.
		:raises TypeError:  If parameter 'nodeID' is not of type :class:`str`.
		:raises TypeError:  If parameter 'location' is not of type :class:`~docutils.nodes.Node`.
		"""
		for parameterName, value in (("objectType", objectType), ("name", name), ("nodeID", nodeID)):
			if value is None:
				raise ValueError(f"Parameter '{parameterName}' is None.")
			elif not isinstance(value, str):
				ex = TypeError(f"Parameter '{parameterName}' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

		if location is not None and not isinstance(location, Node):
			ex = TypeError("Parameter 'location' is not of type 'Node'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(location)}'.")
			raise ex

		objects = self.data["objects"]
		if (known := objects.get((objectType, name), None)) is not None:
			_logger.warning(
				f"Duplicate description of gha:{objectType} '{name}', other instance in '{known[0]}'.",
				location=location, type=WARNING_TYPE, subtype="duplicate"
			)

		objects[(objectType, name)] = (self.env.docname, nodeID)

	def clear_doc(self, docname: str) -> None:
		"""
		Remove the objects of a document, before it is read again.

		:param docname: The document.
		"""
		objects = self.data["objects"]
		for key in [key for key, (document, _) in objects.items() if document == docname]:
			del objects[key]

	def merge_domaindata(self, docnames: Iterable[str], otherdata: dict[str, Any]) -> None:
		"""
		Merge the objects a parallel reader collected for its documents.

		:param docnames:  The documents the other reader read.
		:param otherdata: The other reader's data.
		"""
		documents = set(docnames)
		objects = self.data["objects"]
		for key, (document, nodeID) in otherdata["objects"].items():
			if document in documents:
				objects[key] = (document, nodeID)

	def resolve_xref(
		self,
		env:         BuildEnvironment,
		fromdocname: str,
		builder:     Builder,
		typ:         str,
		target:      str,
		node:        addnodes.pending_xref,
		contnode:    Element
	) -> Nullable[nodes.reference]:
		"""
		Resolve a reference by one of the domain's roles.

		A parameter's name without a workflow is looked up in the workflow current where the role was written.

		:param env:         The build environment.
		:param fromdocname: The document containing the reference.
		:param builder:     The builder.
		:param typ:         The role's name, as ``input``.
		:param target:      The target, as ``Parameters.package_name`` or ``package_name``.
		:param node:        The pending reference.
		:param contnode:    The node rendering the reference's title.
		:returns:           The reference, or ``None`` if the target isn't documented.
		"""
		if typ != "workflow" and "." not in target and (workflowName := node.get("gha:workflow", None)) is not None:
			target = f"{workflowName}.{target}"

		if (location := self.data["objects"].get((typ, target), None)) is None:
			return None

		return make_refnode(builder, fromdocname, location[0], location[1], contnode, target)

	def resolve_any_xref(
		self,
		env:         BuildEnvironment,
		fromdocname: str,
		builder:     Builder,
		target:      str,
		node:        addnodes.pending_xref,
		contnode:    Element
	) -> list[tuple[str, nodes.reference]]:
		"""
		Resolve a reference by the ``:any:`` role, trying every object type.

		:param env:         The build environment.
		:param fromdocname: The document containing the reference.
		:param builder:     The builder.
		:param target:      The target.
		:param node:        The pending reference.
		:param contnode:    The node rendering the reference's title.
		:returns:           A pair of role and reference per object type the target resolves for.
		"""
		results = []
		for objectType in self.object_types:
			if (reference := self.resolve_xref(env, fromdocname, builder, objectType, target, node, contnode)) is not None:
				results.append((f"gha:{objectType}", reference))

		return results

	def get_objects(self) -> Iterable[tuple[str, str, str, str, str, int]]:
		"""
		Iterate the documented objects, for the search index and the inventory.

		:returns: An iterator of (name, display name, type, document, anchor, priority).
		"""
		for (objectType, name), (document, nodeID) in self.data["objects"].items():
			yield name, name, objectType, document, nodeID, 1
