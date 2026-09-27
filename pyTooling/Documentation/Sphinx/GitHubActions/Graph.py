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
A Sphinx directive drawing the pipeline of a GitHub Actions workflow as a Graphviz graph.

The jobs of a workflow and the ``needs`` between them are its pipeline. This directive draws it at build time from the
workflow file, so the picture cannot drift from the file:

.. code-block:: ReST

   .. gha:pipeline-graph:: ../.github/workflows/CompletePipeline.yml
      :depth: 1

A job is a node labelled with its name and, if it calls a reusable workflow, that workflow's file. A reusable workflow
of the documented repository is expanded into a cluster of its own jobs, as many levels deep as ``:depth:`` says. In
HTML, a node links to the page documenting its reusable workflow, if the ``gha`` domain knows one.

.. seealso::

   :mod:`pyTooling.CI.Workflow`
      |rarr| The model of a workflow file the graph is drawn from.
   :mod:`pyTooling.Documentation.Sphinx.SchemaGraph`
      |rarr| The other graph directives of the extension.
"""
from html                                      import escape as html_escape
from pathlib                                   import Path, PurePosixPath
from re                                        import Match, compile as re_compile
from typing                                    import Any, Optional as Nullable

from docutils                                  import nodes
from docutils.parsers.rst                      import directives
from sphinx.application                        import Sphinx
from sphinx.errors                             import ExtensionError
from sphinx.ext.graphviz                       import align_spec, figure_wrapper, graphviz
from sphinx.util.logging                       import getLogger

from pyTooling.Common                          import getFullyQualifiedName
from pyTooling.Decorators                      import export, readonly
from pyTooling.MetaClasses                     import ExtendedType
from pyTooling.CI.Workflow                     import Job, UsesReference, Workflow, WorkflowError, WorkflowResolver
from pyTooling.Documentation.Sphinx.Directives import BaseDirective, SphinxExtensionError, strip, stripAndNormalize


__all__ = ["GRAPH_ATTRIBUTES", "CSS_CLASS", "LINK_MARKER", "CONFIG_VALUES"]

#: Attributes every pipeline graph is drawn with, so two pipelines in one document look alike.
GRAPH_ATTRIBUTES = (
	"compound=true;",
	"newrank=true;",
	'fontname="sans-serif";',
	'fontsize="10";',
	"nodesep=0.25;",
	"ranksep=0.4;",
	'node [shape="box", style="rounded,filled", color="#5f6b7a", fillcolor="#e4ecf7", penwidth="1.0",',
	'      fontname="sans-serif", fontsize="10"];',
	'edge [color="#5f6b7a", arrowsize="0.7"];',
)

#: CSS class of a pipeline graph's ``graphviz`` node, which is also how :func:`resolveLinks` finds it.
CSS_CLASS = "gha-pipeline-graph"

#: A DOT comment, and the whitespace before it, standing where a job's link belongs, until :func:`resolveLinks`
#: replaces it by the link or removes it.
LINK_MARKER = re_compile(r"(?P<space>\s*)/\*gha-link:(?P<stem>[^*]*)\*/")

#: Configuration values of the directive, as ``name: (default, rebuild, types)``.
#:
#: ``gha_ref`` is the ref - a branch or tag - of the documented repository the documentation describes. A job calling
#: a reusable workflow of that repository at another ref is reported. Without it, refs aren't checked.
CONFIG_VALUES: dict[str, tuple[Any, str, Any]] = {
	"gha_ref": (None, "env", (str, )),
}

_logger = getLogger(__name__)


@export
class PipelineDotGraph(metaclass=ExtendedType, slots=True):
	"""
	The pipeline of a workflow in the DOT language: its jobs as nodes, their ``needs`` as edges.

	The kind of a job is its node's shape and style:

	* a job calling a reusable workflow is a rounded box, labelled with the job's name and the workflow's file;
	* a job calling a reusable workflow of another repository is a white rounded box, and its label also names that
	  repository and ref - it is never expanded;
	* a job running steps is a grey box with square corners;
	* a job with an ``if`` condition is dashed, and its tooltip is the condition;
	* a job with a ``strategy.matrix`` has a double border, and its label names the matrix' dimensions, if they are
	  known before the workflow runs.

	A job calling a reusable workflow that :class:`~pyTooling.CI.Workflow.WorkflowResolver` finds locally is drawn as
	a cluster of that workflow's jobs instead, until the depth is used up. An edge to or from such a job ends at the
	cluster's border.

	The graph is drawn in file order, so the same workflow is always drawn as the same DOT.
	"""

	_resolver:   WorkflowResolver  #: Resolver reading the reusable workflows the jobs call.
	_reduce:     bool              #: Whether an edge a longer path implies is dropped.
	_link:       bool              #: Whether a job calling a reusable workflow of the documented repository is linked.
	_statements: list[str]         #: The statements written so far, one per line, already indented.
	_jobs:       list[Job]         #: The jobs drawn, each once, in the order they were drawn.
	_workflows:  list[Workflow]    #: The workflows drawn, each once, the entry-point workflow first.

	def __init__(
		self,
		workflow: Workflow,
		resolver: Nullable[WorkflowResolver] = None,
		direction: str = "LR",
		depth: int = 0,
		reduce: bool = True,
		link: bool = True
	) -> None:
		"""
		Initializes the graph by drawing a workflow.

		:param workflow:       The workflow to draw.
		:param resolver:       Optional, the resolver reading the reusable workflows the jobs call. It also decides which
		                       repository is documented: a local one, and every repository it maps to a directory.
		                       Default: a resolver knowing local references only.
		:param direction:      Optional, direction the pipeline flows in: ``LR`` (left to right) or ``TB`` (top to
		                       bottom). Default: ``LR``.
		:param depth:          Optional, levels of reusable workflows expanded into clusters. Default: ``0``.
		:param reduce:         Optional, drop an edge a longer path implies. Default: ``True``.
		:param link:           Optional, mark a job calling a reusable workflow of the documented repository for
		                       :func:`resolveLinks`. Default: ``True``.
		:raises ValueError:    If parameter 'workflow' is None.
		:raises TypeError:     If parameter 'workflow' is not of type :class:`~pyTooling.CI.Workflow.Workflow`.
		:raises TypeError:     If parameter 'resolver' is not of type :class:`~pyTooling.CI.Workflow.WorkflowResolver`.
		:raises ValueError:    If parameter 'direction' is neither ``LR`` nor ``TB``.
		:raises TypeError:     If parameter 'depth' is not of type :class:`int`.
		:raises ValueError:    If parameter 'depth' is negative.
		:raises TypeError:     If parameter 'reduce' is not of type :class:`bool`.
		:raises TypeError:     If parameter 'link' is not of type :class:`bool`.
		:raises WorkflowError: If a reusable workflow to expand doesn't exist, or is not a well-formed workflow.
		"""
		if workflow is None:
			raise ValueError("Parameter 'workflow' is None.")
		elif not isinstance(workflow, Workflow):
			ex = TypeError("Parameter 'workflow' is not of type 'Workflow'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(workflow)}'.")
			raise ex

		if resolver is None:
			resolver = WorkflowResolver()
		elif not isinstance(resolver, WorkflowResolver):
			ex = TypeError("Parameter 'resolver' is not of type 'WorkflowResolver'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(resolver)}'.")
			raise ex

		if direction not in ("LR", "TB"):
			ex = ValueError("Parameter 'direction' is neither 'LR' nor 'TB'.")
			ex.add_note(f"Got '{direction}'.")
			raise ex

		if not isinstance(depth, int) or isinstance(depth, bool):
			ex = TypeError("Parameter 'depth' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
			raise ex
		elif depth < 0:
			ex = ValueError("Parameter 'depth' is negative.")
			ex.add_note(f"Got value '{depth}'.")
			raise ex

		if not isinstance(reduce, bool):
			ex = TypeError("Parameter 'reduce' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(reduce)}'.")
			raise ex

		if not isinstance(link, bool):
			ex = TypeError("Parameter 'link' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(link)}'.")
			raise ex

		self._resolver =   resolver
		self._reduce =     reduce
		self._link =       link
		self._statements = [f"\trankdir={direction};", *(f"\t{attribute}" for attribute in GRAPH_ATTRIBUTES), ""]
		self._jobs =       []
		self._workflows =  []

		self._DrawWorkflow(workflow, "", depth, "\t")

	@readonly
	def Jobs(self) -> list[Job]:
		"""
		Read-only property to access the jobs drawn (:attr:`_jobs`).

		A reusable workflow expanded twice is drawn twice, but its jobs are listed once.

		:returns: The jobs of every workflow drawn, in the order they were drawn.
		"""
		return self._jobs

	@readonly
	def Workflows(self) -> list[Workflow]:
		"""
		Read-only property to access the workflows drawn (:attr:`_workflows`).

		:returns: The entry-point workflow, followed by every reusable workflow expanded into a cluster, each once.
		"""
		return self._workflows

	@staticmethod
	def _Quote(text: str) -> str:
		"""
		Quote a text as a DOT string, keeping its line breaks as escape sequences.

		:param text: The text to quote.
		:returns:    The text in double quotes.
		"""
		text = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

		return f'"{text}"'

	@staticmethod
	def _Label(title: str, lines: list[str]) -> str:
		"""
		Render an HTML-like label: a title and, below it, lines in a smaller font.

		:param title: The title, unescaped.
		:param lines: The lines below the title, unescaped.
		:returns:     The label in angle brackets, as DOT writes an HTML-like label.
		"""
		label = html_escape(title, quote=False)
		for line in lines:
			label += f'<BR/><FONT POINT-SIZE="8" COLOR="#3d4652">{html_escape(line, quote=False)}</FONT>'

		return f"<{label}>"

	def _IsDocumented(self, uses: UsesReference) -> bool:
		"""
		Return whether a reference names a reusable workflow of the documented repository.

		:param uses: The reference, as :attr:`Job.Uses <pyTooling.CI.Workflow.Job.Uses>`.
		:returns:    ``True``, if the reference is local, or its repository is mapped by the resolver.
		"""
		return uses.IsLocal or (uses.Repository is not None and uses.Repository.lower() in self._resolver.Repositories)

	def _Describe(self, job: Job) -> tuple[list[str], list[str], str]:
		"""
		Describe a job: the lines of its label, the parts of its style, and its tooltip.

		:param job: The job to describe.
		:returns:   The label's lines below the job's name, the style's parts, and the tooltip - the reusable workflow
		            called and the condition, one per line, or an empty string.
		"""
		lines = []
		style = []
		tooltip = []

		if (uses := job.Uses) is not None:
			lines.append(uses.FileName)
			if not self._IsDocumented(uses):
				lines.append(f"{uses.Repository}@{uses.Ref}")
			tooltip.append(f"uses: {uses}")

		if (matrix := job.Matrix) is not None:
			if matrix.IsDynamic or len(matrix.Dimensions) == 0:
				lines.append("matrix")
			else:
				lines.append(f"matrix: {', '.join(matrix.Dimensions)}")

		if (condition := job.Condition) is not None:
			style.append("dashed")
			tooltip.append(f"if: {condition}")

		return lines, style, "\n".join(tooltip)

	def _DrawJob(self, job: Job, identifier: str, indent: str) -> None:
		"""
		Draw a job as a node.

		:param job:        The job to draw.
		:param identifier: Identifier of the node.
		:param indent:     Indentation of the node's statement.
		"""
		lines, style, tooltip = self._Describe(job)

		if (uses := job.Uses) is None:
			attributes = {"style": ",".join(("filled", *style)), "fillcolor": "#f2f2f2"}
		elif self._IsDocumented(uses):
			attributes = {"style": ",".join(("rounded", "filled", *style))}
		else:
			attributes = {"style": ",".join(("rounded", "filled", *style)), "fillcolor": "#ffffff"}

		if job.Matrix is not None:
			attributes["peripheries"] = "2"

		statement = f"{indent}{self._Quote(identifier)} [label={self._Label(job.Name, lines)}"
		for name, value in attributes.items():
			statement += f", {name}={self._Quote(value)}"

		if tooltip != "":
			statement += f", tooltip={self._Quote(tooltip)}"

		if self._link and uses is not None and self._IsDocumented(uses):
			statement += f" /*gha-link:{uses.Stem}*/"

		self._statements.append(f"{statement}];")

	def _DrawWorkflow(self, workflow: Workflow, prefix: str, depth: int, indent: str) -> tuple[str, str]:
		"""
		Draw the jobs of a workflow and the edges between them.

		:param workflow:       The workflow to draw.
		:param prefix:         Prefix of the identifiers of its nodes: the path of the jobs calling it.
		:param depth:          Levels of reusable workflows still to expand.
		:param indent:         Indentation of its statements.
		:returns:              Identifiers of the node an edge into the workflow ends at - the first job needing none -
		                       and of the node an edge out of it starts at - the last job no job needs.
		:raises WorkflowError: If a reusable workflow to expand doesn't exist, or is not a well-formed workflow.
		"""
		if workflow not in self._workflows:
			self._workflows.append(workflow)

		# per job: the node an edge into it ends at, the node an edge out of it starts at, and its cluster
		anchors: dict[str, tuple[str, str, Nullable[str]]] = {}
		for job in workflow:
			if job not in self._jobs:
				self._jobs.append(job)

			identifier = f"{prefix}{job.Name}"
			if depth == 0 or job.Uses is None or (called := self._resolver.Resolve(job.Uses)) is None:
				self._DrawJob(job, identifier, indent)
				anchors[job.Name] = (identifier, identifier, None)
				continue

			lines, style, tooltip = self._Describe(job)
			cluster = f"cluster_{identifier}"
			self._statements.append(f"{indent}subgraph {self._Quote(cluster)} {{")
			self._statements.append(f"{indent}\tlabel={self._Label(job.Name, lines)};")
			self._statements.append(f'{indent}\tlabeljust="l";')
			self._statements.append(f"{indent}\tstyle={self._Quote(','.join(('rounded', 'filled', *style)))};")
			self._statements.append(f'{indent}\tcolor="#8a9bb2";')
			self._statements.append(f'{indent}\tfillcolor="#f6f8fb";')
			if tooltip != "":
				self._statements.append(f"{indent}\ttooltip={self._Quote(tooltip)};")
			if self._link:
				self._statements.append(f"{indent}\t/*gha-link:{job.Uses.Stem}*/")

			entryNode, exitNode = self._DrawWorkflow(called, f"{identifier}/", depth - 1, f"{indent}\t")
			self._statements.append(f"{indent}}}")
			anchors[job.Name] = (entryNode, exitNode, cluster)

		# the jobs needing none start together: in the first rank of the graph, or side by side in their cluster
		roots = [self._Quote(anchors[job.Name][0]) for job in workflow if len(job.NeedNames) == 0]
		if prefix == "":
			self._statements.append(f"{indent}{{rank=min; {'; '.join(roots)};}}")
		elif len(roots) > 1:
			self._statements.append(f"{indent}{{rank=same; {'; '.join(roots)};}}")

		for need, job in workflow.ReducedEdges if self._reduce else workflow.Edges:
			_, tail, tailCluster = anchors[need.Name]
			head, _, headCluster = anchors[job.Name]

			attributes = []
			if tailCluster is not None:
				attributes.append(f"ltail={self._Quote(tailCluster)}")
			if headCluster is not None:
				attributes.append(f"lhead={self._Quote(headCluster)}")

			statement = f"{indent}{self._Quote(tail)} -> {self._Quote(head)}"
			if len(attributes) > 0:
				statement += f" [{', '.join(attributes)}]"

			self._statements.append(f"{statement};")

		needed = {need.Name for need, _ in workflow.Edges}
		first = next(job for job in workflow if len(job.NeedNames) == 0)
		last = [job for job in workflow if job.Name not in needed][-1]

		return anchors[first.Name][0], anchors[last.Name][1]

	def __str__(self) -> str:
		"""
		Render the graph.

		:returns: The graph in the DOT language.
		"""
		statements = "\n".join(self._statements)

		return f"digraph pipeline {{\n{statements}\n}}"


@export
class PipelineGraph(BaseDirective):
	"""
	The ``gha:pipeline-graph`` directive: the pipeline of a workflow, drawn from the workflow file.

	One argument, the path of the workflow file relative to the document using the directive.

	The documented repository and the directory of its workflow files are the configuration values ``gha_repository``
	and ``gha_workflow_directory`` - relative to the source directory, and by default the directory of the drawn
	workflow file. A job calling a reusable workflow of that repository is expanded, while ``:depth:`` allows, and
	checked against the ref ``gha_ref``, if that is configured.
	"""

	directiveName: str = "gha:pipeline-graph"  #: Name the directive is invoked by.

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        1      #: Number of required directive arguments: the workflow file's path.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	# docutils declares 'option_spec' on 'Directive' and 'BaseDirective' assigns it, so mypy calls every
	# spelling of this override a conflict with one of them
	#: Mapping of option names to validator functions.
	option_spec: dict[str, Any] = {  # type: ignore[misc]
		"align":     align_spec,
		"alt":       strip,
		"caption":   strip,
		"depth":     directives.nonnegative_int,
		"direction": strip,
		"link":      stripAndNormalize,
		"name":      strip,
		"reduce":    stripAndNormalize,
	}

	def run(self) -> list[nodes.Node]:
		"""
		Read the workflow file and hand its pipeline to :mod:`sphinx.ext.graphviz` for rendering.

		Every workflow file drawn becomes a dependency of the document. A job calling a reusable workflow of the
		documented repository at another ref than ``gha_ref`` is reported as a warning of type ``gha.ref``.

		:returns: A ``graphviz`` node, wrapped in a figure when a caption was given, or an error node when the options or
		          the workflow files are wrong.
		"""
		relativePath, absolutePath = self.env.relfn2path(self.arguments[0])
		self.env.note_dependency(relativePath)
		workflowFile = Path(absolutePath)

		repository = getattr(self.config, "gha_repository", None)
		directory = getattr(self.config, "gha_workflow_directory", None)
		ref = getattr(self.config, "gha_ref", None)

		try:
			direction = self._ParseStringOption("direction", "LR", "(?i)(LR|TB)$").upper()
			reduce = self._ParseBooleanOption("reduce", True)
			link = self._ParseBooleanOption("link", True)
		except SphinxExtensionError as ex:
			return [self.state.document.reporter.error(str(ex), line=self.lineno)]

		if repository is None:
			repositories = {}
		elif directory is None:
			repositories = {repository: workflowFile.parent}
		else:
			repositories = {repository: Path(self.env.srcdir) / directory}

		try:
			resolver = WorkflowResolver(repositories)
			graph = PipelineDotGraph(
				resolver.Load(workflowFile), resolver, direction, self.options.get("depth", 0), reduce, link
			)
		except (OSError, ValueError, WorkflowError) as ex:
			message = f"{self.directiveName}: Couldn't draw '{self.arguments[0]}': {ex}"
			for note in getattr(ex, "__notes__", []):
				message += f" {note}"

			return [self.state.document.reporter.error(message, line=self.lineno)]

		for workflow in graph.Workflows[1:]:
			self.env.note_dependency(str(workflow.Path))

		if repository is not None and ref is not None:
			for job in graph.Jobs:
				if (
					(uses := job.Uses) is not None and uses.Repository is not None and
					uses.Repository.lower() == repository.lower() and uses.Ref != ref
				):
					_logger.warning(
						f"{self.directiveName}: Job '{job.Name}' calls '{uses.FileName}' at ref '{uses.Ref}', but the "
						f"documentation describes ref '{ref}' ({uses.Location}).",
						location=(self.env.docname, self.lineno),
						type="gha",
						subtype="ref"
					)

		node = graphviz()
		node["code"] = str(graph)
		node["options"] = {"docname": self.env.docname}
		node["alt"] = self.options.get("alt", f"Pipeline of {workflowFile.name}")
		node["classes"] = [CSS_CLASS]
		if "align" in self.options:
			node["align"] = self.options["align"]

		if (caption := self.options.get("caption", None)) is not None:
			figure = figure_wrapper(self, node, caption)
			self.add_name(figure)
			return [figure]

		self.add_name(node)
		return [node]


@export
def resolveLinks(sphinx: Sphinx, doctree: nodes.document, docname: str) -> None:
	"""
	Call-back for Sphinx' ``doctree-resolved`` event, linking the jobs of a pipeline graph to their reusable workflows.

	A job calling a reusable workflow of the documented repository links to the page documenting that workflow, as the
	``gha`` domain resolves the workflow's file stem with ``ResolveWorkflow``. Without the domain, without a page for
	the workflow, or in a format other than HTML, the job has no link.

	:param sphinx:  The Sphinx application.
	:param doctree: The resolved document.
	:param docname: Name of the document.
	"""
	try:
		domain = sphinx.env.get_domain("gha")
	except ExtensionError:
		domain = None

	def link(match: Match[str]) -> str:
		"""
		Nested function returning the link attributes replacing a marker, or nothing.

		:param match: The marker.
		:returns:     The whitespace before the marker and the attributes ``URL`` and ``target``, or an empty string
		              when there is nothing to link to.
		"""
		if domain is None or sphinx.builder.format != "html":
			return ""
		elif (target := domain.ResolveWorkflow(match["stem"])) is None:
			return ""

		targetDocname, anchor = target
		if (uri := sphinx.builder.get_relative_uri(docname, targetDocname)) == "":
			uri = PurePosixPath(sphinx.builder.get_target_uri(targetDocname)).name

		return f'{match["space"]}URL="{uri}#{anchor}" target="_top"'

	for node in doctree.findall(graphviz):
		if CSS_CLASS in node["classes"]:
			node["code"] = LINK_MARKER.sub(link, node["code"])
