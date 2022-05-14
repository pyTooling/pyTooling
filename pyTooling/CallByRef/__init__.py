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
"""
Auxiliary classes to implement call-by-reference.

.. hint:: See :ref:`high-level help <COMMON/CallByRef>` for explanations and usage examples.
"""
from typing import Any, Generic, TypeVar

from ..Decorators import export
from ..MetaClasses import ExtendedType

T = TypeVar("T")


@export
class CallByRefParam(Generic[T], metaclass=ExtendedType, useSlots=True):
	"""
	Implements a *call-by-reference* parameter.

	.. seealso::

	   * :py:class:`CallByRefBoolParam` |br|
	     |rarr| A special *call-by-reference* implementation for boolean reference types.
	   * :py:class:`CallByRefIntParam` |br|
	     |rarr| A special *call-by-reference* implementation for integer reference types.
	"""

	Value: T    #: internal value

	def __init__(self, value: T = None):
		"""Constructs a *call-by-reference* object for any type.

		:param value: The value to be set as an initial value.
		"""
		self.Value = value

	def __ilshift__(self, other: T) -> 'CallByRefParam[T]':
		"""Assigns a value to the *call-by-reference* object.

		:param other: The value to be assigned to this *call-by-reference* object.
		:returns: Itself.
		"""
		self.Value = other
		return self

	# binary operators - comparison
	def __eq__(self, other: Any) -> bool:
		"""Equality: self == other."""
		return self.Value == other

	def __ne__(self, other) -> bool:
		"""Inequality: self != other."""
		return self.Value != other

	# Type conversion operators
	def __repr__(self) -> str:
		"""Returns the wrapped object's string representation."""
		return repr(self.Value)

	def __str__(self) -> str:
		"""Returns the wrapped object's string equivalent."""
		return str(self.Value)


@export
class CallByRefBoolParam(CallByRefParam):
	"""A special *call-by-reference* implementation for boolean reference types."""

	# Binary operators - comparison
	def __eq__(self, other: Any) -> bool:
		"""Equality: self == other."""
		if isinstance(other, bool):
			return self.Value == other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by == operator.")

	def __ne__(self, other) -> bool:
		"""Inequality: self != other."""
		if isinstance(other, bool):
			return self.Value != other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by != operator.")

	# Type conversion operators
	def __bool__(self) -> bool:
		"""Type conversion to :class:`bool`."""
		return self.Value

	def __int__(self) -> int:
		"""Type conversion to :class:`int`."""
		return int(self.Value)


@export
class CallByRefIntParam(CallByRefParam):
	"""A special *call-by-reference* implementation for integer reference types."""

	# Unary operators
	def __neg__(self) -> int:
		"""Negate: -self."""
		return -self.Value

	def __pos__(self) -> int:
		"""Positive: +self."""
		return +self.Value

	def __invert__(self) -> int:
		"""Invert: ~self."""
		return ~self.Value

	# Binary operators - logical
	def __and__(self, other: Any) -> int:
		"""And: self & other."""
		if isinstance(other, int):
			return self.Value & other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by and operator.")

	def __or__(self, other: Any) -> int:
		"""Or: self | other."""
		if isinstance(other, int):
			return self.Value | other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by or operator.")

	def __xor__(self, other: Any) -> int:
		"""Xor: self ^ other."""
		if isinstance(other, int):
			return self.Value ^ other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	# Binary inplace operators
	def __iand__(self, other: Any) -> 'CallByRefIntParam':
		"""Inplace and: self &= other."""
		if isinstance(other, int):
			self.Value &= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by &= operator.")

	def __ior__(self, other: Any) -> 'CallByRefIntParam':
		r"""Inplace or: self \|= other."""
		if isinstance(other, int):
			self.Value |= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by |= operator.")

	def __ixor__(self, other: Any) -> 'CallByRefIntParam':
		r"""Inplace or: self \|= other."""
		if isinstance(other, int):
			self.Value ^= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by ^= operator.")

	# Binary operators - arithmetic
	def __add__(self, other: Any) -> int:
		"""Addition: self + other."""
		if isinstance(other, int):
			return self.Value + other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by + operator.")

	def __sub__(self, other: Any) -> int:
		"""Subtraction: self - other."""
		if isinstance(other, int):
			return self.Value - other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by - operator.")

	def __truediv__(self, other: Any) -> int:
		"""Division: self / other."""
		if isinstance(other, int):
			return self.Value / other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by / operator.")

	def __floordiv__(self, other: Any) -> int:
		"""Floor division: self // other."""
		if isinstance(other, int):
			return self.Value // other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by // operator.")

	def __mul__(self, other: Any) -> int:
		"""Multiplication: self * other."""
		if isinstance(other, int):
			return self.Value * other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by * operator.")

	def __mod__(self, other: Any) -> int:
		"""Modulo: self % other."""
		if isinstance(other, int):
			return self.Value % other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by % operator.")

	def __pow__(self, other: Any) -> int:
		"""Power: self ** other."""
		if isinstance(other, int):
			return self.Value ** other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by ** operator.")

	# Binary inplace operators - arithmetic
	def __iadd__(self, other: Any) -> 'CallByRefIntParam':
		"""Addition: self += other."""
		if isinstance(other, int):
			self.Value += other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __isub__(self, other: Any) -> 'CallByRefIntParam':
		"""Subtraction: self -= other."""
		if isinstance(other, int):
			self.Value -= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __idiv__(self, other: Any) -> 'CallByRefIntParam':
		"""Division: self /= other."""
		if isinstance(other, int):
			self.Value /= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __ifloordiv__(self, other: Any) -> 'CallByRefIntParam':
		"""Floor division: self // other."""
		if isinstance(other, int):
			self.Value //= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __imul__(self, other: Any) -> 'CallByRefIntParam':
		r"""Multiplication: self \*= other."""
		if isinstance(other, int):
			self.Value *= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __imod__(self, other: Any) -> 'CallByRefIntParam':
		"""Modulo: self %= other."""
		if isinstance(other, int):
			self.Value %= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	def __ipow__(self, other: Any) -> 'CallByRefIntParam':
		r"""Power: self \*\*= other."""
		if isinstance(other, int):
			self.Value **= other
			return self
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")

	# Binary operators - comparison
	def __eq__(self, other: Any) -> bool:
		"""Equality: self == other."""
		if isinstance(other, int):
			return self.Value == other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by == operator.")

	def __ne__(self, other) -> bool:
		"""Inequality: self != other."""
		if isinstance(other, int):
			return self.Value != other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by != operator.")

	def __lt__(self, other: Any) -> bool:
		"""Less-than: self < other."""
		if isinstance(other, int):
			return self.Value < other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by < operator.")

	def __le__(self, other: Any) -> bool:
		"""Less-equal: self <= other."""
		if isinstance(other, int):
			return self.Value <= other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by <= operator.")

	def __gt__(self, other: Any) -> bool:
		"""Greater-than: self > other."""
		if isinstance(other, int):
			return self.Value > other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by > operator.")

	def __ge__(self, other: Any) -> bool:
		"""Greater-equal: self >= other."""
		if isinstance(other, int):
			return self.Value >= other
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by >= operator.")

	# Type conversion operators
	def __bool__(self) -> bool:
		"""Type conversion to :class:`bool`."""
		return bool(self.Value)

	def __int__(self) -> int:
		"""Type conversion to :class:`int`."""
		return self.Value
