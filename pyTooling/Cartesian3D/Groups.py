# ==================================================================================================================== #
#             _____           _ _               ____           _            _             _____ ____                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _ _ __| |_ ___  ___(_) __ _ _ __ |___ /|  _ \                  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | '__| __/ _ \/ __| |/ _` | '_ \  |_ \| | | |                 #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | |  | ||  __/\__ \ | (_| | | | |___) | |_| |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|   \__\___||___/_|\__,_|_| |_|____/|____/                  #
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
Groups of 3D cartesian segments and groups.

The coordinates of everything inside a group are relative to the group, so moving a group changes its offset only.

.. seealso::

   :mod:`pyTooling.Cartesian3D`
      |rarr| Points, offsets, bounding boxes and segments.
   :mod:`pyTooling.Cartesian2D.Groups`
      |rarr| The same groups in two dimensions, and a canvas.
"""
from __future__                   import annotations

from copy                         import deepcopy
from typing                       import Any, Generic, Hashable, Iterable, Mapping, Optional as Nullable, Self

from pyTooling.Decorators         import export, readonly
from pyTooling.MetaClasses        import ExtendedType
from pyTooling.Common             import getFullyQualifiedName
from pyTooling.Cartesian2D        import Coordinate, AlreadyOwnedError, NotOwnedError, GroupCycleError
from pyTooling.Cartesian2D.Groups import EmptyGroupError
from pyTooling.Cartesian3D        import Offset3D, BoundingBox3D, Element3D


@export
class Container3DMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for elements holding segments and groups, like :class:`Group3D`.

	The coordinates of the children are relative to the container.
	"""

	_children: list[Element3D]  #: Segments and groups of the container, in insertion order.

	def __init__(self, children: Nullable[Iterable[Element3D]] = None) -> None:
		"""
		Initializes the container's children.

		The children must not belong to another element. They are checked and stored here; the class using this mixin
		sets their parent as its last step, so a failing check of that class leaves them free.

		:param children:           Optional, segments and groups held by the container. Default: ``None``.
		:raises TypeError:         If parameter 'children' is not iterable.
		:raises ValueError:        If an element of parameter 'children' is None.
		:raises TypeError:         If an element of parameter 'children' is not of type
		                           :class:`~pyTooling.Cartesian3D.Element3D`.
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
			elif not isinstance(child, Element3D):
				ex = TypeError("An element of parameter 'children' is not of type 'Element3D'.")
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
	def Children(self) -> tuple[Element3D, ...]:
		"""
		Read-only property to return the segments and groups of the container (:attr:`_children`).

		:returns: Tuple of children, in insertion order.
		"""
		return tuple(self._children)

	@readonly
	def BoundingBox(self) -> BoundingBox3D:
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

	def AddChild(self, child: Element3D) -> None:
		"""
		Add a segment or group to this container.

		The child keeps its coordinates, which are relative to this container from now on.

		:param child:              The segment or group to add.
		:raises ValueError:        If parameter 'child' is None.
		:raises TypeError:         If parameter 'child' is not of type :class:`~pyTooling.Cartesian3D.Element3D`.
		:raises AlreadyOwnedError: If parameter 'child' belongs to another element. |br|
		                           Use :meth:`~pyTooling.Cartesian3D.Element3D.MoveTo` to move it between groups.
		:raises GroupCycleError:   If parameter 'child' is this group or one of its ancestors.
		"""
		if child is None:
			raise ValueError("Parameter 'child' is None.")
		elif not isinstance(child, Element3D):
			ex = TypeError("Parameter 'child' is not of type 'Element3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(child)}'.")
			raise ex
		elif child._parent is not None:
			ex = AlreadyOwnedError("Element is owned by another element already.")
			ex.add_note(f"Got {child!r} owned by {child._parent!r}.")
			ex.add_note("Use 'MoveTo' to move it between groups.")
			raise ex from ValueError("Parameter 'child' belongs to another element.")

		child.Parent = self

	def RemoveChild(self, child: Element3D) -> None:
		"""
		Remove a segment or group from this container.

		The child keeps its coordinates, which are relative to the origin from now on.

		:param child:          The segment or group to remove.
		:raises ValueError:    If parameter 'child' is None.
		:raises TypeError:     If parameter 'child' is not of type :class:`~pyTooling.Cartesian3D.Element3D`.
		:raises NotOwnedError: If parameter 'child' isn't a child of this container.
		"""
		if child is None:
			raise ValueError("Parameter 'child' is None.")
		elif not isinstance(child, Element3D):
			ex = TypeError("Parameter 'child' is not of type 'Element3D'.")
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
			child.Move(Offset3D(distance, 0, 0))

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
			child.Move(Offset3D(0, distance, 0))

	def DistributeZ(self, gap: Nullable[Coordinate] = None) -> None:
		"""
		Move the children along the z-axis, so the gaps between their bounding boxes are equal.

		The children are ordered by their smallest z-coordinate. The first child keeps its position. Without a gap, the
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
			entries.append((box._minZ, box._maxZ, child))

		for child, distance in self._ComputeDistribution(entries, gap):
			child.Move(Offset3D(0, 0, distance))

	@staticmethod
	def _ComputeDistribution(
		entries: list[tuple[Coordinate, Coordinate, Element3D]],
		gap: Nullable[Coordinate]
	) -> list[tuple[Element3D, Coordinate]]:
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
class Group3D(Element3D[Coordinate], Container3DMixin, Generic[Coordinate]):
	"""
	A group holds segments and other groups at an offset.

	The coordinates of the group's children are relative to the group's origin, which is placed at :attr:`Offset` in the
	group's own frame. A group without a parent is relative to the origin.
	"""

	_offset: Offset3D[Coordinate]  #: Offset of the group's origin in the group's frame.

	def __init__(
		self,
		offset:        Nullable[Offset3D[Coordinate]] = None,
		children:      Nullable[Iterable[Element3D[Coordinate]]] = None,
		*,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Group3D[Coordinate]] = None
	) -> None:
		"""
		Initializes a group at an offset, holding the given children.

		The group takes the children, which must not belong to another element. When parameter 'parent' can't take the
		group, the children stay free.

		:param offset:             Optional, offset of the group's origin. Default: ``None``, which places it at
		                           ``(0, 0, 0)``.
		:param children:           Optional, segments and groups held by the group. Default: ``None``.
		:param value:              Optional, value of the group. Default: ``None``.
		:param keyValuePairs:      Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:             Optional, the group this group is added to. Default: ``None``, no parent.
		:raises TypeError:         If parameter 'offset' is not of type :class:`~pyTooling.Cartesian3D.Offset3D`.
		:raises TypeError:         If parameter 'children' is not iterable.
		:raises ValueError:        If an element of parameter 'children' is None.
		:raises TypeError:         If an element of parameter 'children' is not of type
		                           :class:`~pyTooling.Cartesian3D.Element3D`.
		:raises AlreadyOwnedError: If an element of parameter 'children' belongs to another element.
		:raises ValueError:        If an element of parameter 'children' is given twice.
		:raises TypeError:         If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:         If parameter 'parent' is not of type :class:`Group3D`.
		:raises GroupCycleError:   If parameter 'parent' is inside an element of parameter 'children'.
		"""
		super().__init__(value=value, keyValuePairs=keyValuePairs, parent=parent)
		Container3DMixin.__init__(self, children)

		if offset is not None and not isinstance(offset, Offset3D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._offset = Offset3D(0, 0, 0) if offset is None else offset.Copy()

		for child in self._children:
			child._parent = self

		try:
			self.Parent = parent
		except GroupCycleError:
			for child in self._children:
				child._parent = None

			raise

	@property
	def Offset(self) -> Offset3D[Coordinate]:
		"""
		Property to access the offset of the group's origin in the group's frame (:attr:`_offset`).

		An assigned offset is copied, so groups never share an offset.

		:returns:           The group's offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`~pyTooling.Cartesian3D.Offset3D`.
		"""
		return self._offset

	@Offset.setter
	def Offset(self, offset: Offset3D[Coordinate]) -> None:
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, Offset3D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._offset = offset.Copy()

	@readonly
	def AbsoluteOffset(self) -> Offset3D[Coordinate]:
		"""
		Read-only property to return the offset of the group's origin relative to the origin.

		The offsets of all groups up the parent chain are added to :attr:`Offset`.

		:returns: A new 3D-offset.
		"""
		frame = self.Frame
		return self._offset.Copy() if frame is None else self._offset + frame.AbsoluteOffset

	@readonly
	def _ChildFrame(self) -> Group3D[Coordinate]:
		"""
		Read-only property to access the frame the coordinates of this group's children are relative to: the group itself.

		:returns: This group.
		"""
		return self

	@readonly
	def BoundingBox(self) -> BoundingBox3D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing all children.

		The union of the children's bounding boxes is shifted by :attr:`Offset`, so the bounding box is in the group's
		frame.

		:returns:                A new bounding box.
		:raises EmptyGroupError: If the group or a group inside it has no children.
		"""
		return Container3DMixin.BoundingBox.fget(self) + self._offset

	def Move(self, offset: Offset3D[Coordinate]) -> None:
		"""
		Move the group by changing its :attr:`Offset` (inplace).

		The children keep their coordinates.

		:param offset:      The 3D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`~pyTooling.Cartesian3D.Offset3D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, Offset3D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._offset += offset

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the group at a plane parallel to the yz-plane by mirroring the x-component of its :attr:`Offset` (inplace).

		The children are mirrored at the group's origin: every x-coordinate inside the group is negated.

		:param twiceAxis: Twice the x-coordinate of the plane.
		"""
		self._offset._xOffset = twiceAxis - self._offset._xOffset
		for child in self._children:
			child._MirrorX(0)

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the group at a plane parallel to the xz-plane by mirroring the y-component of its :attr:`Offset` (inplace).

		The children are mirrored at the group's origin: every y-coordinate inside the group is negated.

		:param twiceAxis: Twice the y-coordinate of the plane.
		"""
		self._offset._yOffset = twiceAxis - self._offset._yOffset
		for child in self._children:
			child._MirrorY(0)

	def _MirrorZ(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the group at a plane parallel to the xy-plane by mirroring the z-component of its :attr:`Offset` (inplace).

		The children are mirrored at the group's origin: every z-coordinate inside the group is negated.

		:param twiceAxis: Twice the z-coordinate of the plane.
		"""
		self._offset._zOffset = twiceAxis - self._offset._zOffset
		for child in self._children:
			child._MirrorZ(0)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this group for :func:`copy.deepcopy`.

		The copy holds a copy of the offset, deep copies of the children, and deep copies of the :attr:`Value` and the
		key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this group.
		"""
		return self.__class__(
			self._offset,
			(deepcopy(child, memo) for child in self._children),
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

	def __repr__(self) -> str:
		"""
		Returns the group's string representation.

		:returns: The string representation of the group, its offset and number of children.
		"""
		return f"Group3D({self._offset}, children={len(self._children)})"


Element3D._PARENT_TYPE = (Group3D, )
