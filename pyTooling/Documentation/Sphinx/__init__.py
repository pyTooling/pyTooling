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
A Sphinx extension providing the roles, nodes and directives shared by pyTooling and its sibling projects.

Every project in the family used to carry its own :file:`doc/prolog.inc` - eighteen hand-copied files, 36 to 67
lines each, already drifted apart - declaring the same roles as **ReST source** that is re-parsed into every
document of every project. This extension declares them once:

.. code-block:: Python

   # doc/conf.py
   extensions = [
     ...,
     "pyTooling.Documentation.Sphinx",
   ]

.. rubric:: What it registers

* the **style roles** ``:bolditalic:``, ``:underline:``, ``:strike:``, ``:xlarge:``, ``:red:``, ``:green:``,
  ``:blue:``, ``:purple:``, ``:deletion:`` and ``:addition:``, together with the stylesheet they need - so the
  styling is a CSS file instead of a ``raw:: html`` block smuggled into every page;
* the **code role** ``:pycode:``, which highlights inline Python;
* the **directive** :rst:dir:`condensed-class`, which renders a class' public interface from its source.

:class:`~pyTooling.Documentation.Sphinx.Directives.BaseDirective` isn't registered - it is a base-class for a
project's own directives, offering typed option access and table construction over the untyped mapping and the
hand-assembled node trees docutils presents.

.. attention::

   This package imports Sphinx and docutils, which :mod:`pyTooling` itself does not depend on. Install it as
   ``pyTooling[sphinx]``, or rely on Sphinx already being present - which it is, wherever a :file:`conf.py` is
   being executed.

.. seealso::

   :mod:`pyTooling.Documentation`
      |rarr| The doc-string helpers, which need no Sphinx.
"""
from hashlib                                     import md5
from pathlib                                     import Path
from typing                                      import Any

from sphinx.application                          import Sphinx

from pyTooling.Common                            import readResourceFile
from pyTooling.Decorators                        import export
from pyTooling.Documentation.Sphinx              import static as StaticResources
from pyTooling.Documentation.Sphinx.CondensedClass import CondensedClass
from pyTooling.Documentation.Sphinx.Directives   import BaseDirective, SphinxExtensionError, strip, stripAndNormalize
from pyTooling.Documentation.Sphinx.Roles        import PYTHON_CODE_ROLE, STYLE_ROLES, pythonCodeRole, styleRole


__all__ = [
	"STYLESHEET", "SUBSTITUTIONS",
	# re-exported so a consumer imports them from the package rather than from its modules
	"BaseDirective", "SphinxExtensionError", "CondensedClass", "strip", "stripAndNormalize",
	"PYTHON_CODE_ROLE", "STYLE_ROLES", "pythonCodeRole", "styleRole",
]

#: Name of the stylesheet shipped beside this module.
STYLESHEET = "pyTooling.css"

#: Substitutions that have to stay substitutions, because ``|br|`` is written as one in every project.
SUBSTITUTIONS = """
.. |degree| unicode:: U+00B0
   :trim:

.. |br| raw:: html

   <br />

.. |hr| raw:: html

   <hr />
"""


@export
def installStylesheet(sphinx: Sphinx) -> None:
	"""
	Call-back for Sphinx' ``builder-inited`` event, writing the stylesheet into the build and linking it.

	The file is named by the hash of its content, so a browser re-reads it when the styles change and re-uses it when
	they don't. Older copies are removed when the content changed.

	:param sphinx: The Sphinx application.
	"""
	staticDirectory = (Path(sphinx.outdir) / "_pyTooling_static").resolve()
	staticDirectory.mkdir(exist_ok=True)
	sphinx.config.html_static_path.append(str(staticDirectory))

	content = readResourceFile(StaticResources, STYLESHEET)
	digest = md5(content.encode("utf-8")).hexdigest()          # nosec B324 - a cache-busting name, not a signature
	stylesheet = staticDirectory / f"pyTooling.{digest}.css"
	sphinx.add_css_file(stylesheet.name)

	if not stylesheet.exists():
		for outdated in staticDirectory.glob("*.css"):
			outdated.unlink()

		stylesheet.write_text(content, encoding="utf-8")


@export
def extendProlog(sphinx: Sphinx, config: Any) -> None:
	"""
	Call-back for Sphinx' ``config-inited`` event, appending the shared substitutions to ``rst_prolog``.

	A role can be registered; a **substitution** cannot - ``|br|`` is substitution syntax, and every project writes
	it that way already. Appending them here is what lets a project delete them from its own prolog without changing
	a single document.

	:param sphinx: The Sphinx application.
	:param config: The configuration, after :file:`conf.py` was read.
	"""
	config.rst_prolog = (config.rst_prolog or "") + SUBSTITUTIONS


@export
def setup(sphinx: Sphinx) -> dict[str, Any]:
	"""
	Register the roles, the node and the directive with Sphinx.

	:param sphinx: The Sphinx application to register with.
	:returns:      The extension's metadata.
	"""
	for roleName in STYLE_ROLES:
		sphinx.add_role(roleName, styleRole)

	sphinx.add_role(PYTHON_CODE_ROLE, pythonCodeRole)

	sphinx.add_directive("condensed-class", CondensedClass)

	sphinx.connect("config-inited", extendProlog)
	sphinx.connect("builder-inited", installStylesheet)

	return {"version": "0.1.0", "parallel_read_safe": True, "parallel_write_safe": True}
