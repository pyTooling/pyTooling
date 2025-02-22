# ==================================================================================================================== #
#            _   _   _        _ _           _                 _              ____                                      #
#           / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___     / \   _ __ __ _|  _ \ __ _ _ __ ___  ___                  #
#          / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|   / _ \ | '__/ _` | |_) / _` | '__/ __|/ _ \                 #
#   _ _ _ / ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \_ / ___ \| | | (_| |  __/ (_| | |  \__ \  __/                 #
#  (_|_|_)_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___(_)_/   \_\_|  \__, |_|   \__,_|_|  |___/\___|                 #
#                                                                      |___/                                           #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany                                                               #
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
from pathlib import Path
from typing import Type

try:
	from pyTooling.Decorators          import export
	from pyTooling.Attributes.ArgParse import CommandLineArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Attributes.ArgParse.Argument] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                  import export
		from Attributes.ArgParse         import CommandLineArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Attributes.ArgParse.Argument] Could not import directly!")
		raise ex


@export
class DelimiterArgument(CommandLineArgument):
	"""
	Represents a delimiter symbol like ``--``.
	"""


@export
class NamedArgument(CommandLineArgument):
	"""
	Base-class for all command line arguments with a name.
	"""


@export
class ValuedArgument(CommandLineArgument):
	"""
	Base-class for all command line arguments with a value.
	"""


class NamedAndValuedArgument(NamedArgument, ValuedArgument):
	"""
	Base-class for all command line arguments with a name and a value.
	"""


class NamedTupledArgument(NamedArgument, ValuedArgument):
	"""
	Class and base-class for all TupleFlag classes, which represents an argument with separate value.

	A tuple argument is a command line argument followed by a separate value. Name and value are passed as two arguments
	to the executable.

	**Example: **

	* `width 100``
	"""


@export
class PositionalArgument(ValuedArgument):
	"""
	Represents a simple string argument containing any information encoded in a string.

	TODO

	A list of strings is available as :class:`~pyTooling.Attribute.ArgParse.Argument.StringListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, type: Type = str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		args = []
		kwargs = {
			"dest":    dest,
			"metavar": metaName,
			"type":    type,
			"help":    help
		}
		if optional:
			kwargs["nargs"] = "?"

		super().__init__(*args, **kwargs)


@export
class StringArgument(PositionalArgument):
	"""
	Represents a simple string argument.

	A list of strings is available as :class:`~pyTooling.Attribute.ArgParse.Argument.StringListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, str, optional, help)


@export
class IntegerArgument(PositionalArgument):
	"""
	Represents an integer argument.

	A list of strings is available as :class:`~pyTooling.Attribute.ArgParse.Argument.StringListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, int, optional, help)


@export
class FloatArgument(PositionalArgument):
	"""
	Represents a floating point number argument.

	A list of strings is available as :class:`~pyTooling.Attribute.ArgParse.Argument.StringListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, float, optional, help)


# TODO: Add option to class if path should be checked for existence
@export
class PathArgument(PositionalArgument):
	"""
	Represents a single path argument.

	A list of paths is available as :class:`~pyTooling.Attribute.ArgParse.Argument.PathListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, Path, optional, help)


@export
class ListArgument(ValuedArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`).
	"""

	def __init__(self, dest: str, metaName: str, type: Type = str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		args = []
		kwargs = {
			"dest":    dest,
			"metavar": metaName,
			"nargs":   "*" if optional else "+",
			"type":    type,
			"help":    help
		}
		super().__init__(*args, **kwargs)


@export
class StringListArgument(ListArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`).
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, str, optional, help)


@export
class IntegerListArgument(ListArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`).
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, int, optional, help)


@export
class FloatListArgument(ListArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`).
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, float, optional, help)


@export
class PathListArgument(ListArgument):
	"""
	Represents a list of path arguments  (:class:`~pyTooling.Attribute.ArgParse.Argument.PathArgument`).
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, Path, optional, help)
