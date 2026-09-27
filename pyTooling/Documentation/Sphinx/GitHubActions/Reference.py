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
Directives of the ``gha`` domain summarizing the current workflow: its parameters, its interface and its YAML.

Each of them reads the workflow of the preceding ``gha:workflow``:

.. code-block:: ReST

   .. gha:workflow:: Package

   .. gha:parameter-table::
      :kinds: inputs secrets

   .. gha:interface::

   .. gha:yaml::
      :job: Package

   .. gha:autoinputs::

* ``gha:parameter-table`` - the summary tables of the inputs, secrets and outputs;
* ``gha:interface`` - what a caller has to know: the required inputs, the secrets, the outputs, the permissions to
  grant, and the templates and actions used;
* ``gha:yaml`` - the workflow file or a part of it, as a code block linked to the file on GitHub;
* ``gha:autoinputs`` - an entry for every input the document has no ``gha:input`` for.

When a document was read, an input of its workflow without an entry is a ``gha.drift`` warning
(:func:`checkUndocumentedInputs`).

.. seealso::

   :mod:`pyTooling.Documentation.Sphinx.GitHubActions`
      |rarr| The domain ``gha``, its workflows and parameter entries.
"""
from __future__                                   import annotations

from typing                                       import TYPE_CHECKING, Any, Optional as Nullable

from docutils                                     import nodes
from docutils.parsers.rst                         import directives
from sphinx                                       import addnodes
from sphinx.application                           import Sphinx
from sphinx.config                                import Config
from sphinx.directives.code                       import container_wrapper
from sphinx.transforms                            import SphinxTransform
from sphinx.util.logging                          import getLogger

from pyTooling.Decorators                         import export
from pyTooling.Documentation.Sphinx.Directives    import BaseDirective, SphinxExtensionError, strip
from pyTooling.Documentation.Sphinx.GitHubActions import NO_DEFAULT, WARNING_TYPE, InputDirective, formatValue

if TYPE_CHECKING:  # pragma: no cover
	from pyTooling.CI.Workflow                      import UsesReference, ValueT, Workflow


__all__ = ["KINDS", "SECTIONS", "MAX_DEFAULT_LENGTH"]

#: The kinds of parameters ``gha:parameter-table`` summarizes, in the order it shows them by default: kind |rarr| the
#: columns.
KINDS = {
	"inputs":  ("Parameter Name", "Required", "Type", "Default"),
	"secrets": ("Token Name",     "Required", "Type", "Default"),
	"outputs": ("Result Name",    "Description"),
}

#: The parts of a workflow file ``gha:yaml`` shows by option ``:section:``.
SECTIONS = ("inputs", "outputs", "secrets", "jobs")

#: The length a default is shortened to in a summary table; a multi-line default is shortened to its first line.
MAX_DEFAULT_LENGTH = 120

_logger = getLogger(__name__)


def _indentation(line: str) -> int:
	"""
	Return the indentation of a line of a YAML file.

	:param line: The line.
	:returns:    The number of spaces the line starts with.
	"""
	return len(line) - len(line.lstrip(" "))


def _reference(objectType: str, target: str, text: str) -> addnodes.pending_xref:
	"""
	Create a reference to an object of the domain, shown as literal text if the object isn't documented.

	:param objectType: The object type, as ``input``.
	:param target:     The object's name, as ``Package.package_name``.
	:param text:       The text of the reference.
	:returns:          The pending reference.
	"""
	return addnodes.pending_xref(
		"", nodes.literal(text, text), refdomain="gha", reftype=objectType, reftarget=target, refexplicit=True,
		refwarn=False
	)


def _gitHubURL(config: Config, fileName: str, first: Nullable[int] = None, last: Nullable[int] = None) -> Nullable[str]:
	"""
	Return the URL of a workflow file of the documented repository on GitHub, at the documented ref.

	:param config:   The Sphinx configuration, with ``gha_repository`` and ``gha_ref``.
	:param fileName: The workflow file's name, as ``Package.yml``.
	:param first:    Optional, the first line to mark. Default: ``None``.
	:param last:     Optional, the last line to mark. Default: ``None``.
	:returns:        The URL, or ``None`` if ``gha_repository`` or ``gha_ref`` isn't configured.
	"""
	if config.gha_repository is None or config.gha_ref is None:
		return None

	url = f"https://github.com/{config.gha_repository}/blob/{config.gha_ref}/.github/workflows/{fileName}"
	if first is None:
		return url
	elif last is None or last == first:
		return f"{url}#L{first}"

	return f"{url}#L{first}-L{last}"


@export
class WorkflowReferenceDirective(BaseDirective):
	"""
	Base-class of the directives summarizing the current workflow, as set by the preceding ``gha:workflow``.
	"""

	def _CurrentWorkflow(self) -> Nullable[Workflow]:
		"""
		Return the model of the current workflow, and warn if there is no ``gha:workflow`` before the directive.

		:returns: The workflow, or ``None`` if there is no ``gha:workflow`` before the directive, or its file couldn't be
		          read - which the ``gha:workflow`` directive reported already.
		"""
		if self.env.ref_context.get("gha:workflow", None) is None:
			_logger.warning(
				f"{self.directiveName} is not preceded by a gha:workflow.",
				location=self.get_location(), type=WARNING_TYPE, subtype="workflow"
			)
			return None

		return self.env.get_domain("gha").GetCurrentWorkflow()


@export
class ParameterTable(WorkflowReferenceDirective):
	"""
	The directive ``gha:parameter-table``: summary tables of the current workflow's inputs, secrets and outputs.

	.. code-block:: ReST

	   .. gha:parameter-table::
	      :kinds: inputs secrets

	A table per kind, in the order written - by default the order of :data:`KINDS` -: the parameters in file order, each
	name linked to its entry. An
	input's or a secret's row states whether it is required, its type and its default - a long or multi-line default
	is shortened, the entry shows it in full. An output's row states its description from the workflow file.

	Without ``:kinds:``, a table is shown for every kind the workflow has parameters of. A kind named explicitly, of
	which the workflow has none, is a table with a single row saying so.
	"""

	directiveName: str = "gha:parameter-table"  #: Name the directive is invoked by.

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        0      #: Number of required directive arguments.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	option_spec: dict[str, Any] = {  # type: ignore[misc]
		"kinds": strip,
	}  #: Mapping of option names to validator functions.

	def run(self) -> list[nodes.Node]:
		"""
		Create the summary tables.

		:returns: A table per kind, an error node if option ``:kinds:`` names an unknown kind, or nothing without a
		          current workflow.
		"""
		try:
			kinds = self._ParseKinds()
		except SphinxExtensionError as ex:
			return [self.state.document.reporter.error(str(ex), line=self.lineno)]

		if (workflow := self._CurrentWorkflow()) is None:
			return []

		workflowName = self.env.ref_context["gha:workflow"]
		tables = []
		for kind in kinds:
			parameters = getattr(workflow, kind.capitalize())
			if len(parameters) == 0 and "kinds" not in self.options:
				continue

			columns = KINDS[kind]
			tableGroup = self._CreateSingleRowTableHeader(
				columns=[(title, None) for title in columns],
				identifier=f"{workflowName}-{kind}",
				classes=["gha-parameter-table", f"gha-{kind}"]
			)
			tableGroup += (tableBody := nodes.tbody())

			if len(parameters) == 0:
				entry = nodes.entry("", nodes.paragraph("", "", nodes.emphasis(text=f"No {kind}")), morecols=len(columns) - 1)
				tableBody += nodes.row("", entry)

			for name, parameter in parameters.items():
				row = nodes.row()
				row += nodes.entry("", nodes.paragraph("", "", _reference(kind[:-1], f"{workflowName}.{name}", name)))
				if kind == "outputs":
					description = "" if parameter.Description is None else parameter.Description.strip()
					row += nodes.entry("", nodes.paragraph(description, description))
				else:
					row += nodes.entry("", nodes.paragraph(text="yes" if parameter.Required else "no"))
					row += nodes.entry("", nodes.paragraph(text=parameter.Type.value if kind == "inputs" else "string"))
					row += nodes.entry("", self._DefaultParagraph(parameter.Default if kind == "inputs" else None))

				tableBody += row

			tables.append(tableGroup.parent)

		return tables

	def _ParseKinds(self) -> tuple[str, ...]:
		"""
		Read option ``:kinds:``, a list of kinds separated by spaces or commas.

		:returns:                     The kinds named, in the order written and each once, or every kind of :data:`KINDS`
		                              without the option.
		:raises SphinxExtensionError: If a kind is not one of :data:`KINDS`.
		"""
		if "kinds" not in self.options:
			return tuple(KINDS)

		kinds = tuple(dict.fromkeys(self.options["kinds"].replace(",", " ").split()))
		for kind in kinds:
			if kind not in KINDS:
				raise SphinxExtensionError(
					f"{self.directiveName}::kinds: '{kind}' is not one of {', '.join(KINDS)}."
				)

		return kinds

	@staticmethod
	def _DefaultParagraph(value: ValueT) -> nodes.paragraph:
		"""
		Create the paragraph of a table cell showing a default.

		A multi-line string is shortened to its first line, and a longer text to :data:`MAX_DEFAULT_LENGTH` characters,
		each followed by ``…``.

		:param value: The default, as :attr:`Input.Default <pyTooling.CI.Workflow.Input.Default>`.
		:returns:     The paragraph, holding :data:`~pyTooling.Documentation.Sphinx.GitHubActions.NO_DEFAULT` for
		              ``None``, or the default as literal text.
		"""
		if value is None:
			return nodes.paragraph(NO_DEFAULT, NO_DEFAULT)

		if isinstance(value, str):
			lines = value.splitlines()
			first = lines[0] if len(lines) > 0 else ""
			if len(lines) > 1 or len(first) > MAX_DEFAULT_LENGTH:
				value = f"{first[:MAX_DEFAULT_LENGTH]}…"

		text = formatValue(value)
		return nodes.paragraph("", "", nodes.literal(text, text))


@export
class Interface(WorkflowReferenceDirective):
	"""
	The directive ``gha:interface``: what a caller of the current workflow has to know, as a field list.

	.. code-block:: ReST

	   .. gha:interface::

	* *Required Inputs*, *Secrets* and *Outputs* - the parameters, each linked to its entry; a secret a caller has to
	  pass is marked *required*.
	* *Permissions* - the permissions a caller has to grant the ``GITHUB_TOKEN``: what the workflow's jobs and the
	  jobs of the workflows they call declare, the highest access per scope, each with the job and the place in the
	  workflow file asking for it.
	* *Templates* - the reusable workflows the jobs call, each with the templates and actions it uses in turn, as far
	  as its file is known.
	* *Actions* - the actions the workflow's steps run.

	Templates and actions are listed only if the workflow uses some.
	"""

	directiveName: str = "gha:interface"  #: Name the directive is invoked by.

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        0      #: Number of required directive arguments.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	option_spec: dict[str, Any] = {}  #: Mapping of option names to validator functions.

	def run(self) -> list[nodes.Node]:
		"""
		Create the field list.

		:returns: The field list, or nothing without a current workflow.
		"""
		from pyTooling.CI.Workflow import WorkflowError

		if (workflow := self._CurrentWorkflow()) is None:
			return []

		workflowName = self.env.ref_context["gha:workflow"]

		fieldList = nodes.field_list(classes=["gha-interface"])
		fieldList += self._Field("Required Inputs", [
			[_reference("input", f"{workflowName}.{name}", name)]
			for name, parameter in workflow.Inputs.items() if parameter.Required
		])
		secrets = []
		for name, secret in workflow.Secrets.items():
			secrets.append([_reference("secret", f"{workflowName}.{name}", name)])
			if secret.Required:
				secrets[-1].append(nodes.Text(" (required)"))

		fieldList += self._Field("Secrets", secrets)
		fieldList += self._Field("Outputs", [
			[_reference("output", f"{workflowName}.{name}", name)] for name in workflow.Outputs
		])

		# listing the templates reports a template whose file is missing or malformed, which then excludes the
		# templates from the permissions
		templates = self._Templates(workflow, {id(workflow)})
		try:
			permissions = workflow.CollectPermissions(self.env.get_domain("gha").Resolver)
		except WorkflowError:
			permissions = workflow.CollectPermissions()

		items = []
		for permission in permissions.values():
			text = str(permission)
			item: list[nodes.Node] = [nodes.literal(text, text), nodes.Text(" - ")]
			if permission.Parent is permission.Workflow:
				item.append(nodes.Text("the workflow"))
			else:
				item.extend((nodes.Text("job "), nodes.emphasis(text=permission.Parent.Name)))

			location = permission.Location
			item.append(nodes.Text(" ("))
			if (url := _gitHubURL(self.config, permission.Workflow.Path.name, permission.Line)) is None:
				item.append(nodes.Text(location))
			else:
				item.append(nodes.reference(location, location, refuri=url))
			item.append(nodes.Text(")"))
			items.append(item)

		fieldList += self._Field("Permissions", items, bullets=True)

		if len(templates) > 0:
			fieldList += nodes.field("", nodes.field_name(text="Templates"), nodes.field_body("", templates))
		if len(actions := self._Actions(workflow)) > 0:
			fieldList += nodes.field("", nodes.field_name(text="Actions"), nodes.field_body("", actions))

		return [fieldList]

	@staticmethod
	def _Field(name: str, items: list[list[nodes.Node]], bullets: bool = False) -> nodes.field:
		"""
		Create a field listing items, or saying *none*.

		:param name:    The field's name.
		:param items:   The items, each as the nodes of a line.
		:param bullets: Optional, ``True`` to list the items as bullets, else separated by commas. Default: ``False``.
		:returns:       The field.
		"""
		if len(items) == 0:
			body = nodes.paragraph("", "", nodes.emphasis(text="none"))
		elif bullets:
			body = nodes.bullet_list("", *(nodes.list_item("", nodes.paragraph("", "", *item)) for item in items))
		else:
			body = nodes.paragraph()
			for index, item in enumerate(items):
				if index > 0:
					body += nodes.Text(", ")
				body.extend(item)

		return nodes.field("", nodes.field_name(text=name), nodes.field_body("", body))

	def _Uses(self, uses: UsesReference) -> nodes.paragraph:
		"""
		Create the paragraph naming a template or an action.

		A template of the documented repository links to its ``gha:workflow``, if that is documented; one of another
		repository and an action link to GitHub.

		:param uses: The reference, as written in the workflow file.
		:returns:    The paragraph.
		"""
		text = str(uses)
		repositories = self.env.get_domain("gha").Resolver.Repositories
		if uses.IsWorkflow and (uses.IsLocal or (uses.Repository is not None and uses.Repository.lower() in repositories)):
			return nodes.paragraph("", "", _reference("workflow", uses.Stem, text))
		elif uses.Repository is None:
			return nodes.paragraph("", "", nodes.literal(text, text))

		url = f"https://github.com/{uses.Repository}"
		if uses.Path != "":
			url += f"/{'blob' if uses.IsWorkflow else 'tree'}/{uses.Ref}/{uses.Path}"

		return nodes.paragraph("", "", nodes.reference(text, "", nodes.literal(text, text), refuri=url))

	def _Actions(self, workflow: Workflow) -> nodes.bullet_list:
		"""
		List the actions a workflow's steps run, each once.

		:param workflow: The workflow.
		:returns:        A bullet list, empty if the workflow runs no action.
		"""
		actions = {str(uses): uses for uses in workflow.IterateActions()}

		return nodes.bullet_list("", *(nodes.list_item("", self._Uses(uses)) for uses in actions.values()))

	def _Templates(self, workflow: Workflow, visited: set[int]) -> nodes.bullet_list:
		"""
		List the templates a workflow's jobs call, each once, with the templates and actions each uses in turn.

		:param workflow: The workflow.
		:param visited:  The identities of the workflows listed on the path to this one, which aren't expanded again.
		:returns:        A bullet list, empty if no job calls a template.
		"""
		from pyTooling.CI.Workflow import WorkflowError

		templates = {str(job.Uses): job.Uses for job in workflow if job.Uses is not None and job.Uses.IsWorkflow}

		bulletList = nodes.bullet_list()
		for uses in templates.values():
			item = nodes.list_item("", self._Uses(uses))
			try:
				called = self.env.get_domain("gha").Resolver.Resolve(uses)
			except WorkflowError as ex:
				_logger.warning(
					f"{self.directiveName}: {ex}", location=self.get_location(), type=WARNING_TYPE, subtype="workflow"
				)
				called = None

			if called is not None and id(called) not in visited:
				nested = self._Templates(called, visited | {id(called)})
				nested.extend(self._Actions(called).children)
				if len(nested) > 0:
					item += nested

			bulletList += item

		return bulletList


@export
class YAMLExcerpt(WorkflowReferenceDirective):
	"""
	The directive ``gha:yaml``: the current workflow's file or a part of it, as a YAML code block.

	.. code-block:: ReST

	   .. gha:yaml::
	      :section: inputs

	Option ``:section:`` selects the ``inputs``, ``outputs`` or ``secrets`` of ``on.workflow_call``, or the ``jobs``;
	option ``:job:`` selects one job. Without either, the whole file is shown.

	The lines are numbered as in the file, and the part is shifted left by the indentation of its first line. The
	caption names the file and the lines, and links to them on GitHub at ``gha_ref``, if ``gha_repository`` and
	``gha_ref`` are configured.
	"""

	directiveName: str = "gha:yaml"  #: Name the directive is invoked by.

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        0      #: Number of required directive arguments.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	option_spec: dict[str, Any] = {  # type: ignore[misc]
		"caption": directives.unchanged_required,
		"job":     strip,
		"name":    strip,
		"section": strip,
	}  #: Mapping of option names to validator functions.

	def run(self) -> list[nodes.Node]:
		"""
		Create the code block.

		:returns: The code block in a captioned container, an error node for wrong options, or nothing without a current
		          workflow or when the part doesn't exist.
		"""
		if "section" in self.options and "job" in self.options:
			return [self.state.document.reporter.error(
				f"{self.directiveName}: Options ':section:' and ':job:' exclude each other.", line=self.lineno
			)]
		elif (section := self.options.get("section", None)) is not None and section not in SECTIONS:
			return [self.state.document.reporter.error(
				f"{self.directiveName}::section: '{section}' is not one of {', '.join(SECTIONS)}.", line=self.lineno
			)]

		if (workflow := self._CurrentWorkflow()) is None:
			return []

		lines = workflow.Path.read_text(encoding="utf-8").splitlines()
		if section is not None:
			if len(parameters := getattr(workflow, section.capitalize())) == 0:
				_logger.warning(
					f"{self.directiveName}: Workflow '{workflow.Name}' has no {section}.",
					location=self.get_location(), type=WARNING_TYPE, subtype="drift"
				)
				return []

			first, last = self._BlockOf(lines, self._ParentOf(lines, next(iter(parameters.values())).Line))
		elif (jobName := self.options.get("job", None)) is not None:
			if (job := workflow.Jobs.get(jobName, None)) is None:
				_logger.warning(
					f"{self.directiveName}: Workflow '{workflow.Name}' has no job '{jobName}'.",
					location=self.get_location(), type=WARNING_TYPE, subtype="drift"
				)
				return []

			first, last = self._BlockOf(lines, job.Line)
		else:
			first, last = 1, len(lines)

		indentation = _indentation(lines[first - 1])
		excerpt = [line[min(indentation, _indentation(line)):] for line in lines[first - 1:last]]

		text = "\n".join(excerpt)
		literal = nodes.literal_block(text, text, language="yaml", linenos=True)
		literal["highlight_args"] = {"linenostart": first}
		self.set_source_info(literal)

		if (caption := self.options.get("caption", None)) is None:
			fileName = workflow.Path.name
			if (first, last) == (1, len(lines)):
				caption = fileName
				url = _gitHubURL(self.config, fileName)
			else:
				caption = f"{fileName}, lines {first}-{last}"
				url = _gitHubURL(self.config, fileName, first, last)

			if url is not None:
				caption = f"`{caption} <{url}>`__"

		container = container_wrapper(self, literal, caption)
		self.add_name(container)

		return [container]

	@staticmethod
	def _IsBlank(line: str) -> bool:
		"""
		Return whether a line is empty or a comment.

		:param line: The line.
		:returns:    ``True``, if the line holds nothing but whitespace or a comment.
		"""
		stripped = line.strip()
		return stripped == "" or stripped.startswith("#")

	@classmethod
	def _ParentOf(cls, lines: list[str], line: int) -> int:
		"""
		Return the line of the key a line is nested in.

		:param lines: The lines of the file.
		:param line:  The nested line, starting at 1.
		:returns:     The nearest line above it that is indented less, starting at 1, or ``1``.
		"""
		indentation = _indentation(lines[line - 1])
		for index in range(line - 2, -1, -1):
			text = lines[index]
			if not cls._IsBlank(text) and _indentation(text) < indentation:
				return index + 1

		return 1

	@classmethod
	def _BlockOf(cls, lines: list[str], line: int) -> tuple[int, int]:
		"""
		Return the lines of a key and its value.

		The block ends before the next line - not empty and not a comment - indented as much as the key or less. A
		comment indented as much as the key or less, and empty lines, at the end aren't part of it.

		:param lines: The lines of the file.
		:param line:  The key's line, starting at 1.
		:returns:     The first and the last line of the block, starting at 1.
		"""
		indentation = _indentation(lines[line - 1])
		last = line
		for index in range(line, len(lines)):
			text = lines[index]
			if text.strip() == "":
				continue
			elif _indentation(text) > indentation:
				last = index + 1
			elif not cls._IsBlank(text):
				break

		return line, last


@export
class AutoInputs(WorkflowReferenceDirective):
	"""
	The directive ``gha:autoinputs``: an entry for every input of the current workflow the document has no
	``gha:input`` for.

	.. code-block:: ReST

	   .. gha:autoinputs::

	An entry is created as a ``gha:input`` without content creates it: the fields *Type*, *Required*, *Default Value*
	and the *Description* of the workflow file. Inputs documented by a ``gha:input`` later in the document are left
	out, too - the entries are created by :class:`AutoInputsTransform` when the whole document was parsed.
	"""

	directiveName: str = "gha:autoinputs"  #: Name the directive is invoked by.

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        0      #: Number of required directive arguments.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	option_spec: dict[str, Any] = {}  #: Mapping of option names to validator functions.

	def run(self) -> list[nodes.Node]:
		"""
		Create a placeholder, replaced by the entries once the document was parsed.

		:returns: The placeholder, or nothing without a current workflow.
		"""
		if (workflow := self._CurrentWorkflow()) is None:
			return []

		details = {"workflow": self.env.ref_context["gha:workflow"], "path": workflow.Path}
		pending = nodes.pending(AutoInputsTransform, details)
		self.set_source_info(pending)
		self.state.document.note_pending(pending)

		return [pending]


@export
class AutoInputsTransform(SphinxTransform):
	"""
	Replaces the placeholder of a ``gha:autoinputs`` by an entry for every input of its workflow the document has no
	``gha:input`` for.

	It runs after the document was parsed - so every ``gha:input`` has registered its entry - and before the entries
	are collected for the table of contents and the index.
	"""

	default_priority = 400  #: Priority among the transforms: before the local table of contents and the smart quotes.

	def apply(self, **kwargs: Any) -> None:
		"""
		Replace the placeholder by the entries.

		:param kwargs: Unused.
		"""
		pending: nodes.pending = self.startnode
		workflowName = pending.details["workflow"]
		domain = self.env.get_domain("gha")
		workflow = domain.Resolver.Load(pending.details["path"])

		entries = []
		for name, parameter in workflow.Inputs.items():
			if domain.Objects.get(("input", f"{workflowName}.{name}"), ("", ""))[0] != self.env.docname:
				entries.extend(InputDirective.CreateEntry(
					self.env, self.document, workflowName, name, parameter, [], [], pending.source, pending.line
				))

		pending.replace_self(entries)


@export
def checkUndocumentedInputs(sphinx: Sphinx, doctree: nodes.document) -> None:
	"""
	Call-back for Sphinx' ``doctree-read`` event, warning about inputs the document has no entry for.

	Every input of a workflow the document names by ``gha:workflow`` needs an entry in the document, by a ``gha:input``
	or a ``gha:autoinputs``; one without is a warning of type ``gha.drift`` at the ``gha:workflow``.

	:param sphinx:  The Sphinx application.
	:param doctree: The document read.
	"""
	if (workflows := sphinx.env.current_document.get("gha:workflows", None)) is None:
		return

	domain = sphinx.env.get_domain("gha")
	for workflowName, path, location in workflows:
		for name in domain.Resolver.Load(path).Inputs:
			if domain.Objects.get(("input", f"{workflowName}.{name}"), ("", ""))[0] != sphinx.env.docname:
				_logger.warning(
					f"Input '{name}' of workflow '{workflowName}' has no entry: add a gha:input or a gha:autoinputs.",
					location=location, type=WARNING_TYPE, subtype="drift"
				)
