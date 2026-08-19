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

Command line arguments with an optional value, like ``--width`` or ``--width=100``.

The argument renders one of two patterns: the one with a value when a value was assigned, and the one without a value
otherwise - which is why an optional-valued flag carries two format strings instead of one.

"""
from typing import ClassVar, Union, Iterable, Any, Optional as Nullable

from pyTooling.Decorators              import export
from pyTooling.MetaClasses             import abstractclass
from pyTooling.CLIAbstraction.Argument import NamedAndValuedArgument


@export
@abstractclass
class OptionalValuedFlag(NamedAndValuedArgument, pattern="{0"):
	"""
	Class and base-class for all OptionalValuedFlag classes, which represents a flag argument with data.

	An optional valued flag is a flag name followed by a value. The default delimiter sign is equal (``=``). Name and
	value are passed as one argument to the executable even if the delimiter sign is a whitespace character. If the value
	is None, no delimiter sign and value is passed.

	Example: ``width=100``
	"""
	_patternWithValue: ClassVar[str]  #: Format string used when the flag has a value; :attr:`_pattern` is used without one.

	def __init_subclass__(cls, *args: Any, pattern: str = "{0}", patternWithValue: str = "{0}={1}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:             Any positional arguments.
		:param pattern:          Optional, this pattern is used to format an argument without a value. |br|
		                         Default: ``"{0}"``.
		:param patternWithValue: Optional, this pattern is used to format an argument with a value. |br|
		                         Default: ``"{0}={1}"``.
		:param kwargs:           Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)
		cls._patternWithValue = patternWithValue

	def __init__(self, value: Nullable[str] = None) -> None:
		"""
		Initialize the flag, optionally with a value.

		:param value: Optional, value of the flag, or ``None`` to render the flag without a value.
		"""
		self._value = value

	@property
	def Value(self) -> Nullable[str]:
		"""
		Property to access the internal value (:attr:`_value`).

		:returns: Internal value, or ``None`` if the flag is used without a value.
		"""
		return self._value

	@Value.setter
	def Value(self, value: Nullable[str]) -> None:
		self._value = value

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal name and optional value.

		:returns:           Formatted argument.
		:raises ValueError: If internal name is None.
		"""
		if self._name is None:
			raise ValueError(f"Internal value '_name' is None.")

		pattern = self._pattern if self._value is None else self._patternWithValue
		return pattern.format(self._name, self._value)

	def __str__(self) -> str:
		"""
		Return the argument as a quoted string, ready to be pasted into a shell.

		:returns: The rendered argument, in double quotes.
		"""
		return f"\"{self.AsArgument()}\""

	__repr__ = __str__


@export
@abstractclass
class ShortOptionalValuedFlag(OptionalValuedFlag, pattern="-{0}", patternWithValue="-{0}={1}"):
	"""
	Represents a :py:class:`OptionalValuedFlag` with a single dash.

	Example: ``-optimizer=on``
	"""
	def __init_subclass__(cls, *args: Any, pattern: str = "-{0}", patternWithValue: str = "-{0}={1}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:             Any positional arguments.
		:param pattern:          Optional, this pattern is used to format an argument without a value. |br|
		                         Default: ``"-{0}"``.
		:param patternWithValue: Optional, this pattern is used to format an argument with a value. |br|
		                         Default: ``"-{0}={1}"``.
		:param kwargs:           Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		kwargs["patternWithValue"] = patternWithValue
		super().__init_subclass__(*args, **kwargs)


@export
@abstractclass
class LongOptionalValuedFlag(OptionalValuedFlag, pattern="--{0}", patternWithValue="--{0}={1}"):
	"""
	Represents a :py:class:`OptionalValuedFlag` with a double dash.

	Example: ``--optimizer=on``
	"""
	def __init_subclass__(cls, *args: Any, pattern: str = "--{0}", patternWithValue: str = "--{0}={1}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:             Any positional arguments.
		:param pattern:          Optional, this pattern is used to format an argument without a value. |br|
		                         Default: ``"--{0}"``.
		:param patternWithValue: Optional, this pattern is used to format an argument with a value. |br|
		                         Default: ``"--{0}={1}"``.
		:param kwargs:           Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		kwargs["patternWithValue"] = patternWithValue
		super().__init_subclass__(*args, **kwargs)


@export
@abstractclass
class WindowsOptionalValuedFlag(OptionalValuedFlag, pattern="/{0}", patternWithValue="/{0}:{1}"):
	"""
	Represents a :py:class:`OptionalValuedFlag` with a single slash.

	Example: ``/optimizer:on``
	"""
	def __init_subclass__(cls, *args: Any, pattern: str = "/{0}", patternWithValue: str = "/{0}:{1}", **kwargs: Any) -> None:
		"""
		This method is called when a class is derived.

		:param args:             Any positional arguments.
		:param pattern:          Optional, this pattern is used to format an argument without a value. |br|
		                         Default: ``"/{0}"``.
		:param patternWithValue: Optional, this pattern is used to format an argument with a value. |br|
		                         Default: ``"/{0}:{1}"``.
		:param kwargs:           Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		kwargs["patternWithValue"] = patternWithValue
		super().__init_subclass__(*args, **kwargs)
