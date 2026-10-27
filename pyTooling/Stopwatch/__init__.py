# ==================================================================================================================== #
#              _____           _ _               ____  _                           _       _                           #
#   _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|| |_ ___  _ ____      ____ _| |_ ___| |__                        #
#  | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | \___ \| __/ _ \| '_ \ \ /\ / / _` | __/ __| '_ \                       #
#  | |_) | |_| || | (_) | (_) | | | | | | (_| |_ ___) | || (_) | |_) \ V  V / (_| | || (__| | | |                      #
#  | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \__\___/| .__/ \_/\_/ \__,_|\__\___|_| |_|                      #
#  |_|    |___/                          |___/                 |_|                                                     #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A stopwatch to measure execution times.

.. hint::

   See :ref:`high-level help <COMMON/Stopwatch>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.Tracing`
      |rarr| Nested timespans instead of a single measurement, for tracing an execution.
   :mod:`pyTooling.Process`
      |rarr| The process' memory usage, next to its runtime.
"""
from __future__            import annotations

from datetime              import datetime, timedelta
from time                  import perf_counter_ns
from types                 import TracebackType
from typing                import Optional as Nullable, Any, Callable, ClassVar, Iterator, Self

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import SlottedObject
from pyTooling.Exceptions  import ToolingException


@export
class StopwatchError(ToolingException):
	"""This exception is caused by wrong usage of the stopwatch."""


@export
class Duration(timedelta):
	"""
	A :class:`~datetime.timedelta` resolving nanoseconds, which can be formatted by a format specification.

	The constructor takes the parameters of :class:`~datetime.timedelta` (``days``, ``seconds``, ``microseconds``,
	``milliseconds``, ``minutes``, ``hours``, ``weeks``) and ``nanoseconds``; all of them are added up. Like
	:class:`~datetime.timedelta`, a duration is normalized into components: :attr:`~datetime.timedelta.days` (the only
	one with a sign), :attr:`~datetime.timedelta.seconds` (``0`` to ``86399``) and :attr:`nanoseconds` (``0`` to
	``999999999``). The inherited :attr:`~datetime.timedelta.microseconds` is ``nanoseconds // 1000``, so code written
	for :class:`~datetime.timedelta` sees the duration truncated to microseconds. An existing
	:class:`~datetime.timedelta` is converted by :meth:`FromTimedelta`.

	Arithmetic and comparisons involving a duration calculate in nanoseconds and return a duration (or a number, where
	:class:`~datetime.timedelta` returns one). A :class:`~datetime.timedelta` operand is converted.
	``datetime + duration`` stays the arithmetic of :class:`~datetime.datetime`, which resolves microseconds.

	.. note::

	   :class:`~datetime.timedelta` is a C type, so this is a plain class with ``__slots__``, not an
	   :class:`~pyTooling.MetaClasses.ExtendedType` class.
	"""

	__slots__ = ("_nanoseconds",)

	_nanoseconds: int  #: Sub-second component in nanoseconds, ``0`` to ``999999999``.

	_FIELDS: ClassVar[dict[str, Callable[[int], str]]] = {
		"H": lambda nanoseconds: f"{nanoseconds // 3_600_000_000_000:02}",
		"M": lambda nanoseconds: f"{nanoseconds // 60_000_000_000 % 60:02}",
		"S": lambda nanoseconds: f"{nanoseconds // 1_000_000_000 % 60:02}",
		"L": lambda nanoseconds: f"{nanoseconds // 1_000_000 % 1_000:03}",
		"U": lambda nanoseconds: f"{nanoseconds // 1_000 % 1_000_000:06}",
		"N": lambda nanoseconds: f"{nanoseconds % 1_000_000_000:09}",
		"s": lambda nanoseconds: f"{nanoseconds // 1_000_000_000}",
		"m": lambda nanoseconds: f"{nanoseconds // 1_000_000}",
		"u": lambda nanoseconds: f"{nanoseconds // 1_000}",
		"n": lambda nanoseconds: f"{nanoseconds}",
	}  #: Functions rendering a format specifier from a non-negative duration in nanoseconds.

	def __new__(
		cls,
		days:         float = 0,
		seconds:      float = 0,
		microseconds: float = 0,
		milliseconds: float = 0,
		minutes:      float = 0,
		hours:        float = 0,
		weeks:        float = 0,
		nanoseconds:  float = 0
	) -> Self:
		"""
		Initializes a duration from the sum of all given units.

		The units of :class:`~datetime.timedelta` are converted by :class:`~datetime.timedelta`, so they resolve
		microseconds; ``nanoseconds`` resolves nanoseconds. A float number of nanoseconds is rounded to the nearest
		integer.

		:param days:         Optional, number of days. Default: ``0``.
		:param seconds:      Optional, number of seconds. Default: ``0``.
		:param microseconds: Optional, number of microseconds. Default: ``0``.
		:param milliseconds: Optional, number of milliseconds. Default: ``0``.
		:param minutes:      Optional, number of minutes. Default: ``0``.
		:param hours:        Optional, number of hours. Default: ``0``.
		:param weeks:        Optional, number of weeks. Default: ``0``.
		:param nanoseconds:  Optional, number of nanoseconds. Default: ``0``.
		:returns:            The duration.
		:raises TypeError:   If one of the parameters 'days' to 'weeks' is not a number (raised by
		                     :class:`~datetime.timedelta`).
		:raises ValueError:  If parameter 'nanoseconds' is None.
		:raises TypeError:   If parameter 'nanoseconds' is not of type :class:`int` or :class:`float`.
		"""
		if nanoseconds is None:
			raise ValueError("Parameter 'nanoseconds' is None.")
		elif isinstance(nanoseconds, float):
			nanoseconds = round(nanoseconds)
		elif not isinstance(nanoseconds, int):
			ex = TypeError("Parameter 'nanoseconds' is not of type 'int' or 'float'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(nanoseconds)}'.")
			raise ex

		if days == seconds == microseconds == milliseconds == minutes == hours == weeks == 0:
			total = nanoseconds
		else:
			delta = timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)
			total = ((delta.days * 86_400 + delta.seconds) * 1_000_000 + delta.microseconds) * 1_000 + nanoseconds

		wholeSeconds, fraction = divmod(total, 1_000_000_000)

		duration = super().__new__(cls, seconds=wholeSeconds, microseconds=fraction // 1_000)
		duration._nanoseconds = fraction

		return duration

	@classmethod
	def FromTimedelta(cls, value: timedelta) -> Self:
		"""
		Convert a :class:`~datetime.timedelta` into a duration.

		A duration given as ``value`` keeps its nanoseconds.

		:param value:       The time delta to convert.
		:returns:           A duration of the same length.
		:raises ValueError: If parameter 'value' is None.
		:raises TypeError:  If parameter 'value' is not of type :class:`~datetime.timedelta`.
		"""
		if value is None:
			raise ValueError("Parameter 'value' is None.")
		elif isinstance(value, Duration):
			return cls(value.days, value.seconds, nanoseconds=value._nanoseconds)
		elif not isinstance(value, timedelta):
			ex = TypeError("Parameter 'value' is not of type 'timedelta'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		return cls(value.days, value.seconds, value.microseconds)

	@readonly
	def nanoseconds(self) -> int:
		"""
		Read-only property to access the sub-second component in nanoseconds (:attr:`_nanoseconds`).

		It is the counterpart of :attr:`~datetime.timedelta.microseconds` at nanosecond resolution.

		:returns: The nanoseconds of the duration's last second, ``0`` to ``999999999``.
		"""
		return self._nanoseconds

	def total_nanoseconds(self) -> int:
		"""
		Return the whole duration in nanoseconds.

		It is the counterpart of :meth:`total_seconds` at nanosecond resolution.

		:returns: The duration in nanoseconds.
		"""
		return (self.days * 86_400 + self.seconds) * 1_000_000_000 + self._nanoseconds

	def total_seconds(self) -> float:
		"""
		Return the whole duration in seconds.

		:returns: The duration in seconds, including the nanoseconds.
		"""
		return self.total_nanoseconds() / 1e9

	@staticmethod
	def _TotalNanoseconds(value: timedelta) -> int:
		"""
		Return a time delta in nanoseconds.

		:param value: A :class:`~datetime.timedelta` or a duration.
		:returns:     The time delta in nanoseconds.
		"""
		if isinstance(value, Duration):
			return value.total_nanoseconds()

		return ((value.days * 86_400 + value.seconds) * 1_000_000 + value.microseconds) * 1_000

	@staticmethod
	def _DivideRounded(numerator: int, denominator: int) -> int:
		"""
		Divide two integers, rounding half to even like :class:`~datetime.timedelta` does.

		:param numerator:   The dividend.
		:param denominator: The divisor.
		:returns:           The quotient, rounded to the nearest integer; on a tie to the even one.
		"""
		quotient, remainder = divmod(numerator, denominator)
		doubled = remainder * 2
		if denominator < 0:
			doubled =     -doubled
			denominator = -denominator

		if doubled > denominator or (doubled == denominator and quotient % 2 == 1):
			quotient += 1

		return quotient

	def __bool__(self) -> bool:
		"""
		Check if the duration is not zero.

		:returns: ``True``, if the duration is not zero.
		"""
		return self.days != 0 or self.seconds != 0 or self._nanoseconds != 0

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two durations for equality, in nanoseconds.

		:param other:      A duration or a :class:`~datetime.timedelta` to compare with.
		:returns:          ``True``, if both durations are equal.
		:raises TypeError: If parameter 'other' is not of type :class:`~datetime.timedelta`.
		"""
		if isinstance(other, Duration):
			return self.days == other.days and self.seconds == other.seconds and self._nanoseconds == other._nanoseconds
		elif isinstance(other, timedelta):
			return self._nanoseconds % 1_000 == 0 and super().__eq__(other)

		ex = TypeError("Second operand is not supported by == operator.")
		ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
		ex.add_note("Supported types for second operand: Duration, timedelta")
		raise ex

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two durations for inequality, in nanoseconds.

		:param other:      A duration or a :class:`~datetime.timedelta` to compare with.
		:returns:          ``True``, if both durations are not equal.
		:raises TypeError: If parameter 'other' is not of type :class:`~datetime.timedelta`.
		"""
		if not isinstance(other, timedelta):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Duration, timedelta")
			raise ex

		return not self.__eq__(other)

	def __lt__(self, other: Any) -> bool:
		"""
		Compare two durations for less-than, in nanoseconds.

		:param other:      A duration or a :class:`~datetime.timedelta` to compare with.
		:returns:          ``True``, if this duration is shorter.
		:raises TypeError: If parameter 'other' is not of type :class:`~datetime.timedelta`.
		"""
		if isinstance(other, timedelta):
			return self.total_nanoseconds() < self._TotalNanoseconds(other)

		ex = TypeError("Second operand is not supported by < operator.")
		ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
		ex.add_note("Supported types for second operand: Duration, timedelta")
		raise ex

	def __le__(self, other: Any) -> bool:
		"""
		Compare two durations for less-than-or-equal, in nanoseconds.

		:param other:      A duration or a :class:`~datetime.timedelta` to compare with.
		:returns:          ``True``, if this duration is shorter or equal.
		:raises TypeError: If parameter 'other' is not of type :class:`~datetime.timedelta`.
		"""
		if isinstance(other, timedelta):
			return self.total_nanoseconds() <= self._TotalNanoseconds(other)

		ex = TypeError("Second operand is not supported by <= operator.")
		ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
		ex.add_note("Supported types for second operand: Duration, timedelta")
		raise ex

	def __gt__(self, other: Any) -> bool:
		"""
		Compare two durations for greater-than, in nanoseconds.

		:param other:      A duration or a :class:`~datetime.timedelta` to compare with.
		:returns:          ``True``, if this duration is longer.
		:raises TypeError: If parameter 'other' is not of type :class:`~datetime.timedelta`.
		"""
		if isinstance(other, timedelta):
			return self.total_nanoseconds() > self._TotalNanoseconds(other)

		ex = TypeError("Second operand is not supported by > operator.")
		ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
		ex.add_note("Supported types for second operand: Duration, timedelta")
		raise ex

	def __ge__(self, other: Any) -> bool:
		"""
		Compare two durations for greater-than-or-equal, in nanoseconds.

		:param other:      A duration or a :class:`~datetime.timedelta` to compare with.
		:returns:          ``True``, if this duration is longer or equal.
		:raises TypeError: If parameter 'other' is not of type :class:`~datetime.timedelta`.
		"""
		if isinstance(other, timedelta):
			return self.total_nanoseconds() >= self._TotalNanoseconds(other)

		ex = TypeError("Second operand is not supported by >= operator.")
		ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
		ex.add_note("Supported types for second operand: Duration, timedelta")
		raise ex

	def __hash__(self) -> int:
		"""
		Return a hash, which equals the hash of an equal :class:`~datetime.timedelta`.

		:returns: The hash value.
		"""
		if self._nanoseconds % 1_000 == 0:
			return super().__hash__()

		return hash((self.days, self.seconds, self._nanoseconds))

	def __neg__(self) -> Self:
		"""
		Negate the duration.

		:returns: The negated duration.
		"""
		return self.__class__(nanoseconds=-self.total_nanoseconds())

	def __pos__(self) -> Self:
		"""
		Return the duration unchanged.

		:returns: This duration.
		"""
		return self

	def __abs__(self) -> Self:
		"""
		Return the absolute duration.

		:returns: The duration without sign.
		"""
		return self if self.days >= 0 else self.__neg__()

	def __add__(self, other: Any) -> Any:
		"""
		Add a duration or a :class:`~datetime.timedelta`.

		Other operands are left to :class:`~datetime.timedelta`: ``duration + datetime`` is a
		:class:`~datetime.datetime`.

		:param other: The second operand.
		:returns:     The sum as a duration.
		"""
		if isinstance(other, timedelta):
			return self.__class__(nanoseconds=self.total_nanoseconds() + self._TotalNanoseconds(other))

		return super().__add__(other)

	def __radd__(self, other: Any) -> Any:
		"""
		Add this duration to a :class:`~datetime.timedelta`.

		:param other: The first operand.
		:returns:     The sum as a duration.
		"""
		if isinstance(other, timedelta):
			return self.__class__(nanoseconds=self._TotalNanoseconds(other) + self.total_nanoseconds())

		return super().__radd__(other)

	def __sub__(self, other: Any) -> Any:
		"""
		Subtract a duration or a :class:`~datetime.timedelta`.

		:param other: The second operand.
		:returns:     The difference as a duration.
		"""
		if isinstance(other, timedelta):
			return self.__class__(nanoseconds=self.total_nanoseconds() - self._TotalNanoseconds(other))

		return super().__sub__(other)

	def __rsub__(self, other: Any) -> Any:
		"""
		Subtract this duration from a :class:`~datetime.timedelta`.

		:param other: The first operand.
		:returns:     The difference as a duration.
		"""
		if isinstance(other, timedelta):
			return self.__class__(nanoseconds=self._TotalNanoseconds(other) - self.total_nanoseconds())

		return super().__rsub__(other)

	def __mul__(self, other: Any) -> Any:
		"""
		Multiply the duration by a number.

		A product with a :class:`float` is rounded to the nearest nanosecond, on a tie to the even one.

		:param other: An :class:`int` or :class:`float` factor.
		:returns:     The product as a duration.
		"""
		if isinstance(other, int):
			return self.__class__(nanoseconds=self.total_nanoseconds() * other)
		elif isinstance(other, float):
			numerator, denominator = other.as_integer_ratio()
			return self.__class__(nanoseconds=self._DivideRounded(self.total_nanoseconds() * numerator, denominator))

		return super().__mul__(other)

	def __rmul__(self, other: Any) -> Any:
		"""
		Multiply a number by the duration.

		:param other: An :class:`int` or :class:`float` factor.
		:returns:     The product as a duration.
		"""
		return self.__mul__(other)

	def __truediv__(self, other: Any) -> Any:
		"""
		Divide the duration by a duration, a :class:`~datetime.timedelta` or a number.

		A quotient of a number is rounded to the nearest nanosecond, on a tie to the even one.

		:param other: The divisor.
		:returns:     The ratio as a :class:`float` for a time delta divisor, otherwise the quotient as a duration.
		"""
		if isinstance(other, timedelta):
			return self.total_nanoseconds() / self._TotalNanoseconds(other)
		elif isinstance(other, int):
			return self.__class__(nanoseconds=self._DivideRounded(self.total_nanoseconds(), other))
		elif isinstance(other, float):
			numerator, denominator = other.as_integer_ratio()
			return self.__class__(nanoseconds=self._DivideRounded(self.total_nanoseconds() * denominator, numerator))

		return super().__truediv__(other)

	def __rtruediv__(self, other: Any) -> Any:
		"""
		Divide a :class:`~datetime.timedelta` by the duration.

		:param other: The dividend.
		:returns:     The ratio as a :class:`float`.
		"""
		if isinstance(other, timedelta):
			return self._TotalNanoseconds(other) / self.total_nanoseconds()

		return super().__rtruediv__(other)

	def __floordiv__(self, other: Any) -> Any:
		"""
		Divide the duration by a duration, a :class:`~datetime.timedelta` or an integer, rounding down.

		:param other: The divisor.
		:returns:     The ratio as an :class:`int` for a time delta divisor, otherwise the quotient as a duration.
		"""
		if isinstance(other, timedelta):
			return self.total_nanoseconds() // self._TotalNanoseconds(other)
		elif isinstance(other, int):
			return self.__class__(nanoseconds=self.total_nanoseconds() // other)

		return super().__floordiv__(other)

	def __rfloordiv__(self, other: Any) -> Any:
		"""
		Divide a :class:`~datetime.timedelta` by the duration, rounding down.

		:param other: The dividend.
		:returns:     The ratio as an :class:`int`.
		"""
		if isinstance(other, timedelta):
			return self._TotalNanoseconds(other) // self.total_nanoseconds()

		return super().__rfloordiv__(other)

	def __mod__(self, other: Any) -> Any:
		"""
		Return the remainder of dividing the duration by a duration or a :class:`~datetime.timedelta`.

		:param other: The divisor.
		:returns:     The remainder as a duration.
		"""
		if isinstance(other, timedelta):
			return self.__class__(nanoseconds=self.total_nanoseconds() % self._TotalNanoseconds(other))

		return super().__mod__(other)

	def __rmod__(self, other: Any) -> Any:
		"""
		Return the remainder of dividing a :class:`~datetime.timedelta` by the duration.

		:param other: The dividend.
		:returns:     The remainder as a duration.
		"""
		if isinstance(other, timedelta):
			return self.__class__(nanoseconds=self._TotalNanoseconds(other) % self.total_nanoseconds())

		return super().__rmod__(other)

	def __divmod__(self, other: Any) -> Any:
		"""
		Divide the duration by a duration or a :class:`~datetime.timedelta`, returning quotient and remainder.

		:param other: The divisor.
		:returns:     The quotient as an :class:`int` and the remainder as a duration.
		"""
		if isinstance(other, timedelta):
			quotient, remainder = divmod(self.total_nanoseconds(), self._TotalNanoseconds(other))
			return quotient, self.__class__(nanoseconds=remainder)

		return super().__divmod__(other)

	def __rdivmod__(self, other: Any) -> Any:
		"""
		Divide a :class:`~datetime.timedelta` by the duration, returning quotient and remainder.

		:param other: The dividend.
		:returns:     The quotient as an :class:`int` and the remainder as a duration.
		"""
		if isinstance(other, timedelta):
			quotient, remainder = divmod(self._TotalNanoseconds(other), self.total_nanoseconds())
			return quotient, self.__class__(nanoseconds=remainder)

		return super().__rdivmod__(other)

	def __reduce__(self) -> tuple[type[Self], tuple[int, ...]]:
		"""
		Return how to rebuild the duration, so :mod:`pickle` and :mod:`copy` keep its nanoseconds.

		:returns: The class and its constructor arguments.
		"""
		return self.__class__, (self.days, self.seconds, 0, 0, 0, 0, 0, self._nanoseconds)

	def __repr__(self) -> str:
		"""
		Return the duration as a constructor call.

		Only components other than zero are named. A duration resolving more than microseconds names ``nanoseconds``
		instead of ``microseconds``. A zero duration is ``Duration(0)``.

		:returns: The constructor call, e.g. ``Duration(seconds=1, nanoseconds=5)``.
		"""
		arguments = []
		if self.days != 0:
			arguments.append(f"days={self.days}")

		if self.seconds != 0:
			arguments.append(f"seconds={self.seconds}")

		if self._nanoseconds % 1_000 != 0:
			arguments.append(f"nanoseconds={self._nanoseconds}")
		elif self._nanoseconds != 0:
			arguments.append(f"microseconds={self._nanoseconds // 1_000}")

		if len(arguments) == 0:
			return f"{self.__class__.__name__}(0)"

		return f"{self.__class__.__name__}({', '.join(arguments)})"

	def __str__(self) -> str:
		"""
		Return the duration like :class:`~datetime.timedelta` does.

		A duration resolving more than microseconds shows 9 fractional digits instead of 6.

		:returns: The duration as ``[D day[s], ]H:MM:SS[.ffffff]``, or with 9 fractional digits.
		"""
		text = super().__str__()
		if self._nanoseconds % 1_000 == 0:
			return text
		elif self.microseconds != 0:
			text = text[:-7]

		return f"{text}.{self._nanoseconds:09}"

	def __format__(self, formatSpec: str) -> str:
		"""
		Return the duration according to the format specification.

		.. topic:: Format Specifiers

		   An **uppercase** specifier is a field of the duration as it would be displayed. A **lowercase** specifier is
		   the whole duration expressed in one unit, which is what a report or a comparison wants.

		   +-----------+--------------------------------------------------------+
		   | Specifier | Meaning                                                |
		   +===========+========================================================+
		   | ``%H``    | hours, not capped - a 26 hour duration shows ``26``    |
		   +-----------+--------------------------------------------------------+
		   | ``%M``    | minutes, ``00`` to ``59``                              |
		   +-----------+--------------------------------------------------------+
		   | ``%S``    | seconds, ``00`` to ``59``                              |
		   +-----------+--------------------------------------------------------+
		   | ``%L``    | fractional seconds, 3 digits (milliseconds)            |
		   +-----------+--------------------------------------------------------+
		   | ``%U``    | fractional seconds, 6 digits (microseconds)            |
		   +-----------+--------------------------------------------------------+
		   | ``%N``    | fractional seconds, 9 digits (nanoseconds)             |
		   +-----------+--------------------------------------------------------+
		   | ``%s``    | the whole duration in seconds                          |
		   +-----------+--------------------------------------------------------+
		   | ``%m``    | the whole duration in milliseconds                     |
		   +-----------+--------------------------------------------------------+
		   | ``%u``    | the whole duration in microseconds                     |
		   +-----------+--------------------------------------------------------+
		   | ``%n``    | the whole duration in nanoseconds                      |
		   +-----------+--------------------------------------------------------+

		   The fractional specifiers are truncations of the same fraction, so ``%S.%U`` renders ``04.123456`` without
		   having to be combined with anything. ``%H`` is not capped, so ``%H:%M:%S`` never silently drops a day.

		   A negative duration renders the fields of its absolute value, with a ``-`` in front of the first placeholder:
		   ``took %s s`` renders ``took -5 s``.

		   ``%%`` renders a literal percent sign. An empty format specification returns :meth:`__str__`.

		:param formatSpec:  The format specification, using ``%``-placeholders for the duration's parts.
		:returns:           The formatted duration.
		:raises ValueError: If the format specification contains an unknown placeholder.
		"""
		if formatSpec == "":
			return self.__str__()

		nanoseconds = self.total_nanoseconds()
		if nanoseconds < 0:
			sign =        "-"
			nanoseconds = -nanoseconds
		else:
			sign = ""

		fields = self._FIELDS
		parts =  []
		for part in formatSpec.split("%%"):
			text, *placeholders = part.split("%")
			for placeholder in placeholders:
				field = fields.get(placeholder[:1], None)
				if field is None:
					raise ValueError(f"Unknown format specifier '%{placeholder[:1]}' in '{formatSpec}'.")

				text += sign + field(nanoseconds) + placeholder[1:]
				sign = ""

			parts.append(text)

		return "%".join(parts)


@export
class ExcludeContextManager:
	"""
	A stopwatch context manager for excluding certain time spans from measurement.

	While a normal stopwatch's embedded context manager (re)starts the stopwatch on every *enter* event and pauses the
	stopwatch on every *exit* event, this context manager pauses on *enter* events and restarts on every *exit* event.
	"""
	_stopwatch: Stopwatch  #: Reference to the stopwatch.

	def __init__(self, stopwatch: Stopwatch) -> None:
		"""
		Initializes an excluding context manager.

		:param stopwatch: Reference to the stopwatch.
		"""
		self._stopwatch = stopwatch

	def __enter__(self) -> Self:
		"""
		Enter the context and pause the stopwatch.

		:returns: Excluding stopwatch context manager instance.
		"""
		self._stopwatch.Pause()

		return self

	def __exit__(
		self,
		exc_type: Nullable[type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the context and restart stopwatch.

		:param exc_type: Optional, exception type.
		:param exc_val:  Optional, exception instance.
		:param exc_tb:   Optional, exception's traceback.
		:returns:        ``None``
		"""
		self._stopwatch.Resume()


@export
class Stopwatch(SlottedObject):
	"""
	The stopwatch implements a solution to measure and collect timings.

	The time measurement can be started, paused, resumed and stopped. More over, split times can be taken too. The
	measurement is based on :func:`time.perf_counter_ns`. Additionally, starting and stopping is preserved as absolute
	time via :meth:`datetime.datetime.now`.

	Every split time taken is a time delta to the previous operation. These are preserved in an internal sequence of
	splits. This sequence includes time deltas of activity and inactivity. Thus, a running stopwatch can be split as well
	as a paused stopwatch.

	The stopwatch can also be used in a :ref:`with-statement <with>`, because it implements the :ref:`context manager protocol <context-managers>`.

	A stopwatch measures one time span: it is started once and stopped once. There is no restart or reset operation; a
	new stopwatch measures again.
	"""

	_name:         Nullable[str]  #: Optional name of the stopwatch.
	_preferPause:  bool           #: If ``True``, the context manager pauses instead of stopping on exit.
	_digits:       int            #: Number of fractional digits ``__str__`` renders the duration with.

	_beginTime:    Nullable[datetime]        #: Absolute time when the stopwatch was started.
	_endTime:      Nullable[datetime]        #: Absolute time when the stopwatch was stopped.
	_startTime:    Nullable[int]             #: Performance counter in ns when the stopwatch was started.
	_resumeTime:   Nullable[int]             #: Performance counter in ns of the latest resume operation.
	_pauseTime:    Nullable[int]             #: Performance counter in ns of the latest pause operation.
	_stopTime:     Nullable[int]             #: Performance counter in ns when the stopwatch was stopped.
	_totalTime:    Nullable[int]             #: Duration in ns from starting to stopping, activity and inactivity.
	_duration:     Nullable[Duration]        #: :attr:`Duration` of a stopped stopwatch, computed on first access.
	_splits:       list[tuple[float, bool]]  #: Split times as (duration, is-active) pairs, in the order they were taken.

	_excludeContextManager: ExcludeContextManager  #: The nested context manager excluding time spans from measurement.

	def __init__(
		self,
		name: Nullable[str] = None,
		started: bool = False,
		preferPause: bool = False,
		digits: int = 3
	) -> None:
		"""
		Initializes the fields of the stopwatch.

		If parameter ``started`` is set to true, the stopwatch will immediately start.

		:param name:        Optional, name of the stopwatch.
		:param started:     Optional, if ``True``, start the stopwatch immediately.
		:param preferPause: Optional, if ``True``, ``__exit__(...)`` prefers pause over stop behavior.
		:param digits:      Optional, number of fractional digits :meth:`__str__` renders the duration with.
		:raises TypeError:  If parameter 'digits' is not of type :class:`int`.
		:raises ValueError: If parameter 'digits' is negative or greater than 9.
		"""
		if not isinstance(digits, int):
			ex = TypeError("Parameter 'digits' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(digits)}'.")
			raise ex
		elif not 0 <= digits <= 9:
			ex = ValueError(f"Parameter 'digits' is out of range 0..9. Got {digits}.")
			ex.add_note("A duration in seconds has at most 9 digits (nanoseconds).")
			raise ex

		self._name =         name
		self._preferPause =  preferPause
		self._digits =       digits

		self._endTime =      None
		self._pauseTime =    None
		self._stopTime =     None
		self._totalTime =    None
		self._duration =     None
		self._splits =       []

		self._excludeContextManager = None

		if started is False:
			self._beginTime =  None
			self._startTime =  None
			self._resumeTime = None
		else:
			self._beginTime =  datetime.now()
			self._resumeTime = self._startTime = perf_counter_ns()

	def Start(self) -> None:
		"""
		Start the stopwatch.

		A stopwatch can only be started once. There is no restart or reset operation provided; a new stopwatch measures
		again.

		:raises StopwatchError: If stopwatch was already started.
		:raises StopwatchError: If stopwatch was already started and stopped. |br|
		                        Create a new stopwatch to measure again.
		"""
		if self._totalTime is not None:
			ex = StopwatchError("Stopwatch was already used (started and stopped).")
			ex.add_note("A stopwatch can't be restarted. Create a new one to measure again.")
			raise ex
		elif self._startTime is not None:
			raise StopwatchError("Stopwatch was already started.")

		self._beginTime = datetime.now()
		self._resumeTime = self._startTime = perf_counter_ns()

	def Split(self) -> float:
		"""
		Take a split time and return the time delta to the previous stopwatch operation.

		The stopwatch needs to be running to take a split time. See property :data:`IsRunning` to check if the stopwatch
		is running and the split operation is possible. |br|
		Depending on the previous operation, the time delta will be:

		* the duration from start operation to the first split.
		* the duration from last resume to this split.

		:returns:               Duration in seconds since last stopwatch operation
		:raises StopwatchError: If stopwatch was not started or resumed.
		"""
		pauseTime = perf_counter_ns()

		if self._resumeTime is None:
			raise StopwatchError("Stopwatch was not started or resumed.")

		diff = (pauseTime - self._resumeTime) / 1e9
		self._splits.append((diff, True))
		self._resumeTime = pauseTime

		return diff

	def Pause(self) -> float:
		"""
		Pause the stopwatch and return the time delta to the previous stopwatch operation.

		The stopwatch needs to be running to pause it. See property :data:`IsRunning` to check if the stopwatch is running
		and the pause operation is possible. |br|
		Depending on the previous operation, the time delta will be:

		* the duration from start operation to the first pause.
		* the duration from last resume to this pause.

		:returns:               Duration in seconds since last stopwatch operation
		:raises StopwatchError: If stopwatch was not started or resumed.
		"""
		self._pauseTime = perf_counter_ns()

		if self._resumeTime is None:
			raise StopwatchError("Stopwatch was not started or resumed.")

		diff = (self._pauseTime - self._resumeTime) / 1e9
		self._splits.append((diff, True))
		self._resumeTime = None

		return diff

	def Resume(self) -> float:
		"""
		Resume the stopwatch and return the time delta to the previous pause operation.

		The stopwatch needs to be paused to resume it. See property :data:`IsPaused` to check if the stopwatch is paused
		and the resume operation is possible. |br|
		The time delta will be the duration from last pause to this resume.

		:returns:               Duration in seconds since last pause operation
		:raises StopwatchError: If stopwatch was not paused.
		"""
		self._resumeTime = perf_counter_ns()

		if self._pauseTime is None:
			raise StopwatchError("Stopwatch was not paused.")

		diff = (self._resumeTime - self._pauseTime) / 1e9
		self._splits.append((diff, False))
		self._pauseTime = None

		return diff

	def Stop(self) -> float:
		"""
		Stop the stopwatch and return the time delta to the previous stopwatch operation.

		The stopwatch needs to be started to stop it. See property :data:`IsStarted` to check if the stopwatch was started
		and the stop operation is possible. |br|
		Depending on the previous operation, the time delta will be:

		* the duration from start operation to the stop operation.
		* the duration from last resume to the stop operation.

		:returns:               Duration in seconds since last stopwatch operation
		:raises StopwatchError: If stopwatch was not started.
		:raises StopwatchError: If stopwatch was already stopped.
		"""
		stopTime = perf_counter_ns()
		endTime =  datetime.now()

		if self._startTime is None:
			raise StopwatchError("Stopwatch was never started.")

		if self._totalTime is not None:
			raise StopwatchError("Stopwatch was already stopped.")

		self._stopTime = stopTime
		self._endTime =  endTime

		if len(self._splits) == 0:    # was never paused
			diff = (self._stopTime - self._startTime) / 1e9
		elif self._resumeTime is None:    # is paused
			diff = (self._stopTime - self._pauseTime) / 1e9
			self._splits.append((diff, False))
		else:                           # is running
			diff = (self._stopTime - self._resumeTime) / 1e9
			self._splits.append((diff, True))

		self._pauseTime =  None
		self._resumeTime = None
		self._totalTime =  self._stopTime - self._startTime

		# FIXME: why is this unused?
		beginEndDiff = self._endTime - self._beginTime

		return diff

	@property
	def Digits(self) -> int:
		"""
		Property to get and set the number of fractional digits (:attr:`_digits`) used by :meth:`__str__`.

		The measurement itself is unaffected - this only decides how many digits of the duration in seconds are
		rendered. It defaults to ``3``, which is milliseconds.

		:returns:           Number of fractional digits.
		:raises TypeError:  If the assigned value is not of type :class:`int`.
		:raises ValueError: If the assigned value is negative or greater than 9.
		"""
		return self._digits

	@Digits.setter
	def Digits(self, digits: int) -> None:
		if not isinstance(digits, int):
			ex = TypeError("Parameter 'digits' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(digits)}'.")
			raise ex
		elif not 0 <= digits <= 9:
			ex = ValueError(f"Parameter 'digits' is out of range 0..9. Got {digits}.")
			ex.add_note("A duration in seconds has at most 9 digits (nanoseconds).")
			raise ex

		self._digits = digits

	@readonly
	def Name(self) -> Nullable[str]:
		"""
		Read-only property returning the name of the stopwatch.

		:returns: Name of the stopwatch.
		"""
		return self._name

	@readonly
	def IsStarted(self) -> bool:
		"""
		Read-only property returning the IsStarted state of the stopwatch.

		:returns: True, if stopwatch was started.
		"""
		return self._startTime is not None and self._stopTime is None

	@readonly
	def IsRunning(self) -> bool:
		"""
		Read-only property returning the IsRunning state of the stopwatch.

		:returns: True, if stopwatch was started and is currently not paused.
		"""
		return self._startTime is not None and self._resumeTime is not None

	@readonly
	def IsPaused(self) -> bool:
		"""
		Read-only property returning the IsPaused state of the stopwatch.

		:returns: True, if stopwatch was started and is currently paused.
		"""
		return self._startTime is not None and self._pauseTime is not None

	@readonly
	def IsStopped(self) -> bool:
		"""
		Read-only property returning the IsStopped state of the stopwatch.

		:returns: True, if stopwatch was stopped.
		"""
		return self._stopTime is not None

	@readonly
	def StartTime(self) -> Nullable[datetime]:
		"""
		Read-only property returning the absolute time when the stopwatch was started.

		:returns: The time when the stopwatch was started, otherwise None.
		"""
		return self._beginTime

	@readonly
	def StopTime(self) -> Nullable[datetime]:
		"""
		Read-only property returning the absolute time when the stopwatch was stopped.

		:returns: The time when the stopwatch was stopped, otherwise None.
		"""
		return self._endTime

	@readonly
	def HasSplitTimes(self) -> bool:
		"""
		Read-only property checking if split times have been taken.

		:returns: True, if at least one split time has been taken.
		"""
		return len(self._splits) > 0

	@readonly
	def SplitCount(self) -> int:
		"""
		Read-only property returning the number of split times.

		:returns: Number of split times.
		"""
		return len(self._splits)

	@readonly
	def ActiveCount(self) -> int:
		"""
		Read-only property returning the number of active split times.

		A running stopwatch is inside an active span that hasn't been recorded yet, and that span is counted here -
		the result is what the stopwatch would report if it were stopped right now. This matches
		:attr:`Activity`, which includes the running span's duration.

		:returns: Number of active split times, including the one in progress.
		"""
		if self._startTime is None:
			return 0

		return len([t for t, a in self._splits if a is True]) + (1 if self._resumeTime is not None else 0)

	@readonly
	def InactiveCount(self) -> int:
		"""
		Read-only property returning the number of inactive split times.

		A paused stopwatch is inside an inactive span that hasn't been recorded yet, and that span is counted here -
		the result is what the stopwatch would report if it were stopped right now. This matches
		:attr:`Inactivity`, which includes the paused span's duration.

		:returns: Number of inactive split times, including the one in progress.
		"""
		if self._startTime is None:
			return 0

		return len([t for t, a in self._splits if a is False]) + (1 if self._pauseTime is not None else 0)

	@readonly
	def Activity(self) -> Duration:
		"""
		Read-only property returning the duration of all active split times.

		If the stopwatch is currently running, the duration since start or last resume operation will be included. It is
		built from :attr:`ActivityInSeconds`, the same value as a float, so it resolves microseconds.

		:returns: Duration of all active split times. If the stopwatch was never started, the return value is a zero
		          duration.
		"""
		return Duration(seconds=self.ActivityInSeconds)

	@readonly
	def ActivityInSeconds(self) -> float:
		"""
		Read-only property returning the same duration as :attr:`Activity`, but in seconds.

		:returns: Duration of all active split times in seconds. If the stopwatch was never started, the return value will
		          be 0.0.
		"""
		if self._startTime is None:
			return 0.0

		currentDiff = 0.0 if self._resumeTime is None else ((perf_counter_ns() - self._resumeTime) / 1e9)
		return sum(t for t, a in self._splits if a is True) + currentDiff

	@readonly
	def Inactivity(self) -> Duration:
		"""
		Read-only property returning the duration of all inactive split times.

		If the stopwatch is currently paused, the duration since last pause operation will be included. It is built from
		:attr:`InactivityInSeconds`, the same value as a float, so it resolves microseconds.

		:returns: Duration of all inactive split times. If the stopwatch was never started, the return value is a zero
		          duration.
		"""
		return Duration(seconds=self.InactivityInSeconds)

	@readonly
	def InactivityInSeconds(self) -> float:
		"""
		Read-only property returning the same duration as :attr:`Inactivity`, but in seconds.

		:returns: Duration of all inactive split times in seconds. If the stopwatch was never started, the return value will
		          be 0.0.
		"""
		if self._startTime is None:
			return 0.0

		currentDiff = 0.0 if self._pauseTime is None else ((perf_counter_ns() - self._pauseTime) / 1e9)
		return sum(t for t, a in self._splits if a is False) + currentDiff

	@readonly
	def Duration(self) -> Duration:
		"""
		Read-only property returning the duration from start operation to stop operation.

		If the stopwatch is not yet stopped, the duration from start to now is returned. A
		:class:`~pyTooling.Stopwatch.Duration` prints as hours, minutes and seconds, accepts a format specification and
		resolves nanoseconds; :attr:`DurationInSeconds` and :attr:`DurationInNanoseconds` are the same measurement as
		numbers. The duration of a stopped stopwatch is computed once (:attr:`_duration`).

		:returns: Duration since the stopwatch was started. If the stopwatch was never started, the return value is a zero
		          duration.
		"""
		if self._duration is not None:
			return self._duration

		duration = Duration(nanoseconds=self.DurationInNanoseconds)
		if self._totalTime is not None:
			self._duration = duration

		return duration

	@readonly
	def DurationInSeconds(self) -> float:
		"""
		Read-only property returning the same duration as :attr:`Duration`, but in seconds.

		:returns: Duration since stopwatch was started in seconds. If the stopwatch was never started, the return value will
		          be 0.0.
		"""
		return self.DurationInNanoseconds / 1e9

	@readonly
	def DurationInNanoseconds(self) -> int:
		"""
		Read-only property returning the same duration as :attr:`Duration`, but in whole nanoseconds.

		This is the measurement as the underlying :func:`time.perf_counter_ns` took it, so anything that divides a
		duration into parts - :meth:`__format__` does - works from an integer instead of converting a float back.

		Precision is not the reason to prefer it. A float holds a duration in seconds exactly, to the nanosecond, up
		to :math:`2^{53}` ns - a little over 104 days - which no stopwatch will reach.

		:returns: Duration since the stopwatch was started in nanoseconds. If the stopwatch was never started, the
		          return value will be 0.
		"""
		if self._startTime is None:
			return 0
		elif self._totalTime is not None:    # was stopped, so the total is final
			return self._totalTime

		return perf_counter_ns() - self._startTime

	@readonly
	def Exclude(self) -> ExcludeContextManager:
		"""
		Return an *exclude* context manager for the stopwatch instance.

		:returns: An excluding context manager.
		"""
		if self._excludeContextManager is None:
			self._excludeContextManager = ExcludeContextManager(self)

		return self._excludeContextManager

	def __enter__(self) -> Self:
		"""
		Enter the context and start or resume the stopwatch.

		An unstarted stopwatch is started, a paused one is resumed.

		:returns:               The stopwatch itself.
		:raises StopwatchError: If the stopwatch is running.
		:raises StopwatchError: If the stopwatch was already stopped. |br|
		                        Create a new stopwatch to measure again, or create it with ``preferPause=True`` to
		                        measure several ``with``-blocks.
		"""
		if self._startTime is None:           # start stopwatch
			self._beginTime = datetime.now()
			self._resumeTime = self._startTime = perf_counter_ns()
		elif self._pauseTime is not None:     # resume after pause
			self._resumeTime = perf_counter_ns()

			diff = (self._resumeTime - self._pauseTime) / 1e9
			self._splits.append((diff, False))
			self._pauseTime = None
		elif self._resumeTime is not None:    # is running?
			raise StopwatchError("Stopwatch is currently running and can not be started/resumed again.")
		elif self._stopTime is not None:      # is stopped?
			ex = StopwatchError("Stopwatch was already stopped.")
			ex.add_note("A stopwatch can't be restarted. Create a new one, or one with 'preferPause=True'.")
			raise ex
		else:
			raise StopwatchError("Internal error.")

		return self

	def __exit__(
		self,
		exc_type: Nullable[type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the context and pause or stop the stopwatch.

		A running stopwatch is paused, if ``preferPause`` was set, otherwise it's stopped.

		:param exc_type:        Optional, exception type, otherwise None.
		:param exc_val:         Optional, exception object, otherwise None.
		:param exc_tb:          Optional, exception's traceback, otherwise None.
		:returns:               ``None``
		:raises StopwatchError: If the stopwatch was never started.
		:raises StopwatchError: If the stopwatch was already stopped.
		:raises StopwatchError: If the stopwatch is paused, because it wasn't resumed.
		"""
		if self._startTime is None:           # never started?
			raise StopwatchError("Stopwatch was never started.")
		elif self._stopTime is not None:
			raise StopwatchError("Stopwatch was already stopped.")
		elif self._resumeTime is not None:    # pause or stop
			if self._preferPause:
				self._pauseTime = perf_counter_ns()
				diff = (self._pauseTime - self._resumeTime) / 1e9
				self._splits.append((diff, True))
				self._resumeTime = None
			else:
				self._stopTime = perf_counter_ns()
				self._endTime =  datetime.now()

				diff = (self._stopTime - self._resumeTime) / 1e9
				self._splits.append((diff, True))

				self._pauseTime =  None
				self._resumeTime = None
				self._totalTime =  self._stopTime - self._startTime
		else:
			raise StopwatchError("Stopwatch was not resumed.")

	def __len__(self) -> int:
		"""
		Implementation of ``len(...)`` to return the number of split times.

		:returns: Number of split times.
		"""
		return len(self._splits)

	def __getitem__(self, index: int) -> tuple[float, bool]:
		"""
		Implementation of ``split = object[i]`` to return the i-th split time.

		:param index:       Index to access the i-th split time.
		:returns:           i-th split time as a tuple of: |br|
		                    (1) delta time to the previous stopwatch operation and |br|
		                    (2) a boolean indicating if the split was an activity (true) or inactivity (false).
		:raises IndexError: If index *i* doesn't exist.
		"""
		return self._splits[index]

	def __iter__(self) -> Iterator[tuple[float, bool]]:
		"""
		Return an iterator of tuples to iterate all split times.

		If the stopwatch is not stopped yet, the last split won't be included.

		:returns: Iterator of split time tuples of: |br|
		          (1) delta time to the previous stopwatch operation and |br|
		          (2) a boolean indicating if the split was an activity (true) or inactivity (false).
		"""
		return self._splits.__iter__()

	def __format__(self, formatSpec: str) -> str:
		"""
		Return the measured duration according to the format specification.

		.. topic:: Format Specifiers

		   An **uppercase** specifier is a field of the duration as it would be displayed. A **lowercase** specifier is
		   the whole duration expressed in one unit, which is what a report or a comparison wants.

		   +-----------+--------------------------------------------------------+
		   | Specifier | Meaning                                                |
		   +===========+========================================================+
		   | ``%H``    | hours, not capped - a 26 hour measurement shows ``26`` |
		   +-----------+--------------------------------------------------------+
		   | ``%M``    | minutes, ``00`` to ``59``                              |
		   +-----------+--------------------------------------------------------+
		   | ``%S``    | seconds, ``00`` to ``59``                              |
		   +-----------+--------------------------------------------------------+
		   | ``%L``    | fractional seconds, 3 digits (milliseconds)            |
		   +-----------+--------------------------------------------------------+
		   | ``%U``    | fractional seconds, 6 digits (microseconds)            |
		   +-----------+--------------------------------------------------------+
		   | ``%N``    | fractional seconds, 9 digits (nanoseconds)             |
		   +-----------+--------------------------------------------------------+
		   | ``%s``    | the whole duration in seconds                          |
		   +-----------+--------------------------------------------------------+
		   | ``%m``    | the whole duration in milliseconds                     |
		   +-----------+--------------------------------------------------------+
		   | ``%u``    | the whole duration in microseconds                     |
		   +-----------+--------------------------------------------------------+
		   | ``%n``    | the whole duration in nanoseconds                      |
		   +-----------+--------------------------------------------------------+

		   The fractional specifiers are truncations of the same fraction, so ``%S.%U`` renders ``04.123456`` without
		   having to be combined with anything. ``%H`` is not capped, so ``%H:%M:%S`` never silently drops a day.

		   ``%%`` renders a literal percent sign. An empty format specification returns :meth:`__str__`.

		:param formatSpec:  The format specification, using ``%``-placeholders for the duration's parts.
		:returns:           The formatted duration.
		:raises ValueError: If the format specification contains an unknown placeholder.
		"""
		if formatSpec == "":
			return self.__str__()

		return self.Duration.__format__(formatSpec)

	def __str__(self) -> str:
		"""
		Returns the stopwatch's state and its measured time span.

		The duration is rendered in seconds with :attr:`Digits` fractional digits, in every state - a running and a
		stopped stopwatch report the same unit at the same resolution.

		:returns: The string equivalent of the stopwatch.
		"""
		name = f" {self._name}" if self._name is not None else ""
		duration = f"{self.DurationInSeconds:.{self._digits}f}"

		if self.IsStopped:
			return f"Stopwatch{name} (stopped): {self._beginTime} -> {self._endTime}: {duration}"
		elif self.IsRunning:
			return f"Stopwatch{name} (running): {self._beginTime} -> now: {duration}"
		elif self.IsPaused:
			return f"Stopwatch{name} (paused): {self._beginTime} -> now: {duration}"
		else:
			return f"Stopwatch{name}: not started"
