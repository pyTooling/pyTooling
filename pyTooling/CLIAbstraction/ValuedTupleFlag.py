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
Valued tuple-flag arguments represent a name and a value as a 2-tuple.

.. seealso::

   * For flags with a value. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.ValuedFlag`
   * For flags that have an optional value. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.NamedOptionalValuedFlag`
"""
from typing import Any

try:
	from pyTooling.Decorators              import export
	from pyTooling.CLIAbstraction.Argument import NamedTupledArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                      import export
		from CLIAbstraction.Argument         import NamedTupledArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


@export
class ShortTupleFlag(NamedTupledArgument, pattern="-{0}"):
	"""
	Represents a :class:`ValuedTupleArgument` with a single dash in front of the switch name.

	**Example:**

	* ``-file file1.txt``
	"""
	def __init_subclass__(cls, *args: Any, pattern: str = "-{0}", **kwargs: Any):
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is ShortTupleFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class LongTupleFlag(NamedTupledArgument, pattern="--{0}"):
	"""
	Represents a :class:`ValuedTupleArgument` with a double dash in front of the switch name.

	**Example:**

	* ``--file file1.txt``
	"""
	def __init_subclass__(cls, *args: Any, pattern: str = "--{0}", **kwargs: Any):
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is LongTupleFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class WindowsTupleFlag(NamedTupledArgument, pattern="/{0}"):
	"""
	Represents a :class:`ValuedTupleArgument` with a single slash in front of the switch name.

	**Example:**

	* ``/file file1.txt``
	"""
	def __init_subclass__(cls, *args: Any, pattern: str = "/{0}", **kwargs: Any):
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is WindowsTupleFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)
