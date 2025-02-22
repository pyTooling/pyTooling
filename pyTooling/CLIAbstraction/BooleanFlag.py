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
Boolean flags are arguments with a name and different pattern for a positive (``True``) and negative (``False``) value.

.. seealso::

   * For simple flags. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.Flag`
   * For flags with a value. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.ValuedFlag`
   * For flags that have an optional value. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.NamedOptionalValuedFlag`
"""
from typing import ClassVar, Union, Iterable, Any, Optional as Nullable

try:
	from pyTooling.Decorators              import export
	from pyTooling.CLIAbstraction.Argument import NamedArgument, ValuedArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                      import export
		from CLIAbstraction.Argument         import NamedArgument, ValuedArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


@export
class BooleanFlag(NamedArgument, ValuedArgument):
	"""
	Class and base-class for all BooleanFlag classes, which represents a flag argument with different pattern for an
	enabled/positive (``True``) or disabled/negative (``False``) state.

	When deriving a subclass from an abstract BooleanFlag class, the parameters ``pattern`` and ``falsePattern`` are
	expected.

	**Example:**

	* True: ``with-checks``
	* False: ``without-checks``
	"""

	_falsePattern: ClassVar[str]

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "with-{0}", falsePattern: str = "without-{0}", **kwargs: Any):
		"""This method is called when a class is derived.

		:param args: Any positional arguments.
		:param pattern: This pattern is used to format an argument when the value is ``True``.
		:param falsePattern: This pattern is used to format an argument when the value is ``False``.
		:param kwargs: Any keyword argument.
		"""
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)
		del kwargs["name"]
		del kwargs["pattern"]
		ValuedArgument.__init_subclass__(*args, **kwargs)

		cls._falsePattern = falsePattern

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is BooleanFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)

	def __init__(self, value: bool) -> None:
		"""Initializes a BooleanFlag instance.

		:param value: Initial value set for this argument instance.
		"""
		ValuedArgument.__init__(self, value)

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""Convert this argument instance to a string representation with proper escaping using the matching pattern based
		on the internal name and value.

		:return: Formatted argument.
		:raises ValueError: If internal name is None.
		"""
		if self._name is None:
			raise ValueError(f"Internal value '_name' is None.")

		pattern = self._pattern if self._value is True else self._falsePattern
		return pattern.format(self._name)


@export
class ShortBooleanFlag(BooleanFlag, pattern="-with-{0}", falsePattern="-without-{0}"):
	"""Represents a :py:class:`BooleanFlag` with a single dash.

	**Example:**

	* True: ``-with-checks``
	* False: ``-without-checks``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "-with-{0}", falsePattern: str = "-without-{0}", **kwargs: Any):
		"""This method is called when a class is derived.

		:param args: Any positional arguments.
		:param pattern: This pattern is used to format an argument when the value is ``True``.
		:param falsePattern: This pattern is used to format an argument when the value is ``False``.
		:param kwargs: Any keyword argument.
		"""
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		kwargs["falsePattern"] = falsePattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is ShortBooleanFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class LongBooleanFlag(BooleanFlag, pattern="--with-{0}", falsePattern="--without-{0}"):
	"""Represents a :py:class:`BooleanFlag` with a double dash.

	**Example:**

	* True: ``--with-checks``
	* False: ``--without-checks``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "--with-{0}", falsePattern: str = "--without-{0}", **kwargs: Any):
		"""This method is called when a class is derived.

		:param args: Any positional arguments.
		:param pattern: This pattern is used to format an argument when the value is ``True``.
		:param falsePattern: This pattern is used to format an argument when the value is ``False``.
		:param kwargs: Any keyword argument.
		"""
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		kwargs["falsePattern"] = falsePattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is LongBooleanFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class WindowsBooleanFlag(BooleanFlag, pattern="/with-{0}", falsePattern="/without-{0}"):
	"""Represents a :py:class:`BooleanFlag` with a slash.

	**Example:**

	* True: ``/with-checks``
	* False: ``/without-checks``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "/with-{0}", falsePattern: str = "/without-{0}", **kwargs: Any):
		"""This method is called when a class is derived.

		:param args: Any positional arguments.
		:param pattern: This pattern is used to format an argument when the value is ``True``.
		:param falsePattern: This pattern is used to format an argument when the value is ``False``.
		:param kwargs: Any keyword argument.
		"""
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		kwargs["falsePattern"] = falsePattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is WindowsBooleanFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)
