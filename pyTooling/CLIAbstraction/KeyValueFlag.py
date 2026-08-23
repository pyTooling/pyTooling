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
   :class:`~pyTooling.CLIAbstraction.OptionalValuedFlag.OptionalValuedFlag`
      |rarr| For flags that have an optional value.
"""
from typing                            import Union, Iterable, cast, Any, Optional as Nullable
from pyTooling.Decorators              import export
from pyTooling.MetaClasses             import abstractclass
from pyTooling.Common                  import getFullyQualifiedName
from pyTooling.CLIAbstraction.Argument import NamedAndValuedArgument


@export
@abstractclass
class NamedKeyValuePairsArgument(NamedAndValuedArgument[str], pattern="{0}{1}={2}"):
	"""
	Class and base-class for all KeyValueFlag classes, which represents a flag argument with key and value
	(key-value-pairs).

	An optional valued flag is a flag name followed by a value. The default delimiter sign is equal (``=``). Name and
	value are passed as one argument to the executable even if the delimiter sign is a whitespace character. If the value
	is None, no delimiter sign and value is passed.

	**Example:**

	* ``-gWidth=100``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "{0}{1}={2}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param name:    Optional, name of the CLI argument.
		:param pattern: Optional, this pattern is used to format an argument. |br|
		                Default: ``"{0}{1}={2}"``.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __init__(self, keyValuePairs: dict[str, str]) -> None:
		"""
		Initialize the argument with a mapping of key-value-pairs, each rendered as its own command line element.

		:param keyValuePairs: Key-value-pairs of the argument.
		:raises TypeError:    If a key or a value is not a string.
		"""
		super().__init__({})

		for key, value in keyValuePairs.items():
			if not isinstance(key, str):
				ex = TypeError("Parameter 'keyValuePairs' contains a pair, where the key is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
				raise ex
			elif not isinstance(value, str):
				ex = TypeError("Parameter 'keyValuePairs' contains a pair, where the value is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

			self._value[key] = value

	@property
	def Value(self) -> dict[str, str]:
		"""
		Property to access the internal key-value-pairs (:attr:`_value`).

		.. note:: On assignment, the dictionary object is not replaced, but cleared and then reused by adding the given
		   pairs.

		:returns:          Internal dictionary of key-value-pairs.
		:raises TypeError: If an assigned pair has a key or a value which is not of type string.
		"""
		return self._value

	@Value.setter
	def Value(self, keyValuePairs: dict[str, str]) -> None:
		innerDict = cast(dict[str, str], self._value)
		innerDict.clear()
		for key, value in keyValuePairs.items():
			if not isinstance(key, str):
				ex = TypeError("Parameter 'keyValuePairs' contains a pair, where the key is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
				raise ex
			elif not isinstance(value, str):
				ex = TypeError("Parameter 'keyValuePairs' contains a pair, where the value is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

			innerDict[key] = value

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal name.

		:returns:           Formatted argument.
		:raises ValueError: If internal name is None.
		"""
		if self._name is None:
			raise ValueError("Internal value '_name' is None.")

		return [self._pattern.format(self._name, key, value) for key, value in self._value.items()]


@export
@abstractclass
class ShortKeyValueFlag(NamedKeyValuePairsArgument, pattern="-{0}{1}={2}"):
	"""
	Represents a :py:class:`NamedKeyValueFlagArgument` with a single dash in front of the switch name.

	**Example:**

	* ``-DDEBUG=TRUE``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "-{0}{1}={2}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param name:    Optional, name of the CLI argument.
		:param pattern: Optional, this pattern is used to format an argument. |br|
		                Default: ``"-{0}{1}={2}"``.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)


@export
@abstractclass
class LongKeyValueFlag(NamedKeyValuePairsArgument, pattern="--{0}{1}={2}"):
	"""
	Represents a :py:class:`NamedKeyValueFlagArgument` with a double dash in front of the switch name.

	**Example:**

	* ``--DDEBUG=TRUE``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "--{0}{1}={2}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param name:    Optional, name of the CLI argument.
		:param pattern: Optional, this pattern is used to format an argument. |br|
		                Default: ``"--{0}{1}={2}"``.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)


@export
@abstractclass
class WindowsKeyValueFlag(NamedKeyValuePairsArgument, pattern="/{0}:{1}={2}"):
	"""
	Represents a :py:class:`NamedKeyValueFlagArgument` with a double dash in front of the switch name.

	**Example:**

	* ``--DDEBUG=TRUE``
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "/{0}:{1}={2}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param name:    Optional, name of the CLI argument.
		:param pattern: Optional, this pattern is used to format an argument. |br|
		                Default: ``"/{0}:{1}={2}"``.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)
