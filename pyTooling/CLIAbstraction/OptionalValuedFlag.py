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

.. TODO:: Write module documentation.

"""
from typing import ClassVar, Union, Iterable, Any, Optional as Nullable

try:
	from pyTooling.Decorators              import export
	from pyTooling.CLIAbstraction.Argument import NamedAndValuedArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                      import export
		from CLIAbstraction.Argument         import NamedAndValuedArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


@export
class OptionalValuedFlag(NamedAndValuedArgument, pattern="{0"):
	"""
	Class and base-class for all OptionalValuedFlag classes, which represents a flag argument with data.

	An optional valued flag is a flag name followed by a value. The default delimiter sign is equal (``=``). Name and
	value are passed as one argument to the executable even if the delimiter sign is a whitespace character. If the value
	is None, no delimiter sign and value is passed.

	Example: ``width=100``
	"""
	_patternWithValue: ClassVar[str]

	def __init_subclass__(cls, *args: Any, pattern: str = "{0}", patternWithValue: str = "{0}={1}", **kwargs: Any):
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)
		cls._patternWithValue = patternWithValue

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is OptionalValuedFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)

	def __init__(self, value: Nullable[str] = None) -> None:
		self._value = value

	@property
	def Value(self) -> Nullable[str]:
		"""
		Get the internal value.

		:return: Internal value.
		"""
		return self._value

	@Value.setter
	def Value(self, value: Nullable[str]) -> None:
		"""
		Set the internal value.

		:param value: Value to set.
		"""
		self._value = value

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal name and optional value.

		:return:            Formatted argument.
		:raises ValueError: If internal name is None.
		"""
		if self._name is None:
			raise ValueError(f"Internal value '_name' is None.")

		pattern = self._pattern if self._value is None else self._patternWithValue
		return pattern.format(self._name, self._value)

	def __str__(self) -> str:
		return f"\"{self.AsArgument()}\""

	__repr__ = __str__


@export
class ShortOptionalValuedFlag(OptionalValuedFlag, pattern="-{0}", patternWithValue="-{0}={1}"):
	"""
	Represents a :py:class:`OptionalValuedFlag` with a single dash.

	Example: ``-optimizer=on``
	"""
	def __init_subclass__(cls, *args: Any, pattern: str = "-{0}", patternWithValue: str = "-{0}={1}", **kwargs: Any):
		kwargs["pattern"] = pattern
		kwargs["patternWithValue"] = patternWithValue
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is ShortOptionalValuedFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class LongOptionalValuedFlag(OptionalValuedFlag, pattern="--{0}", patternWithValue="--{0}={1}"):
	"""
	Represents a :py:class:`OptionalValuedFlag` with a double dash.

	Example: ``--optimizer=on``
	"""
	def __init_subclass__(cls, *args: Any, pattern: str = "--{0}", patternWithValue: str = "--{0}={1}", **kwargs: Any):
		kwargs["pattern"] = pattern
		kwargs["patternWithValue"] = patternWithValue
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is LongOptionalValuedFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class WindowsOptionalValuedFlag(OptionalValuedFlag, pattern="/{0}", patternWithValue="/{0}:{1}"):
	"""
	Represents a :py:class:`OptionalValuedFlag` with a single slash.

	Example: ``/optimizer:on``
	"""
	def __init_subclass__(cls, *args: Any, pattern: str = "/{0}", patternWithValue: str = "/{0}:{1}", **kwargs: Any):
		kwargs["pattern"] = pattern
		kwargs["patternWithValue"] = patternWithValue
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is WindowsOptionalValuedFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)
