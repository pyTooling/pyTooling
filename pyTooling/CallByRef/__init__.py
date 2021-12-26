# ==================================================================================================================== #
#             _____           _ _               ____      _ _ ____        ____       __                                #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _| | | __ ) _   _|  _ \ ___ / _|                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | | |  _ \| | | | |_) / _ \ |_                                #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | | | |_) | |_| |  _ <  __/  _|                               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|_|____/ \__, |_| \_\___|_|                                 #
# |_|    |___/                          |___/                       |___/                                              #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2021 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Auxiliary classes to implement call by reference."""
from ..Decorators import export


@export
class CallByRefParam:
	"""Implements a *call-by-reference* parameter.

	.. seealso::

	   :py:class:`CallByRefBoolParam`
	     A special *call-by-reference* implementation for boolean reference types.
	   :py:class:`CallByRefIntParam`
	     A special *call-by-reference* implementation for integer reference types.
	"""

	value = None    #: internal value

	def __init__(self, value=None) -> None:
		"""Constructs a *call-by-reference* object for any type."""
		self.value = value

	def __ilshift__(self, other):
		"""Assigns a value to the *call-by-reference* object."""
		self.value = other
		return self

	# binary operators - comparison
	def __eq__(self, other) -> bool:
		"""Equality: self = other."""
		return self.value == other

	def __ne__(self, other) -> bool:
		"""Inequality: self != other."""
		return self.value != other

	# type conversion operators
	def __repr__(self) -> str:
		"""Returns the wrapped object's string representation."""
		return repr(self.value)

	def __str__(self) -> str:
		"""Returns the wrapped object's string equivalent."""
		return str(self.value)


@export
class CallByRefBoolParam(CallByRefParam):
	"""A special *call-by-reference* implementation for boolean reference types."""

	# type conversion operators
	def __bool__(self) -> bool:
		"""Type conversion to :class:`bool`."""
		return self.value

	def __int__(self) -> int:
		"""Type conversion to :class:`int`."""
		return int(self.value)


@export
class CallByRefIntParam(CallByRefParam):
	"""A special *call-by-reference* implementation for integer reference types."""

	# unary operators
	def __neg__(self) -> int:
		"""Negate: -self."""
		return -self.value

	def __pos__(self) -> int:
		"""Positive: +self."""
		return +self.value

	def __invert__(self) -> int:
		"""Invert: ~self."""
		return ~self.value

	# binary operators - logical
	def __and__(self, other) -> int:
		"""And: self & other."""
		return self.value & other

	def __or__(self, other) -> int:
		"""Or: self | other."""
		return self.value | other

	def __xor__(self, other) -> int:
		"""Xor: self ^ other."""
		return self.value ^ other

	# binary inplace operators
	def __iand__(self, other) -> 'CallByRefIntParam':
		"""Inplace and: self &= other."""
		self.value &= other
		return self

	def __ior__(self, other) -> 'CallByRefIntParam':
		"""Inplace or: self |= other."""
		self.value |= other
		return self

	def __ixor__(self, other) -> 'CallByRefIntParam':
		"""Inplace or: self |= other."""
		self.value ^= other
		return self

	# binary operators - arithmetic
	def __add__(self, other) -> int:
		"""Addition: self + other."""
		return self.value + other

	def __sub__(self, other) -> int:
		"""Substraction: self - other."""
		return self.value - other

	def __truediv__(self, other) -> int:
		"""Division: self / other."""
		return self.value / other

	def __floordiv__(self, other) -> int:
		"""Floor division: self // other."""
		return self.value // other

	def __mul__(self, other) -> int:
		"""Multiplication: self * other."""
		return self.value * other

	def __mod__(self, other) -> int:
		"""Modulo: self % other."""
		return self.value % other

	def __pow__(self, other) -> int:
		"""Power: self ** other."""
		return self.value ** other

	# binary inplace operators - arithmetic
	def __iadd__(self, other) -> 'CallByRefIntParam':
		"""Addition: self += other."""
		self.value += other
		return self

	def __isub__(self, other) -> 'CallByRefIntParam':
		"""Substraction: self -= other."""
		self.value -= other
		return self

	def __idiv__(self, other) -> 'CallByRefIntParam':
		"""Division: self /= other."""
		self.value /= other
		return self

	def __ifloordiv__(self, other) -> 'CallByRefIntParam':
		"""Floor division: self // other."""
		self.value //= other
		return self

	def __imul__(self, other) -> 'CallByRefIntParam':
		"""Multiplication: self *= other."""
		self.value *= other
		return self

	def __imod__(self, other) -> 'CallByRefIntParam':
		"""Modulo: self %= other."""
		self.value %= other
		return self

	def __ipow__(self, other) -> 'CallByRefIntParam':
		"""Power: self **= other."""
		self.value **= other
		return self

	# binary operators - comparison
	def __lt__(self, other) -> bool:
		"""Less-than: self < other."""
		return self.value < other

	def __le__(self, other) -> bool:
		"""Less-equal: self <= other."""
		return self.value <= other

	def __gt__(self, other) -> bool:
		"""Greater-than: self > other."""
		return self.value > other

	def __ge__(self, other) -> bool:
		"""Greater-equal: self >= other."""
		return self.value >= other

	# type conversion operators
	def __bool__(self) -> bool:
		"""Type conversion to :class:`bool`."""
		return bool(self.value)

	def __int__(self) -> int:
		"""Type conversion to :class:`int`."""
		return self.value
