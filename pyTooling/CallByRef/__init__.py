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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from decimal       import Decimal
from sys           import version_info           # needed for versions before Python 3.11
from typing        import Any, Generic, TypeVar, Optional as Nullable

try:
	from pyTooling.Decorators  import export
	from pyTooling.MetaClasses import ExtendedType
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.CallByRef] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export
		from MetaClasses         import ExtendedType
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.CallByRef] Could not import directly!")
		raise ex


T = TypeVar("T")


@export
class CallByRefParam(Generic[T], metaclass=ExtendedType, slots=True):
	"""
	Implements a *call-by-reference* parameter.

	.. seealso::

	   * :class:`CallByRefBoolParam` |br|
	     |rarr| A special *call-by-reference* implementation for boolean reference types.
	   * :class:`CallByRefIntParam` |br|
	     |rarr| A special *call-by-reference* implementation for integer reference types.
	"""

	Value: T    #: internal value

	def __init__(self, value: Nullable[T] = None) -> None:
		"""Constructs a *call-by-reference* object for any type.

		:param value: The value to be set as an initial value.
		"""
		self.Value = value

	def __ilshift__(self, other: T) -> 'CallByRefParam[T]':  # Starting with Python 3.11+, use typing.Self as return type
		"""Assigns a value to the *call-by-reference* object.

		:param other: The value to be assigned to this *call-by-reference* object.
		:returns:     Itself.
		"""
		self.Value = other
		return self

	# binary operators - comparison
	def __eq__(self, other: Any) -> bool:
		"""
		Compare a CallByRefParam wrapped value with another instances (CallbyRefParam) or non-wrapped value for equality.

		:param other: Parameter to compare against.
		:returns:     ``True``, if both values are equal.
		"""
		if isinstance(other, CallByRefParam):
			return self.Value == other.Value
		else:
			return self.Value == other

	def __ne__(self, other) -> bool:
		"""
		Compare a CallByRefParam wrapped value with another instances (CallbyRefParam) or non-wrapped value for inequality.

		:param other: Parameter to compare against.
		:returns:     ``True``, if both values are unequal.
		"""
		if isinstance(other, CallByRefParam):
			return self.Value != other.Value
		else:
			return self.Value != other

	# Type conversion operators
	def __repr__(self) -> str:
		"""
		Returns the wrapped object's string representation.

		:returns: The string representation of the wrapped value.
		"""
		return repr(self.Value)

	def __str__(self) -> str:
		"""
		Returns the wrapped object's string equivalent.

		:returns: The string equivalent of the wrapped value.
		"""
		return str(self.Value)


@export
class CallByRefBoolParam(CallByRefParam):
	"""A special *call-by-reference* implementation for boolean reference types."""

	# Binary operators - comparison
	def __eq__(self, other: Any) -> bool:
		"""
		Compare a CallByRefBoolParam wrapped boolean value with another instances (CallByRefBoolParam) or non-wrapped boolean value for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both values are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`bool` or :class:`CallByRefBoolParam`.
		"""
		if isinstance(other, bool):
			return self.Value == other
		elif isinstance(other, CallByRefBoolParam):
			return self.Value == other.Value
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by == operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: bool, CallByRefBoolParam")
			raise ex

	def __ne__(self, other) -> bool:
		"""
		Compare a CallByRefBoolParam wrapped boolean value with another instances (CallByRefBoolParam) or non-wrapped boolean value for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both values are unequal.
		:raises TypeError: If parameter ``other`` is not of type :class:`bool` or :class:`CallByRefBoolParam`.
		"""
		if isinstance(other, bool):
			return self.Value != other
		elif isinstance(other, CallByRefBoolParam):
			return self.Value != other.Value
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by != operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: bool, CallByRefBoolParam")
			raise ex

	# Type conversion operators
	def __bool__(self) -> bool:
		"""
		Type conversion to :class:`bool`.

		:returns: The wrapped value.
		"""
		return self.Value

	def __int__(self) -> int:
		"""
		Type conversion to :class:`int`.

		:returns: The integer representation of the wrapped boolean value.
		"""
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by and operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __or__(self, other: Any) -> int:
		"""Or: self | other."""
		if isinstance(other, int):
			return self.Value | other
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by or operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __xor__(self, other: Any) -> int:
		"""Xor: self ^ other."""
		if isinstance(other, int):
			return self.Value ^ other
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	# Binary inplace operators
	def __iand__(self, other: Any) -> 'CallByRefIntParam':  # Starting with Python 3.11+, use typing.Self as return type
		"""Inplace and: self &= other."""
		if isinstance(other, int):
			self.Value &= other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by &= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __ior__(self, other: Any) -> 'CallByRefIntParam':  # Starting with Python 3.11+, use typing.Self as return type
		r"""Inplace or: self \|= other."""
		if isinstance(other, int):
			self.Value |= other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by |= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __ixor__(self, other: Any) -> 'CallByRefIntParam':  # Starting with Python 3.11+, use typing.Self as return type
		r"""Inplace or: self \|= other."""
		if isinstance(other, int):
			self.Value ^= other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by ^= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	# Binary operators - arithmetic
	def __add__(self, other: Any) -> int:
		"""Addition: self + other."""
		if isinstance(other, int):
			return self.Value + other
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by + operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __sub__(self, other: Any) -> int:
		"""Subtraction: self - other."""
		if isinstance(other, int):
			return self.Value - other
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by - operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __truediv__(self, other: Any) -> int:
		"""Division: self / other."""
		if isinstance(other, int):
			return self.Value / other
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by / operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __floordiv__(self, other: Any) -> int:
		"""Floor division: self // other."""
		if isinstance(other, int):
			return self.Value // other
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by // operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __mul__(self, other: Any) -> int:
		"""Multiplication: self * other."""
		if isinstance(other, int):
			return self.Value * other
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by * operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __mod__(self, other: Any) -> int:
		"""Modulo: self % other."""
		if isinstance(other, int):
			return self.Value % other
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by % operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __pow__(self, other: Any) -> int:
		"""Power: self ** other."""
		if isinstance(other, int):
			return self.Value ** other
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by ** operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	# Binary inplace operators - arithmetic
	def __iadd__(self, other: Any) -> 'CallByRefIntParam':
		"""Addition: self += other."""
		if isinstance(other, int):
			self.Value += other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __isub__(self, other: Any) -> 'CallByRefIntParam':
		"""Subtraction: self -= other."""
		if isinstance(other, int):
			self.Value -= other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __idiv__(self, other: Any) -> 'CallByRefIntParam':
		"""Division: self /= other."""
		if isinstance(other, int):
			self.Value /= other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __ifloordiv__(self, other: Any) -> 'CallByRefIntParam':
		"""Floor division: self // other."""
		if isinstance(other, int):
			self.Value //= other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __imul__(self, other: Any) -> 'CallByRefIntParam':
		r"""Multiplication: self \*= other."""
		if isinstance(other, int):
			self.Value *= other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __imod__(self, other: Any) -> 'CallByRefIntParam':
		"""Modulo: self %= other."""
		if isinstance(other, int):
			self.Value %= other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	def __ipow__(self, other: Any) -> 'CallByRefIntParam':
		r"""Power: self \*\*= other."""
		if isinstance(other, int):
			self.Value **= other
			return self
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by xor operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int")
			raise ex

	# Binary operators - comparison
	def __eq__(self, other: Any) -> bool:
		"""
		Compare a CallByRefIntParam wrapped integer value with another instances (CallByRefIntParam) or non-wrapped integer value for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both values are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`int`, :class:`float`, :class:`complex`, :class:`Decimal` or :class:`CallByRefParam`.
		"""
		if isinstance(other, (int, float, complex, Decimal)) and not isinstance(other, bool):
			return self.Value == other
		elif isinstance(other, CallByRefIntParam):
			return self.Value == other.Value
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by == operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int, float, complex, Decimal, CallByRefIntParam")
			raise ex

	def __ne__(self, other) -> bool:
		"""
		Compare a CallByRefIntParam wrapped integer value with another instances (CallByRefIntParam) or non-wrapped integer value for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both values are unequal.
		:raises TypeError: If parameter ``other`` is not of type :class:`int`, :class:`float`, :class:`complex`, :class:`Decimal` or :class:`CallByRefParam`.
		"""
		if isinstance(other, (int, float, complex, Decimal)) and not isinstance(other, bool):
			return self.Value != other
		elif isinstance(other, CallByRefIntParam):
			return self.Value != other.Value
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by != operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int, float, complex, Decimal, CallByRefIntParam")
			raise ex

	def __lt__(self, other: Any) -> bool:
		"""
		Compare a CallByRefIntParam wrapped integer value with another instances (CallByRefIntParam) or non-wrapped integer value for less-than.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if the wrapped value is less than the other value.
		:raises TypeError: If parameter ``other`` is not of type :class:`int`, :class:`float`, :class:`complex`, :class:`Decimal` or :class:`CallByRefParam`.
		"""
		if isinstance(other, (int, float, complex, Decimal)) and not isinstance(other, bool):
			return self.Value < other
		elif isinstance(other, CallByRefIntParam):
			return self.Value < other.Value
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by < operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int, float, complex, Decimal, CallByRefIntParam")
			raise ex

	def __le__(self, other: Any) -> bool:
		"""
		Compare a CallByRefIntParam wrapped integer value with another instances (CallByRefIntParam) or non-wrapped integer value for less-than-or-equal.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if the wrapped value is less than or equal the other value.
		:raises TypeError: If parameter ``other`` is not of type :class:`int`, :class:`float`, :class:`complex`, :class:`Decimal` or :class:`CallByRefParam`.
		"""
		if isinstance(other, (int, float, complex, Decimal)) and not isinstance(other, bool):
			return self.Value <= other
		elif isinstance(other, CallByRefIntParam):
			return self.Value <= other.Value
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by <= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int, float, complex, Decimal, CallByRefIntParam")
			raise ex

	def __gt__(self, other: Any) -> bool:
		"""
		Compare a CallByRefIntParam wrapped integer value with another instances (CallByRefIntParam) or non-wrapped integer value for geater-than.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if the wrapped value is greater than the other value.
		:raises TypeError: If parameter ``other`` is not of type :class:`int`, :class:`float`, :class:`complex`, :class:`Decimal` or :class:`CallByRefParam`.
		"""
		if isinstance(other, (int, float, complex, Decimal)) and not isinstance(other, bool):
			return self.Value > other
		elif isinstance(other, CallByRefIntParam):
			return self.Value > other.Value
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by > operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int, float, complex, Decimal, CallByRefIntParam")
			raise ex

	def __ge__(self, other: Any) -> bool:
		"""
		Compare a CallByRefIntParam wrapped integer value with another instances (CallByRefIntParam) or non-wrapped integer value for greater-than-or-equal.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if the wrapped value is greater than or equal the other value.
		:raises TypeError: If parameter ``other`` is not of type :class:`int`, :class:`float`, :class:`complex`, :class:`Decimal` or :class:`CallByRefParam`.
		"""
		if isinstance(other, (int, float, complex, Decimal)) and not isinstance(other, bool):
			return self.Value >= other
		elif isinstance(other, CallByRefIntParam):
			return self.Value >= other.Value
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by >= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: int, float, complex, Decimal, CallByRefIntParam")
			raise ex

	# Type conversion operators
	def __bool__(self) -> bool:
		"""
		Type conversion to :class:`bool`.

		:returns: The boolean representation of the wrapped integer value.
		"""
		return bool(self.Value)

	def __int__(self) -> int:
		"""
		Type conversion to :class:`int`.

		:returns: The wrapped value."""
		return self.Value

	def __float__(self):
		"""
		Type conversion to :class:`float`.

		:returns: The float representation of the wrapped integer value.
		"""
		return float(self.Value)
