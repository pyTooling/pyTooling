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
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from typing       import Any

from ..Decorators import export


@export
class CallByRefParam:
	"""
	Implements a *call-by-reference* parameter.

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

	def __ilshift__(self, other: Any) -> 'CallByRefParam':
		"""Assigns a value to the *call-by-reference* object."""
		self.value = other
		return self

	# binary operators - comparison
	def __eq__(self, other: Any) -> bool:
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

	# binary operators - comparison
	def __eq__(self, other: Any) -> bool:
		"""Equality: self = other."""
		if isinstance(other, bool):
			return self.value == other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by equal operator.")

	def __ne__(self, other) -> bool:
		"""Inequality: self != other."""
		if isinstance(other, bool):
			return self.value != other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by unequal operator.")

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
	def __and__(self, other: Any) -> int:
		"""And: self & other."""
		if isinstance(other, int):
			return self.value & other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by and operator.")

	def __or__(self, other: Any) -> int:
		"""Or: self | other."""
		if isinstance(other, int):
			return self.value | other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by or operator.")

	def __xor__(self, other: Any) -> int:
		"""Xor: self ^ other."""
		if isinstance(other, int):
			return self.value ^ other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	# binary inplace operators
	def __iand__(self, other: Any) -> 'CallByRefIntParam':
		"""Inplace and: self &= other."""
		if isinstance(other, int):
			self.value &= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by &= operator.")

	def __ior__(self, other: Any) -> 'CallByRefIntParam':
		"""Inplace or: self |= other."""
		if isinstance(other, int):
			self.value |= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by |= operator.")

	def __ixor__(self, other: Any) -> 'CallByRefIntParam':
		"""Inplace or: self |= other."""
		if isinstance(other, int):
			self.value ^= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by ^= operator.")

	# binary operators - arithmetic
	def __add__(self, other: Any) -> int:
		"""Addition: self + other."""
		if isinstance(other, int):
			return self.value + other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by + operator.")

	def __sub__(self, other: Any) -> int:
		"""Substraction: self - other."""
		if isinstance(other, int):
			return self.value - other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by - operator.")

	def __truediv__(self, other: Any) -> int:
		"""Division: self / other."""
		if isinstance(other, int):
			return self.value / other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by / operator.")

	def __floordiv__(self, other: Any) -> int:
		"""Floor division: self // other."""
		if isinstance(other, int):
			return self.value // other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by // operator.")

	def __mul__(self, other: Any) -> int:
		"""Multiplication: self * other."""
		if isinstance(other, int):
			return self.value * other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by * operator.")

	def __mod__(self, other: Any) -> int:
		"""Modulo: self % other."""
		if isinstance(other, int):
			return self.value % other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by % operator.")

	def __pow__(self, other: Any) -> int:
		"""Power: self ** other."""
		if isinstance(other, int):
			return self.value ** other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by ** operator.")

	# binary inplace operators - arithmetic
	def __iadd__(self, other: Any) -> 'CallByRefIntParam':
		"""Addition: self += other."""
		if isinstance(other, int):
			self.value += other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __isub__(self, other: Any) -> 'CallByRefIntParam':
		"""Substraction: self -= other."""
		if isinstance(other, int):
			self.value -= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __idiv__(self, other: Any) -> 'CallByRefIntParam':
		"""Division: self /= other."""
		if isinstance(other, int):
			self.value /= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __ifloordiv__(self, other: Any) -> 'CallByRefIntParam':
		"""Floor division: self // other."""
		if isinstance(other, int):
			self.value //= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __imul__(self, other: Any) -> 'CallByRefIntParam':
		"""Multiplication: self *= other."""
		if isinstance(other, int):
			self.value *= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __imod__(self, other: Any) -> 'CallByRefIntParam':
		"""Modulo: self %= other."""
		if isinstance(other, int):
			self.value %= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __ipow__(self, other: Any) -> 'CallByRefIntParam':
		"""Power: self **= other."""
		if isinstance(other, int):
			self.value **= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	# binary operators - comparison
	def __eq__(self, other: Any) -> bool:
		"""Equality: self = other."""
		if isinstance(other, int):
			return self.value == other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by equal operator.")

	def __ne__(self, other) -> bool:
		"""Inequality: self != other."""
		if isinstance(other, int):
			return self.value != other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by unequal operator.")

	def __lt__(self, other: Any) -> bool:
		"""Less-than: self < other."""
		if isinstance(other, int):
			return self.value < other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by < operator.")

	def __le__(self, other: Any) -> bool:
		"""Less-equal: self <= other."""
		if isinstance(other, int):
			return self.value <= other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by <= operator.")

	def __gt__(self, other: Any) -> bool:
		"""Greater-than: self > other."""
		if isinstance(other, int):
			return self.value > other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by > operator.")

	def __ge__(self, other: Any) -> bool:
		"""Greater-equal: self >= other."""
		if isinstance(other, int):
			return self.value >= other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by >= operator.")

	# type conversion operators
	def __bool__(self) -> bool:
		"""Type conversion to :class:`bool`."""
		return bool(self.value)

	def __int__(self) -> int:
		"""Type conversion to :class:`int`."""
		return self.value
