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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""
Attributes describing options carrying key-value-pairs, like ``-Dkey=value``.

The pairs are collected into a dictionary and passed to the handler method as one parameter.
"""
from argparse                               import Action, ArgumentError, ArgumentParser, Namespace
from typing                                 import Any, Optional as Nullable, Sequence, Union

from pyTooling.Decorators                   import export
from pyTooling.Attributes.ArgParse.Argument import NamedAndValuedArgument


@export
class KeyValuePairsAction(Action):
	"""
	An :mod:`argparse` action collecting ``key=value`` pairs into a dictionary.

	Every occurrence of the option adds one pair; a later value of the same key replaces the earlier one. A key without
	``=`` (``-Dflag``) has the value ``None``. The dictionary is created on the first occurrence, so the option's
	default is never modified.
	"""

	def __call__(
		self,
		parser:        ArgumentParser,
		namespace:     Namespace,
		values:        Union[str, Sequence[Any], None],
		option_string: Nullable[str] = None
	) -> None:
		"""
		Add the pair given with one occurrence of the option.

		:param parser:         The parser running the action.
		:param namespace:      The namespace collecting the parsed arguments.
		:param values:         The option's value, ``key=value`` or ``key``.
		:param option_string:  The option string the value was given with, e.g. ``-D``.
		:raises ArgumentError: When the key is empty (``-D=value``).
		"""
		key, separator, value = str(values).partition("=")
		if key == "":
			raise ArgumentError(self, f"expected KEY=VALUE, got '{values}'")

		pairs = dict(getattr(namespace, self.dest) or {})
		pairs[key] = value if separator == "=" else None
		setattr(namespace, self.dest, pairs)


@export
class NamedKeyValuePairsArgument(NamedAndValuedArgument):
	"""
	Defines a key-value argument like ``-Dkey=value``.

	Some of the named parameters passed to :meth:`~argparse.ArgumentParser.add_argument` are predefined (or overwritten),
	so every occurrence of the option adds a ``key=value`` pair to a dictionary, which is passed to the registered
	handler method. The dictionary is ``None``, if the option isn't given.
	"""

	def __init__(
		self,
		short:    Nullable[str] = None,
		long:     Nullable[str] = None,
		dest:     Nullable[str] = None,
		metaName: str = "KEY=VALUE",
		help:     Nullable[str] = None
	) -> None:
		"""
		Initializes a key-value argument.

		.. admonition:: ArgParse parameterization

		   :meth:`~argparse.ArgumentParser.add_argument` is called with the option strings from ``short`` and ``long``
		   as positional parameters, and with these named parameters:

		   * ``dest=dest``
		   * ``action=KeyValuePairsAction``
		   * ``metavar=metaName``
		   * ``default=None``
		   * ``help=help``

		   :class:`KeyValuePairsAction` adds each ``key=value`` to a dictionary: ``-DA=1 -D B=2`` (or
		   ``--define A=1 --define=B=2``) passes ``{"A": "1", "B": "2"}`` to the handler method.

		:param short:    Optional, short option name including the dash, e.g. ``"-D"``. Default: ``None``.
		:param long:     Optional, long option name including the dashes, e.g. ``"--define"``. Default: ``None``.
		:param dest:     Optional, name the parsed dictionary is stored under in the :class:`~argparse.Namespace`, and
		                 the name the handler method reads it by.
		:param metaName: Optional, name shown for the value in the help page (``metavar``). Default: ``"KEY=VALUE"``.
		:param help:     Optional, help text shown for this argument in the help page. Default: ``None``.
		"""
		args = []
		if short is not None:
			args.append(short)

		if long is not None:
			args.append(long)

		kwargs = {
			"dest":    dest,
			"action":  KeyValuePairsAction,
			"metavar": metaName,
			"default": None,
			"help":    help,
		}
		super().__init__(*args, **kwargs)


@export
class ShortKeyValueFlag(NamedKeyValuePairsArgument):
	"""Defines a key-value argument in short form like ``-Dkey=value``."""

	def __init__(
		self,
		short:    Nullable[str] = None,
		dest:     Nullable[str] = None,
		metaName: str = "KEY=VALUE",
		help:     Nullable[str] = None
	) -> None:
		"""
		Initialize a key-value argument in its short form.

		:param short:    Optional, short form of the option, including its dash, e.g. :pycode:`short="-D"`.
		:param dest:     Optional, name of the parameter the parsed dictionary is passed to the handler method as.
		:param metaName: Optional, name of the value in the help page. Default: ``"KEY=VALUE"``.
		:param help:     Optional, help text of the option, displayed in the help page.
		"""
		super().__init__(short=short, dest=dest, metaName=metaName, help=help)


@export
class LongKeyValueFlag(NamedKeyValuePairsArgument):
	"""Defines a key-value argument in long form like ``--define key=value``."""

	def __init__(
		self,
		long:     Nullable[str] = None,
		dest:     Nullable[str] = None,
		metaName: str = "KEY=VALUE",
		help:     Nullable[str] = None
	) -> None:
		"""
		Initialize a key-value argument in its long form.

		:param long:     Optional, long form of the option, including its dashes, e.g. :pycode:`long="--define"`.
		:param dest:     Optional, name of the parameter the parsed dictionary is passed to the handler method as.
		:param metaName: Optional, name of the value in the help page. Default: ``"KEY=VALUE"``.
		:param help:     Optional, help text of the option, displayed in the help page.
		"""
		super().__init__(long=long, dest=dest, metaName=metaName, help=help)
