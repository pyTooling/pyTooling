.. _STRUCT/Cartesian2D:

2D Cartesian
############

The :mod:`pyTooling.Cartesian2D` package implements points, offsets, sizes and line segments in a 2-dimensional
cartesian coordinate system, plus the shapes built from them.

.. seealso::

   :ref:`STRUCT/Cartesian3D`
      |rarr| The same classes with a third axis, and the volumes built from them.

.. #contents:: Table of Contents
   :local:
   :depth: 2

.. rubric:: 2D Cartesian Properties:

* Coordinates as ``int`` or ``float``.
* Every class is generic in its coordinate type, so a grid of integers and a drawing of floats use the same classes.
* A point and an offset are **different types**, which is what makes the arithmetic below unambiguous.

.. _STRUCT/Cartesian2D/Features:

Features
********

* An **integer or a floating-point coordinate system**, chosen per instance - every class is generic in its
  coordinate type, so a grid of integers and a drawing of floats use the same classes.
* **Points and offsets as separate types**, with the arithmetic relating them: a point plus an offset is a point, a
  point minus a point is an offset - in both the copying and the in-place form.
* **Distances measured** - a line segment reports its length and its angle.
* **Curved segments** - a circular :class:`~pyTooling.Cartesian2D.ArcSegment2D` around a center, reporting its
  radius, angles and length, and quadratic and cubic Bezier curves, with exact bounding boxes.
* **Paths** - a :class:`~pyTooling.Cartesian2D.Shapes.Path` chains line segments, arcs and Bezier curves, open or
  closed, like SVG's ``<path>``.
* **Shapes placed by their corners**, so a shape is positioned by the points it is built from - a circle by its
  center.
* Shapes validated on construction: a :class:`~pyTooling.Cartesian2D.Shapes.Polygon` with any number of corners, the
  four-cornered :class:`~pyTooling.Cartesian2D.Shapes.Trapezium` narrowed down to a
  :class:`~pyTooling.Cartesian2D.Shapes.Square`, and a :class:`~pyTooling.Cartesian2D.Shapes.Circle`.
* **A circle measured** - it reports its diameter, circumference and area.
* **Bounding boxes** - every shape and segment reports the smallest axis-aligned
  :class:`~pyTooling.Cartesian2D.BoundingBox2D` enclosing it, and bounding boxes unite, intersect and contain points.
* **Shapes and segments moved as a whole** - ``Move(offset)`` shifts all their points in place.
* **Points owned by one element** - a shape or segment owns its points, so a point can't silently belong to two
  shapes. Coordinates of different frames aren't mixed in a computation.
* **Groups with relative coordinates** - a :class:`~pyTooling.Cartesian2D.Groups.Group2D` holds shapes, segments and
  groups at an offset, so moving a group moves everything in it. Absolute positions, alignment and distribution are
  computed across groups.
* **Data attached to elements** - every shape, segment and group carries a value and key-value-pairs, so a drawing
  element knows the model object it draws.
* **A canvas knowing its y-axis** - a :class:`~pyTooling.Cartesian2D.Groups.Canvas2D` is the root of a drawing, with
  the y-axis pointing up (mathematics) or down (screen, SVG), and flips a whole drawing to the other direction.
* **Independent copies** - ``Copy()``, :func:`copy.copy` and :func:`copy.deepcopy` return an object sharing no point
  with the original. A shape's copy is of the same class, and its edges share the copied corners.
* Conversion to plain tuples through ``ToTuple``, for handing coordinates to a library that expects them.


.. _STRUCT/Cartesian2D/MissingFeatures:

Missing Features
================

* Rotation and scaling - an element can be shifted and mirrored at a vertical or horizontal axis, but not rotated or
  scaled.
* Ellipses and elliptical arcs.
* The length of a Bezier curve.
* Exact containment and intersection tests (*is this point inside that rotated rectangle?*). Only bounding boxes are
  compared.
* Area and perimeter of a polygon.


.. _STRUCT/Cartesian2D/PlannedFeatures:

Planned Features
================

* An area per polygon, and a perimeter derived from its segments.
* The 3-dimensional volumes, which currently exist as empty classes - see :ref:`STRUCT/Cartesian3D/Volumes`.


.. _STRUCT/Cartesian2D/RejectedFeatures:

Out of Scope
============

* A general-purpose geometry or linear-algebra library. These classes exist to give coordinates a **name and a
  type** in the packages using them. |br|
  For doing real geometry have a look at `NumPy <https://numpy.org/>`__ or
  `Shapely <https://shapely.readthedocs.io/>`__.
* Rendering. Nothing here draws anything - ``ToTuple`` hands the numbers to whatever does.
* Coordinate systems other than cartesian - no polar, spherical or geographic coordinates.


.. _STRUCT/Cartesian2D/ByFeature:

By Feature
**********

.. danger::

   Accessing internal fields of a origin, point, offset, ... is strongly not recommended for users, as it might lead to
   a corrupted data structure. If a power-user wants to access these fields, feel free to use them for achieving a
   higher performance, but you got warned 😉.


.. _STRUCT/Cartesian2D/Classes:

Basic Classes
*************

All of them are generic in ``Coordinate``, a type variable bound to :class:`int` or :class:`float`, so the coordinate
type is chosen once and then checked throughout.

Their coordinates, offsets, sizes and end points are properties. A constructor parameter and an assignment are
checked alike: ``None`` raises :exc:`ValueError`, a value of another type raises :exc:`TypeError`. The lower-case names
(``x``, ``xOffset``, ``width``, ``start``, ...) are deprecated aliases of these properties; they are removed in v11.0.0.


.. _STRUCT/Cartesian2D/Point2D:

Point2D
=======

A :class:`~pyTooling.Cartesian2D.Point2D` is a **position**: properties :attr:`~pyTooling.Cartesian2D.Point2D.X` and
:attr:`~pyTooling.Cartesian2D.Point2D.Y`, and the arithmetic that keeps a position distinct from a displacement.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Expression
     - Result
   * - ``point + offset``
     - A new :class:`~pyTooling.Cartesian2D.Point2D`, shifted.
   * - ``point - offset``
     - A new :class:`~pyTooling.Cartesian2D.Point2D`, shifted back.
   * - ``point - point``
     - An :class:`~pyTooling.Cartesian2D.Offset2D` - the displacement between them.
   * - ``point += offset``
     - The **same** point, moved in place.

.. code-block:: Python

   from pyTooling.Cartesian2D import Point2D, Offset2D

   start = Point2D(3, 4)
   moved = start + Offset2D(1, 1)     # Point2D(4, 5)
   delta = moved - start              # Offset2D(1, 1)

An offset may be written as a plain 2-tuple wherever one is accepted. Anything else raises :exc:`TypeError`, with
the offending type in a note.

:meth:`~pyTooling.Cartesian2D.Point2D.Copy` returns an independent point and
:meth:`~pyTooling.Cartesian2D.Point2D.ToTuple` the ``(x, y)`` pair. :attr:`~pyTooling.Cartesian2D.Point2D.Absolute`
returns a new point relative to the origin, for a point inside a :ref:`group <STRUCT/Cartesian2D/Groups>`.

A point is owned by at most one element, the segment or shape it belongs to: the read-only
:attr:`~pyTooling.Cartesian2D.Base2D.Parent`. A new point and a copy have no owner, unless parameter ``parent`` sets
one. See :ref:`STRUCT/Cartesian2D/Ownership`.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Point3D`
      |rarr| Its counterpart, the point with a ``z`` coordinate.


.. _STRUCT/Cartesian2D/Origin2D:

Origin2D
========

An :class:`~pyTooling.Cartesian2D.Origin2D` is a :class:`~pyTooling.Cartesian2D.Point2D` fixed at ``(0, 0)`` - its
constructor takes no coordinates. It exists so a function needing *the* origin can say so in its signature instead
of checking two numbers.

An origin can't be copied: ``Copy()``, :func:`copy.copy` and :func:`copy.deepcopy` raise
:exc:`~pyTooling.Exceptions.InvalidOperationError` (a :exc:`RuntimeError`).

.. seealso::

   :ref:`STRUCT/Cartesian2D/Point2D`
      |rarr| Its base-class, the 2-dimensional point.
   :ref:`STRUCT/Cartesian3D/Origin3D`
      |rarr| Its counterpart, the origin with a ``z`` coordinate.


.. _STRUCT/Cartesian2D/Offset2D:

Offset2D
========

An :class:`~pyTooling.Cartesian2D.Offset2D` is a **displacement**: properties
:attr:`~pyTooling.Cartesian2D.Offset2D.XOffset` and :attr:`~pyTooling.Cartesian2D.Offset2D.YOffset`. Offsets add and
subtract with each other, and negate:

.. code-block:: Python

   right = Offset2D(1, 0)
   left  = -right                     # Offset2D(-1, 0)
   diag  = right + Offset2D(0, 1)     # Offset2D(1, 1)

Unlike a point, an offset compares with ``==`` and ``!=`` - two displacements are equal when their components are.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Offset3D`
      |rarr| Its counterpart, the offset with a ``ZOffset``.


.. _STRUCT/Cartesian2D/Size2D:

Size2D
======

A :class:`~pyTooling.Cartesian2D.Size2D` is an **extent**: :attr:`~pyTooling.Cartesian2D.Size2D.Width` and
:attr:`~pyTooling.Cartesian2D.Size2D.Height`. It is deliberately not an offset - adding a size to a point is
meaningless, and keeping the types apart is what prevents it.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Size3D`
      |rarr| Its counterpart, the size with a depth.


.. _STRUCT/Cartesian2D/BoundingBox2D:

BoundingBox2D
=============

A :class:`~pyTooling.Cartesian2D.BoundingBox2D` is the smallest **axis-aligned rectangle** enclosing something: the
read-only properties :attr:`~pyTooling.Cartesian2D.BoundingBox2D.MinX`,
:attr:`~pyTooling.Cartesian2D.BoundingBox2D.MinY`, :attr:`~pyTooling.Cartesian2D.BoundingBox2D.MaxX` and
:attr:`~pyTooling.Cartesian2D.BoundingBox2D.MaxY`, and from them :attr:`~pyTooling.Cartesian2D.BoundingBox2D.Width`,
:attr:`~pyTooling.Cartesian2D.BoundingBox2D.Height` and
:attr:`~pyTooling.Cartesian2D.BoundingBox2D.Center`. A maximum less than its minimum raises :exc:`ValueError`.

It is a computed value, not a shape: the ``BoundingBox`` property of a shape, segment or group returns a new one on
every access, so it always follows moved points. :meth:`~pyTooling.Cartesian2D.BoundingBox2D.FromPoints` encloses any
number of points, and ``box + offset`` returns a shifted bounding box.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Expression
     - Result
   * - ``box.Union(other)``
     - A new :class:`~pyTooling.Cartesian2D.BoundingBox2D` enclosing both.
   * - ``box.HasOverlap(other)``
     - ``True``, if the inner areas overlap - touching borders don't count.
   * - ``box.ContainsPoint(point)``, ``point in box``
     - ``True``, if the point lies inside or on the border.
   * - ``box.ToRectangle()``
     - A new :class:`~pyTooling.Cartesian2D.Shapes.Rectangle` with the box's corners.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D
   from pyTooling.Cartesian2D.Shapes import Circle, Polygon

   triangle = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
   bubble =   Circle(Point2D(5, 1), 1)

   triangle.BoundingBox                            # BoundingBox2D(0, 0, 4, 3)
   triangle.BoundingBox.Union(bubble.BoundingBox)  # BoundingBox2D(0, 0, 6, 3)

Like an offset, a bounding box compares with ``==`` and ``!=``, and ``Copy()``, :func:`copy.copy` and
:func:`copy.deepcopy` return an independent one.


.. _STRUCT/Cartesian2D/Segment2D:

Segment2D
=========

A :class:`~pyTooling.Cartesian2D.Segment2D` is a :attr:`~pyTooling.Cartesian2D.Segment2D.Start` and an
:attr:`~pyTooling.Cartesian2D.Segment2D.End` point.

Its constructor **copies both points by default**, so a segment doesn't change when the points it was built from
move later. ``copyPoints=False`` keeps the references instead: the segment takes ownership of both points. A point
assigned to :attr:`~pyTooling.Cartesian2D.Segment2D.Start` or :attr:`~pyTooling.Cartesian2D.Segment2D.End` is
referenced too; the segment owns it and releases the previous one.

A segment with a :attr:`~pyTooling.Cartesian2D.Base2D.Parent` shape is an **edge** of that shape, like the edges of
a :class:`~pyTooling.Cartesian2D.Shapes.Polygon`: it references two of the shape's corners, which stay owned by the
shape. An edge can't replace its points.

:attr:`~pyTooling.Cartesian2D.Segment2D.BoundingBox` encloses both points, and
:meth:`~pyTooling.Cartesian2D.Segment2D.Move` shifts both by an :class:`~pyTooling.Cartesian2D.Offset2D`, in place.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Segment3D`
      |rarr| Its counterpart, the segment between two 3D points.


.. _STRUCT/Cartesian2D/LineSegment2D:

LineSegment2D
=============

A :class:`~pyTooling.Cartesian2D.LineSegment2D` is a segment understood as a straight line, which is what gives it
measurements:

* :attr:`~pyTooling.Cartesian2D.LineSegment2D.Length` - the Euclidean distance between its ends, a :class:`float`
  even for integer coordinates;
* :meth:`~pyTooling.Cartesian2D.LineSegment2D.AngleTo` - the angle to another line segment's direction, from 0 to
  :data:`math.pi`; a line segment of length 0 has no direction and raises :exc:`ValueError`;
* :meth:`~pyTooling.Cartesian2D.LineSegment2D.ToOffset` - the segment as the displacement from start to end.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Segment2D`
      |rarr| Its base-class, the 2-dimensional segment.
   :ref:`STRUCT/Cartesian3D/LineSegment3D`
      |rarr| Its counterpart, the line segment in 3D.


.. _STRUCT/Cartesian2D/CurvedSegments:

Curved Segments
===============

A curved segment is a :ref:`segment <STRUCT/Cartesian2D/Segment2D>` too: it has a start and an end point, a group
can hold it, and a shape can use it as an edge. A Bezier curve's control points are owned like the start and end
point: copied by default, referenced with ``copyPoints=False``, and moved and mirrored with the segment. An arc keeps
only its end points and describes its curve relative to them.

.. _STRUCT/Cartesian2D/ArcSegment2D:

ArcSegment2D
------------

An :class:`~pyTooling.Cartesian2D.ArcSegment2D` is a piece of a circle from a start to an end point. It stores its
curve relative to its chord, the line segment from the start to the end point: the
:attr:`~pyTooling.Cartesian2D.ArcSegment2D.ChordPosition` of a root point on the chord, and the arc's
:attr:`~pyTooling.Cartesian2D.ArcSegment2D.Height` over the chord at that point, as a fraction of the chord's length.
The :attr:`~pyTooling.Cartesian2D.ArcSegment2D.Center` (a new point on each access), the
:attr:`~pyTooling.Cartesian2D.ArcSegment2D.Radius` and the :attr:`~pyTooling.Cartesian2D.ArcSegment2D.Direction` from
the start to the end point, a :class:`~pyTooling.Cartesian2D.SweepDirection` - ``Counterclockwise`` or ``Clockwise``,
seen with the y-axis pointing up - are computed from them. Besides the start and end point, the constructor takes
exactly one group of keyword parameters describing the circle; none or more than one group raises :exc:`ValueError`:

``center`` and ``direction``
   The center of the circle and the direction. The end point must have the start point's distance to the center,
   compared with :func:`math.isclose`. Only the center's coordinates are used.

``arcPoint``
   A third point of the arc: the arc runs from the start point through this point to the end point, so the order of
   the three points gives the direction. Only its coordinates are used. Three points on a line raise
   :exc:`ValueError`.

``height`` and optionally ``chordPosition``
   The arc's distance from its chord, the line segment from the start to the end point, measured perpendicular at a
   root point. ``chordPosition`` places the root point on the chord, as a fraction from ``0.0`` at the start point to
   ``1.0`` at the end point; the default ``0.5`` is the chord's midpoint, where the height is the arc's *sagitta*. A
   positive height lies on the left of the chord, seen from the start point, so the arc runs clockwise; a negative
   height lies on the right. The height is given as a distance and stored relative to the chord's length.

.. code-block:: text

                    arc point
                .-------x-------.
             .'         |         '.
           /            | height     \
    start x-------------+-------------x end
                    root point
          |<----------->|
          chordPosition * chord length

.. code-block:: Python

   from pyTooling.Cartesian2D import Point2D, Offset2D, ArcSegment2D, SweepDirection

   start = Point2D(0, 0)
   end =   Point2D(2, 0)

   # Three times the upper half of the circle around (1, 0) with radius 1, clockwise:
   byCenter =   ArcSegment2D(start, end, center=Point2D(1, 0), direction=SweepDirection.Clockwise)
   byArcPoint = ArcSegment2D(start, end, arcPoint=Point2D(1, 1))
   byHeight =   ArcSegment2D(start, end, height=1)

   flat = ArcSegment2D(Point2D(0, 0), Point2D(4, 0), height=-1)
   flat.Center                        # (2.0, 1.5)
   flat.Radius                        # 2.5
   flat.Direction                     # SweepDirection.Counterclockwise

A ``center`` or an ``arcPoint`` is converted to the sagitta, the height at the chord's midpoint. An arc isn't a circle:
a start and an end point at the same position have no chord and raise :exc:`ValueError`, whatever the group.

Moving an end point, or assigning another point to :attr:`~pyTooling.Cartesian2D.ArcSegment2D.Start` or
:attr:`~pyTooling.Cartesian2D.ArcSegment2D.End`, keeps the arc's shape: its height scales with the chord, and its
center, radius and direction follow. So an arc stays valid when a joint of a
:ref:`path <STRUCT/Cartesian2D/Path>` moves.

.. code-block:: Python

   arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)
   end = arc.End
   end += Offset2D(2, 0)              # the chord is twice as long
   arc.Height                         # 2.0
   arc.Center                         # (2.0, 0.0)

* :attr:`~pyTooling.Cartesian2D.ArcSegment2D.StartAngle` and :attr:`~pyTooling.Cartesian2D.ArcSegment2D.EndAngle` -
  the angles of both points seen from the center, in radians, from -:data:`math.pi` to :data:`math.pi`;
* :attr:`~pyTooling.Cartesian2D.ArcSegment2D.SweepAngle` - the angle from the start to the end point, positive
  counterclockwise and negative clockwise;
* :attr:`~pyTooling.Cartesian2D.ArcSegment2D.Length` - the radius times the absolute sweep angle;
* :attr:`~pyTooling.Cartesian2D.ArcSegment2D.BoundingBox` - exact: where the arc passes the leftmost, rightmost,
  lowest or highest point of its circle, it bulges past its start and end point;
* :meth:`~pyTooling.Cartesian2D.ArcSegment2D.ToChord` - a new :class:`~pyTooling.Cartesian2D.LineSegment2D` from the
  start to the end point.

.. code-block:: Python

   arc = ArcSegment2D(Point2D(2, 0), Point2D(-2, 0), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)
   arc.SweepAngle                     # 3.14159... (math.pi)
   arc.Length                         # 6.28318...
   arc.BoundingBox                    # BoundingBox2D(-2, 0, 2, 2.0)
   arc.ToChord().Length               # 4.0
   arc.MirrorY()                      # arc.Direction is SweepDirection.Clockwise

Mirroring an arc reverses its direction, so the mirrored arc bulges to the other side.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Segment2D`
      |rarr| Its base-class, the 2-dimensional segment.
   :ref:`STRUCT/Cartesian2D/Circle`
      |rarr| The full circle as a shape.

.. _STRUCT/Cartesian2D/BezierSegment2D:

BezierSegment2D
---------------

A Bezier curve runs from its start point to its end point and is pulled towards its
:attr:`~pyTooling.Cartesian2D.BezierSegment2D.ControlPoints`, like SVG's ``Q`` and ``C`` commands or TikZ'
``.. controls ..``. Its points are given in curve order:

* a :class:`~pyTooling.Cartesian2D.QuadraticBezierSegment2D` has one
  :attr:`~pyTooling.Cartesian2D.QuadraticBezierSegment2D.ControlPoint` - ``(start, controlPoint, end)``;
* a :class:`~pyTooling.Cartesian2D.CubicBezierSegment2D` has two,
  :attr:`~pyTooling.Cartesian2D.CubicBezierSegment2D.ControlPoint1` next to the start point and
  :attr:`~pyTooling.Cartesian2D.CubicBezierSegment2D.ControlPoint2` next to the end point -
  ``(start, controlPoint1, controlPoint2, end)``.

:meth:`~pyTooling.Cartesian2D.BezierSegment2D.PointAt` returns the point of the curve at a curve parameter ``t``, from
0 (the start point) to 1 (the end point). The :attr:`~pyTooling.Cartesian2D.QuadraticBezierSegment2D.BoundingBox` is
exact: it adds the points where the curve turns in x- or y-direction. The box of the control points is larger, as the
curve passes them only in special cases. :meth:`~pyTooling.Cartesian2D.BezierSegment2D.ToTuple` returns the points as
tuples, in curve order.

.. code-block:: Python

   from pyTooling.Cartesian2D import Point2D, QuadraticBezierSegment2D, CubicBezierSegment2D

   hill = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))
   hill.PointAt(0.5)                  # (2.0, 2.0)
   hill.BoundingBox                   # BoundingBox2D(0, 0, 4, 2.0)

   bow = CubicBezierSegment2D(Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6))
   bow.BoundingBox                    # BoundingBox2D(0, 0, 4.5, 6)

A Bezier curve has no ``Length``: a cubic curve's length has no closed form, it needs a numeric approximation.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Segment2D`
      |rarr| Its base-class, the 2-dimensional segment.


.. _STRUCT/Cartesian2D/Ownership:

Ownership and Frames
====================

Every point is owned by at most one element: a standalone segment owns its two points, a shape owns its corners or
its center. An element given a point with ``copyPoints=False`` takes ownership of it; a point owned by another element
raises :exc:`~pyTooling.Cartesian2D.AlreadyOwnedError`, so two shapes never move each other's corners by accident.
The same point object given twice raises :exc:`~pyTooling.Cartesian2D.DuplicatePointError`. Copying is always possible -
the copy has no owner.

``Point2D(x, y, parent=shape)`` sets the owner, but doesn't register the point: the shape's points don't change. Such a
point is in the shape's frame, so it can be combined with the shape's points, and it can replace the start or end point
of its parent segment.

The edges of a polygon or trapezium are views: they reference the shape's corners, but don't own them. Moving an edge
moves the corners it references; replacing an edge's point raises :exc:`~pyTooling.Cartesian2D.NotOwnedError`.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D
   from pyTooling.Cartesian2D.Shapes import Circle, Polygon

   center =   Point2D(1, 1)
   bubble =   Circle(center, 1, copyPoints=False)   # center.Parent is bubble
   triangle = Polygon((center, Point2D(4, 0), Point2D(2, 3)), copyPoints=False)
   # AlreadyOwnedError: Point is owned by another element already.

The coordinates of a point are relative to a **frame**: :attr:`~pyTooling.Cartesian2D.Base2D.Frame` is the frame of its
owner, and an element without a frame has ``None``. Points, segments and shapes derive from the abstract
:class:`~pyTooling.Cartesian2D.Base2D`, which holds the parent and returns the frame; segments and shapes also from
:class:`~pyTooling.Cartesian2D.Element2D`. Subtracting points or measuring the angle between line
segments of different frames raises :exc:`~pyTooling.Cartesian2D.NotInSameFrameError` instead of mixing unrelated
coordinates.


.. _STRUCT/Cartesian2D/Shapes:

Shapes
******

The shapes live in :mod:`pyTooling.Cartesian2D.Shapes`. The four-cornered shapes form a chain in which **each class
is the one above it with one more constraint**. The constraint is checked in the constructor, so an object that exists
is an object of that shape. A polygon and a circle stand beside that chain.


.. _STRUCT/Cartesian2D/Shape:

Shape
=====

:class:`~pyTooling.Cartesian2D.Shapes.Shape` is the abstract base-class of every 2D shape. It carries no fields; it
exists so a function can accept *a shape*. Instantiating it raises :exc:`~pyTooling.MetaClasses.AbstractClassError`.

A shape is an :ref:`element <STRUCT/Cartesian2D/Element2D>`, so a group can hold it. Every shape implements the
element's two abstract members:

* :attr:`~pyTooling.Cartesian2D.Element2D.BoundingBox` - the smallest axis-aligned
  :ref:`bounding box <STRUCT/Cartesian2D/BoundingBox2D>` enclosing the shape, computed on every access;
* :meth:`~pyTooling.Cartesian2D.Element2D.Move` - shifts all points of the shape by an
  :class:`~pyTooling.Cartesian2D.Offset2D`, in place. Edges share the corners, so they move along.

Every shape is created by :class:`~pyTooling.MetaClasses.ExtendedType` and stores its fields in slots, so a class
derived from a shape can declare ``slots=True`` too and gets no instance dictionary.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Volume`
      |rarr| Its counterpart, the base-class of the 3-dimensional volumes.


.. _STRUCT/Cartesian2D/Polygon:

Polygon
=======

A :class:`~pyTooling.Cartesian2D.Shapes.Polygon` is a closed shape with three or more corners, given as one iterable
of :class:`~pyTooling.Cartesian2D.Point2D` in drawing order. The edges connect the corners in that order, the last
corner back to the first one.

It keeps both views: :attr:`~pyTooling.Cartesian2D.Shapes.Polygon.Points`, the corners as a tuple, and
:attr:`~pyTooling.Cartesian2D.Shapes.Polygon.Segments`, one :class:`~pyTooling.Cartesian2D.LineSegment2D` edge per
corner, with consecutive edges sharing a corner object. The corners are copied by default; ``copyPoints=False`` keeps
the given points instead, as for a :ref:`segment <STRUCT/Cartesian2D/Segment2D>`. The polygon owns its corners, and
its edges have the polygon as parent.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D
   from pyTooling.Cartesian2D.Shapes import Polygon

   triangle = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
   str(triangle)                      # ((0, 0) → (4, 0) → (2, 3) → (0, 0))

A corner that isn't a :class:`~pyTooling.Cartesian2D.Point2D` raises :exc:`TypeError`, fewer than three corners
raise :exc:`~pyTooling.Cartesian2D.NotEnoughCornersError`. The corners are not checked any further: edges may cross
each other.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Shape`
      |rarr| Its base-class, the base-class of the 2-dimensional shapes.
   :ref:`STRUCT/Cartesian2D/Trapezium`
      |rarr| The polygon with exactly four corners, given as four parameters.


.. _STRUCT/Cartesian2D/Trapezium:

Trapezium
=========

A :class:`~pyTooling.Cartesian2D.Shapes.Trapezium` is a four-sided polygon, built from four corners given in the
order ``p00``, ``p01``, ``p11``, ``p10`` - around the outline, not across it.

It keeps both views: :attr:`~pyTooling.Cartesian2D.Shapes.Trapezium.Points`, the four corners it copied, and
:attr:`~pyTooling.Cartesian2D.Shapes.Trapezium.Segments`, the four :class:`~pyTooling.Cartesian2D.LineSegment2D` edges
between them. The segments are built with ``copyPoints=False``, so consecutive edges share a corner object and the
outline stays closed.

Both properties are read-only. Their deprecated aliases ``points`` and ``segments`` are assignable until v11.0.0, but
an assignment replaces only its own tuple: the other one isn't updated, and the shape of a
:class:`~pyTooling.Cartesian2D.Shapes.Rectangle` or :class:`~pyTooling.Cartesian2D.Shapes.Square` isn't checked again.

A corner that isn't a :class:`~pyTooling.Cartesian2D.Point2D` raises :exc:`TypeError`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Shape`
      |rarr| Its base-class, the base-class of the 2-dimensional shapes.
   :ref:`STRUCT/Cartesian2D/Polygon`
      |rarr| The closed shape with any number of corners.


.. _STRUCT/Cartesian2D/Rectangle:

Rectangle
=========

A :class:`~pyTooling.Cartesian2D.Shapes.Rectangle` is a trapezium whose opposite edges are parallel and equal in
length, with 90 |degree| inner angles. The constructor compares the opposite edges' lengths and the four inner angles,
and raises :exc:`ValueError` when the four corners describe something else - a parallelogram, for example, or two
consecutive corners at the same point. Lengths and angles are compared with :func:`math.isclose`, so a rectangle
rotated by an arbitrary angle, with floating-point corners, is accepted.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Trapezium`
      |rarr| Its base-class, the four-cornered shape every other one narrows.
   :ref:`STRUCT/Cartesian3D/Cuboid`
      |rarr| Its counterpart, the volume a rectangle corresponds to.


.. _STRUCT/Cartesian2D/Square:

Square
======

A :class:`~pyTooling.Cartesian2D.Shapes.Square` is a rectangle whose edges are all the same length - one more
comparison, one more :exc:`ValueError`. A rhombus has four equally long edges, but fails the rectangle's angle check.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Rectangle`
      |rarr| Its base-class, the trapezium with four right angles.
   :ref:`STRUCT/Cartesian3D/Cube`
      |rarr| Its counterpart, the volume a square corresponds to.


.. _STRUCT/Cartesian2D/Circle:

Circle
======

A :class:`~pyTooling.Cartesian2D.Shapes.Circle` is placed by its :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Center`, a
:class:`~pyTooling.Cartesian2D.Point2D`, and sized by its :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Radius`, a
positive :class:`int` or :class:`float`. The center is copied by default; ``copyPoints=False`` keeps the given
point instead. The circle owns its center.

Three read-only properties measure it:

* :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Diameter` - twice the radius, in the radius' type;
* :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Circumference` - the length of its outline, a :class:`float`;
* :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Area` - the area it encloses, a :class:`float`.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D
   from pyTooling.Cartesian2D.Shapes import Circle

   bubble = Circle(Point2D(10, 5), 2)
   bubble.Diameter                    # 4
   bubble.Area                        # 12.566...

A center that isn't a :class:`~pyTooling.Cartesian2D.Point2D` or a radius that isn't a number raises
:exc:`TypeError`; a radius of 0 or below raises :exc:`ValueError`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Shape`
      |rarr| Its base-class, the base-class of the 2-dimensional shapes.


.. _STRUCT/Cartesian2D/Path:

Path
====

A :class:`~pyTooling.Cartesian2D.Shapes.Path` is a chain of connected segments, like SVG's ``<path>``: line segments,
:ref:`arcs and Bezier curves <STRUCT/Cartesian2D/CurvedSegments>`, in any mix. It is built from a sequence of
segments, each starting at the end point of the previous one - the coordinates must be equal, else the constructor
raises :exc:`ValueError`. With ``closed=True``, the last segment must end at the start point of the first one; no
closing line is added.

The path copies the given segments as its **edges**, the way a :ref:`polygon <STRUCT/Cartesian2D/Polygon>` builds its
edges from its corners: consecutive edges share their joint, and the path owns every point - the joints in
:attr:`~pyTooling.Cartesian2D.Shapes.Path.Points` and the points defining the curves, like a Bezier curve's control
points.
:attr:`~pyTooling.Cartesian2D.Shapes.Path.Segments` holds the edges, :attr:`~pyTooling.Cartesian2D.Shapes.Path.IsClosed`
tells whether the path is closed. The given segments stay as they are; an edge references its segment's
:attr:`~pyTooling.Cartesian2D.Element2D.Value` and holds a shallow copy of its key-value-pairs.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D, LineSegment2D, ArcSegment2D, QuadraticBezierSegment2D, \
                                            SweepDirection
   from pyTooling.Cartesian2D.Shapes import Path

   drop = Path((
     LineSegment2D(Point2D(0, 0), Point2D(4, 0)),
     ArcSegment2D(Point2D(4, 0), Point2D(4, 4), center=Point2D(4, 2), direction=SweepDirection.Counterclockwise),
     QuadraticBezierSegment2D(Point2D(4, 4), Point2D(2, 6), Point2D(0, 4)),
     LineSegment2D(Point2D(0, 4), Point2D(0, 0))
   ), closed=True)

   line, arc, curve, back = drop.Segments
   len(drop.Points)                   # 4 joints
   line.End is arc.Start              # True
   drop.BoundingBox                   # BoundingBox2D(0, 0, 6.0, 5.0)

The :attr:`~pyTooling.Cartesian2D.Shapes.Path.BoundingBox` is the union of the edges' exact bounding boxes.
:attr:`~pyTooling.Cartesian2D.Shapes.Path.Length` sums the edges' lengths; a Bezier curve has none, so a path with one
raises :exc:`~pyTooling.Exceptions.InvalidOperationError`. Moving or mirroring a path moves or mirrors each joint once
and the edges' other points; a mirrored arc reverses its direction. A copy shares its copied joints between its edges,
like the original.

An open path grows at both ends: :meth:`~pyTooling.Cartesian2D.Shapes.Path.AppendSegment` takes a segment starting at
the path's end point, :meth:`~pyTooling.Cartesian2D.Shapes.Path.PrependSegment` one ending at its start point. The path
copies the segment as a new edge sharing that joint, like the initializer does. A closed path doesn't get opened: both
raise :exc:`~pyTooling.Exceptions.InvalidOperationError`.

.. code-block:: Python

   wire = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))
   wire.AppendSegment(ArcSegment2D(Point2D(4, 0), Point2D(4, 4), height=-2))
   wire.PrependSegment(LineSegment2D(Point2D(-2, 0), Point2D(0, 0)))

   len(wire.Segments)                 # 3
   wire.Points[-1]                    # (4, 4)
   wire.BoundingBox                   # BoundingBox2D(-2, 0, 6.0, 4)

.. seealso::

   :ref:`STRUCT/Cartesian2D/Shape`
      |rarr| Its base-class, the base-class of the 2-dimensional shapes.
   :ref:`STRUCT/Cartesian2D/Polygon`
      |rarr| The closed shape of straight edges, built from its corners.


.. _STRUCT/Cartesian2D/Groups:

Groups
******

The groups live in :mod:`pyTooling.Cartesian2D.Groups`. A group places shapes, segments and other groups at an
offset, so a drawing is built from parts that are positioned as a whole.


.. _STRUCT/Cartesian2D/Element2D:

Element2D
=========

:class:`~pyTooling.Cartesian2D.Element2D` is the abstract base-class of everything a group or canvas can hold: shapes,
segments and groups. An element belongs to at most one group or canvas, its
:attr:`~pyTooling.Cartesian2D.Element2D.Parent`, and offers:

* :attr:`~pyTooling.Cartesian2D.Element2D.BoundingBox` in its frame and
  :attr:`~pyTooling.Cartesian2D.Element2D.AbsoluteBoundingBox` relative to the origin;
* :meth:`~pyTooling.Cartesian2D.Element2D.Move`, shifting it in its frame;
* :meth:`~pyTooling.Cartesian2D.Element2D.MirrorX` and :meth:`~pyTooling.Cartesian2D.Element2D.MirrorY`, mirroring
  it vertically at a vertical axis (the x-coordinates flip) or horizontally at a horizontal axis (the y-coordinates
  flip), through an edge or the center of its bounding box, named by an :class:`~pyTooling.Cartesian2D.Alignment2D` and
  optionally shifted by an offset;
* :meth:`~pyTooling.Cartesian2D.Element2D.MoveTo`, moving it into another group - by default keeping its absolute
  position, so its local coordinates change;
* :meth:`~pyTooling.Cartesian2D.Element2D.AlignTo`, moving it so an edge or the center of its bounding box aligns
  with another element's - see :class:`~pyTooling.Cartesian2D.Alignment2D`. Both elements may be in different groups.

Assigning :attr:`~pyTooling.Cartesian2D.Element2D.Parent` moves an element into a group too, but keeps its local
coordinates. A group can't become its own descendant: that raises :exc:`~pyTooling.Cartesian2D.GroupCycleError`. An
edge of a shape belongs to its shape and can't be moved into a group.

Every shape, segment and group takes a keyword-only parameter ``parent``: a group or canvas given there registers the
new element, as :meth:`~pyTooling.Cartesian2D.Groups.Group2D.AddChild` does. The element registers when it is fully
initialized, so a failing check leaves nothing in the group or canvas. A segment with a shape as ``parent`` is an edge
of that shape instead. A :class:`~pyTooling.Cartesian2D.Point2D` with a ``parent`` is different, it isn't registered:
see :ref:`STRUCT/Cartesian2D/Ownership`.

An element carries an optional :attr:`~pyTooling.Cartesian2D.Element2D.Value` and arbitrary key-value-pairs
(:class:`~pyTooling.DataModel.KeyValuePairsMixin`), given by the keyword-only parameters ``value`` and
``keyValuePairs``. The value is any object, for example the model object a shape draws. The key-value-pairs are read
and written with the dictionary syntax; ``in``, :pycode:`len(element)` and iterating an element address the
key-value-pairs, not its points or children. ``Copy()`` and :func:`copy.copy` keep the value (the same object) and copy
the key-value-pairs shallowly; :func:`copy.deepcopy` copies both deeply. Points carry neither, to stay small.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D
   from pyTooling.Cartesian2D.Shapes import Circle

   pin = Circle(Point2D(10, 5), 2, value="clock", keyValuePairs={"layer": 1})

   pin["inverted"] = True

   pin.Value                          # 'clock'
   len(pin)                           # 2
   pin.Copy()["layer"]                # 1


.. _STRUCT/Cartesian2D/Group2D:

Group2D
=======

A :class:`~pyTooling.Cartesian2D.Groups.Group2D` has an :attr:`~pyTooling.Cartesian2D.Groups.Group2D.Offset` and
:attr:`~pyTooling.Cartesian2D.Groups.Group2D.Children`. The coordinates of all children are **relative to the group**,
and a group without a parent is relative to the origin. So moving a group changes its offset only - the coordinates of
its children stay as they are.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D, Offset2D
   from pyTooling.Cartesian2D.Shapes import Circle
   from pyTooling.Cartesian2D.Groups import Group2D

   wheel = Circle(Point2D(1, 1), 1)
   axle =  Group2D(Offset2D(10, 0), (wheel, ))
   car =   Group2D(Offset2D(0, 5), (axle, ))

   wheel.Center                       # (1, 1), relative to axle
   wheel.Center.Absolute              # (11, 6)
   car.BoundingBox                    # BoundingBox2D(10, 5, 12, 7)
   car.Move(Offset2D(100, 0))         # wheel.Center is still (1, 1)

Children are given to the constructor or added by :meth:`~pyTooling.Cartesian2D.Groups.Group2D.AddChild`, and removed
by :meth:`~pyTooling.Cartesian2D.Groups.Group2D.RemoveChild`. A child of another element raises
:exc:`~pyTooling.Cartesian2D.AlreadyOwnedError` - use :meth:`~pyTooling.Cartesian2D.Element2D.MoveTo` to move it.

A group's :attr:`~pyTooling.Cartesian2D.Groups.Group2D.BoundingBox` is the union of its children's bounding boxes,
shifted by its offset, so it is in the group's own frame. A group without children has no bounding box and raises
:exc:`~pyTooling.Cartesian2D.Groups.EmptyGroupError`. :meth:`~pyTooling.Cartesian2D.Groups.Group2D.DistributeX` and
:meth:`~pyTooling.Cartesian2D.Groups.Group2D.DistributeY` move the children along that axis, so the gaps between them
are equal: either at a given distance after the first child, or evenly between the first and the last child.

The frame of a point, segment or shape inside a group is that group. Subtracting points of different groups raises
:exc:`~pyTooling.Cartesian2D.NotInSameFrameError`; subtract their absolute positions instead.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Ownership`
      |rarr| How points belong to shapes and segments.


.. _STRUCT/Cartesian2D/Canvas2D:

Canvas2D
========

A :class:`~pyTooling.Cartesian2D.Groups.Canvas2D` is the root of a drawing. It holds shapes, segments and groups like a
group does, but has no offset and no parent: its children are relative to the origin. It knows the
:attr:`~pyTooling.Cartesian2D.Groups.Canvas2D.Direction` of its y-axis, a
:class:`~pyTooling.Cartesian2D.Groups.YAxisDirection`:

* ``Up`` - y-coordinates grow upwards, as in mathematics (the default);
* ``Down`` - y-coordinates grow downwards, as on a screen or in SVG.

A canvas has an optional :attr:`~pyTooling.Cartesian2D.Groups.Canvas2D.Size`, a
:class:`~pyTooling.Cartesian2D.Size2D` starting at the origin. Without one, it is open in every direction.

:meth:`~pyTooling.Cartesian2D.Groups.Canvas2D.Mirror` flips the canvas to the other direction, so the drawing looks the
same afterwards. Every level of the drawing negates its y-coordinates - a group's offset relative to its parent, every
point relative to its group. On a canvas with a size, the top level uses ``height - y`` instead, so the drawing stays
on the canvas.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D, Offset2D, Size2D
   from pyTooling.Cartesian2D.Shapes import Circle
   from pyTooling.Cartesian2D.Groups import Canvas2D, Group2D, YAxisDirection

   wheel =  Circle(Point2D(1, 2), 1)
   axle =   Group2D(Offset2D(10, 20), (wheel, ))
   canvas = Canvas2D(YAxisDirection.Down, Size2D(400, 300), (axle, ))

   canvas.Top(wheel)                  # 21
   canvas.Mirror()                    # canvas.Direction is YAxisDirection.Up
   axle.Offset                        # (10, 280)
   wheel.Center                       # (1, -2)
   canvas.Top(wheel)                  # 279

A bounding box keeps its minimum and maximum, whatever the direction. Which of them is the top edge depends on the
canvas: :meth:`~pyTooling.Cartesian2D.Groups.Canvas2D.Top` and :meth:`~pyTooling.Cartesian2D.Groups.Canvas2D.Bottom`
return the absolute y-coordinate of an element's top and bottom edge, and
:attr:`~pyTooling.Cartesian2D.Groups.Canvas2D.TopAlignment` and
:attr:`~pyTooling.Cartesian2D.Groups.Canvas2D.BottomAlignment` the :class:`~pyTooling.Cartesian2D.Alignment2D` to pass
to :meth:`~pyTooling.Cartesian2D.Element2D.AlignTo`. An element of another canvas raises
:exc:`~pyTooling.Cartesian2D.NotInSameFrameError`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Group2D`
      |rarr| The nested container, placed at an offset.


.. _STRUCT/Cartesian3D:

3D Cartesian
############

The :mod:`pyTooling.Cartesian3D` package is :mod:`pyTooling.Cartesian2D` with a third axis: the same classes, the
same arithmetic, and a ``z`` coordinate throughout. Everything above applies, so this section names only what
differs.

.. seealso::

   :ref:`STRUCT/Cartesian2D`
      |rarr| The 2-dimensional classes this package extends, where the arithmetic is written out.


.. _STRUCT/Cartesian3D/Classes:

Basic Classes
*************


.. _STRUCT/Cartesian3D/Point3D:

Point3D
=======

A :class:`~pyTooling.Cartesian3D.Point3D` has :attr:`~pyTooling.Cartesian3D.Point3D.X`,
:attr:`~pyTooling.Cartesian3D.Point3D.Y` and :attr:`~pyTooling.Cartesian3D.Point3D.Z`, and the same arithmetic against
an :class:`~pyTooling.Cartesian3D.Offset3D`. A plain 3-tuple is accepted wherever an offset is.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Point2D`
      |rarr| Its counterpart, the 2-dimensional point.


.. _STRUCT/Cartesian3D/Origin3D:

Origin3D
========

:class:`~pyTooling.Cartesian3D.Origin3D` is a :class:`~pyTooling.Cartesian3D.Point3D` fixed at ``(0, 0, 0)``.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Point3D`
      |rarr| Its base-class, the point with a ``z`` coordinate.
   :ref:`STRUCT/Cartesian2D/Origin2D`
      |rarr| Its counterpart, the 2-dimensional origin.


.. _STRUCT/Cartesian3D/Offset3D:

Offset3D
========

:class:`~pyTooling.Cartesian3D.Offset3D` holds :attr:`~pyTooling.Cartesian3D.Offset3D.XOffset`,
:attr:`~pyTooling.Cartesian3D.Offset3D.YOffset` and :attr:`~pyTooling.Cartesian3D.Offset3D.ZOffset`, and negates, adds,
subtracts and compares as its 2D counterpart does.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Offset2D`
      |rarr| Its counterpart, the 2-dimensional offset.


.. _STRUCT/Cartesian3D/Size3D:

Size3D
======

:class:`~pyTooling.Cartesian3D.Size3D` is :attr:`~pyTooling.Cartesian3D.Size3D.Width`,
:attr:`~pyTooling.Cartesian3D.Size3D.Height` and :attr:`~pyTooling.Cartesian3D.Size3D.Depth`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Size2D`
      |rarr| Its counterpart, the 2-dimensional size.


.. _STRUCT/Cartesian3D/Segment3D:

Segment3D
=========

:class:`~pyTooling.Cartesian3D.Segment3D` is a :attr:`~pyTooling.Cartesian3D.Segment3D.Start` and an
:attr:`~pyTooling.Cartesian3D.Segment3D.End` point, copied on construction unless
``copyPoints=False``.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Segment2D`
      |rarr| Its counterpart, the 2-dimensional segment.


.. _STRUCT/Cartesian3D/LineSegment3D:

LineSegment3D
=============

:class:`~pyTooling.Cartesian3D.LineSegment3D` adds the measurements - length in three dimensions, the angle to
another line segment, and conversion to an offset.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Segment3D`
      |rarr| Its base-class, the segment between two 3D points.
   :ref:`STRUCT/Cartesian2D/LineSegment2D`
      |rarr| Its counterpart, the 2-dimensional line segment.


.. _STRUCT/Cartesian3D/Volumes:

Volumes
*******

.. attention::

   The volumes in :mod:`pyTooling.Cartesian3D.Volumes` are **declared but not implemented**. All three classes are
   empty: no corners, no constructor, no validation. They are not the 3D counterpart of the 2D shapes yet, and are
   listed here because they exist and can be subclassed, not because they can be used.


.. _STRUCT/Cartesian3D/Volume:

Volume
======

:class:`~pyTooling.Cartesian3D.Volumes.Volume` is the empty base-class of every 3D volume, matching
:class:`~pyTooling.Cartesian2D.Shapes.Shape`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Shape`
      |rarr| Its counterpart, the base-class of the 2-dimensional shapes.


.. _STRUCT/Cartesian3D/Cuboid:

Cuboid
======

:class:`~pyTooling.Cartesian3D.Volumes.Cuboid` is intended as a volume bounded by six rectangles - the counterpart
of :class:`~pyTooling.Cartesian2D.Shapes.Rectangle`.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Volume`
      |rarr| Its base-class, the base-class of the 3-dimensional volumes.
   :ref:`STRUCT/Cartesian2D/Rectangle`
      |rarr| Its counterpart, the trapezium with four right angles.


.. _STRUCT/Cartesian3D/Cube:

Cube
====

:class:`~pyTooling.Cartesian3D.Volumes.Cube` is intended as a cuboid of six equally sized squares - the counterpart
of :class:`~pyTooling.Cartesian2D.Shapes.Square`.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Cuboid`
      |rarr| Its base-class, the volume a rectangle corresponds to.
   :ref:`STRUCT/Cartesian2D/Square`
      |rarr| Its counterpart, the rectangle with four equal sides.