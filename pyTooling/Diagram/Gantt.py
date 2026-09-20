# ==================================================================================================================== #
#               _____           _ _               ____  _                                   ____             _   _     #
#    _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \(_) __ _  __ _ _ __ __ _ _ __ ___   / ___| __ _ _ __ | |_| |_   #
#   | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | | |/ _` |/ _` | '__/ _` | '_ ` _ \ | |  _ / _` | '_ \| __| __|  #
#   | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| | | (_| | (_| | | | (_| | | | | | || |_| | (_| | | | | |_| |_   #
#   | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/|_|\__,_|\__, |_|  \__,_|_| |_| |_(_)____|\__,_|_| |_|\__|\__|  #
#   |_|    |___/                          |___/                 |___/                                                  #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A Gantt chart: rows of bars on a time scale.

.. code-block:: python

   from datetime import datetime, timedelta
   from pyTooling.Diagram.Gantt import Diagram, Row, Bar

   begin =   datetime(2026, 9, 15, 8, 0)
   diagram = Diagram("Nightly build", begin)

   row = Row("Compile", parent=diagram)
   Bar(begin, begin + timedelta(minutes=4), parent=row)

   print(f"{row.Name}: {row.DurationInSeconds} s, beginning {row.BeginSinceOrigin} after the diagram's origin")

Every element knows the :class:`Diagram` it belongs to and the element containing it, so an offset is answered
without a search: a bar reports its begin as a time, as the distance from the diagram's **origin**, and as the
distance from the **row** it sits in.

The classes describe a chart; they don't draw one. A producer of data derives from them and adds what its domain
knows - :class:`pyTooling.Tracing.Render.GanttLayout` builds a diagram from a software execution trace - and a
renderer draws what any of them describe.

.. seealso::

   :mod:`pyTooling.Tracing.Render`
      |rarr| A software execution trace as a Gantt chart, and the renderers drawing it.
"""
from __future__            import annotations

from datetime              import datetime, timedelta
from typing                import Iterator, Optional as Nullable

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Diagram     import DiagramError


@export
class Bar(metaclass=ExtendedType, slots=True):
	"""
	A bar of a Gantt chart: a time range within one :class:`Row`.

	A bar reports its position three ways - as the times themselves (:attr:`Begin`, :attr:`End`), as the distance
	from the diagram's origin (:attr:`BeginSinceOrigin`), and as the distance from the row it sits in
	(:attr:`BeginSinceParent`) - because a chart is drawn on the second and a report usually wants one of the others.
	"""
	_parent:  Row       #: The row this bar sits in.
	_diagram: Diagram   #: The diagram this bar belongs to.
	_begin:   datetime  #: Begin of the bar.
	_end:     datetime  #: End of the bar.

	def __init__(self, begin: datetime, end: datetime, *, parent: Row) -> None:
		"""
		Initializes a bar and appends it to its row.

		:param begin:       Begin of the bar.
		:param end:         End of the bar, which may equal the begin but must not precede it.
		:param parent:      The row the bar sits in.
		:raises ValueError: If parameter 'begin', 'end' or 'parent' is None.
		:raises TypeError:  If parameter 'begin' or 'end' is not of type :class:`~datetime.datetime`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Row`.
		:raises ValueError: If the end precedes the begin.
		"""
		for parameterName, parameter in (("begin", begin), ("end", end)):
			if parameter is None:
				raise ValueError(f"Parameter '{parameterName}' is None.")
			elif not isinstance(parameter, datetime):
				ex = TypeError(f"Parameter '{parameterName}' is not of type 'datetime'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(parameter)}'.")
				raise ex

		if parent is None:
			raise ValueError("Parameter 'parent' is None.")
		elif not isinstance(parent, Row):
			ex = TypeError("Parameter 'parent' is not of type 'Row'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		if end < begin:
			ex = ValueError("A bar's end precedes its begin.")
			ex.add_note(f"Got begin '{begin}' and end '{end}'.")
			raise ex

		self._parent =  parent
		self._diagram = parent.Diagram
		self._begin =   begin
		self._end =     end
		parent._bars.append(self)

	@readonly
	def Parent(self) -> Row:
		"""
		Read-only property to access the row this bar sits in (:attr:`_parent`).

		:returns: The row.
		"""
		return self._parent

	@readonly
	def Diagram(self) -> Diagram:
		"""
		Read-only property to access the diagram this bar belongs to (:attr:`_diagram`).

		:returns: The diagram.
		"""
		return self._diagram

	@readonly
	def Begin(self) -> datetime:
		"""
		Read-only property to access the begin of the bar (:attr:`_begin`).

		:returns: The time the bar begins.
		"""
		return self._begin

	@readonly
	def End(self) -> datetime:
		"""
		Read-only property to access the end of the bar (:attr:`_end`).

		:returns: The time the bar ends.
		"""
		return self._end

	@readonly
	def Duration(self) -> timedelta:
		"""
		Read-only property to return the length of the bar.

		:returns: The length from the bar's begin to its end.
		"""
		return self._end - self._begin

	@readonly
	def DurationInSeconds(self) -> float:
		"""
		Read-only property to return the length of the bar as a number.

		:returns: The length in seconds.
		"""
		return (self._end - self._begin).total_seconds()

	@readonly
	def BeginSinceOrigin(self) -> timedelta:
		"""
		Read-only property to return how long after the diagram's origin the bar begins.

		:returns: The distance from the origin to the bar's begin.
		"""
		return self._begin - self._diagram.Origin

	@readonly
	def EndSinceOrigin(self) -> timedelta:
		"""
		Read-only property to return how long after the diagram's origin the bar ends.

		:returns: The distance from the origin to the bar's end.
		"""
		return self._end - self._diagram.Origin

	@readonly
	def BeginSinceOriginInSeconds(self) -> float:
		"""
		Read-only property to return how long after the diagram's origin the bar begins, as a number.

		:returns: The distance from the origin to the bar's begin, in seconds.
		"""
		return (self._begin - self._diagram.Origin).total_seconds()

	@readonly
	def EndSinceOriginInSeconds(self) -> float:
		"""
		Read-only property to return how long after the diagram's origin the bar ends, as a number.

		:returns: The distance from the origin to the bar's end, in seconds.
		"""
		return (self._end - self._diagram.Origin).total_seconds()

	@readonly
	def BeginSinceParent(self) -> timedelta:
		"""
		Read-only property to return how long after its row the bar begins.

		:returns: The distance from the row's begin to the bar's begin, which is zero for the row's earliest bar.
		"""
		return self._begin - self._parent.Begin

	@readonly
	def EndSinceParent(self) -> timedelta:
		"""
		Read-only property to return how long after its row's begin the bar ends.

		:returns: The distance from the row's begin to the bar's end.
		"""
		return self._end - self._parent.Begin


@export
class Row(metaclass=ExtendedType, slots=True):
	"""
	A row of a Gantt chart: the bars drawn on one line, under one name.

	A row spans its bars: it begins with its earliest bar and ends with its latest, whether or not they touch.
	"""
	_parent: Diagram     #: The diagram this row belongs to.
	_name:   str         #: Name of the row, which labels it in a chart.
	_bars:   list[Bar]   #: The bars of this row, in the order they were added.

	def __init__(self, name: str, *, parent: Diagram) -> None:
		"""
		Initializes a row without bars and appends it to its diagram.

		:param name:        Name of the row.
		:param parent:      The diagram the row belongs to.
		:raises ValueError: If parameter 'name' or 'parent' is None.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Diagram`.
		"""
		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		if parent is None:
			raise ValueError("Parameter 'parent' is None.")
		elif not isinstance(parent, Diagram):
			ex = TypeError("Parameter 'parent' is not of type 'Diagram'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent
		self._name =   name
		self._bars =   []
		parent._rows.append(self)

	@readonly
	def Parent(self) -> Diagram:
		"""
		Read-only property to access the diagram this row belongs to (:attr:`_parent`).

		:returns: The diagram.
		"""
		return self._parent

	@readonly
	def Diagram(self) -> Diagram:
		"""
		Read-only property to access the diagram this row belongs to (:attr:`_parent`), which is what contains it.

		:returns: The diagram.
		"""
		return self._parent

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the name of the row (:attr:`_name`).

		:returns: The name.
		"""
		return self._name

	@readonly
	def Bars(self) -> tuple[Bar, ...]:
		"""
		Read-only property to return the bars of this row (:attr:`_bars`).

		:returns: The bars, in the order they were added.
		"""
		return tuple(self._bars)

	@readonly
	def Begin(self) -> datetime:
		"""
		Read-only property to return the begin of the row's earliest bar.

		:returns:             The time the row begins.
		:raises DiagramError: If the row has no bars.
		"""
		if len(self._bars) == 0:
			raise DiagramError(f"Row '{self._name}' has no bars, so it has no begin.")

		return min(bar.Begin for bar in self._bars)

	@readonly
	def End(self) -> datetime:
		"""
		Read-only property to return the end of the row's latest bar.

		:returns:             The time the row ends.
		:raises DiagramError: If the row has no bars.
		"""
		if len(self._bars) == 0:
			raise DiagramError(f"Row '{self._name}' has no bars, so it has no end.")

		return max(bar.End for bar in self._bars)

	@readonly
	def Duration(self) -> timedelta:
		"""
		Read-only property to return the length of the row.

		:returns:             The length from the row's begin to its end, gaps between its bars included.
		:raises DiagramError: If the row has no bars.
		"""
		return self.End - self.Begin

	@readonly
	def DurationInSeconds(self) -> float:
		"""
		Read-only property to return the length of the row as a number.

		:returns:             The length in seconds, gaps between its bars included.
		:raises DiagramError: If the row has no bars.
		"""
		return (self.End - self.Begin).total_seconds()

	@readonly
	def BeginSinceOrigin(self) -> timedelta:
		"""
		Read-only property to return how long after the diagram's origin the row begins.

		:returns:             The distance from the origin to the row's begin.
		:raises DiagramError: If the row has no bars.
		"""
		return self.Begin - self._parent.Origin

	@readonly
	def EndSinceOrigin(self) -> timedelta:
		"""
		Read-only property to return how long after the diagram's origin the row ends.

		:returns:             The distance from the origin to the row's end.
		:raises DiagramError: If the row has no bars.
		"""
		return self.End - self._parent.Origin

	def __len__(self) -> int:
		"""
		Returns the number of bars in this row.

		:returns: Number of bars.
		"""
		return len(self._bars)

	def __iter__(self) -> Iterator[Bar]:
		"""
		Returns an iterator to iterate the bars of this row.

		:returns: Iterator to iterate all bars, in the order they were added.
		"""
		return iter(self._bars)


@export
class Diagram(metaclass=ExtendedType, slots=True):
	"""
	A Gantt chart: rows of bars, and the origin their offsets are counted from.

	The origin is stated rather than derived, because the scale a chart is drawn on usually begins before its first
	bar - a pipeline starts before its first job does.
	"""
	_title:  str         #: Title of the diagram.
	_origin: datetime    #: The time offsets are counted from.
	_rows:   list[Row]   #: The rows of this diagram, in the order they were added.

	def __init__(self, title: str, origin: datetime) -> None:
		"""
		Initializes a diagram without rows.

		:param title:       Title of the diagram.
		:param origin:      The time offsets are counted from.
		:raises ValueError: If parameter 'title' or 'origin' is None.
		:raises TypeError:  If parameter 'title' is not of type :class:`str`.
		:raises TypeError:  If parameter 'origin' is not of type :class:`~datetime.datetime`.
		"""
		if title is None:
			raise ValueError("Parameter 'title' is None.")
		elif not isinstance(title, str):
			ex = TypeError("Parameter 'title' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(title)}'.")
			raise ex

		if origin is None:
			raise ValueError("Parameter 'origin' is None.")
		elif not isinstance(origin, datetime):
			ex = TypeError("Parameter 'origin' is not of type 'datetime'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(origin)}'.")
			raise ex

		self._title =  title
		self._origin = origin
		self._rows =   []

	@readonly
	def Diagram(self) -> Diagram:
		"""
		Read-only property to access the diagram this element belongs to, which for a diagram is itself.

		:returns: This diagram, so a bar, a row and the diagram answer the same question.
		"""
		return self

	@readonly
	def Title(self) -> str:
		"""
		Read-only property to access the title of the diagram (:attr:`_title`).

		:returns: The title.
		"""
		return self._title

	@readonly
	def Origin(self) -> datetime:
		"""
		Read-only property to access the time offsets are counted from (:attr:`_origin`).

		:returns: The origin.
		"""
		return self._origin

	@readonly
	def Rows(self) -> tuple[Row, ...]:
		"""
		Read-only property to return the rows of this diagram (:attr:`_rows`).

		:returns: The rows, in the order they were added.
		"""
		return tuple(self._rows)

	@readonly
	def RowCount(self) -> int:
		"""
		Read-only property to return the number of rows.

		:returns: Number of rows.
		"""
		return len(self._rows)

	def IterateRows(self) -> Iterator[Row]:
		"""
		Returns an iterator to iterate the rows of this diagram.

		:returns: Iterator to iterate all rows, in the order they were added.
		"""
		return iter(self._rows)

	def __len__(self) -> int:
		"""
		Returns the number of rows in this diagram.

		:returns: Number of rows.
		"""
		return len(self._rows)

	def __iter__(self) -> Iterator[Row]:
		"""
		Returns an iterator to iterate the rows of this diagram.

		:returns: Iterator to iterate all rows, in the order they were added.
		"""
		return iter(self._rows)
