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
Flag arguments represent simple boolean values by being present or absent.

.. seealso::

   * For flags with different pattern based on the boolean value itself. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.BooleanFlag`
   * For flags with a value. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.ValuedFlag`
   * For flags that have an optional value. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.NamedOptionalValuedFlag`
"""
from sys    import version_info           # needed for versions before Python 3.11
from typing import Union, Iterable, Dict, cast, Any, Optional as Nullable

try:
	from pyTooling.Decorators              import export
	from pyTooling.Common                  import getFullyQualifiedName
	from pyTooling.CLIAbstraction.Argument import NamedAndValuedArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                      import export
		from Common                          import getFullyQualifiedName
		from CLIAbstraction.Argument         import NamedAndValuedArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


@export
class NamedKeyValuePairsArgument(NamedAndValuedArgument, pattern="{0}{1}={2}"):
	"""
	Class and base-class for all KeyValueFlag classes, which represents a flag argument with key and value
	(key-value-pairs).

	An optional valued flag is a flag name followed by a value. The default delimiter sign is equal (``=``). Name and
	value are passed as one argument to the executable even if the delimiter sign is a whitespace character. If the value
	is None, no delimiter sign and value is passed.

	**Example:**

	* ``-gWidth=100``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "{0}{1}={2}", **kwargs: Any):
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is NamedKeyValuePairsArgument:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)

	def __init__(self, keyValuePairs: Dict[str, str]) -> None:
		super().__init__({})

		for key, value in keyValuePairs.items():
			if not isinstance(key, str):
				ex = TypeError(f"Parameter 'keyValuePairs' contains a pair, where the key is not of type 'str'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
				raise ex
			elif not isinstance(value, str):
				ex = TypeError(f"Parameter 'keyValuePairs' contains a pair, where the value is not of type 'str'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

			self._value[key] = value

	@property
	def Value(self) -> Dict[str, str]:
		"""
		Get the internal value.

		:return: Internal value.
		"""
		return self._value

	@Value.setter
	def Value(self, keyValuePairs: Dict[str, str]) -> None:
		"""
		Set the internal value.

		:param keyValuePairs: Value to set.
		:raises ValueError:   If value to set is None.
		"""
		innerDict = cast(Dict[str, str], self._value)
		innerDict.clear()
		for key, value in keyValuePairs.items():
			if not isinstance(key, str):
				ex = TypeError(f"Parameter 'keyValuePairs' contains a pair, where the key is not of type 'str'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
				raise ex
			elif not isinstance(value, str):
				ex = TypeError(f"Parameter 'keyValuePairs' contains a pair, where the value is not of type 'str'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

			innerDict[key] = value

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal name.

		:return:            Formatted argument.
		:raises ValueError: If internal name is None.
		"""
		if self._name is None:
			raise ValueError(f"Internal value '_name' is None.")

		return [self._pattern.format(self._name, key, value) for key, value in self._value.items()]


@export
class ShortKeyValueFlag(NamedKeyValuePairsArgument, pattern="-{0}{1}={2}"):
	"""
	Represents a :py:class:`NamedKeyValueFlagArgument` with a single dash in front of the switch name.

	**Example:**

	* ``-DDEBUG=TRUE``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "-{0}{1}={2}", **kwargs: Any):
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is ShortKeyValueFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class LongKeyValueFlag(NamedKeyValuePairsArgument, pattern="--{0}{1}={2}"):
	"""
	Represents a :py:class:`NamedKeyValueFlagArgument` with a double dash in front of the switch name.

	**Example:**

	* ``--DDEBUG=TRUE``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "--{0}{1}={2}", **kwargs: Any):
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is LongKeyValueFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class WindowsKeyValueFlag(NamedKeyValuePairsArgument, pattern="/{0}:{1}={2}"):
	"""
	Represents a :py:class:`NamedKeyValueFlagArgument` with a double dash in front of the switch name.

	**Example:**

	* ``--DDEBUG=TRUE``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "/{0}:{1}={2}", **kwargs: Any):
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is LongKeyValueFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)
