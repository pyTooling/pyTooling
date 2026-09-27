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
Directives of the ``gha`` domain summarizing the current workflow: its parameters, interface, dependencies and YAML.

Each of them reads the workflow of the preceding ``gha:workflow``:

.. code-block:: ReST

   .. gha:workflow:: Package

   .. gha:parameter-table::
      :kinds: inputs secrets

   .. gha:interface::

   .. gha:dependencies::

      * pip

   .. gha:yaml::
      :job: Package

   .. gha:autoinputs::

* ``gha:parameter-table`` - the summary tables of the inputs, secrets and outputs;
* ``gha:interface`` - the contract with a caller: the required inputs, the secrets, the outputs, the permissions to
  grant;
* ``gha:dependencies`` - the templates, actions and container images used, merged with hand-written ones;
* ``gha:yaml`` - the workflow file or a part of it, as a code block linked to the file on GitHub;
* ``gha:autoinputs`` - an entry for every input the document has no ``gha:input`` for.

When a document was read, an input of its workflow without an entry is a ``gha.drift`` warning
(:func:`checkUndocumentedInputs`).

.. seealso::

   :mod:`pyTooling.Documentation.Sphinx.GitHubActions`
      |rarr| The domain ``gha``, its workflows and parameter entries.
"""
from __future__                                   import annotations

from typing                                       import TYPE_CHECKING, Any, Iterable, Optional as Nullable

from docutils                                     import nodes
from docutils.parsers.rst                         import directives
from sphinx                                       import addnodes
from sphinx.application                           import Sphinx
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


@export
class WorkflowReferenceDirective(BaseDirective):
	"""
	Base-class of the directives summarizing the current workflow, as set by the preceding ``gha:workflow``.
	"""

	@staticmethod
	def _Reference(objectType: str, target: str, text: str) -> addnodes.pending_xref:
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

	def _GitHubURL(self, fileName: str, first: Nullable[int] = None, last: Nullable[int] = None) -> Nullable[str]:
		"""
		Return the URL of a workflow file of the documented repository on GitHub, at the documented ref.

		:param fileName: The workflow file's name, as ``Package.yml``.
		:param first:    Optional, the first line to mark. Default: ``None``.
		:param last:     Optional, the last line to mark. Default: ``None``.
		:returns:        The URL, or ``None`` if ``gha_repository`` or ``gha_ref`` isn't configured.
		"""
		if self.config.gha_repository is None or self.config.gha_ref is None:
			return None

		url = f"https://github.com/{self.config.gha_repository}/blob/{self.config.gha_ref}/.github/workflows/{fileName}"
		if first is None:
			return url
		elif last is None or last == first:
			return f"{url}#L{first}"

		return f"{url}#L{first}-L{last}"

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

	A table per kind, in the order ``:kinds:`` names them, by default the order of :data:`KINDS`. A table lists the
	parameters in file order, each name linked to its entry. An input's or a secret's row states whether it is
	required, its type and its default - a long or multi-line default is shortened, the entry shows it in full. An
	output's row states its description from the workflow file.

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
				row += nodes.entry("", nodes.paragraph("", "", self._Reference(kind[:-1], f"{workflowName}.{name}", name)))
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
	The directive ``gha:interface``: the contract of the current workflow with its caller, as a field list.

	.. code-block:: ReST

	   .. gha:interface::

	* *Required Inputs*, *Secrets* and *Outputs* - the parameters, each linked to its entry; a secret a caller has to
	  pass is marked *required*.
	* *Permissions* - the permissions a caller has to grant the ``GITHUB_TOKEN``: what the workflow's jobs and the
	  jobs of the workflows they call declare, the highest access per scope, each with the job and the place in the
	  workflow file asking for it.

	The templates and actions the workflow uses are listed by :class:`Dependencies`.
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

		A called workflow whose file is missing or malformed is reported, and the permissions are then those of the
		current workflow alone.

		:returns: The field list, or nothing without a current workflow.
		"""
		from pyTooling.CI.Workflow import WorkflowError

		if (workflow := self._CurrentWorkflow()) is None:
			return []

		workflowName = self.env.ref_context["gha:workflow"]

		fieldList = nodes.field_list(classes=["gha-interface"])
		fieldList += self._Field("Required Inputs", [
			[self._Reference("input", f"{workflowName}.{name}", name)]
			for name, parameter in workflow.Inputs.items() if parameter.Required
		])
		secrets = []
		for name, secret in workflow.Secrets.items():
			secrets.append([self._Reference("secret", f"{workflowName}.{name}", name)])
			if secret.Required:
				secrets[-1].append(nodes.Text(" (required)"))

		fieldList += self._Field("Secrets", secrets)
		fieldList += self._Field("Outputs", [
			[self._Reference("output", f"{workflowName}.{name}", name)] for name in workflow.Outputs
		])

		try:
			permissions = workflow.CollectPermissions(self.env.get_domain("gha").Resolver)
		except WorkflowError as ex:
			_logger.warning(
				f"{self.directiveName}: {ex}", location=self.get_location(), type=WARNING_TYPE, subtype="workflow"
			)
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
			if (url := self._GitHubURL(permission.Workflow.Path.name, permission.Line)) is None:
				item.append(nodes.Text(location))
			else:
				item.append(nodes.reference(location, location, refuri=url))
			item.append(nodes.Text(")"))
			items.append(item)

		fieldList += self._Field("Permissions", items, bullets=True)

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


@export
class Dependencies(WorkflowReferenceDirective):
	"""
	The directive ``gha:dependencies``: what the current workflow uses, as a nested bullet list.

	.. code-block:: ReST

	   .. gha:dependencies::

	      * UnitTesting.yml

	        * pip

	          * Python packages given by :gha:input:`UnitTesting.requirements`.

	From the workflow file, and the files of the templates and actions it uses, as far as they are known locally:

	* the templates the jobs call, each once - with the jobs calling it, if several do -, each with its own
	  dependencies;
	* the actions the steps run, each once; a composite action with the actions its steps run, a Docker action with its
	  image;
	* the images of the containers and service containers the jobs run in.

	The content is a bullet list of what a file can't tell, like packages installed by a step. It is merged into the
	derived list: an item whose text is the name of a derived item - a template as ``UnitTesting.yml``, an action as
	``actions/checkout``, a container as ``container``, each also as written in the file - adds its nested list to
	that item, recursively. Any other item is appended to the list it is in. Content after the bullet list follows the
	list.
	"""

	directiveName: str = "gha:dependencies"  #: Name the directive is invoked by.

	has_content =               True   #: The hand-written dependencies.
	required_arguments =        0      #: Number of required directive arguments.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	option_spec: dict[str, Any] = {}  #: Mapping of option names to validator functions.

	_keys: dict[int, tuple[set[str], nodes.list_item]]  #: Names of each derived item, by the item's identity.

	def run(self) -> list[nodes.Node]:
		"""
		Create the list: the derived dependencies, merged with the hand-written ones.

		:returns: The list and the content following it, a paragraph saying *none* if there are no dependencies, or
		          nothing without a current workflow.
		"""
		if (workflow := self._CurrentWorkflow()) is None:
			return []

		self._keys = {}
		dependencies = self._WorkflowItems(workflow, {id(workflow)})
		dependencies["classes"].append("gha-dependencies")

		others = []
		for node in self.parse_content_to_nodes():
			if isinstance(node, nodes.bullet_list):
				self._Merge(dependencies, node)
			else:
				others.append(node)

		if len(dependencies) == 0:
			return [nodes.paragraph("", "", nodes.emphasis(text="none")), *others]

		return [dependencies, *others]

	def _Item(self, paragraph: nodes.paragraph, keys: set[str]) -> nodes.list_item:
		"""
		Create a derived item, known by the names a hand-written item may refer to it by.

		:param paragraph: The item's text.
		:param keys:      The names of the item.
		:returns:         The item.
		"""
		item = nodes.list_item("", paragraph)
		self._keys[id(item)] = (keys, item)

		return item

	def _UsesItem(self, uses: UsesReference) -> nodes.list_item:
		"""
		Create the item of a template or an action.

		A template of the documented repository links to its ``gha:workflow``, if that is documented; one of another
		repository and an action link to GitHub, as does a local action when ``gha_repository`` and ``gha_ref`` are
		configured.

		:param uses: The reference, as written in the workflow file.
		:returns:    The item, known by the reference as written, without its ref, and by a template's file name and
		             stem.
		"""
		text = str(uses)
		keys = {text, text.partition("@")[0]}
		if uses.IsWorkflow:
			keys.update((uses.FileName, uses.Stem))

		repositories = self.env.get_domain("gha").Resolver.Repositories
		literal = nodes.literal(text, text)
		if uses.IsWorkflow and (uses.IsLocal or (uses.Repository is not None and uses.Repository.lower() in repositories)):
			return self._Item(nodes.paragraph("", "", self._Reference("workflow", uses.Stem, text)), keys)
		elif uses.IsLocal and self.config.gha_repository is not None and self.config.gha_ref is not None:
			url = f"https://github.com/{self.config.gha_repository}/tree/{self.config.gha_ref}/{uses.Path}"
		elif uses.Repository is None:
			return self._Item(nodes.paragraph("", "", literal), keys)
		else:
			url = f"https://github.com/{uses.Repository}"
			if uses.Path != "":
				url += f"/{'blob' if uses.IsWorkflow else 'tree'}/{uses.Ref}/{uses.Path}"

		return self._Item(nodes.paragraph("", "", nodes.reference(text, "", literal, refuri=url)), keys)

	def _ImageItem(self, kind: str, image: str, name: str = "") -> nodes.list_item:
		"""
		Create the item of a container's image.

		:param kind:  The kind of container, as ``container``, ``service`` or ``image``.
		:param image: The image, as written.
		:param name:  Optional, the service's name. Default: ``""``.
		:returns:     The item, known by the kind - followed by the service's name -, the service's name and the image.
		"""
		paragraph = nodes.paragraph("", f"{kind} ")
		keys = {kind, image}
		if name != "":
			paragraph += (nodes.literal(name, name), nodes.Text(": "))
			keys.update((f"{kind} {name}", name))
		paragraph += nodes.literal(image, image)

		return self._Item(paragraph, keys)

	def _WorkflowItems(self, workflow: Workflow, visited: set[int]) -> nodes.bullet_list:
		"""
		List a workflow's dependencies: its templates, actions and container images.

		:param workflow: The workflow.
		:param visited:  The identities of the workflows and actions on the path to this one, which aren't expanded again.
		:returns:        A bullet list, empty if the workflow uses nothing.
		"""
		from pyTooling.CI.Workflow import WorkflowError

		templates: dict[str, tuple[UsesReference, list[str]]] = {}
		containers: dict[str, None] = {}
		services: dict[tuple[str, str], None] = {}
		for job in workflow:
			if job.Uses is not None and job.Uses.IsWorkflow:
				templates.setdefault(str(job.Uses), (job.Uses, []))[1].append(job.Name)
			if job.Container is not None:
				containers[job.Container] = None
			for serviceName, image in job.Services.items():
				services[(serviceName, image)] = None

		bulletList = nodes.bullet_list()
		for uses, jobNames in templates.values():
			item = self._UsesItem(uses)
			if len(jobNames) > 1:
				item[0] += nodes.Text(f" (called by {len(jobNames)} jobs: {', '.join(jobNames)})")

			try:
				called = self.env.get_domain("gha").Resolver.Resolve(uses)
			except WorkflowError as ex:
				_logger.warning(
					f"{self.directiveName}: {ex}", location=self.get_location(), type=WARNING_TYPE, subtype="workflow"
				)
				called = None

			if called is not None and id(called) not in visited:
				if len(nested := self._WorkflowItems(called, visited | {id(called)})) > 0:
					item += nested

			bulletList += item

		bulletList.extend(self._ActionItems(workflow.IterateActions(), visited))
		bulletList.extend(self._ImageItem("container", image) for image in containers)
		bulletList.extend(self._ImageItem("service", image, name) for name, image in services)

		return bulletList

	def _ActionItems(self, references: Iterable[UsesReference], visited: set[int]) -> list[nodes.list_item]:
		"""
		List actions, each once; a composite action with the actions its steps run, a Docker action with its image.

		:param references: The references to the actions, in file order.
		:param visited:    The identities of the workflows and actions on the path, which aren't expanded again.
		:returns:          The items.
		"""
		from pyTooling.CI.Workflow import WorkflowError

		items = []
		for uses in {str(uses): uses for uses in references}.values():
			item = self._UsesItem(uses)
			try:
				action = self.env.get_domain("gha").Resolver.ResolveAction(uses)
			except WorkflowError as ex:
				_logger.warning(
					f"{self.directiveName}: {ex}", location=self.get_location(), type=WARNING_TYPE, subtype="workflow"
				)
				action = None

			if action is not None and id(action) not in visited:
				nested = nodes.bullet_list("", *self._ActionItems(action.IterateActions(), visited | {id(action)}))
				if action.Image is not None:
					nested += self._ImageItem("image", action.Image)
				if len(nested) > 0:
					item += nested

			items.append(item)

		return items

	def _Merge(self, derived: nodes.bullet_list, handwritten: nodes.bullet_list) -> None:
		"""
		Merge a hand-written list into a derived one.

		A hand-written item whose text is a name of a derived item of this list adds its nested lists to that item,
		merged recursively; any other item is appended.

		:param derived:     The derived list.
		:param handwritten: The hand-written list.
		"""
		for item in list(handwritten.children):
			text = item[0].astext().strip() if len(item) > 0 and isinstance(item[0], nodes.paragraph) else None
			match = next(
				(child for child in derived.children if text is not None and text in self._keys.get(id(child), ((), None))[0]),
				None
			)
			if match is None:
				derived += item
				continue

			for node in item.children[1:]:
				nested = next((child for child in match.children if isinstance(child, nodes.bullet_list)), None)
				if isinstance(node, nodes.bullet_list) and nested is not None:
					self._Merge(nested, node)
				else:
					match += node


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

		indentation = self._Indentation(lines[first - 1])
		excerpt = [line[min(indentation, self._Indentation(line)):] for line in lines[first - 1:last]]

		text = "\n".join(excerpt)
		literal = nodes.literal_block(text, text, language="yaml", linenos=True)
		literal["highlight_args"] = {"linenostart": first}
		self.set_source_info(literal)

		if (caption := self.options.get("caption", None)) is None:
			fileName = workflow.Path.name
			if (first, last) == (1, len(lines)):
				caption = fileName
				url = self._GitHubURL(fileName)
			else:
				caption = f"{fileName}, lines {first}-{last}"
				url = self._GitHubURL(fileName, first, last)

			if url is not None:
				caption = f"`{caption} <{url}>`__"

		container = container_wrapper(self, literal, caption)
		self.add_name(container)

		return [container]

	@staticmethod
	def _Indentation(line: str) -> int:
		"""
		Return the indentation of a line of a YAML file.

		:param line: The line.
		:returns:    The number of spaces the line starts with.
		"""
		return len(line) - len(line.lstrip(" "))

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
		indentation = cls._Indentation(lines[line - 1])
		for index in range(line - 2, -1, -1):
			text = lines[index]
			if not cls._IsBlank(text) and cls._Indentation(text) < indentation:
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
		indentation = cls._Indentation(lines[line - 1])
		last = line
		for index in range(line, len(lines)):
			text = lines[index]
			if text.strip() == "":
				continue
			elif cls._Indentation(text) > indentation:
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
