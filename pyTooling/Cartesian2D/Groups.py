# ==================================================================================================================== #
#             _____           _ _               ____           _            _             ____  ____                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _ _ __| |_ ___  ___(_) __ _ _ __ |___ \|  _ \                  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | '__| __/ _ \/ __| |/ _` | '_ \  __) | | | |                 #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | |  | ||  __/\__ \ | (_| | | | |/ __/| |_| |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|   \__\___||___/_|\__,_|_| |_|_____|____/                  #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
Groups of 2D cartesian shapes, segments and groups, placed by an offset.

The coordinates of everything inside a group are relative to the group, so moving a group changes its offset only.

.. seealso::

   :mod:`pyTooling.Cartesian2D`
      |rarr| Points, offsets, bounding boxes and segments.
   :mod:`pyTooling.Cartesian2D.Shapes`
      |rarr| Shapes a group can hold.
"""
from __future__                   import annotations

from enum                         import Enum
from typing                       import Generic, Iterable, Optional as Nullable

from pyTooling.Decorators         import export, readonly
from pyTooling.Common             import getFullyQualifiedName
from pyTooling.Cartesian2D        import Coordinate, Offset2D, BoundingBox, Element2D, Segment2D, Cartesian2DError, \
                                         AlreadyOwnedError, GroupCycleError, NotOwnedError
from pyTooling.Cartesian2D.Shapes import Shape


@export
class Axis(Enum):
	"""Axis of the coordinate system."""

	X = 0  #: The x-axis.
	Y = 1  #: The y-axis.


@export
class EmptyGroupError(Cartesian2DError):
	"""The exception is raised when the bounding box of a group without children is requested."""


@export
class Group(Element2D[Coordinate], Generic[Coordinate]):
	"""
	A group holds shapes, segments and other groups at an offset.

	The coordinates of the group's children are relative to the group's origin, which is placed at :attr:`Offset` in the
	group's own frame. A group without a parent is relative to the origin.
	"""

	_offset:   Offset2D[Coordinate]         #: Offset of the group's origin in the group's frame.
	_children: list[Element2D[Coordinate]]  #: Shapes, segments and groups of the group, in insertion order.

	def __init__(
		self,
		offset:   Nullable[Offset2D[Coordinate]] = None,
		children: Nullable[Iterable[Element2D[Coordinate]]] = None,
		*,
		parent:   Nullable[Group[Coordinate]] = None
	) -> None:
		"""
		Initializes a group at an offset, holding the given children.

		The group takes the children, which must not belong to another element. When parameter 'parent' can't take the
		group, the children stay free.

		:param offset:             Optional, offset of the group's origin. Default: ``None``, which places it at ``(0, 0)``.
		:param children:           Optional, shapes, segments and groups held by the group. Default: ``None``.
		:param parent:             Optional, the group this group is added to. Default: ``None``, no group.
		:raises TypeError:         If parameter 'offset' is not of type :class:`~pyTooling.Cartesian2D.Offset2D`.
		:raises TypeError:         If parameter 'children' is not iterable.
		:raises ValueError:        If an element of parameter 'children' is None.
		:raises TypeError:         If an element of parameter 'children' is not of type
		                           :class:`~pyTooling.Cartesian2D.Element2D`.
		:raises AlreadyOwnedError: If an element of parameter 'children' belongs to another element.
		:raises ValueError:        If an element of parameter 'children' is given twice.
		:raises TypeError:         If parameter 'parent' is not of type :class:`Group`.
		:raises GroupCycleError:   If parameter 'parent' is inside an element of parameter 'children'.
		"""
		super().__init__(parent=parent)

		if offset is not None and not isinstance(offset, Offset2D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		if children is not None and not isinstance(children, Iterable):
			ex = TypeError("Parameter 'children' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(children)}'.")
			raise ex

		self._offset =   Offset2D(0, 0) if offset is None else offset.Copy()
		self._children = childList = []

		if children is not None:
			seenChildren = set()
			for child in children:
				if child is None:
					raise ValueError("An element of parameter 'children' is None.")
				elif not isinstance(child, Element2D):
					ex = TypeError("An element of parameter 'children' is not of type 'Element2D'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(child)}'.")
					raise ex
				elif child._parent is not None:
					ex = AlreadyOwnedError("Element is owned by another element already.")
					ex.add_note(f"Got {child!r} owned by {child._parent!r}.")
					raise ex from ValueError("An element of parameter 'children' belongs to another element.")
				elif child in seenChildren:
					ex = ValueError("An element of parameter 'children' is given twice.")
					ex.add_note(f"Got {child!r}.")
					raise ex

				seenChildren.add(child)
				childList.append(child)

			for child in childList:
				child._parent = self

		try:
			self.Parent = parent
		except GroupCycleError:
			for child in childList:
				child._parent = None

			raise

	@property
	def Offset(self) -> Offset2D[Coordinate]:
		"""
		Property to access the offset of the group's origin in the group's frame (:attr:`_offset`).

		An assigned offset is copied, so groups never share an offset.

		:returns:           The group's offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`~pyTooling.Cartesian2D.Offset2D`.
		"""
		return self._offset

	@Offset.setter
	def Offset(self, offset: Offset2D[Coordinate]) -> None:
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, Offset2D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._offset = offset.Copy()

	@readonly
	def AbsoluteOffset(self) -> Offset2D[Coordinate]:
		"""
		Read-only property to return the offset of the group's origin relative to the origin.

		The offsets of all groups up the parent chain are added to :attr:`Offset`.

		:returns: A new 2D-offset.
		"""
		frame = self.Frame
		return self._offset.Copy() if frame is None else self._offset + frame.AbsoluteOffset

	@readonly
	def Children(self) -> tuple[Element2D[Coordinate], ...]:
		"""
		Read-only property to return the shapes, segments and groups of the group (:attr:`_children`).

		:returns: Tuple of children, in insertion order.
		"""
		return tuple(self._children)

	@readonly
	def _ChildFrame(self) -> Group[Coordinate]:
		"""
		Read-only property to access the frame the coordinates of this group's children are relative to: the group itself.

		:returns: This group.
		"""
		return self

	@readonly
	def BoundingBox(self) -> BoundingBox[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing all children.

		The union of the children's bounding boxes is shifted by :attr:`Offset`, so the bounding box is in the group's
		frame.

		:returns:                A new bounding box.
		:raises EmptyGroupError: If the group or a group inside it has no children.
		"""
		if len(self._children) == 0:
			ex = EmptyGroupError("Group has no children.")
			ex.add_note(f"Got {self!r}.")
			raise ex

		box = self._children[0].BoundingBox
		for child in self._children[1:]:
			box = box.Union(child.BoundingBox)

		return box + self._offset

	def AddChild(self, child: Element2D[Coordinate]) -> None:
		"""
		Add a shape, segment or group to this group.

		The child keeps its coordinates, which are relative to this group from now on.

		:param child:              The shape, segment or group to add.
		:raises ValueError:        If parameter 'child' is None.
		:raises TypeError:         If parameter 'child' is not of type :class:`~pyTooling.Cartesian2D.Element2D`.
		:raises AlreadyOwnedError: If parameter 'child' belongs to another element. |br|
		                           Use :meth:`~pyTooling.Cartesian2D.Element2D.MoveTo` to move it between groups.
		:raises GroupCycleError:   If parameter 'child' is this group or one of its ancestors.
		"""
		if child is None:
			raise ValueError("Parameter 'child' is None.")
		elif not isinstance(child, Element2D):
			ex = TypeError("Parameter 'child' is not of type 'Element2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(child)}'.")
			raise ex
		elif child._parent is not None:
			ex = AlreadyOwnedError("Element is owned by another element already.")
			ex.add_note(f"Got {child!r} owned by {child._parent!r}.")
			ex.add_note("Use 'MoveTo' to move it between groups.")
			raise ex from ValueError("Parameter 'child' belongs to another element.")

		child.Parent = self

	def RemoveChild(self, child: Element2D[Coordinate]) -> None:
		"""
		Remove a shape, segment or group from this group.

		The child keeps its coordinates, which are relative to the origin from now on.

		:param child:          The shape, segment or group to remove.
		:raises ValueError:    If parameter 'child' is None.
		:raises TypeError:     If parameter 'child' is not of type :class:`~pyTooling.Cartesian2D.Element2D`.
		:raises NotOwnedError: If parameter 'child' isn't a child of this group.
		"""
		if child is None:
			raise ValueError("Parameter 'child' is None.")
		elif not isinstance(child, Element2D):
			ex = TypeError("Parameter 'child' is not of type 'Element2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(child)}'.")
			raise ex
		elif child._parent is not self:
			ex = NotOwnedError("Element isn't a child of this group.")
			ex.add_note(f"Got {child!r} owned by {child._parent!r}.")
			raise ex from ValueError("Parameter 'child' isn't a child of this group.")

		child.Parent = None

	def Move(self, offset: Offset2D[Coordinate]) -> None:
		"""
		Move the group by changing its :attr:`Offset` (inplace).

		The children keep their coordinates.

		:param offset:      The 2D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`~pyTooling.Cartesian2D.Offset2D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, Offset2D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._offset += offset

	def Distribute(self, axis: Axis, gap: Nullable[Coordinate] = None) -> None:
		"""
		Move the children along an axis, so the gaps between their bounding boxes are equal.

		The children are ordered by the smallest coordinate of their bounding boxes on that axis. The first child keeps its
		position. Without a gap, the last child keeps its position too and the gaps follow from the space between them. With
		fewer than three children, there is then nothing to distribute. With a gap, the other children follow the first one
		at that distance.

		:param axis:             The axis to distribute the children along.
		:param gap:              Optional, the distance between two bounding boxes. Default: ``None``, equal gaps between
		                         the first and the last child.
		:raises ValueError:      If parameter 'axis' is None.
		:raises TypeError:       If parameter 'axis' is not of type :class:`Axis`.
		:raises TypeError:       If parameter 'gap' is not of type :class:`float` or :class:`int`.
		:raises ValueError:      If parameter 'gap' is negative.
		:raises EmptyGroupError: If a group inside this group has no children.
		"""
		if axis is None:
			raise ValueError("Parameter 'axis' is None.")
		elif not isinstance(axis, Axis):
			ex = TypeError("Parameter 'axis' is not of type 'Axis'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(axis)}'.")
			raise ex

		if gap is not None:
			if not isinstance(gap, (int, float)):
				ex = TypeError("Parameter 'gap' is not of type 'float' or 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(gap)}'.")
				raise ex
			elif gap < 0:
				ex = ValueError("Parameter 'gap' is negative.")
				ex.add_note(f"Got value '{gap}'.")
				raise ex

		if len(self._children) < (3 if gap is None else 2):
			return

		entries = []
		for child in self._children:
			box = child.BoundingBox
			if axis is Axis.X:
				entries.append((box._minX, box._maxX, child))
			else:
				entries.append((box._minY, box._maxY, child))

		entries.sort(key=lambda entry: entry[0])
		first = entries[0]
		if gap is None:
			last =  entries[-1]
			gap =   (last[1] - first[0] - sum(high - low for low, high, _ in entries)) / (len(entries) - 1)
			moved = entries[1:-1]
		else:
			moved = entries[1:]

		position = first[1] + gap
		for low, high, child in moved:
			if axis is Axis.X:
				child.Move(Offset2D(position - low, 0))
			else:
				child.Move(Offset2D(0, position - low))

			position += high - low + gap

	def __repr__(self) -> str:
		"""
		Returns the group's string representation.

		:returns: The string representation of the group, its offset and number of children.
		"""
		return f"Group({self._offset}, children={len(self._children)})"


Element2D._PARENT_TYPE = (Group, )
Segment2D._PARENT_TYPE = (Shape, Group)
