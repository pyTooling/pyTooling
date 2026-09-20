# ==================================================================================================================== #
#               _____           _ _               ____ _     ___                                                       #
#    _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___| |   |_ _|                                                      #
#   | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   | |    | |                                                       #
#   | |_) | |_| || | (_) | (_) | | | | | | (_| || |___| |___ | |                                                       #
#   | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|_____|___|                                                      #
#   |_|    |___/                          |___/                                                                        #
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
The command line interface of pyTooling, and its :program:`pyTooling` program.

.. rubric:: Usage

.. code-block:: bash

   pyTooling help
   pyTooling version

.. hint::

   See :ref:`high-level help <CLI>` for explanations and usage examples.
"""
from argparse                               import RawDescriptionHelpFormatter, Namespace
from textwrap                               import dedent
from typing                                 import ClassVar, NoReturn

from pyTooling.Decorators                   import export
from pyTooling.Exceptions                   import ExceptionBase, ToolingException
from pyTooling.Attributes.ArgParse          import ArgParseHelperMixin, DefaultHandler, CommandHandler
from pyTooling.Attributes.ArgParse.Flag     import FlagArgument
from pyTooling.Attributes.ArgParse.Argument import StringArgument
from pyTooling.TerminalUI                   import TerminalApplication, Mode

from pyTooling.CLI.Pipeline                  import PipelineHandlers


@export
class Application(TerminalApplication, PipelineHandlers, ArgParseHelperMixin):
	"""
	The :program:`pyTooling` program: a terminal application whose commands are declared as attributes.

	Every command is a method marked with :class:`~pyTooling.Attributes.ArgParse.CommandHandler`, and the arguments
	of a command are the attributes written on that method. A group of related commands is a mixin-class of its own,
	which this class inherits from - so a new command is a new mixin and one more base-class, and nothing here has
	to know what it does.
	"""
	HeadLine: ClassVar[str] = "pyTooling Service Program"  #: Headline printed above every command's output.

	def __init__(self) -> None:
		"""Initializes the program, its terminal and its command line parser."""
		super().__init__(Mode.TextToStdOut_ErrorsToStdErr)

		textWidth = min(self.Width, 160)

		class HelpFormatter(RawDescriptionHelpFormatter):
			"""Nested class widening argparse's help page to the terminal, and its option column to 30 characters."""

			def __init__(self, *args, **kwargs) -> None:
				"""
				Initializes the formatter with the widths this program wants.

				:param args:   Positional parameters, passed on to :class:`~argparse.RawDescriptionHelpFormatter`.
				:param kwargs: Keyword parameters, passed on after the two widths were set.
				"""
				kwargs["max_help_position"] = 30
				kwargs["width"] = textWidth
				super().__init__(*args, **kwargs)

		ArgParseHelperMixin.__init__(
			self,
			prog="pyTooling",
			description=dedent(f"""\
				'{self.HeadLine}' to work with pyTooling data models.
				"""),
			formatter_class=HelpFormatter,
			add_help=False
		)

	def Run(self, enableAutoComplete: bool = True) -> None:
		"""
		Parses the command line and dispatches to the handler of the command it names.

		:param enableAutoComplete: Optional, register the parser with ``argcomplete``, if that package is installed.
		                           Default: ``True``.
		"""
		ArgParseHelperMixin.Run(self, enableAutoComplete)

	@DefaultHandler()
	@FlagArgument("-q", "--quiet", dest="quiet", help="Reduce messages to a minimum.")
	@FlagArgument("-v", "--verbose", dest="verbose", help="Print out detailed messages.")
	@FlagArgument("-d", "--debug", dest="debug", help="Enable debug mode.")
	def HandleDefault(self, _: Namespace) -> None:
		"""Handle program calls without any command."""
		self._PrintHeadline()
		self._PrintHelp()

	@CommandHandler("help", help="Display help page(s) for the given command name.",
	                description="Display help page(s) for the given command name.")
	@StringArgument(dest="Command", metaName="Command", optional=True, help="Print help page(s) for a command.")
	def HandleHelp(self, args: Namespace) -> None:
		"""
		Handle program calls with command ``help``.

		:param args: The parsed command line, whose ``Command`` names the command to print the help page of.
		"""
		self._PrintHeadline()
		self._PrintHelp(args.Command)

	@CommandHandler("version", help="Display version information.", description="Display version information.")
	def HandleVersion(self, _: Namespace) -> None:
		"""Handle program calls with command ``version``."""
		from pyTooling import Common as DunderModule

		self._PrintHeadline()
		self._PrintVersion(DunderModule, "pyTooling")


@export
def main() -> NoReturn:
	"""
	Entrypoint to start program execution.

	This function is called either from :pycode:`if __name__ == "__main__":` or through the ``console_scripts``
	entry point :program:`pyTooling`, which :file:`setup.py` registers.

	It creates the :class:`Application` and runs it in a ``try ... except`` environment, so an exception is reported
	as a message and a non-zero exit code rather than as a traceback.
	"""
	from sys import argv

	program = Application()
	program.Configure(
		verbose=("-v" in argv or "--verbose" in argv),
		debug=("-d" in argv or "--debug" in argv),
		silent=("-q" in argv or "--quiet" in argv)
	)

	try:
		program.Run()
	except ToolingException as ex:
		program.WriteLineToStdErr(f"{{RED}}[ERROR] {ex}{{NOCOLOR}}".format(**program.Foreground))
		if ex.__cause__ is not None:
			program.WriteLineToStdErr(f"{{DARK_YELLOW}}Because of: {ex.__cause__}{{NOCOLOR}}".format(**program.Foreground))
		for note in getattr(ex, "__notes__", ()) or ():
			program.WriteLineToStdErr(f"{{DARK_YELLOW}} [NOTE] {note}{{NOCOLOR}}".format(**program.Foreground))
		program.Exit(1)
	except ExceptionBase as ex:
		program.PrintExceptionBase(ex)
	except NotImplementedError as ex:
		program.PrintNotImplementedError(ex)
	except Exception as ex:
		program.PrintException(ex)


if __name__ == "__main__":
	main()
