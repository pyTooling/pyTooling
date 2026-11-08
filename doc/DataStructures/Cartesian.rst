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
  closed, like SVG's ``<path>``; a :class:`~pyTooling.Cartesian2D.Shapes.PolyLine` is a path of line segments, built
  from points. Paths, polylines and polygons convert into each other, where no approximation is needed.
* **Shapes placed by their corners**, so a shape is positioned by the points it is built from - a circle by its
  center.
* Shapes validated on construction: a :class:`~pyTooling.Cartesian2D.Shapes.Polygon` with any number of corners, the
  four-cornered :class:`~pyTooling.Cartesian2D.Shapes.Trapezium` narrowed down to a
  :class:`~pyTooling.Cartesian2D.Shapes.Square`, a :class:`~pyTooling.Cartesian2D.Shapes.Circle` and an axis-aligned
  :class:`~pyTooling.Cartesian2D.Shapes.Ellipse`.
* **Closed shapes measured** - every :class:`~pyTooling.Cartesian2D.Shapes.Geometry2D`, like a polygon or a circle,
  reports the area it encloses and its perimeter, an ellipse an approximate one; a circle its diameter too.
* **Bounding boxes** - every shape and segment reports the smallest axis-aligned
  :class:`~pyTooling.Cartesian2D.BoundingBox2D` enclosing it, and bounding boxes unite, intersect and contain points.
* **Shapes and segments moved as a whole** - ``Move(offset)`` shifts all their points in place.
* **Mirroring at a shared line** - a :class:`~pyTooling.Cartesian2D.VerticalLine2D` or
  :class:`~pyTooling.Cartesian2D.HorizontalLine2D` is in absolute coordinates, so elements of different groups are
  mirrored at the same line.
* **Points owned by one element** - a shape or segment owns its points, so a point can't silently belong to two
  shapes. Coordinates of different frames aren't mixed in a computation.
* **Groups with relative coordinates** - a :class:`~pyTooling.Cartesian2D.Groups.Group2D` holds shapes, segments and
  groups at an offset, so moving a group moves everything in it. Absolute positions, alignment and distribution are
  computed across groups.
* **Data attached to elements** - every shape, segment and group carries a value and key-value-pairs, so a drawing
  element knows the model object it draws.
* **A canvas knowing its y-axis** - a :class:`~pyTooling.Cartesian2D.Groups.Canvas2D` is the root of a drawing, with
  the y-axis pointing up (mathematics) or down (screen, SVG), and flips a whole drawing to the other direction.
* **Drawing styles** - colors, strokes, fills and fonts as values, which elements can share, and drawable shapes
  carrying an outline and a fill.
* **Independent copies** - ``Copy()``, :func:`copy.copy` and :func:`copy.deepcopy` return an object sharing no point
  with the original. A shape's copy is of the same class, and its edges share the copied corners. A copy owns its
  points and isn't in a group.
* Conversion to plain tuples through ``ToTuple``, for handing coordinates to a library that expects them.


.. _STRUCT/Cartesian2D/MissingFeatures:

Missing Features
================

* Rotation and scaling - an element can be shifted and mirrored at a vertical or horizontal axis, but not rotated or
  scaled.
* Rotated ellipses and elliptical arcs.
* The length of a Bezier curve.
* Exact containment and intersection tests (*is this point inside that rotated rectangle?*). Only bounding boxes are
  compared.


.. _STRUCT/Cartesian2D/PlannedFeatures:

Planned Features
================

* The 3-dimensional volumes, which currently exist as empty classes - see :ref:`STRUCT/Cartesian3D/Volumes`.


.. _STRUCT/Cartesian2D/RejectedFeatures:

Out of Scope
============

* A general-purpose geometry or linear-algebra library. These classes exist to give coordinates a **name and a
  type** in the packages using them. |br|
  For doing real geometry have a look at `NumPy <https://numpy.org/>`__ or
  `Shapely <https://shapely.readthedocs.io/>`__.
* Rendering. Styles describe how an element looks, but nothing here draws anything - ``ToTuple`` hands the numbers
  to whatever does.
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


.. _STRUCT/Cartesian2D/Line2D:

Line2D
======

A :class:`~pyTooling.Cartesian2D.Line2D` is a line in the geometric sense: infinite in both directions, unlike a
:class:`~pyTooling.Cartesian2D.LineSegment2D`, which ends at its start and end point. It is the abstract base-class of
the lines an element can be mirrored at:

* :class:`~pyTooling.Cartesian2D.VerticalLine2D` - the line ``x = c``, all its points have the same
  :attr:`~pyTooling.Cartesian2D.VerticalLine2D.X`;
* :class:`~pyTooling.Cartesian2D.HorizontalLine2D` - the line ``y = c``, all its points have the same
  :attr:`~pyTooling.Cartesian2D.HorizontalLine2D.Y`.

:func:`str` returns the line's equation.

A line is in **absolute coordinates**, relative to the origin. :meth:`~pyTooling.Cartesian2D.Element2D.MirrorAt`
mirrors an element at it in the element's frame, so elements of different groups are mirrored at the same line.
:meth:`VerticalLine2D.FromElement <pyTooling.Cartesian2D.VerticalLine2D.FromElement>` creates the line through an edge
or the center of an element's absolute bounding box, named by an :class:`~pyTooling.Cartesian2D.Alignment2D` (``MinX``,
``CenterX`` or ``MaxX``); :meth:`HorizontalLine2D.FromElement <pyTooling.Cartesian2D.HorizontalLine2D.FromElement>`
takes ``MinY``, ``CenterY`` or ``MaxY``.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D, Offset2D, Alignment2D, VerticalLine2D, HorizontalLine2D
   from pyTooling.Cartesian2D.Shapes import Circle, Square
   from pyTooling.Cartesian2D.Groups import Group2D

   pad =    Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2))
   wheel =  Circle(Point2D(1, 1), 1)
   axle =   Group2D(Offset2D(10, 0), (wheel, ))
   mirror = VerticalLine2D(20)

   str(mirror)                        # 'x = 20'
   pad.MirrorAt(mirror)               # pad.BoundingBox is BoundingBox2D(38, 0, 40, 2)
   wheel.MirrorAt(mirror)             # wheel.Center is (19, 1), relative to axle
   wheel.Center.Absolute              # (29, 1)

   HorizontalLine2D.FromElement(wheel, Alignment2D.MinY)   # HorizontalLine2D(0)

Like a :ref:`style <STRUCT/Cartesian2D/Drawing>`, a line is a **value**: its properties are read-only, it compares
with ``==`` and ``!=`` by value and is hashable. A vertical and a horizontal line are never equal.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Plane3D`
      |rarr| Its counterpart, the plane parallel to a coordinate plane.


.. _STRUCT/Cartesian2D/Ray2D:

Ray2D
=====

A :class:`~pyTooling.Cartesian2D.Ray2D` is a half-line: it starts at a point and is infinite in one direction. It is
built from a start point and a direction, an :class:`~pyTooling.Cartesian2D.Offset2D`; it copies both, so it owns no
point of an element. The start point is taken in absolute coordinates: a point inside a group is converted. A zero
direction raises :exc:`ValueError`. :attr:`~pyTooling.Cartesian2D.Ray2D.Start` and
:attr:`~pyTooling.Cartesian2D.Ray2D.Direction` return the stored point and offset.
:meth:`~pyTooling.Cartesian2D.Ray2D.PointAt` returns the point at a distance from the start point, whatever the length
of the direction; a negative distance raises :exc:`ValueError`.

.. code-block:: Python

   from pyTooling.Cartesian2D import Point2D, Offset2D, Ray2D

   ray = Ray2D(Point2D(1, 2), Offset2D(3, 4))

   str(ray)                           # '(1, 2) + t * (3, 4), t >= 0'
   ray.PointAt(5)                     # (4.0, 6.0)

Like a line, a ray is in absolute coordinates and compares by value; as its start point and direction can be changed, it
is unhashable (like an :class:`~pyTooling.Cartesian2D.Offset2D`). Two rays are equal (``==``), if they start at the same
point and their directions point the same way - the cross product of the directions is zero and their dot product is
positive. The lengths of the directions don't matter, and integer coordinates compare exactly:

.. code-block:: Python

   Ray2D(Point2D(1, 2), Offset2D(3, 4)) == Ray2D(Point2D(1, 2), Offset2D(6, 8))     # True
   Ray2D(Point2D(1, 2), Offset2D(3, 4)) == Ray2D(Point2D(1, 2), Offset2D(-3, -4))   # False, opposite direction


.. _STRUCT/Cartesian2D/Segment2D:

Segment2D
=========

A :class:`~pyTooling.Cartesian2D.Segment2D` is a :attr:`~pyTooling.Cartesian2D.Segment2D.Start` and an
:attr:`~pyTooling.Cartesian2D.Segment2D.End` point.

It is abstract: a straight segment is a :class:`~pyTooling.Cartesian2D.LineSegment2D`, curved segments are described
below.

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

The geometry behind arcs and circles is public: :func:`~pyTooling.Cartesian2D.chordPoint` computes the point at a
height over a chord, :func:`~pyTooling.Cartesian2D.circumcenter` the center of the circle through three points.

A ``center`` or an ``arcPoint`` is converted to the sagitta, the height at the chord's midpoint. An arc isn't a circle:
a start and an end point at the same position have no chord and raise :exc:`ValueError`, whatever the group - also
when assigned to :attr:`~pyTooling.Cartesian2D.ArcSegment2D.Start` or :attr:`~pyTooling.Cartesian2D.ArcSegment2D.End`.
An end point moved in place onto the other one isn't checked: the arc has no center then.

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

The edges of a shape, like those of a polygon or a polyline, are views: they reference the shape's corners, but don't
own them. Moving an edge moves the corners it references; replacing an edge's point raises
:exc:`~pyTooling.Cartesian2D.NotOwnedError`.

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
is an object of that shape. A polygon, a circle and an ellipse stand beside that chain. The closed shapes derive from
:ref:`Geometry2D <STRUCT/Cartesian2D/Geometry2D>`, a circle and an ellipse through
:ref:`EllipticalGeometry2D <STRUCT/Cartesian2D/EllipticalGeometry2D>`, which holds their center; a
:ref:`path <STRUCT/Cartesian2D/Path>` and a :ref:`polyline <STRUCT/Cartesian2D/PolyLine>`, a path of line segments, are
shapes, but no geometries.


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


.. _STRUCT/Cartesian2D/Geometry2D:

Geometry2D
==========

:class:`~pyTooling.Cartesian2D.Shapes.Geometry2D` is the abstract base-class of the closed shapes, the ones enclosing
an area. Besides the members of a :ref:`shape <STRUCT/Cartesian2D/Shape>`, it declares two abstract read-only
properties:

* :attr:`~pyTooling.Cartesian2D.Shapes.Geometry2D.Area` - the area it encloses, a :class:`float`;
* :attr:`~pyTooling.Cartesian2D.Shapes.Geometry2D.Perimeter` - the length of its outline, a :class:`float`.

A polygon and a trapezium compute both from their corners, which may be given clockwise or counterclockwise; a
rectangle and a square inherit them. A circle and an ellipse compute them from their radii; they share their center
through :ref:`EllipticalGeometry2D <STRUCT/Cartesian2D/EllipticalGeometry2D>`. A :ref:`path <STRUCT/Cartesian2D/Path>`
is a shape, but no geometry, even when it is closed.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D
   from pyTooling.Cartesian2D.Shapes import Polygon

   corner = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(4, 1), Point2D(1, 1), Point2D(1, 3), Point2D(0, 3)))
   corner.Area                        # 6.0
   corner.Perimeter                   # 14.0

.. seealso::

   :ref:`STRUCT/Cartesian2D/Shape`
      |rarr| Its base-class, the base-class of the 2-dimensional shapes.


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
raise :exc:`~pyTooling.Cartesian2D.NotEnoughCornersError`. Edges must not cross: two edges may have only their shared
corner in common, else :exc:`~pyTooling.Cartesian2D.CrossingEdgesError` is raised - for crossing edges, a corner on
another edge, or an edge running back along the previous one. The coordinates are compared exactly. Corners moved in
place later aren't checked again.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Geometry2D`
      |rarr| Its base-class, the base-class of the closed 2-dimensional shapes.
   :ref:`STRUCT/Cartesian2D/PolyLine`
      |rarr| A path of line segments, built from points like a polygon.
   :ref:`STRUCT/Cartesian2D/Trapezium`
      |rarr| The polygon with exactly four corners, given as four parameters.


.. _STRUCT/Cartesian2D/Trapezium:

Trapezium
=========

A :class:`~pyTooling.Cartesian2D.Shapes.Trapezium` is a :ref:`polygon <STRUCT/Cartesian2D/Polygon>` with exactly
four corners, given as four parameters in the order ``p00``, ``p01``, ``p11``, ``p10`` - around the outline, not
across it. It copies them, and inherits everything else from the polygon: the corners in
:attr:`~pyTooling.Cartesian2D.Shapes.Polygon.Points`, the four :class:`~pyTooling.Cartesian2D.LineSegment2D` edges in
:attr:`~pyTooling.Cartesian2D.Shapes.Polygon.Segments` sharing the corners, its area and perimeter, and the check that
its edges don't cross.

Both properties are read-only. Their deprecated aliases ``points`` and ``segments`` are assignable until v11.0.0, but
an assignment replaces only its own tuple: the other one isn't updated, and the shape of a
:class:`~pyTooling.Cartesian2D.Shapes.Rectangle` or :class:`~pyTooling.Cartesian2D.Shapes.Square` isn't checked again.

A corner that isn't a :class:`~pyTooling.Cartesian2D.Point2D` raises :exc:`TypeError`, crossing edges raise
:exc:`~pyTooling.Cartesian2D.CrossingEdgesError`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Polygon`
      |rarr| Its base-class, the closed shape with any number of corners.


.. _STRUCT/Cartesian2D/Rectangle:

Rectangle
=========

A :class:`~pyTooling.Cartesian2D.Shapes.Rectangle` is a trapezium whose opposite edges are parallel and equal in
length, with 90 |degree| inner angles. The constructor compares the opposite edges' lengths and the four inner angles,
and raises :exc:`ValueError` when the four corners describe something else - a parallelogram, for example. Two
consecutive corners at the same point make edges touching each other, which the polygon rejects with
:exc:`~pyTooling.Cartesian2D.CrossingEdgesError`. Lengths and angles are compared with :func:`math.isclose`, so a
rectangle rotated by an arbitrary angle, with floating-point corners, is accepted.

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


.. _STRUCT/Cartesian2D/EllipticalGeometry2D:

EllipticalGeometry2D
====================

:class:`~pyTooling.Cartesian2D.Shapes.EllipticalGeometry2D` is the abstract base-class of the round
:ref:`geometries <STRUCT/Cartesian2D/Geometry2D>`, the closed shapes around a center they own: a
:ref:`circle <STRUCT/Cartesian2D/Circle>` and an :ref:`ellipse <STRUCT/Cartesian2D/Ellipse>` derive from it. It holds
the :attr:`~pyTooling.Cartesian2D.Shapes.EllipticalGeometry2D.Center`, a :class:`~pyTooling.Cartesian2D.Point2D`. The
center is copied by default; with ``copyPoints=False``, the given point is kept, and a point owned by another element
raises :exc:`~pyTooling.Cartesian2D.AlreadyOwnedError`. Moving or mirroring the shape moves or mirrors its center.

The radii are fields of the derived classes, and so are the bounding box, the area and the perimeter computed from
them: a circle has one radius, an ellipse two, and neither class derives from the other. Instantiating
:class:`~pyTooling.Cartesian2D.Shapes.EllipticalGeometry2D` raises :exc:`~pyTooling.MetaClasses.AbstractClassError`.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D, Offset2D
   from pyTooling.Cartesian2D.Shapes import Circle, Ellipse

   bubble = Circle(Point2D(0, 0), 2)
   egg =    Ellipse(Point2D(5, 0), 3, 2)
   for shape in (bubble, egg):
     shape.Move(Offset2D(1, 1))

   bubble.Center                      # (1, 1)
   egg.Center                         # (6, 1)

.. seealso::

   :ref:`STRUCT/Cartesian2D/Geometry2D`
      |rarr| Its base-class, the base-class of the closed 2-dimensional shapes.
   :ref:`STRUCT/Cartesian2D/Circle`
      |rarr| The round shape with one radius.
   :ref:`STRUCT/Cartesian2D/Ellipse`
      |rarr| The round shape with two radii.


.. _STRUCT/Cartesian2D/Circle:

Circle
======

A :class:`~pyTooling.Cartesian2D.Shapes.Circle` is placed by its :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Center`, a
:class:`~pyTooling.Cartesian2D.Point2D`, and sized by its :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Radius`, a
positive :class:`int` or :class:`float`. The center is copied by default; ``copyPoints=False`` keeps the given
point instead. The circle owns its center.

Three read-only properties measure it:

* :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Diameter` - twice the radius, in the radius' type;
* :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Perimeter` - the length of its outline (circumference), a :class:`float`;
* :attr:`~pyTooling.Cartesian2D.Shapes.Circle.Area` - the area it encloses, a :class:`float`.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D
   from pyTooling.Cartesian2D.Shapes import Circle

   bubble = Circle(Point2D(10, 5), 2)
   bubble.Diameter                    # 4
   bubble.Area                        # 12.566...

A center that isn't a :class:`~pyTooling.Cartesian2D.Point2D` or a radius that isn't a number raises
:exc:`TypeError`; a radius of 0 or below raises :exc:`ValueError`.

Two class methods create a circle from the parameter groups of an :ref:`arc <STRUCT/Cartesian2D/ArcSegment2D>`; the
circle owns a new center, the given points are only read:

* :meth:`~pyTooling.Cartesian2D.Shapes.Circle.FromPoints` - the circle through three or more points: the first three
  must be distinct and not on one line, and every further point must be on their circle;
* :meth:`~pyTooling.Cartesian2D.Shapes.Circle.FromChord` - the circle through the end points of a chord and a point
  at a signed ``height`` over the chord, measured at ``chordPosition`` (default ``0.5``, the midpoint). A positive
  height is on the left of the chord, seen from its start point.

.. code-block:: Python

   ring = Circle.FromPoints((Point2D(0, 0), Point2D(4, 0), Point2D(0, 3), Point2D(4, 3)))
   ring.Center                        # (2.0, 1.5)
   ring.Radius                        # 2.5

   dome = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), 1)
   dome.Center                        # (2.0, -1.5)

.. seealso::

   :ref:`STRUCT/Cartesian2D/EllipticalGeometry2D`
      |rarr| Its base-class, the base-class of the round 2-dimensional shapes around a center.
   :ref:`STRUCT/Cartesian2D/Ellipse`
      |rarr| The round shape with two radii.
   :ref:`STRUCT/Cartesian2D/ArcSegment2D`
      |rarr| A piece of a circle, given by the same parameter groups.


.. _STRUCT/Cartesian2D/Ellipse:

Ellipse
=======

An :class:`~pyTooling.Cartesian2D.Shapes.Ellipse` is placed by its
:attr:`~pyTooling.Cartesian2D.Shapes.Ellipse.Center`, a :class:`~pyTooling.Cartesian2D.Point2D`, and sized by two
radii, SVG's ``rx`` and ``ry``: :attr:`~pyTooling.Cartesian2D.Shapes.Ellipse.RadiusX` in x-direction and
:attr:`~pyTooling.Cartesian2D.Shapes.Ellipse.RadiusY` in y-direction, each a positive :class:`int` or :class:`float`.
Its axes are parallel to the coordinate axes; an ellipse can't be rotated. The center is copied by default;
``copyPoints=False`` keeps the given point instead. The ellipse owns its center.

An ellipse is a closed shape, an :ref:`EllipticalGeometry2D <STRUCT/Cartesian2D/EllipticalGeometry2D>` like a
circle, measured by two read-only properties:

* :attr:`~pyTooling.Cartesian2D.Shapes.Ellipse.Area` - the area it encloses, a :class:`float`;
* :attr:`~pyTooling.Cartesian2D.Shapes.Ellipse.Perimeter` - the length of its outline (circumference), a
  :class:`float`. It is Ramanujan's second approximation: exact for equal radii, otherwise less than 0.04 % too small.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D
   from pyTooling.Cartesian2D.Shapes import Ellipse

   egg = Ellipse(Point2D(10, 5), 3, 2)
   egg.BoundingBox                    # BoundingBox2D(7, 3, 13, 7)
   egg.Area                           # 18.849...
   egg.Perimeter                      # 15.865...

A center that isn't a :class:`~pyTooling.Cartesian2D.Point2D` or a radius that isn't a number raises
:exc:`TypeError`; a radius of 0 or below raises :exc:`ValueError`. Equal radii are accepted: such an ellipse is a
circle, but not a :class:`~pyTooling.Cartesian2D.Shapes.Circle` object.

.. seealso::

   :ref:`STRUCT/Cartesian2D/EllipticalGeometry2D`
      |rarr| Its base-class, the base-class of the round 2-dimensional shapes around a center.
   :ref:`STRUCT/Cartesian2D/Circle`
      |rarr| The round shape with one radius.


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


.. _STRUCT/Cartesian2D/PolyLine:

PolyLine
========

A :class:`~pyTooling.Cartesian2D.Shapes.PolyLine` is a :ref:`path <STRUCT/Cartesian2D/Path>` of line segments, like
SVG's ``<polyline>``. It is built from two or more points instead of segments, given as one iterable of
:class:`~pyTooling.Cartesian2D.Point2D` in drawing order: every edge is a :class:`~pyTooling.Cartesian2D.LineSegment2D`
between two consecutive points, and consecutive edges share their point. With ``closed=True``, an edge connects the
last point back to the first one; a closed polyline needs three or more points.

It inherits the path's members: :attr:`~pyTooling.Cartesian2D.Shapes.Path.Points`,
:attr:`~pyTooling.Cartesian2D.Shapes.Path.Segments`, :attr:`~pyTooling.Cartesian2D.Shapes.Path.IsClosed`,
:attr:`~pyTooling.Cartesian2D.Shapes.Path.Length`, the bounding box, moving and mirroring. The points are copied by
default; ``copyPoints=False`` keeps the given points instead, as for a polygon.

.. code-block:: Python

   from pyTooling.Cartesian2D        import Point2D
   from pyTooling.Cartesian2D.Shapes import PolyLine

   zigzag = PolyLine((Point2D(0, 0), Point2D(3, 4), Point2D(6, 0)))
   str(zigzag)                        # ((0, 0) → (3, 4) → (6, 0))
   zigzag.Length                      # 10.0

   wedge = PolyLine((Point2D(0, 0), Point2D(3, 4), Point2D(6, 0)), closed=True)
   len(wedge.Segments)                # 3
   wedge.Length                       # 16.0

A point that isn't a :class:`~pyTooling.Cartesian2D.Point2D` raises :exc:`TypeError`, fewer than two points - three
for a closed polyline - raise :exc:`~pyTooling.Cartesian2D.NotEnoughCornersError`. Unlike a polygon's, a polyline's
edges may cross each other.

Paths, polylines and polygons convert into each other, where no approximation is needed. Each conversion copies the
points, references the same value and copies the key-value-pairs shallowly:

* :meth:`~pyTooling.Cartesian2D.Shapes.Path.ToPolyLine` - a path of line segments becomes a polyline, open or closed
  like the path; a polyline inherits it, a copy;
* :meth:`~pyTooling.Cartesian2D.Shapes.Path.ToPolygon` - a closed path of line segments, a closed polyline too,
  becomes a polygon, which checks its edges for crossings;
* :meth:`~pyTooling.Cartesian2D.Shapes.Polygon.ToPolyLine` - a polygon, and so a trapezium, rectangle or square,
  becomes a closed polyline.

An open path or polyline encloses no area: :meth:`~pyTooling.Cartesian2D.Shapes.Path.ToPolygon` raises
:exc:`~pyTooling.Exceptions.InvalidOperationError`. So do both path conversions for a path with an arc or a Bezier
curve, as a curve can't be converted without an approximation.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Path`
      |rarr| Its base-class, the chain of segments of any kind.
   :ref:`STRUCT/Cartesian2D/Polygon`
      |rarr| The closed shape of straight edges, which encloses an area.


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
* :meth:`~pyTooling.Cartesian2D.Element2D.MirrorAt`, mirroring it at a :ref:`line <STRUCT/Cartesian2D/Line2D>` in
  absolute coordinates, which several elements can share;
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
the key-value-pairs shallowly; :func:`copy.deepcopy` copies both deeply. Points carry neither, to stay small. A copy
isn't in the group or canvas of the original.

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

``Copy()`` and :func:`copy.copy` copy a group or a canvas with a copy of each child, made by the child's ``Copy()``;
:func:`copy.deepcopy` uses deep copies of the children. The copy of a group has no parent.

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


.. _STRUCT/Cartesian2D/Drawing:

Drawing
*******

The styles live in :mod:`pyTooling.Cartesian2D.Drawing`. They are **values**: their properties are read-only, they
compare with ``==`` and ``!=`` by value and are hashable, so any number of elements can share one style object. A
style of another type in a comparison raises :exc:`TypeError`.

.. code-block:: Python

   from pyTooling.Cartesian2D.Drawing import Fill, Font, LineStyle, RGBAColor, Stroke

   black =   RGBAColor(0, 0, 0)
   outline = Stroke(1.5, black, LineStyle.Dashed)
   shade =   Fill(RGBAColor.Parse("#ff800080"))
   label =   Font("monospace", 10, bold=True)

   shade.Color.Alpha                  # 0.50196...
   shade.Color.ToHex()                # '#ff800080'
   outline == Stroke(1.5, black, LineStyle.Dashed)   # True


.. _STRUCT/Cartesian2D/Color:

Color
=====

:class:`~pyTooling.Cartesian2D.Drawing.Color` is the abstract base-class of all colors. A color is given in a color
system, and every color converts to red, green and blue components and an opacity with
:meth:`~pyTooling.Cartesian2D.Drawing.Color.ToRGBA`, so a renderer handles any color. A stroke or fill takes a color of
any color system. A further color system, like HSL or CMYK, is a class derived from
:class:`~pyTooling.Cartesian2D.Drawing.Color` implementing :meth:`~pyTooling.Cartesian2D.Drawing.Color.ToRGBA`.

An :class:`~pyTooling.Cartesian2D.Drawing.RGBAColor` has a :attr:`~pyTooling.Cartesian2D.Drawing.RGBAColor.Red`,
:attr:`~pyTooling.Cartesian2D.Drawing.RGBAColor.Green` and :attr:`~pyTooling.Cartesian2D.Drawing.RGBAColor.Blue`
component, integers from 0 to 255, and an opacity :attr:`~pyTooling.Cartesian2D.Drawing.RGBAColor.Alpha` from ``0.0``
(transparent) to ``1.0`` (opaque, the default). A component out of range raises :exc:`ValueError`. Its
:meth:`~pyTooling.Cartesian2D.Drawing.RGBAColor.ToRGBA` returns the color itself.

:meth:`~pyTooling.Cartesian2D.Drawing.RGBAColor.Parse` reads the hexadecimal form of CSS and SVG, ``#rrggbb`` or
``#rrggbbaa``, and :meth:`~pyTooling.Cartesian2D.Drawing.RGBAColor.ToHex` and :func:`str` return it. The opacity is
stored as given, but written with two hexadecimal digits, so ``ToHex()`` rounds it to a multiple of 1/255.


.. _STRUCT/Cartesian2D/Stroke:

Stroke and Fill
===============

A :class:`~pyTooling.Cartesian2D.Drawing.Stroke` is the style of a line or an outline: a positive
:attr:`~pyTooling.Cartesian2D.Drawing.Stroke.Width` in the unit of the coordinates, a
:attr:`~pyTooling.Cartesian2D.Drawing.Stroke.Color` and a :class:`~pyTooling.Cartesian2D.Drawing.LineStyle`: ``Solid``
(the default), ``Dashed`` or ``Dotted``. A :class:`~pyTooling.Cartesian2D.Drawing.Fill` is the style of an area, its
:attr:`~pyTooling.Cartesian2D.Drawing.Fill.Color`.


.. _STRUCT/Cartesian2D/Font:

Font
====

A :class:`~pyTooling.Cartesian2D.Drawing.Font` has a :attr:`~pyTooling.Cartesian2D.Drawing.Font.Family` and a
:attr:`~pyTooling.Cartesian2D.Drawing.Font.Size` in points. The family is a font name or a generic family, as in CSS -
``"DejaVu Sans Mono"`` or ``"monospace"``; a renderer maps it to its format.

Its style has three independent parts, as in CSS: the font is :attr:`~pyTooling.Cartesian2D.Drawing.Font.Bold` or not,
has :attr:`~pyTooling.Cartesian2D.Drawing.Font.SmallCaps` or not, and its letters have a posture, the
:attr:`~pyTooling.Cartesian2D.Drawing.Font.FontStyle`: a :class:`~pyTooling.Cartesian2D.Drawing.FontStyle` of
``Upright`` (the default), ``Italic`` or ``Slanted``.


.. _STRUCT/Cartesian2D/Drawables:

Drawable Shapes
===============

A drawable shape is a geometry class with a style, and has **the same name**:
:class:`pyTooling.Cartesian2D.Drawing.Rectangle` is a :class:`pyTooling.Cartesian2D.Shapes.Rectangle`, so it is
checked, measured, moved, mirrored and grouped like one. :mod:`~pyTooling.Cartesian2D.Drawing` has a drawable
:class:`~pyTooling.Cartesian2D.Drawing.Polygon`, :class:`~pyTooling.Cartesian2D.Drawing.Trapezium`,
:class:`~pyTooling.Cartesian2D.Drawing.Rectangle`, :class:`~pyTooling.Cartesian2D.Drawing.Square`,
:class:`~pyTooling.Cartesian2D.Drawing.Circle`, :class:`~pyTooling.Cartesian2D.Drawing.Ellipse`,
:class:`~pyTooling.Cartesian2D.Drawing.Path` and :class:`~pyTooling.Cartesian2D.Drawing.PolyLine`, and the drawable
segments :class:`~pyTooling.Cartesian2D.Drawing.LineSegment2D`, :class:`~pyTooling.Cartesian2D.Drawing.ArcSegment2D`,
:class:`~pyTooling.Cartesian2D.Drawing.QuadraticBezierSegment2D` and
:class:`~pyTooling.Cartesian2D.Drawing.CubicBezierSegment2D`.

The constructors take the geometry's parameters, the keyword-only parameters ``value`` and ``keyValuePairs`` of every
:ref:`element <STRUCT/Cartesian2D/Element2D>`, and the keyword-only parameters ``stroke`` and ``fill``:

* :attr:`~pyTooling.Cartesian2D.Drawing.StrokeMixin.Stroke` - the outline, or ``None`` for no outline;
* :attr:`~pyTooling.Cartesian2D.Drawing.StyleMixin.Fill` - the area, or ``None`` for a transparent area.

Both are properties with a setter; a value of another type raises :exc:`TypeError`. A segment has no area, so it has a
stroke only (:class:`~pyTooling.Cartesian2D.Drawing.StrokeMixin`); the shapes have both
(:class:`~pyTooling.Cartesian2D.Drawing.StyleMixin`). A path or polyline encloses an area only when it is closed: a
fill for an open one raises :exc:`ValueError`, given to the constructor or assigned. ``Copy()`` and :func:`copy.copy`
return a drawable shape of the same class with copied points, the same style objects and value, and a shallow copy of
the key-value-pairs. :func:`copy.deepcopy` keeps the same style objects too, and copies the value and the
key-value-pairs deeply.

.. code-block:: Python

   from pyTooling.Cartesian2D         import Point2D
   from pyTooling.Cartesian2D.Drawing import Circle, Fill, PolyLine, Rectangle, RGBAColor, Stroke
   from pyTooling.Cartesian2D.Groups  import Canvas2D, YAxisDirection

   outline = Stroke(1, RGBAColor(0, 0, 0))
   canvas =  Canvas2D(YAxisDirection.Down)
   box =     Rectangle(Point2D(0, 0), Point2D(40, 0), Point2D(40, 20), Point2D(0, 20), stroke=outline, parent=canvas)
   dot =     Circle(Point2D(40, 10), 3, stroke=outline, fill=Fill(RGBAColor(255, 255, 255)), parent=canvas)
   wire =    PolyLine((Point2D(40, 10), Point2D(60, 10), Point2D(60, 30)), stroke=outline, parent=canvas)

   box.Fill = Fill(RGBAColor.Parse("#ffffe0"))
   dot.BoundingBox                    # BoundingBox2D(37, 7, 43, 13)
   len(canvas.Children)               # 3
   wire.IsClosed                      # False

A drawable shape checks its ``parent`` first and registers in it when its geometry and styles are checked, so a failing
check leaves nothing in the group or canvas, and points given with ``copyPoints=False`` stay free. A drawable segment
is no edge of a shape: its ``parent`` is a group or canvas. So a path can't be built from drawable segments, a
:class:`~pyTooling.Cartesian2D.Shapes.Path` raises :exc:`TypeError` for one: build the path from geometric segments
and draw it as a :class:`~pyTooling.Cartesian2D.Drawing.Path`.


.. _STRUCT/Cartesian2D/Text:

Text
====

A :class:`~pyTooling.Cartesian2D.Drawing.Text` is an element of one or more lines at a
:attr:`~pyTooling.Cartesian2D.Drawing.Text.Position`, so it groups, moves and aligns like a shape. Newlines in its
:attr:`~pyTooling.Cartesian2D.Drawing.Text.Content` separate the lines, which
:attr:`~pyTooling.Cartesian2D.Drawing.Text.Lines` returns; a text without a newline has one line. The glyphs are drawn
with the text's fill, an outline around them with its stroke. The text owns its position point, like a circle owns its
center. Like every element, it takes a ``value`` and ``keyValuePairs``.

* :attr:`~pyTooling.Cartesian2D.Drawing.Text.Alignment` - a :class:`~pyTooling.Cartesian2D.Drawing.TextAlignment`:
  every line starts (``Left``, the default), is centered (``Center``) or ends (``Right``) at the position's
  x-coordinate.
* :attr:`~pyTooling.Cartesian2D.Drawing.Text.Anchor` - a :class:`~pyTooling.Cartesian2D.Drawing.VerticalAnchor`: the
  point of the text at the position's y-coordinate - the ``Top`` of the text, its ``Middle``, the ``Baseline`` of its
  first line (the default, as in SVG) or its ``Bottom``.
* :attr:`~pyTooling.Cartesian2D.Drawing.Text.LineHeight` - the distance of two baselines as a factor of the font size,
  ``1.2`` by default.

Top and bottom are those of the :ref:`canvas <STRUCT/Cartesian2D/Canvas2D>` holding the text: with the y-axis pointing
down, the top of a text has its smallest y-coordinate. Without a canvas, the y-axis points up.
:meth:`~pyTooling.Cartesian2D.Groups.Canvas2D.Mirror` therefore keeps a text where it is drawn. Mirroring a text with
``MirrorX`` or ``MirrorY`` moves its position only: the glyphs aren't mirrored, and its alignment and anchor stay.

.. code-block:: Python

   from pyTooling.Cartesian2D         import Point2D
   from pyTooling.Cartesian2D.Drawing import Font, Text, TextAlignment, VerticalAnchor
   from pyTooling.Cartesian2D.Groups  import Canvas2D, YAxisDirection

   canvas = Canvas2D(YAxisDirection.Down)
   label =  Text(
       Point2D(20, 10), "clock\nreset",
       font=Font("monospace", 10),
       alignment=TextAlignment.Center,
       anchor=VerticalAnchor.Top,
       parent=canvas
   )

   label.Lines                        # ('clock', 'reset')
   label.BoundingBox                  # BoundingBox2D(5.0, 10, 35.0, 32.0)

.. attention::

   The :attr:`~pyTooling.Cartesian2D.Drawing.Text.BoundingBox` of a text is an **estimate**: the longest line times the
   font's :attr:`~pyTooling.Cartesian2D.Drawing.Font.CharacterWidth` (``0.6`` of the size by default, the advance width
   of common monospace fonts) is its width; a line is one font size high, ``0.8`` of it above the baseline, and each
   further line adds the line height. A renderer measuring the glyphs gets other values, for a proportional font
   especially.


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


.. _STRUCT/Cartesian3D/BoundingBox3D:

BoundingBox3D
=============

A :class:`~pyTooling.Cartesian3D.BoundingBox3D` is the smallest **axis-aligned cuboid** enclosing something: the
read-only properties :attr:`~pyTooling.Cartesian3D.BoundingBox3D.MinX` to
:attr:`~pyTooling.Cartesian3D.BoundingBox3D.MaxZ`, and from them :attr:`~pyTooling.Cartesian3D.BoundingBox3D.Width`,
:attr:`~pyTooling.Cartesian3D.BoundingBox3D.Height`, :attr:`~pyTooling.Cartesian3D.BoundingBox3D.Depth` and
:attr:`~pyTooling.Cartesian3D.BoundingBox3D.Center`. Its constructor takes the smallest coordinates first, then the
largest: ``BoundingBox3D(minX, minY, minZ, maxX, maxY, maxZ)``.

It unites, overlaps, contains points, shifts by an :class:`~pyTooling.Cartesian3D.Offset3D`, compares and copies as
its 2D counterpart does. :meth:`~pyTooling.Cartesian3D.BoundingBox3D.HasOverlap` compares the inner volumes, so boxes
touching at a face, an edge or a corner don't overlap. There is no conversion to a volume yet.

.. code-block:: Python

   from pyTooling.Cartesian3D import Point3D, LineSegment3D

   line = LineSegment3D(Point3D(4, 1, -2), Point3D(-1, 3, 5))

   line.BoundingBox                      # BoundingBox3D(-1, 1, -2, 4, 3, 5)
   Point3D(0, 2, 0) in line.BoundingBox  # True

.. seealso::

   :ref:`STRUCT/Cartesian2D/BoundingBox2D`
      |rarr| Its counterpart, the 2-dimensional bounding box.


.. _STRUCT/Cartesian3D/Plane3D:

Plane3D
=======

A :class:`~pyTooling.Cartesian3D.Plane3D` is a plane, infinite in all directions within it. It is the abstract
base-class of the planes an element can be mirrored at, each named after the coordinate plane it is parallel to:

* :class:`~pyTooling.Cartesian3D.YZPlane3D` - the plane ``x = c``, all its points have the same
  :attr:`~pyTooling.Cartesian3D.YZPlane3D.X`;
* :class:`~pyTooling.Cartesian3D.XZPlane3D` - the plane ``y = c``, with :attr:`~pyTooling.Cartesian3D.XZPlane3D.Y`;
* :class:`~pyTooling.Cartesian3D.XYPlane3D` - the plane ``z = c``, with :attr:`~pyTooling.Cartesian3D.XYPlane3D.Z`.

Like the 2D line, a plane is a value in absolute coordinates: :meth:`~pyTooling.Cartesian3D.Element3D.MirrorAt` mirrors
an element of any group at it, and ``FromElement`` creates the plane through a face or the center of an element's
absolute bounding box, named by an :class:`~pyTooling.Cartesian3D.Alignment3D` of the plane's axis.

.. code-block:: Python

   from pyTooling.Cartesian3D        import Point3D, Offset3D, Alignment3D, XYPlane3D, LineSegment3D
   from pyTooling.Cartesian3D.Groups import Group3D

   rod =   LineSegment3D(Point3D(0, 0, 0), Point3D(0, 0, 2))
   part =  Group3D(Offset3D(10, 0, 1), (rod, ))
   floor = XYPlane3D(0)

   str(floor)                         # 'z = 0'
   rod.MirrorAt(floor)                # rod.End is (0, 0, -4), relative to part
   rod.End.Absolute                   # (10, 0, -3)

   XYPlane3D.FromElement(rod, Alignment3D.MinZ)   # XYPlane3D(-3)

.. seealso::

   :ref:`STRUCT/Cartesian2D/Line2D`
      |rarr| Its counterpart, the line parallel to a coordinate axis.


.. _STRUCT/Cartesian3D/Ray3D:

Ray3D
=====

A :class:`~pyTooling.Cartesian3D.Ray3D` is the 3D counterpart of a :ref:`Ray2D <STRUCT/Cartesian2D/Ray2D>`: a
half-line from a start point (:attr:`~pyTooling.Cartesian3D.Ray3D.Start`) in a direction
(:attr:`~pyTooling.Cartesian3D.Ray3D.Direction`, an :class:`~pyTooling.Cartesian3D.Offset3D`), a value in absolute
coordinates. :meth:`~pyTooling.Cartesian3D.Ray3D.PointAt` returns the point at a distance from the start point. Two
rays are equal, if they start at the same point and their directions point the same way: all three components of the
cross product are zero and the dot product is positive.

.. code-block:: Python

   from pyTooling.Cartesian3D import Point3D, Offset3D, Ray3D

   ray = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))

   str(ray)                           # '(1, 2, 3) + t * (0, 3, 4), t >= 0'
   ray.PointAt(5)                     # (1.0, 5.0, 7.0)


.. _STRUCT/Cartesian3D/Segment3D:

Segment3D
=========

:class:`~pyTooling.Cartesian3D.Segment3D` is a :attr:`~pyTooling.Cartesian3D.Segment3D.Start` and an
:attr:`~pyTooling.Cartesian3D.Segment3D.End` point, copied on construction unless ``copyPoints=False``. Either way,
the segment owns its points; an assigned start or end point is referenced and owned too.
It is abstract: a straight segment is a :class:`~pyTooling.Cartesian3D.LineSegment3D`.

:attr:`~pyTooling.Cartesian3D.Segment3D.BoundingBox` encloses both points, and
:meth:`~pyTooling.Cartesian3D.Segment3D.Move` shifts both by an :class:`~pyTooling.Cartesian3D.Offset3D`, in place.

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


.. _STRUCT/Cartesian3D/Ownership:

Ownership and Frames
====================

Points belong to segments as in 2D: a segment owns its two points, a point owned by another segment raises
:exc:`~pyTooling.Cartesian2D.AlreadyOwnedError`, and the same point object given twice raises
:exc:`~pyTooling.Cartesian2D.DuplicatePointError`. ``Point3D(x, y, z, parent=segment)`` sets the owner without
registering the point.

Points, segments and groups derive from the abstract :class:`~pyTooling.Cartesian3D.Base3D`, which holds the parent
and returns the :attr:`~pyTooling.Cartesian3D.Base3D.Frame`; segments and groups also from
:class:`~pyTooling.Cartesian3D.Element3D`.
Subtracting points or measuring the angle between line segments of different frames raises
:exc:`~pyTooling.Cartesian2D.NotInSameFrameError`. The errors are the classes of :mod:`pyTooling.Cartesian2D`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Ownership`
      |rarr| Its counterpart, where ownership and frames are explained.


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


.. _STRUCT/Cartesian3D/Groups:

Groups
******

The groups live in :mod:`pyTooling.Cartesian3D.Groups` and work as in 2D: a group places segments and other groups at
an offset, and the coordinates of its children are relative to the group. There is no 3D canvas yet, so a group
without a parent is the root of a drawing, relative to the origin.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Groups`
      |rarr| Its counterpart, the 2D groups and the canvas.


.. _STRUCT/Cartesian3D/Element3D:

Element3D
=========

:class:`~pyTooling.Cartesian3D.Element3D` is the abstract base-class of everything a group can hold: segments and
groups. An element belongs to at most one group, its :attr:`~pyTooling.Cartesian3D.Element3D.Parent`, and offers:

* :attr:`~pyTooling.Cartesian3D.Element3D.BoundingBox` in its frame and
  :attr:`~pyTooling.Cartesian3D.Element3D.AbsoluteBoundingBox` relative to the origin;
* :meth:`~pyTooling.Cartesian3D.Element3D.Move`, shifting it in its frame;
* :meth:`~pyTooling.Cartesian3D.Element3D.MirrorX`, :meth:`~pyTooling.Cartesian3D.Element3D.MirrorY` and
  :meth:`~pyTooling.Cartesian3D.Element3D.MirrorZ`, mirroring it at a plane parallel to the yz-, xz- or xy-plane (the
  x-, y- or z-coordinates flip), through an edge or the center of its bounding box, named by an
  :class:`~pyTooling.Cartesian3D.Alignment3D` and optionally shifted by an offset;
* :meth:`~pyTooling.Cartesian3D.Element3D.MirrorAt`, mirroring it at an
  :ref:`plane <STRUCT/Cartesian3D/Plane3D>` in absolute coordinates, which several elements can share;
* :meth:`~pyTooling.Cartesian3D.Element3D.MoveTo`, moving it into another group - by default keeping its absolute
  position, so its local coordinates change;
* :meth:`~pyTooling.Cartesian3D.Element3D.AlignTo`, moving it so an edge or the center of its bounding box aligns
  with another element's - see :class:`~pyTooling.Cartesian3D.Alignment3D`. Both elements may be in different groups.

Assigning :attr:`~pyTooling.Cartesian3D.Element3D.Parent` moves an element into a group too, but keeps its local
coordinates. A group can't become its own descendant: that raises :exc:`~pyTooling.Cartesian2D.GroupCycleError`.
Every segment and group takes a keyword-only parameter ``parent``: a group given there registers the new element, as
:meth:`~pyTooling.Cartesian3D.Groups.Group3D.AddChild` does.

An element carries an optional :attr:`~pyTooling.Cartesian3D.Element3D.Value` and arbitrary key-value-pairs
(:class:`~pyTooling.DataModel.KeyValuePairsMixin`), given by the keyword-only parameters ``value`` and
``keyValuePairs``, as in 2D. ``Copy()`` and :func:`copy.copy` keep the value (the same object) and copy the
key-value-pairs shallowly; :func:`copy.deepcopy` copies both deeply. Points carry neither. A copy isn't in the group of
the original.

.. code-block:: Python

   from pyTooling.Cartesian3D import Point3D, LineSegment3D

   wire = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 0, 2), value="clock", keyValuePairs={"layer": 1})

   wire["shielded"] = True

   wire.Value                         # 'clock'
   len(wire)                          # 2
   wire.Copy()["layer"]               # 1

.. seealso::

   :ref:`STRUCT/Cartesian2D/Element2D`
      |rarr| Its counterpart, the 2-dimensional element.


.. _STRUCT/Cartesian3D/Group3D:

Group3D
=======

A :class:`~pyTooling.Cartesian3D.Groups.Group3D` has an :attr:`~pyTooling.Cartesian3D.Groups.Group3D.Offset` and
:attr:`~pyTooling.Cartesian3D.Groups.Group3D.Children`. Moving a group changes its offset only - the coordinates of its
children stay as they are.

.. code-block:: Python

   from pyTooling.Cartesian3D        import Point3D, Offset3D, LineSegment3D
   from pyTooling.Cartesian3D.Groups import Group3D

   rod =      LineSegment3D(Point3D(0, 0, 0), Point3D(0, 0, 2))
   part =     Group3D(Offset3D(10, 0, 0), (rod, ))
   assembly = Group3D(Offset3D(0, 5, 1), (part, ))

   rod.End                            # (0, 0, 2), relative to part
   rod.End.Absolute                   # (10, 5, 3)
   assembly.BoundingBox               # BoundingBox3D(10, 5, 1, 10, 5, 3)
   assembly.Move(Offset3D(100, 0, 0)) # rod.End is still (0, 0, 2)

Children are given to the constructor or added by :meth:`~pyTooling.Cartesian3D.Groups.Group3D.AddChild`, and removed
by :meth:`~pyTooling.Cartesian3D.Groups.Group3D.RemoveChild`; a child of another group raises
:exc:`~pyTooling.Cartesian2D.AlreadyOwnedError` - use :meth:`~pyTooling.Cartesian3D.Element3D.MoveTo` to move it -,
removing an element of another group :exc:`~pyTooling.Cartesian2D.NotOwnedError`. A group without children has no
bounding box and raises :exc:`~pyTooling.Cartesian2D.Groups.EmptyGroupError`.
:meth:`~pyTooling.Cartesian3D.Groups.Group3D.DistributeX`, :meth:`~pyTooling.Cartesian3D.Groups.Group3D.DistributeY`
and :meth:`~pyTooling.Cartesian3D.Groups.Group3D.DistributeZ` move the children along that axis, so the gaps between
them are equal. Subtracting points of different groups raises
:exc:`~pyTooling.Cartesian2D.NotInSameFrameError`; subtract their absolute positions instead. ``Copy()`` and
:func:`copy.copy` copy a group with a copy of each child, :func:`copy.deepcopy` with deep copies of its children; the
copy has no parent.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Group2D`
      |rarr| Its counterpart, the 2-dimensional group.
