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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Flag arguments represent simple boolean values by being present or absent.

.. seealso::

   :mod:`~pyTooling.CLIAbstraction.BooleanFlag`
      |rarr| For flags with a different pattern based on the boolean value itself.
   :mod:`~pyTooling.CLIAbstraction.ValuedFlag`
      |rarr| For flags with a value.
   :mod:`~pyTooling.CLIAbstraction.NamedOptionalValuedFlag`
      |rarr| For flags that have an optional value.
"""
from typing import Any

from pyTooling.Decorators              import export
from pyTooling.MetaClasses             import abstractclass
from pyTooling.CLIAbstraction.Argument import NamedArgument


@export
@abstractclass
class FlagArgument(NamedArgument):
	"""
	Base-class for all Flag classes, which represents a simple flag argument like ``-v`` or ``--verbose``.

	A simple flag is a single value (absent/present or off/on) with no additional data (value).
	"""


@export
@abstractclass
class ShortFlag(FlagArgument, pattern="-{0}"):
	"""
	Represents a :class:`~pyTooling.CLIAbstraction.Flag.Flag` argument with a single dash.

	**Example:**

	* ``-optimize``
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "-{0}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument. |br|
		                Default: ``"-{0}"``.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)


@export
@abstractclass
class LongFlag(FlagArgument, pattern="--{0}"):
	"""
	Represents a :class:`~pyTooling.CLIAbstraction.Flag.Flag` argument with a double dash.

	**Example:**

	* ``--optimize``
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "--{0}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument. |br|
		                Default: ``"--{0}"``.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)


@export
@abstractclass
class WindowsFlag(FlagArgument, pattern="/{0}"):
	"""
	Represents a :class:`~pyTooling.CLIAbstraction.Flag.Flag` argument with a single slash.

	**Example:**

	* ``/optimize``
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "/{0}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument. |br|
		                Default: ``"/{0}"``.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)
