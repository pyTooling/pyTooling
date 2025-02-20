# ==================================================================================================================== #
#             _____           _ _               ____ _     ___    _    _         _                  _   _              #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___| |   |_ _|  / \  | |__  ___| |_ _ __ __ _  ___| |_(_) ___  _ __   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   | |    | |  / _ \ | '_ \/ __| __| '__/ _` |/ __| __| |/ _ \| '_ \  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |___| |___ | | / ___ \| |_) \__ \ |_| | | (_| | (__| |_| | (_) | | | | #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|_____|___/_/   \_\_.__/|___/\__|_|  \__,_|\___|\__|_|\___/|_| |_| #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2014-2016 Technische Universität Dresden - Germany, Chair of VLSI-Design, Diagnostics and Architecture     #
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
This module implements command arguments. Usually, commands are mutually exclusive and the first argument in a list of
arguments to a program.

While commands can or cannot have prefix characters, they shouldn't be confused with flag arguments or string arguments.

**Example:**

* ``prog command -arg1 --argument2``

.. seealso::

   * For simple flags (various formats). |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.Flag`
   * For string arguments. |br|
     |rarr| :class:`~pyTooling.CLIAbstraction.Argument.StringArgument`
"""
from typing import Any

try:
	from pyTooling.Decorators              import export
	from pyTooling.CLIAbstraction.Argument import NamedArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                      import export
		from CLIAbstraction.Argument         import NamedArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


# TODO: make this class abstract
@export
class CommandArgument(NamedArgument):
	"""
	Represents a command argument.

	It is usually used to select a sub parser in a CLI argument parser or to hand over all following parameters to a
	separate tool. An example for a command is 'checkout' in ``git.exe checkout``, which calls ``git-checkout.exe``.

	**Example:**

	* ``command``
	"""

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is CommandArgument:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class ShortCommand(CommandArgument, pattern="-{0}"):
	"""
	Represents a command name with a single dash.

	**Example:**

	* ``-command``
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "-{0}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is ShortCommand:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class LongCommand(CommandArgument, pattern="--{0}"):
	"""
	Represents a command name with a double dash.

	**Example:**

	* ``--command``
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "--{0}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is LongCommand:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class WindowsCommand(CommandArgument, pattern="/{0}"):
	"""
	Represents a command name with a single slash.

	**Example:**

	* ``/command``
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "/{0}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is WindowsCommand:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)
