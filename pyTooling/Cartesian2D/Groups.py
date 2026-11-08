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
Groups and canvases of 2D cartesian shapes, segments and groups.

The coordinates of everything inside a group are relative to the group, so moving a group changes its offset only. A
canvas is the root of such a tree and knows the direction of its y-axis.

.. seealso::

   :mod:`pyTooling.Cartesian2D`
      |rarr| Points, offsets, bounding boxes and segments.
   :mod:`pyTooling.Cartesian2D.Shapes`
      |rarr| Shapes a group can hold.
"""
from __future__                   import annotations

from enum                         import Enum
from typing                       import Any, Generic, Hashable, Iterable, Mapping, Optional as Nullable, Union

from pyTooling.Decorators         import export, readonly
from pyTooling.Exceptions         import EmptyError
from pyTooling.MetaClasses        import ExtendedType
from pyTooling.Common             import getFullyQualifiedName
from pyTooling.Cartesian2D        import Coordinate, Base2D, Offset2D, Size2D, BoundingBox2D, Alignment2D, Element2D, \
                                         Segment2D, Cartesian2DError, AlreadyOwnedError, GroupCycleError, \
                                         NotOwnedError, NotInSameFrameError
from pyTooling.Cartesian2D.Shapes import Shape


@export
class YAxisDirection(Enum):
	"""Direction, in which the y-coordinates of a canvas grow."""

	Up =   0  #: Y-coordinates grow upwards, as in mathematics.
	Down = 1  #: Y-coordinates grow downwards, as on a screen or in SVG.


@export
class EmptyGroupError(Cartesian2DError, EmptyError):
	"""
	The exception is raised when the bounding box of a group or canvas without children is requested.

	:mod:`pyTooling.Cartesian3D.Groups` raises it too.
	"""


@export
class Container2DMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for elements holding shapes, segments and groups: groups and canvases.

	The coordinates of the children are relative to the container.
	"""

	_children: list[Element2D]  #: Shapes, segments and groups of the container, in insertion order.

	def __init__(self, children: Nullable[Iterable[Element2D]] = None) -> None:
		"""
		Initializes the container's children.

		The children must not belong to another element. They are checked and stored here; the class using this mixin
		sets their parent as its last step, so a failing check of that class leaves them free.

		:param children:           Optional, shapes, segments and groups held by the container. Default: ``None``.
		:raises TypeError:         If parameter 'children' is not iterable.
		:raises ValueError:        If an element of parameter 'children' is None.
		:raises TypeError:         If an element of parameter 'children' is not of type
		                           :class:`~pyTooling.Cartesian2D.Element2D`.
		:raises AlreadyOwnedError: If an element of parameter 'children' belongs to another element.
		:raises ValueError:        If an element of parameter 'children' is given twice.
		"""
		if children is not None and not isinstance(children, Iterable):
			ex = TypeError("Parameter 'children' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(children)}'.")
			raise ex

		self._children = childList = []

		if children is None:
			return

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

	@readonly
	def Children(self) -> tuple[Element2D, ...]:
		"""
		Read-only property to return the shapes, segments and groups of the container (:attr:`_children`).

		:returns: Tuple of children, in insertion order.
		"""
		return tuple(self._children)

	@readonly
	def BoundingBox(self) -> BoundingBox2D:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing all children.

		The bounding box is in the coordinates of the children.

		:returns:                A new bounding box.
		:raises EmptyGroupError: If the container or a group inside it has no children.
		"""
		if len(self._children) == 0:
			ex = EmptyGroupError(f"{self.__class__.__name__} has no children.")
			ex.add_note(f"Got {self!r}.")
			raise ex

		box = self._children[0].BoundingBox
		for child in self._children[1:]:
			box = box.Union(child.BoundingBox)

		return box

	def AddChild(self, child: Element2D) -> None:
		"""
		Add a shape, segment or group to this container.

		The child keeps its coordinates, which are relative to this container from now on.

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

	def RemoveChild(self, child: Element2D) -> None:
		"""
		Remove a shape, segment or group from this container.

		The child keeps its coordinates, which are relative to the origin from now on.

		:param child:          The shape, segment or group to remove.
		:raises ValueError:    If parameter 'child' is None.
		:raises TypeError:     If parameter 'child' is not of type :class:`~pyTooling.Cartesian2D.Element2D`.
		:raises NotOwnedError: If parameter 'child' isn't a child of this container.
		"""
		if child is None:
			raise ValueError("Parameter 'child' is None.")
		elif not isinstance(child, Element2D):
			ex = TypeError("Parameter 'child' is not of type 'Element2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(child)}'.")
			raise ex
		elif child._parent is not self:
			ex = NotOwnedError(f"Element isn't a child of this {self.__class__.__name__}.")
			ex.add_note(f"Got {child!r} owned by {child._parent!r}.")
			raise ex from ValueError(f"Parameter 'child' isn't a child of this {self.__class__.__name__}.")

		child.Parent = None

	def DistributeX(self, gap: Nullable[Coordinate] = None) -> None:
		"""
		Move the children along the x-axis, so the gaps between their bounding boxes are equal.

		The children are ordered by their smallest x-coordinate. The first child keeps its position. Without a gap, the
		last child keeps its position too and the gaps follow from the space between them. With fewer than three children,
		there is then nothing to distribute. With a gap, the other children follow the first one at that distance.

		:param gap:              Optional, the distance between two bounding boxes. Default: ``None``, equal gaps between
		                         the first and the last child.
		:raises TypeError:       If parameter 'gap' is not of type :class:`float` or :class:`int`.
		:raises ValueError:      If parameter 'gap' is negative.
		:raises EmptyGroupError: If a group inside this container has no children.
		"""
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
			entries.append((box._minX, box._maxX, child))

		for child, distance in self._ComputeDistribution(entries, gap):
			child.Move(Offset2D(distance, 0))

	def DistributeY(self, gap: Nullable[Coordinate] = None) -> None:
		"""
		Move the children along the y-axis, so the gaps between their bounding boxes are equal.

		The children are ordered by their smallest y-coordinate. The first child keeps its position. Without a gap, the
		last child keeps its position too and the gaps follow from the space between them. With fewer than three children,
		there is then nothing to distribute. With a gap, the other children follow the first one at that distance.

		:param gap:              Optional, the distance between two bounding boxes. Default: ``None``, equal gaps between
		                         the first and the last child.
		:raises TypeError:       If parameter 'gap' is not of type :class:`float` or :class:`int`.
		:raises ValueError:      If parameter 'gap' is negative.
		:raises EmptyGroupError: If a group inside this container has no children.
		"""
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
			entries.append((box._minY, box._maxY, child))

		for child, distance in self._ComputeDistribution(entries, gap):
			child.Move(Offset2D(0, distance))

	@staticmethod
	def _ComputeDistribution(
		entries: list[tuple[Coordinate, Coordinate, Element2D]],
		gap: Nullable[Coordinate]
	) -> list[tuple[Element2D, Coordinate]]:
		"""
		Compute how far the children move along an axis, so the gaps between their bounding boxes are equal.

		:param entries: Smallest coordinate, largest coordinate and child, for each child.
		:param gap:     The distance between two bounding boxes, or ``None`` for equal gaps between the first and last
		                child.
		:returns:       The children to move, each with the distance to move it by.
		"""
		entries.sort(key=lambda entry: entry[0])
		first = entries[0]
		if gap is None:
			last =  entries[-1]
			gap =   (last[1] - first[0] - sum(high - low for low, high, _ in entries)) / (len(entries) - 1)
			moved = entries[1:-1]
		else:
			moved = entries[1:]

		distances = []
		position =  first[1] + gap
		for low, high, child in moved:
			distances.append((child, position - low))
			position += high - low + gap

		return distances


@export
class Group2D(Element2D[Coordinate], Container2DMixin, Generic[Coordinate]):
	"""
	A group holds shapes, segments and other groups at an offset.

	The coordinates of the group's children are relative to the group's origin, which is placed at :attr:`Offset` in the
	group's own frame. A group without a parent is relative to the origin.
	"""

	_offset: Offset2D[Coordinate]  #: Offset of the group's origin in the group's frame.

	def __init__(
		self,
		offset:        Nullable[Offset2D[Coordinate]] = None,
		children:      Nullable[Iterable[Element2D[Coordinate]]] = None,
		*,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a group at an offset, holding the given children.

		The group takes the children, which must not belong to another element. When parameter 'parent' can't take the
		group, the children stay free.

		:param offset:             Optional, offset of the group's origin. Default: ``None``, which places it at ``(0, 0)``.
		:param children:           Optional, shapes, segments and groups held by the group. Default: ``None``.
		:param value:              Optional, value of the group. Default: ``None``.
		:param keyValuePairs:      Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:             Optional, the group or canvas this group is added to. Default: ``None``, no parent.
		:raises TypeError:         If parameter 'offset' is not of type :class:`~pyTooling.Cartesian2D.Offset2D`.
		:raises TypeError:         If parameter 'children' is not iterable.
		:raises ValueError:        If an element of parameter 'children' is None.
		:raises TypeError:         If an element of parameter 'children' is not of type
		                           :class:`~pyTooling.Cartesian2D.Element2D`.
		:raises AlreadyOwnedError: If an element of parameter 'children' belongs to another element.
		:raises ValueError:        If an element of parameter 'children' is given twice.
		:raises TypeError:         If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:         If parameter 'parent' is not of type :class:`Group2D` or :class:`Canvas2D`.
		:raises GroupCycleError:   If parameter 'parent' is inside an element of parameter 'children'.
		"""
		super().__init__(value=value, keyValuePairs=keyValuePairs, parent=parent)
		Container2DMixin.__init__(self, children)

		if offset is not None and not isinstance(offset, Offset2D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._offset = Offset2D(0, 0) if offset is None else offset.Copy()

		for child in self._children:
			child._parent = self

		try:
			self.Parent = parent
		except GroupCycleError:
			for child in self._children:
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
	def _ChildFrame(self) -> Group2D[Coordinate]:
		"""
		Read-only property to access the frame the coordinates of this group's children are relative to: the group itself.

		:returns: This group.
		"""
		return self

	@readonly
	def BoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing all children.

		The union of the children's bounding boxes is shifted by :attr:`Offset`, so the bounding box is in the group's
		frame.

		:returns:                A new bounding box.
		:raises EmptyGroupError: If the group or a group inside it has no children.
		"""
		return Container2DMixin.BoundingBox.fget(self) + self._offset

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

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the group at a horizontal axis by mirroring the y-component of its :attr:`Offset` (inplace).

		The children are mirrored at the group's origin: every y-coordinate inside the group is negated.

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		self._offset._yOffset = twiceAxis - self._offset._yOffset
		for child in self._children:
			child._MirrorY(0)

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the group at a vertical axis by mirroring the x-component of its :attr:`Offset` (inplace).

		The children are mirrored at the group's origin: every x-coordinate inside the group is negated.

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		self._offset._xOffset = twiceAxis - self._offset._xOffset
		for child in self._children:
			child._MirrorX(0)

	def __repr__(self) -> str:
		"""
		Returns the group's string representation.

		:returns: The string representation of the group, its offset and number of children.
		"""
		return f"Group2D({self._offset}, children={len(self._children)})"


@export
class Canvas2D(Base2D[Coordinate], Container2DMixin, Generic[Coordinate]):
	"""
	A canvas is the root of a drawing: it holds shapes, segments and groups, and knows the direction of its y-axis.

	The coordinates of the canvas' children are relative to the origin. A canvas has an optional :attr:`Size`; without
	one, it is open in every direction.

	As the root, it has no parent and no frame: :attr:`~pyTooling.Cartesian2D.Base2D.Parent` and
	:attr:`~pyTooling.Cartesian2D.Base2D.Frame` are always ``None``.
	"""

	_direction: YAxisDirection    #: Direction, in which the y-coordinates grow.
	_size:      Nullable[Size2D]  #: Width and height of the canvas from the origin, or ``None`` for an open canvas.

	def __init__(
		self,
		direction: YAxisDirection = YAxisDirection.Up,
		size:      Nullable[Size2D[Coordinate]] = None,
		children:  Nullable[Iterable[Element2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a canvas with a y-axis direction and an optional size, holding the given children.

		The canvas takes the children, which must not belong to another element.

		:param direction:          Optional, direction, in which the y-coordinates grow. Default: ``YAxisDirection.Up``.
		:param size:               Optional, width and height of the canvas, starting at the origin. Default: ``None``,
		                           which makes an open canvas.
		:param children:           Optional, shapes, segments and groups held by the canvas. Default: ``None``.
		:raises ValueError:        If parameter 'direction' is None.
		:raises TypeError:         If parameter 'direction' is not of type :class:`YAxisDirection`.
		:raises TypeError:         If parameter 'size' is not of type :class:`~pyTooling.Cartesian2D.Size2D`.
		:raises TypeError:         If parameter 'children' is not iterable.
		:raises ValueError:        If an element of parameter 'children' is None.
		:raises TypeError:         If an element of parameter 'children' is not of type
		                           :class:`~pyTooling.Cartesian2D.Element2D`.
		:raises AlreadyOwnedError: If an element of parameter 'children' belongs to another element.
		:raises ValueError:        If an element of parameter 'children' is given twice.
		"""
		super().__init__()
		Container2DMixin.__init__(self, children)

		if direction is None:
			raise ValueError("Parameter 'direction' is None.")
		elif not isinstance(direction, YAxisDirection):
			ex = TypeError("Parameter 'direction' is not of type 'YAxisDirection'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(direction)}'.")
			raise ex

		if size is not None and not isinstance(size, Size2D):
			ex = TypeError("Parameter 'size' is not of type 'Size2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(size)}'.")
			raise ex

		self._direction = direction
		self._size =      None if size is None else size.Copy()

		for child in self._children:
			child._parent = self

	@readonly
	def Direction(self) -> YAxisDirection:
		"""
		Read-only property to access the direction, in which the y-coordinates grow (:attr:`_direction`).

		:meth:`Mirror` changes it.

		:returns: The y-axis direction.
		"""
		return self._direction

	@readonly
	def Size(self) -> Nullable[Size2D[Coordinate]]:
		"""
		Read-only property to access the width and height of the canvas (:attr:`_size`).

		:returns: The canvas' size, or ``None`` for an open canvas.
		"""
		return self._size

	@readonly
	def AbsoluteOffset(self) -> Offset2D[Coordinate]:
		"""
		Read-only property to return the offset of the canvas' origin relative to the origin.

		:returns: A new 2D-offset ``(0, 0)``.
		"""
		return Offset2D(0, 0)

	@Base2D.Parent.setter
	def Parent(self, parent: None) -> None:
		ex = TypeError(f"A '{getFullyQualifiedName(self)}' has no parent.")
		ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
		raise ex

	@readonly
	def _ChildFrame(self) -> Canvas2D[Coordinate]:
		"""
		Read-only property to access the frame the coordinates of this canvas' children are relative to: the canvas itself.

		:returns: This canvas.
		"""
		return self

	@readonly
	def TopAlignment(self) -> Alignment2D:
		"""
		Read-only property to return the alignment of the elements' top edges on this canvas.

		:returns: :attr:`Alignment2D.MaxY <pyTooling.Cartesian2D.Alignment2D.MaxY>`, if the y-axis points up, else
		          :attr:`Alignment2D.MinY <pyTooling.Cartesian2D.Alignment2D.MinY>`.
		"""
		return Alignment2D.MaxY if self._direction is YAxisDirection.Up else Alignment2D.MinY

	@readonly
	def BottomAlignment(self) -> Alignment2D:
		"""
		Read-only property to return the alignment of the elements' bottom edges on this canvas.

		:returns: :attr:`Alignment2D.MinY <pyTooling.Cartesian2D.Alignment2D.MinY>`, if the y-axis points up, else
		          :attr:`Alignment2D.MaxY <pyTooling.Cartesian2D.Alignment2D.MaxY>`.
		"""
		return Alignment2D.MinY if self._direction is YAxisDirection.Up else Alignment2D.MaxY

	def Top(self, element: Element2D[Coordinate]) -> Coordinate:
		"""
		Return the absolute y-coordinate of an element's top edge on this canvas.

		:param element:              An element on this canvas.
		:returns:                    The largest absolute y-coordinate of the element, if the y-axis points up, else the
		                             smallest one.
		:raises ValueError:          If parameter 'element' is None.
		:raises TypeError:           If parameter 'element' is not of type :class:`~pyTooling.Cartesian2D.Element2D`.
		:raises NotInSameFrameError: If parameter 'element' isn't on this canvas.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, Element2D):
			ex = TypeError("Parameter 'element' is not of type 'Element2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		frame = element.Frame
		while frame is not None and frame is not self:
			frame = frame.Frame

		if frame is None:
			ex = NotInSameFrameError("Element isn't on this canvas.")
			ex.add_note(f"Got {element!r}.")
			raise ex from ValueError("Parameter 'element' isn't on this canvas.")

		box = element.AbsoluteBoundingBox
		return box._maxY if self._direction is YAxisDirection.Up else box._minY

	def Bottom(self, element: Element2D[Coordinate]) -> Coordinate:
		"""
		Return the absolute y-coordinate of an element's bottom edge on this canvas.

		:param element:              An element on this canvas.
		:returns:                    The smallest absolute y-coordinate of the element, if the y-axis points up, else the
		                             largest one.
		:raises ValueError:          If parameter 'element' is None.
		:raises TypeError:           If parameter 'element' is not of type :class:`~pyTooling.Cartesian2D.Element2D`.
		:raises NotInSameFrameError: If parameter 'element' isn't on this canvas.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, Element2D):
			ex = TypeError("Parameter 'element' is not of type 'Element2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		frame = element.Frame
		while frame is not None and frame is not self:
			frame = frame.Frame

		if frame is None:
			ex = NotInSameFrameError("Element isn't on this canvas.")
			ex.add_note(f"Got {element!r}.")
			raise ex from ValueError("Parameter 'element' isn't on this canvas.")

		box = element.AbsoluteBoundingBox
		return box._minY if self._direction is YAxisDirection.Up else box._maxY

	def Mirror(self) -> None:
		"""
		Flip the canvas to the other y-axis direction, keeping the drawing's appearance (inplace).

		Every level of the drawing negates its y-coordinates: a group's offset relative to its parent, and every point
		relative to its group. On a canvas with a :attr:`Size`, the top level uses ``height - y`` instead, so the
		drawing stays within the canvas.
		"""
		height = 0 if self._size is None else self._size._height
		for child in self._children:
			child._MirrorY(height)

		self._direction = YAxisDirection.Down if self._direction is YAxisDirection.Up else YAxisDirection.Up

	def __repr__(self) -> str:
		"""
		Returns the canvas' string representation.

		:returns: The string representation of the canvas, its direction, size and number of children.
		"""
		return f"Canvas2D({self._direction.name}, {self._size}, children={len(self._children)})"


Element2D._PARENT_TYPE = (Group2D, Canvas2D)
Segment2D._PARENT_TYPE = (Shape, Group2D, Canvas2D)
