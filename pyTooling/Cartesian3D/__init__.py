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
# Copyright 2025-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
An implementation of 3D cartesian data structures for Python.

.. seealso::

   :mod:`pyTooling.Cartesian2D`
      |rarr| The same data structures in two dimensions.
   :mod:`pyTooling.Cartesian3D.Volumes`
      |rarr| Volumes built from these points and offsets.
   :mod:`pyTooling.Cartesian3D.Groups`
      |rarr| Groups of segments and groups, with coordinates relative to the group.
"""
from __future__            import annotations

from math                  import atan2, sqrt
from typing                import TYPE_CHECKING, Any, ClassVar, Generic, Iterable, Optional as Nullable, Self, Union

from pyTooling.Decorators  import readonly, export
from pyTooling.MetaClasses import ExtendedType, abstractclass, abstractmethod
from pyTooling.Exceptions  import InvalidOperationError
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Cartesian2D import Coordinate, AlreadyOwnedError, DuplicatePointError, GroupCycleError, \
                                  NotInSameFrameError

if TYPE_CHECKING:
	from pyTooling.Cartesian3D.Groups import Group3D


@export
@abstractclass
class Base3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	Abstract base-class of everything having a parent and coordinates relative to a frame: points, segments and groups.

	A frame is what the coordinates are relative to, and a group is the frame of its children. Every frame is an instance
	of this class.
	"""

	_PARENT_TYPE: ClassVar[tuple[type, ...]]  #: Types a parent of this class can have.

	_parent: Nullable[Base3D[Coordinate]]  #: Parent of this object, or ``None``.

	def __init__(self, *, parent: Nullable[Base3D[Coordinate]] = None) -> None:
		"""
		Initializes the parent relation.

		:param parent:     Optional, the parent of this object. Default: ``None``, no parent.
		:raises TypeError: If parameter 'parent' is not of a type in :attr:`_PARENT_TYPE`.
		"""
		if parent is not None and not isinstance(parent, self._PARENT_TYPE):
			typeNames = " or ".join(f"'{parentType.__name__}'" for parentType in self._PARENT_TYPE)
			ex =        TypeError(f"Parameter 'parent' is not of type {typeNames}.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent

	@property
	def Parent(self) -> Nullable[Base3D[Coordinate]]:
		"""
		Property to access the parent of this object (:attr:`_parent`).

		A point's parent is the segment owning it. A segment's or group's parent is the group holding it.

		Only an :class:`Element3D` can be assigned a parent. Assigning a group moves the element into it, assigning
		``None`` removes it from its parent. The element keeps its local coordinates, so its absolute position changes with
		the frame.

		:returns:                The parent, or ``None``, if this object has no parent.
		:raises TypeError:       If an assigned value is not of a type in :attr:`_PARENT_TYPE`.
		:raises TypeError:       If a parent is assigned to a :class:`Point3D`.
		:raises TypeError:       If an assigned value is not of type :class:`~pyTooling.Cartesian3D.Groups.Group3D`, while
		                         this object is an :class:`Element3D`.
		:raises GroupCycleError: If an assigned group is this element or one of its descendants.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, parent: Nullable[Base3D[Coordinate]]) -> None:
		if parent is not None and not isinstance(parent, self._PARENT_TYPE):
			typeNames = " or ".join(f"'{parentType.__name__}'" for parentType in self._PARENT_TYPE)
			ex =        TypeError(f"Parameter 'parent' is not of type {typeNames}.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent

	@readonly
	def Frame(self) -> Nullable[Base3D[Coordinate]]:
		"""
		Read-only property to return the frame this object's coordinates are relative to.

		The frame comes from the parent. An object without a parent has no frame, its coordinates are relative to the
		origin.

		:returns: The frame, or ``None``, if this object has no frame.
		"""
		return None if self._parent is None else self._parent._ChildFrame

	@readonly
	def _ChildFrame(self) -> Nullable[Base3D[Coordinate]]:
		"""
		Read-only property to access the frame the coordinates of this object's children are relative to (:attr:`Frame`).

		:returns: This object's frame, or ``None``, if this object has no frame.
		"""
		return self.Frame


@export
class Point3D(Base3D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 3D cartesian point."""

	_x: Coordinate  #: The x-direction coordinate.
	_y: Coordinate  #: The y-direction coordinate.
	_z: Coordinate  #: The z-direction coordinate.

	def __init__(
		self,
		x:      Coordinate,
		y:      Coordinate,
		z:      Coordinate,
		*,
		parent: Nullable[Element3D[Coordinate]] = None
	) -> None:
		"""
		Initializes a 3-dimensional point.

		A segment takes ownership of the point, when it's given the point instead of copying it.

		Parameter ``parent`` sets the owner, but doesn't register the point in it: the parent's points don't change. The
		point is in the parent's frame, so it can be combined with the parent's points.

		:param x:           X-coordinate.
		:param y:           Y-coordinate.
		:param z:           Z-coordinate.
		:param parent:      Optional, the segment owning the point. Default: ``None``, no owner.
		:raises ValueError: If parameter 'x' is None.
		:raises TypeError:  If parameter 'x' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'y' is None.
		:raises TypeError:  If parameter 'y' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'z' is None.
		:raises TypeError:  If parameter 'z' is not of type :class:`float` or :class:`int`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Element3D`.
		"""
		super().__init__(parent=parent)

		if x is None:
			raise ValueError("Parameter 'x' is None.")
		elif not isinstance(x, (int, float)):
			ex = TypeError("Parameter 'x' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(x)}'.")
			raise ex

		if y is None:
			raise ValueError("Parameter 'y' is None.")
		elif not isinstance(y, (int, float)):
			ex = TypeError("Parameter 'y' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(y)}'.")
			raise ex

		if z is None:
			raise ValueError("Parameter 'z' is None.")
		elif not isinstance(z, (int, float)):
			ex = TypeError("Parameter 'z' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(z)}'.")
			raise ex

		self._x = x
		self._y = y
		self._z = z

	@Base3D.Parent.setter
	def Parent(self, parent: Nullable[Element3D[Coordinate]]) -> None:
		ex = TypeError(f"The parent of a '{getFullyQualifiedName(self)}' is read-only.")
		ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
		ex.add_note("A segment takes ownership of a point, when it's given the point.")
		raise ex

	@property
	def X(self) -> Coordinate:
		"""
		Property to access the x-direction coordinate (:attr:`_x`).

		``x`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The x-direction coordinate.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._x

	@X.setter
	def X(self, x: Coordinate) -> None:
		if x is None:
			raise ValueError("Parameter 'x' is None.")
		elif not isinstance(x, (int, float)):
			ex = TypeError("Parameter 'x' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(x)}'.")
			raise ex

		self._x = x

	x = X

	@property
	def Y(self) -> Coordinate:
		"""
		Property to access the y-direction coordinate (:attr:`_y`).

		``y`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The y-direction coordinate.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._y

	@Y.setter
	def Y(self, y: Coordinate) -> None:
		if y is None:
			raise ValueError("Parameter 'y' is None.")
		elif not isinstance(y, (int, float)):
			ex = TypeError("Parameter 'y' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(y)}'.")
			raise ex

		self._y = y

	y = Y

	@property
	def Z(self) -> Coordinate:
		"""
		Property to access the z-direction coordinate (:attr:`_z`).

		``z`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The z-direction coordinate.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._z

	@Z.setter
	def Z(self, z: Coordinate) -> None:
		if z is None:
			raise ValueError("Parameter 'z' is None.")
		elif not isinstance(z, (int, float)):
			ex = TypeError("Parameter 'z' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(z)}'.")
			raise ex

		self._z = z

	z = Z

	@readonly
	def Absolute(self) -> Point3D[Coordinate]:
		"""
		Read-only property to return the point's position relative to the origin as a new 3D-point.

		The offsets of all groups up the parent chain are added to the point's coordinates. The new point has no owner.

		:returns: A new 3D-point with absolute coordinates.
		"""
		if (frame := self.Frame) is None:
			return Point3D(self._x, self._y, self._z)

		offset = frame.AbsoluteOffset
		return Point3D(self._x + offset._xOffset, self._y + offset._yOffset, self._z + offset._zOffset)

	def Copy(self) -> Self:
		"""
		Create a new 3D-point as a copy of this 3D point.

		The copy has no owner.

		:returns: Copy of this 3D-point.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 3D-point moved by a positive 3D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 3D-point moved by a negative 3D-offset.
		"""
		return self.__class__(self._x, self._y, self._z)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 3D-point for :func:`copy.copy`.

		:returns: Copy of this 3D-point.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 3D-point for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 3D-point.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate, Coordinate]:
		"""
		Convert this 3D-Point to a simple 3-element tuple.

		:returns: ``(x, y, z)`` tuple.
		"""
		return self._x, self._y, self._z

	def __add__(self, other: Any) -> Point3D[Coordinate]:
		"""
		Adds a 3D-offset to this 3D-point and creates a new 3D-point.

		:param other:      A 3D-offset as :class:`Offset3D` or tuple.
		:returns:          A new 3D-point shifted by the 3D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			return self.__class__(
				self._x + other._xOffset,
				self._y + other._yOffset,
				self._z + other._zOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self._x + other[0],
				self._y + other[1],
				self._z + other[2]
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> Self:
		"""
		Adds a 3D-offset to this 3D-point (inplace).

		:param other:      A 3D-offset as :class:`Offset3D` or tuple.
		:returns:          This 3D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			self._x += other._xOffset
			self._y += other._yOffset
			self._z += other._zOffset
		elif isinstance(other, tuple):
			self.X += other[0]
			self.Y += other[1]
			self.Z += other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> Union[Offset3D[Coordinate], Point3D[Coordinate]]:
		"""
		Subtract two 3D-Points from each other and create a new 3D-offset.

		:param other:                The second 3D-point as :class:`Point3D`.
		:returns:                    A new 3D-offset representing the distance between these two points.
		:raises TypeError:           If parameter 'other' is not of type :class:`Point3D`.
		:raises NotInSameFrameError: If parameter 'other' is in another frame than this point. |br|
		                             Subtract the points' :attr:`Absolute` positions instead.
		"""
		if isinstance(other, Point3D):
			if self.Frame is not other.Frame:
				ex = NotInSameFrameError("Points are in different frames.")
				ex.add_note(f"Got points {self} and {other}.")
				ex.add_note("Subtract the points' 'Absolute' positions instead.")
				raise ex from ValueError("Parameter 'other' is in another frame.")

			return Offset3D(
				self._x - other._x,
				self._y - other._y,
				self._z - other._z
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> Self:
		"""
		Subtracts a 3D-offset to this 3D-point (inplace).

		:param other:      A 3D-offset as :class:`Offset3D` or tuple.
		:returns:          This 3D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			self._x -= other._xOffset
			self._y -= other._yOffset
			self._z -= other._zOffset
		elif isinstance(other, tuple):
			self.X -= other[0]
			self.Y -= other[1]
			self.Z -= other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __repr__(self) -> str:
		"""
		Returns the 3D point's string representation.

		:returns: The string representation of the 3D point.
		"""
		return f"Point3D({self._x}, {self._y}, {self._z})"

	def __str__(self) -> str:
		"""
		Returns the 3D point's string equivalent.

		:returns: The string equivalent of the 3D point.
		"""
		return f"({self._x}, {self._y}, {self._z})"


@export
class Origin3D(Point3D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 3D cartesian origin."""

	def __init__(self) -> None:
		"""
		Initializes a 3-dimensional origin.
		"""
		super().__init__(0, 0, 0)

	def Copy(self) -> Self:
		"""
		An origin is a singular point, so it can't be copied.

		:raises InvalidOperationError: Always, because an origin is a singular point.
		"""
		raise InvalidOperationError("An origin can't be copied.")

	def __repr__(self) -> str:
		"""
		Returns the 3D origin's string representation.

		:returns: The string representation of the 3D origin.
		"""
		return f"Origin3D({self._x}, {self._y}, {self._z})"


@export
class Element3D(Base3D[Coordinate], Generic[Coordinate]):
	"""
	Abstract base-class of all elements a :class:`~pyTooling.Cartesian3D.Groups.Group3D` can hold: segments and groups.

	An element belongs to at most one group, its :attr:`Parent`. Its coordinates are relative to its parent, an element
	without a parent is relative to the origin.

	A derived class implements :attr:`BoundingBox` and :meth:`Move`. Its initializer takes the keyword-only parameter
	``parent`` and assigns it to :attr:`Parent` as its last statement, when the element is fully initialized.
	"""

	def __init__(self, *, parent: Nullable[Group3D[Coordinate]] = None) -> None:
		"""
		Initializes an element without a parent and checks the group it will be registered in.

		:param parent:     Optional, the group the derived class registers the element in. Default: ``None``, no parent.
		:raises TypeError: If parameter 'parent' is not of type :class:`~pyTooling.Cartesian3D.Groups.Group3D`.
		"""
		# Imported for its side effect: it assigns '_PARENT_TYPE' of the element classes.
		from pyTooling.Cartesian3D import Groups

		super().__init__(parent=parent)

		# The derived class registers the element by assigning 'Parent' as its last statement.
		self._parent = None

	@Base3D.Parent.setter
	def Parent(self, parent: Nullable[Group3D]) -> None:
		from pyTooling.Cartesian3D.Groups import Container3DMixin

		if parent is not None and not isinstance(parent, Container3DMixin):
			ex = TypeError("Parameter 'parent' is not of type 'Group3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex
		elif parent is self._parent:
			return

		frame = parent
		while frame is not None:
			if frame is self:
				ex = GroupCycleError("Group would contain itself.")
				ex.add_note(f"Got {parent!r} as parent of {self!r}.")
				raise ex from ValueError("Parameter 'parent' is this element or one of its descendants.")

			frame = frame.Frame

		if self._parent is not None:
			self._parent._children.remove(self)

		if parent is not None:
			parent._children.append(self)

		Base3D.Parent.fset(self, parent)

	@readonly
	@abstractmethod
	def BoundingBox(self) -> BoundingBox3D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the element.

		The bounding box is in the element's frame.

		:returns: A new bounding box.
		"""

	@readonly
	def AbsoluteBoundingBox(self) -> BoundingBox3D[Coordinate]:
		"""
		Read-only property to return the element's bounding box relative to the origin.

		The offsets of all groups up the parent chain are added to :attr:`BoundingBox`.

		:returns: A new bounding box.
		"""
		frame = self.Frame
		return self.BoundingBox if frame is None else self.BoundingBox + frame.AbsoluteOffset

	@abstractmethod
	def Move(self, offset: Offset3D[Coordinate]) -> None:
		"""
		Move the element by an offset in its frame (inplace).

		:param offset: The 3D-offset to move by.
		"""


Point3D._PARENT_TYPE = (Element3D, )


@export
class Offset3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 3D cartesian offset."""

	_xOffset: Coordinate  #: The x-direction offset
	_yOffset: Coordinate  #: The y-direction offset
	_zOffset: Coordinate  #: The z-direction offset

	def __init__(self, xOffset: Coordinate, yOffset: Coordinate, zOffset: Coordinate) -> None:
		"""
		Initializes a 3-dimensional offset.

		:param xOffset:     x-direction offset.
		:param yOffset:     y-direction offset.
		:param zOffset:     z-direction offset.
		:raises ValueError: If parameter 'xOffset' is None.
		:raises TypeError:  If parameter 'xOffset' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'yOffset' is None.
		:raises TypeError:  If parameter 'yOffset' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'zOffset' is None.
		:raises TypeError:  If parameter 'zOffset' is not of type :class:`float` or :class:`int`.
		"""
		if xOffset is None:
			raise ValueError("Parameter 'xOffset' is None.")
		elif not isinstance(xOffset, (int, float)):
			ex = TypeError("Parameter 'xOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(xOffset)}'.")
			raise ex

		if yOffset is None:
			raise ValueError("Parameter 'yOffset' is None.")
		elif not isinstance(yOffset, (int, float)):
			ex = TypeError("Parameter 'yOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(yOffset)}'.")
			raise ex

		if zOffset is None:
			raise ValueError("Parameter 'zOffset' is None.")
		elif not isinstance(zOffset, (int, float)):
			ex = TypeError("Parameter 'zOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(zOffset)}'.")
			raise ex

		self._xOffset = xOffset
		self._yOffset = yOffset
		self._zOffset = zOffset

	@property
	def XOffset(self) -> Coordinate:
		"""
		Property to access the x-direction offset (:attr:`_xOffset`).

		``xOffset`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The x-direction offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._xOffset

	@XOffset.setter
	def XOffset(self, xOffset: Coordinate) -> None:
		if xOffset is None:
			raise ValueError("Parameter 'xOffset' is None.")
		elif not isinstance(xOffset, (int, float)):
			ex = TypeError("Parameter 'xOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(xOffset)}'.")
			raise ex

		self._xOffset = xOffset

	xOffset = XOffset

	@property
	def YOffset(self) -> Coordinate:
		"""
		Property to access the y-direction offset (:attr:`_yOffset`).

		``yOffset`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The y-direction offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._yOffset

	@YOffset.setter
	def YOffset(self, yOffset: Coordinate) -> None:
		if yOffset is None:
			raise ValueError("Parameter 'yOffset' is None.")
		elif not isinstance(yOffset, (int, float)):
			ex = TypeError("Parameter 'yOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(yOffset)}'.")
			raise ex

		self._yOffset = yOffset

	yOffset = YOffset

	@property
	def ZOffset(self) -> Coordinate:
		"""
		Property to access the z-direction offset (:attr:`_zOffset`).

		``zOffset`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The z-direction offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._zOffset

	@ZOffset.setter
	def ZOffset(self, zOffset: Coordinate) -> None:
		if zOffset is None:
			raise ValueError("Parameter 'zOffset' is None.")
		elif not isinstance(zOffset, (int, float)):
			ex = TypeError("Parameter 'zOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(zOffset)}'.")
			raise ex

		self._zOffset = zOffset

	zOffset = ZOffset

	def Copy(self) -> Self:
		"""
		Create a new 3D-offset as a copy of this 3D-offset.

		:returns: Copy of this 3D-offset.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 3D-offset moved by a positive 3D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 3D-offset moved by a negative 3D-offset.
		"""
		return self.__class__(self._xOffset, self._yOffset, self._zOffset)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 3D-offset for :func:`copy.copy`.

		:returns: Copy of this 3D-offset.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 3D-offset for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 3D-offset.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate, Coordinate]:
		"""
		Convert this 3D-offset to a simple 3-element tuple.

		:returns: ``(x, y, z)`` tuple.
		"""
		return self._xOffset, self._yOffset, self._zOffset

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two 3D-offsets for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 3D-offsets are equal.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			return self._xOffset == other._xOffset and self._yOffset == other._yOffset and self._zOffset == other._zOffset
		elif isinstance(other, tuple):
			return self._xOffset == other[0] and self._yOffset == other[1] and self._zOffset == other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two 3D-offsets for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 3D-offsets are unequal.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		return not self.__eq__(other)

	def __neg__(self) -> Offset3D[Coordinate]:
		"""
		Negate all components of this 3D-offset and create a new 3D-offset.

		:returns: 3D-offset with negated offset components.
		"""
		return self.__class__(
			-self._xOffset,
			-self._yOffset,
			-self._zOffset
		)

	def __add__(self, other: Any) -> Offset3D[Coordinate]:
		"""
		Adds a 3D-offset to this 3D-offset and creates a new 3D-offset.

		:param other:      A 3D-offset as :class:`Offset3D` or tuple.
		:returns:          A new 3D-offset extended by the 3D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			return self.__class__(
				self._xOffset + other._xOffset,
				self._yOffset + other._yOffset,
				self._zOffset + other._zOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self._xOffset + other[0],
				self._yOffset + other[1],
				self._zOffset + other[2]
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> Self:
		"""
		Adds a 3D-offset to this 3D-offset (inplace).

		:param other:      A 3D-offset as :class:`Offset3D` or tuple.
		:returns:          This 3D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			self._xOffset += other._xOffset
			self._yOffset += other._yOffset
			self._zOffset += other._zOffset
		elif isinstance(other, tuple):
			self.XOffset += other[0]
			self.YOffset += other[1]
			self.ZOffset += other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> Offset3D[Coordinate]:
		"""
		Subtracts a 3D-offset from this 3D-offset and creates a new 3D-offset.

		:param other:      A 3D-offset as :class:`Offset3D` or tuple.
		:returns:          A new 3D-offset reduced by the 3D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			return self.__class__(
				self._xOffset - other._xOffset,
				self._yOffset - other._yOffset,
				self._zOffset - other._zOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self._xOffset - other[0],
				self._yOffset - other[1],
				self._zOffset - other[2]
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> Self:
		"""
		Subtracts a 3D-offset from this 3D-offset (inplace).

		:param other:      A 3D-offset as :class:`Offset3D` or tuple.
		:returns:          This 3D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			self._xOffset -= other._xOffset
			self._yOffset -= other._yOffset
			self._zOffset -= other._zOffset
		elif isinstance(other, tuple):
			self.XOffset -= other[0]
			self.YOffset -= other[1]
			self.ZOffset -= other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __repr__(self) -> str:
		"""
		Returns the 3D offset's string representation.

		:returns: The string representation of the 3D offset.
		"""
		return f"Offset3D({self._xOffset}, {self._yOffset}, {self._zOffset})"

	def __str__(self) -> str:
		"""
		Returns the 3D offset's string equivalent.

		:returns: The string equivalent of the 3D offset.
		"""
		return f"({self._xOffset}, {self._yOffset}, {self._zOffset})"


@export
class Size3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 3D cartesian size."""

	_width:  Coordinate  #: width in x-direction.
	_height: Coordinate  #: height in y-direction.
	_depth:  Coordinate  #: depth in z-direction.

	def __init__(self, width: Coordinate, height: Coordinate, depth: Coordinate) -> None:
		"""
		Initializes a 3-dimensional size.

		:param width:       width in x-direction.
		:param height:      height in y-direction.
		:param depth:       depth in z-direction.
		:raises ValueError: If parameter 'width' is None.
		:raises TypeError:  If parameter 'width' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'height' is None.
		:raises TypeError:  If parameter 'height' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'depth' is None.
		:raises TypeError:  If parameter 'depth' is not of type :class:`float` or :class:`int`.
		"""
		if width is None:
			raise ValueError("Parameter 'width' is None.")
		elif not isinstance(width, (int, float)):
			ex = TypeError("Parameter 'width' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(width)}'.")
			raise ex

		if height is None:
			raise ValueError("Parameter 'height' is None.")
		elif not isinstance(height, (int, float)):
			ex = TypeError("Parameter 'height' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(height)}'.")
			raise ex

		if depth is None:
			raise ValueError("Parameter 'depth' is None.")
		elif not isinstance(depth, (int, float)):
			ex = TypeError("Parameter 'depth' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
			raise ex

		self._width =  width
		self._height = height
		self._depth =  depth

	@property
	def Width(self) -> Coordinate:
		"""
		Property to access the width in x-direction (:attr:`_width`).

		``width`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The width in x-direction.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._width

	@Width.setter
	def Width(self, width: Coordinate) -> None:
		if width is None:
			raise ValueError("Parameter 'width' is None.")
		elif not isinstance(width, (int, float)):
			ex = TypeError("Parameter 'width' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(width)}'.")
			raise ex

		self._width = width

	width = Width

	@property
	def Height(self) -> Coordinate:
		"""
		Property to access the height in y-direction (:attr:`_height`).

		``height`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The height in y-direction.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._height

	@Height.setter
	def Height(self, height: Coordinate) -> None:
		if height is None:
			raise ValueError("Parameter 'height' is None.")
		elif not isinstance(height, (int, float)):
			ex = TypeError("Parameter 'height' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(height)}'.")
			raise ex

		self._height = height

	height = Height

	@property
	def Depth(self) -> Coordinate:
		"""
		Property to access the depth in z-direction (:attr:`_depth`).

		``depth`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The depth in z-direction.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._depth

	@Depth.setter
	def Depth(self, depth: Coordinate) -> None:
		if depth is None:
			raise ValueError("Parameter 'depth' is None.")
		elif not isinstance(depth, (int, float)):
			ex = TypeError("Parameter 'depth' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
			raise ex

		self._depth = depth

	depth = Depth

	def Copy(self) -> Self:
		"""
		Create a new 3D-size as a copy of this 3D-size.

		:returns: Copy of this 3D-size.
		"""
		return self.__class__(self._width, self._height, self._depth)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 3D-size for :func:`copy.copy`.

		:returns: Copy of this 3D-size.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 3D-size for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 3D-size.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate, Coordinate]:
		"""
		Convert this 3D-size to a simple 3-element tuple.

		:returns: ``(width, height, depth)`` tuple.
		"""
		return self._width, self._height, self._depth

	def __repr__(self) -> str:
		"""
		Returns the 3D size's string representation.

		:returns: The string representation of the 3D size.
		"""
		return f"Size3D({self._width}, {self._height}, {self._depth})"

	def __str__(self) -> str:
		"""
		Returns the 3D size's string equivalent.

		:returns: The string equivalent of the 3D size.
		"""
		return f"({self._width}, {self._height}, {self._depth})"


@export
class BoundingBox3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	An axis-aligned 3D bounding box.

	A bounding box is a computed value: segments return a new one from their ``BoundingBox`` property on every access.
	Its borders belong to the box.
	"""

	_minX: Coordinate  #: Smallest x-coordinate.
	_minY: Coordinate  #: Smallest y-coordinate.
	_minZ: Coordinate  #: Smallest z-coordinate.
	_maxX: Coordinate  #: Largest x-coordinate.
	_maxY: Coordinate  #: Largest y-coordinate.
	_maxZ: Coordinate  #: Largest z-coordinate.

	def __init__(
		self,
		minX: Coordinate,
		minY: Coordinate,
		minZ: Coordinate,
		maxX: Coordinate,
		maxY: Coordinate,
		maxZ: Coordinate
	) -> None:
		"""
		Initializes a 3-dimensional bounding box from its smallest and largest coordinates.

		:param minX:        Smallest x-coordinate.
		:param minY:        Smallest y-coordinate.
		:param minZ:        Smallest z-coordinate.
		:param maxX:        Largest x-coordinate.
		:param maxY:        Largest y-coordinate.
		:param maxZ:        Largest z-coordinate.
		:raises ValueError: If parameter 'minX' is None.
		:raises TypeError:  If parameter 'minX' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'minY' is None.
		:raises TypeError:  If parameter 'minY' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'minZ' is None.
		:raises TypeError:  If parameter 'minZ' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxX' is None.
		:raises TypeError:  If parameter 'maxX' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxX' is less than parameter 'minX'.
		:raises ValueError: If parameter 'maxY' is None.
		:raises TypeError:  If parameter 'maxY' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxY' is less than parameter 'minY'.
		:raises ValueError: If parameter 'maxZ' is None.
		:raises TypeError:  If parameter 'maxZ' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxZ' is less than parameter 'minZ'.
		"""
		for name, value in (
			("minX", minX),
			("minY", minY),
			("minZ", minZ),
			("maxX", maxX),
			("maxY", maxY),
			("maxZ", maxZ)
		):
			if value is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(value, (int, float)):
				ex = TypeError(f"Parameter '{name}' is not of type 'float' or 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

		if maxX < minX:
			ex = ValueError("Parameter 'maxX' is less than parameter 'minX'.")
			ex.add_note(f"Got minX={minX} and maxX={maxX}.")
			raise ex

		if maxY < minY:
			ex = ValueError("Parameter 'maxY' is less than parameter 'minY'.")
			ex.add_note(f"Got minY={minY} and maxY={maxY}.")
			raise ex

		if maxZ < minZ:
			ex = ValueError("Parameter 'maxZ' is less than parameter 'minZ'.")
			ex.add_note(f"Got minZ={minZ} and maxZ={maxZ}.")
			raise ex

		self._minX = minX
		self._minY = minY
		self._minZ = minZ
		self._maxX = maxX
		self._maxY = maxY
		self._maxZ = maxZ

	@classmethod
	def FromPoints(cls, points: Iterable[Point3D[Coordinate]]) -> Self:
		"""
		Create the smallest bounding box enclosing all given points.

		:param points:      Points to enclose.
		:returns:           Bounding box enclosing all points.
		:raises ValueError: If parameter 'points' is None.
		:raises TypeError:  If parameter 'points' is not iterable.
		:raises ValueError: If an element of parameter 'points' is None.
		:raises TypeError:  If an element of parameter 'points' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'points' is empty.
		"""
		if points is None:
			raise ValueError("Parameter 'points' is None.")
		elif not isinstance(points, Iterable):
			ex = TypeError("Parameter 'points' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(points)}'.")
			raise ex

		iterator = iter(points)
		try:
			point = next(iterator)
		except StopIteration as ex:
			raise ValueError("Parameter 'points' is empty.") from ex

		if point is None:
			raise ValueError("An element of parameter 'points' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("An element of parameter 'points' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		minX = maxX = point._x
		minY = maxY = point._y
		minZ = maxZ = point._z

		for point in iterator:
			if point is None:
				raise ValueError("An element of parameter 'points' is None.")
			elif not isinstance(point, Point3D):
				ex = TypeError("An element of parameter 'points' is not of type 'Point3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

			x = point._x
			y = point._y
			z = point._z
			if x < minX:
				minX = x
			elif x > maxX:
				maxX = x

			if y < minY:
				minY = y
			elif y > maxY:
				maxY = y

			if z < minZ:
				minZ = z
			elif z > maxZ:
				maxZ = z

		return cls(minX, minY, minZ, maxX, maxY, maxZ)

	@readonly
	def MinX(self) -> Coordinate:
		"""
		Read-only property to access the smallest x-coordinate (:attr:`_minX`).

		:returns: The smallest x-coordinate.
		"""
		return self._minX

	@readonly
	def MinY(self) -> Coordinate:
		"""
		Read-only property to access the smallest y-coordinate (:attr:`_minY`).

		:returns: The smallest y-coordinate.
		"""
		return self._minY

	@readonly
	def MinZ(self) -> Coordinate:
		"""
		Read-only property to access the smallest z-coordinate (:attr:`_minZ`).

		:returns: The smallest z-coordinate.
		"""
		return self._minZ

	@readonly
	def MaxX(self) -> Coordinate:
		"""
		Read-only property to access the largest x-coordinate (:attr:`_maxX`).

		:returns: The largest x-coordinate.
		"""
		return self._maxX

	@readonly
	def MaxY(self) -> Coordinate:
		"""
		Read-only property to access the largest y-coordinate (:attr:`_maxY`).

		:returns: The largest y-coordinate.
		"""
		return self._maxY

	@readonly
	def MaxZ(self) -> Coordinate:
		"""
		Read-only property to access the largest z-coordinate (:attr:`_maxZ`).

		:returns: The largest z-coordinate.
		"""
		return self._maxZ

	@readonly
	def Width(self) -> Coordinate:
		"""
		Read-only property to return the bounding box' extent in x-direction.

		:returns: The width in x-direction.
		"""
		return self._maxX - self._minX

	@readonly
	def Height(self) -> Coordinate:
		"""
		Read-only property to return the bounding box' extent in y-direction.

		:returns: The height in y-direction.
		"""
		return self._maxY - self._minY

	@readonly
	def Depth(self) -> Coordinate:
		"""
		Read-only property to return the bounding box' extent in z-direction.

		:returns: The depth in z-direction.
		"""
		return self._maxZ - self._minZ

	@readonly
	def Center(self) -> Point3D[float]:
		"""
		Read-only property to return the bounding box' center as a new 3D-point.

		:returns: The center point.
		"""
		return Point3D((self._minX + self._maxX) / 2, (self._minY + self._maxY) / 2, (self._minZ + self._maxZ) / 2)

	def Union(self, other: BoundingBox3D[Coordinate]) -> BoundingBox3D[Coordinate]:
		"""
		Create the smallest bounding box enclosing this and another bounding box.

		:param other:       The second bounding box.
		:returns:           A new bounding box enclosing both bounding boxes.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BoundingBox3D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BoundingBox3D):
			ex = TypeError("Parameter 'other' is not of type 'BoundingBox3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self.__class__(
			min(self._minX, other._minX),
			min(self._minY, other._minY),
			min(self._minZ, other._minZ),
			max(self._maxX, other._maxX),
			max(self._maxY, other._maxY),
			max(self._maxZ, other._maxZ)
		)

	def HasOverlap(self, other: BoundingBox3D[Coordinate]) -> bool:
		"""
		Check if this bounding box and another bounding box overlap.

		Two bounding boxes touching only at a face, an edge or a corner don't overlap, so elements can be aligned next to
		each other without a distance.

		:param other:       The second bounding box.
		:returns:           ``True``, if the inner volumes of both bounding boxes overlap.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BoundingBox3D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BoundingBox3D):
			ex = TypeError("Parameter 'other' is not of type 'BoundingBox3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return (
			self._minX < other._maxX and other._minX < self._maxX and
			self._minY < other._maxY and other._minY < self._maxY and
			self._minZ < other._maxZ and other._minZ < self._maxZ
		)

	def ContainsPoint(self, point: Point3D[Coordinate]) -> bool:
		"""
		Check if a point lies within this bounding box.

		A point on a border is contained.

		:param point:       The point to check.
		:returns:           ``True``, if the point lies within the bounding box or on its border.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point3D`.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		return self._ContainsPoint(point)

	def _ContainsPoint(self, point: Point3D[Coordinate]) -> bool:
		"""
		Check if a point lies within this bounding box, without checking the parameter.

		:param point: The point to check.
		:returns:     ``True``, if the point lies within the bounding box or on its border.
		"""
		return (
			self._minX <= point._x <= self._maxX and
			self._minY <= point._y <= self._maxY and
			self._minZ <= point._z <= self._maxZ
		)

	def __contains__(self, other: Any) -> bool:
		"""
		Check if an element lies within this bounding box (``other in box``).

		:param other:      The element to check. Supported: :class:`Point3D`.
		:returns:          ``True``, if the element lies within the bounding box or on its border.
		:raises TypeError: If the first operand is not of type :class:`Point3D`.
		"""
		if isinstance(other, Point3D):
			return self._ContainsPoint(other)

		ex = TypeError("First operand is not supported by in operator.")
		ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
		ex.add_note("Supported types for first operand: Point3D")
		raise ex

	def __add__(self, other: Any) -> BoundingBox3D[Coordinate]:
		"""
		Adds a 3D-offset to this bounding box and creates a new, shifted bounding box.

		:param other:      A 3D-offset as :class:`Offset3D`.
		:returns:          A new bounding box shifted by the 3D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset3D`.
		"""
		if not isinstance(other, Offset3D):
			ex = TypeError("Parameter 'other' is not of type 'Offset3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self.__class__(
			self._minX + other._xOffset,
			self._minY + other._yOffset,
			self._minZ + other._zOffset,
			self._maxX + other._xOffset,
			self._maxY + other._yOffset,
			self._maxZ + other._zOffset
		)

	def Copy(self) -> Self:
		"""
		Create a new bounding box as a copy of this bounding box.

		:returns: Copy of this bounding box.
		"""
		return self.__class__(self._minX, self._minY, self._minZ, self._maxX, self._maxY, self._maxZ)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this bounding box for :func:`copy.copy`.

		:returns: Copy of this bounding box.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this bounding box for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this bounding box.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate, Coordinate, Coordinate, Coordinate, Coordinate]:
		"""
		Convert this bounding box to a simple 6-element tuple.

		:returns: ``(minX, minY, minZ, maxX, maxY, maxZ)`` tuple.
		"""
		return self._minX, self._minY, self._minZ, self._maxX, self._maxY, self._maxZ

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two bounding boxes for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both bounding boxes have the same coordinates.
		:raises TypeError: If the second operand is not of type :class:`BoundingBox3D`.
		"""
		if not isinstance(other, BoundingBox3D):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: BoundingBox3D")
			raise ex

		return (
			self._minX == other._minX and self._minY == other._minY and self._minZ == other._minZ and
			self._maxX == other._maxX and self._maxY == other._maxY and self._maxZ == other._maxZ
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two bounding boxes for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the bounding boxes differ in at least one coordinate.
		:raises TypeError: If the second operand is not of type :class:`BoundingBox3D`.
		"""
		if not isinstance(other, BoundingBox3D):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: BoundingBox3D")
			raise ex

		return (
			self._minX != other._minX or self._minY != other._minY or self._minZ != other._minZ or
			self._maxX != other._maxX or self._maxY != other._maxY or self._maxZ != other._maxZ
		)

	def __repr__(self) -> str:
		"""
		Returns the bounding box' string representation.

		:returns: The string representation of the bounding box.
		"""
		return f"BoundingBox3D({self._minX}, {self._minY}, {self._minZ}, {self._maxX}, {self._maxY}, {self._maxZ})"

	def __str__(self) -> str:
		"""
		Returns the bounding box' string equivalent.

		:returns: The string equivalent of the bounding box, its corners with the smallest and the largest coordinates.
		"""
		return f"(({self._minX}, {self._minY}, {self._minZ}), ({self._maxX}, {self._maxY}, {self._maxZ}))"


@export
class Segment3D(Element3D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of a 3D cartesian segment.

	A segment owns its start and end point; a group can hold it.
	"""

	_start: Point3D[Coordinate]  #: Start point of a segment.
	_end:   Point3D[Coordinate]  #: End point of a segment.

	def __init__(
		self,
		start:      Point3D[Coordinate],
		end:        Point3D[Coordinate],
		*,
		copyPoints: bool = True,
		parent:     Nullable[Group3D[Coordinate]] = None
	) -> None:
		"""
		Initializes a 3-dimensional segment.

		:param start:                Start point of the segment.
		:param end:                  End point of the segment.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param parent:               Optional, the group the segment is added to. Default: ``None``.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`Point3D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`Point3D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian3D.Groups.Group3D`.
		"""
		super().__init__(parent=parent)

		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point3D):
			ex = TypeError("Parameter 'start' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex

		if end is None:
			raise ValueError("Parameter 'end' is None.")
		elif not isinstance(end, Point3D):
			ex = TypeError("Parameter 'end' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex

		if copyPoints is None:
			raise ValueError("Parameter 'copyPoints' is None.")
		elif not isinstance(copyPoints, bool):
			ex = TypeError("Parameter 'copyPoints' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(copyPoints)}'.")
			raise ex

		if copyPoints:
			start = start.Copy()
			end =   end.Copy()
		elif end is start:
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {start}.")
			ex.add_note("Use 'copyPoints=True' to copy the points.")
			raise ex from ValueError("Parameter 'end' is the same point as parameter 'start'.")
		else:
			for name, point in (
				("start", start),
				("end",   end)
			):
				if point._parent is not None:
					ex = AlreadyOwnedError("Point is owned by another element already.")
					ex.add_note(f"Got point {point} owned by {point._parent!r}.")
					ex.add_note("Use 'copyPoints=True' to copy the point.")
					raise ex from ValueError(f"Parameter '{name}' is owned by another element.")

		start._parent = self
		end._parent =   self
		self._start =   start
		self._end =     end

		self.Parent = parent

	@property
	def Start(self) -> Point3D[Coordinate]:
		"""
		Property to access the segment's start point (:attr:`_start`).

		An assigned point is referenced, not copied: the segment takes ownership of it and releases the previous start
		point.

		``start`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    Start point of the segment.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point3D`.
		:raises DuplicatePointError: If an assigned point is the segment's end point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._start

	@Start.setter
	def Start(self, start: Point3D[Coordinate]) -> None:
		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point3D):
			ex = TypeError("Parameter 'start' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex
		elif start is self._start:
			return
		elif start is self._end:
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {start}.")
			raise ex from ValueError("Parameter 'start' is the segment's end point.")
		elif start._parent is not None and start._parent is not self:
			ex = AlreadyOwnedError("Point is owned by another element already.")
			ex.add_note(f"Got point {start} owned by {start._parent!r}.")
			raise ex from ValueError("Parameter 'start' is owned by another element.")

		self._start._parent = None
		start._parent =       self
		self._start =         start

	start = Start

	@property
	def End(self) -> Point3D[Coordinate]:
		"""
		Property to access the segment's end point (:attr:`_end`).

		An assigned point is referenced, not copied: the segment takes ownership of it and releases the previous end
		point.

		``end`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    End point of the segment.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point3D`.
		:raises DuplicatePointError: If an assigned point is the segment's start point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._end

	@End.setter
	def End(self, end: Point3D[Coordinate]) -> None:
		if end is None:
			raise ValueError("Parameter 'end' is None.")
		elif not isinstance(end, Point3D):
			ex = TypeError("Parameter 'end' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex
		elif end is self._end:
			return
		elif end is self._start:
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {end}.")
			raise ex from ValueError("Parameter 'end' is the segment's start point.")
		elif end._parent is not None and end._parent is not self:
			ex = AlreadyOwnedError("Point is owned by another element already.")
			ex.add_note(f"Got point {end} owned by {end._parent!r}.")
			raise ex from ValueError("Parameter 'end' is owned by another element.")

		self._end._parent = None
		end._parent =       self
		self._end =         end

	end = End

	@readonly
	def BoundingBox(self) -> BoundingBox3D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the segment's start and end point.

		:returns: A new bounding box.
		"""
		start = self._start
		end =   self._end
		return BoundingBox3D(
			min(start._x, end._x),
			min(start._y, end._y),
			min(start._z, end._z),
			max(start._x, end._x),
			max(start._y, end._y),
			max(start._z, end._z)
		)

	def Move(self, offset: Offset3D[Coordinate]) -> None:
		"""
		Move the segment by moving its start and end point (inplace).

		:param offset:      The 3D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`Offset3D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, Offset3D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._start += offset
		self._end +=   offset

	def Copy(self) -> Self:
		"""
		Create a new 3D-segment as a copy of this 3D-segment.

		The copy holds copies of the start and end point.

		:returns: Copy of this 3D-segment.
		"""
		return self.__class__(self._start, self._end)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 3D-segment for :func:`copy.copy`.

		:returns: Copy of this 3D-segment.
		"""
		return self.Copy()


@export
class LineSegment3D(Segment3D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 3D cartesian line segment."""

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the Euclidean distance between start and end point.

		:returns: Euclidean distance between start and end point
		"""
		start = self._start
		end =   self._end
		return sqrt((end._x - start._x) ** 2 + (end._y - start._y) ** 2 + (end._z - start._z) ** 2)

	def AngleTo(self, other: LineSegment3D[Coordinate]) -> float:
		"""
		Compute the angle between this line segment and another one.

		The angle is the one between both segments' directions, from ``0`` (same direction) to :data:`math.pi` (opposite
		directions).

		:param other:                The second line segment.
		:returns:                    The angle in radians.
		:raises ValueError:          If parameter 'other' is None.
		:raises TypeError:           If parameter 'other' is not of type :class:`LineSegment3D`.
		:raises NotInSameFrameError: If parameter 'other' is in another frame than this line segment.
		:raises ValueError:          If parameter 'other' has length 0.
		:raises ValueError:          If this line segment has length 0.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, LineSegment3D):
			ex = TypeError("Parameter 'other' is not of type 'LineSegment3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex
		elif self.Frame is not other.Frame:
			ex = NotInSameFrameError("Line segments are in different frames.")
			ex.add_note(f"Got line segments {self} and {other}.")
			raise ex from ValueError("Parameter 'other' is in another frame.")
		elif other._start._x == other._end._x and other._start._y == other._end._y and other._start._z == other._end._z:
			ex = ValueError("Parameter 'other' has length 0.")
			ex.add_note(f"Got line segment {other}.")
			ex.add_note("Can't determine an angle between two lines if one of the lines has no direction, due to a "
			            "zero-length.")
			raise ex

		if self._start._x == self._end._x and self._start._y == self._end._y and self._start._z == self._end._z:
			ex = ValueError("Line segment has length 0.")
			ex.add_note(f"Got line segment {self}.")
			ex.add_note("Can't determine an angle between two lines if one of the lines has no direction, due to a "
			            "zero-length.")
			raise ex

		vectorA =         self.ToOffset()
		vectorB =         other.ToOffset()
		scalarProductAB = (
			vectorA._xOffset * vectorB._xOffset + vectorA._yOffset * vectorB._yOffset + vectorA._zOffset * vectorB._zOffset
		)
		crossProductX =   vectorA._yOffset * vectorB._zOffset - vectorA._zOffset * vectorB._yOffset
		crossProductY =   vectorA._zOffset * vectorB._xOffset - vectorA._xOffset * vectorB._zOffset
		crossProductZ =   vectorA._xOffset * vectorB._yOffset - vectorA._yOffset * vectorB._xOffset

		return atan2(sqrt(crossProductX ** 2 + crossProductY ** 2 + crossProductZ ** 2), scalarProductAB)

	def ToOffset(self) -> Offset3D[Coordinate]:
		"""
		Convert this 3D line segment to a 3D-offset.

		:returns: 3D-offset as :class:`Offset3D`
		"""
		return self._end - self._start

	def ToTuple(self) -> tuple[tuple[Coordinate, Coordinate, Coordinate], tuple[Coordinate, Coordinate, Coordinate]]:
		"""
		Convert this 3D line segment to a simple 2-element tuple of 3D-point tuples.

		:returns: ``((x1, y1, z1), (x2, y2, z2))`` tuple.
		"""
		return self._start.ToTuple(), self._end.ToTuple()

	def __repr__(self) -> str:
		"""
		Returns the 3D line segment's string representation.

		:returns: The string representation of the 3D line segment.
		"""
		return f"LineSegment3D({self._start}, {self._end})"

	def __str__(self) -> str:
		"""
		Returns the 3D line segment's string equivalent.

		:returns: The string equivalent of the 3D line segment.
		"""
		return f"({self._start} → {self._end})"
