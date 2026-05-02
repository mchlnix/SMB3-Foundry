"""Represent small geometry primitives shared by parser-facing helpers.

This module keeps rectangle and point math out of heavier SMB3 parsing and UI
objects. The helpers normalize dimensions, answer containment questions, and
provide lightweight value objects that can move through parser, model, and
rendering code without taking a dependency on Qt geometry types.

See Also
--------
smb3parse.levels.world_map
    World-map model code that consumes coordinate-like values when reasoning
    about tile and pointer placement.
smb3parse.util.parser.object
    Parser-side object wrappers that need geometry-friendly values without GUI
    framework coupling.
"""


class Rect:
    """Store an axis-aligned rectangle using parser-friendly scalar values.

    The rectangle keeps origin and size values in plain Python numbers so
    parser utilities, data-point helpers, and editor-adjacent code can reason
    about overlap and containment without importing GUI geometry classes.

    Parameters
    ----------
    x : int | float, optional
        Left edge of the rectangle.
    y : int | float, optional
        Top edge of the rectangle.
    width : int | float, optional
        Rectangle width. Negative values are normalized into a positive width
        and a shifted ``x`` origin.
    height : int | float, optional
        Rectangle height. Negative values are normalized into a positive height
        and a shifted ``y`` origin.

    Attributes
    ----------
    x : int | float
        Left edge after width normalization.
    y : int | float
        Top edge after height normalization.
    width : int | float
        Non-negative horizontal extent.
    height : int | float
        Non-negative vertical extent.

    Notes
    -----
    ``Rect`` is intentionally tiny, but it still anchors a boundary in the
    codebase: parser and model helpers can exchange spatial values without
    pulling GUI geometry classes into low-level modules.
    """

    def __init__(self, x=0, y=0, width=0, height=0):
        """Normalize rectangle bounds into a left/top origin plus size.

        Downstream overlap, containment, and corner helpers all assume the
        stored extent moves forward from ``x`` and ``y``. This constructor
        enforces that normalization once so call sites do not need to repeat
        sign handling, and every later read helper depends on that normalized
        state rather than recalculating bounds from mixed-sign input.

        Parameters
        ----------
        x : int | float, optional
            Left edge of the rectangle before normalization.
        y : int | float, optional
            Top edge of the rectangle before normalization.
        width : int | float, optional
            Horizontal extent. Negative widths are flipped so downstream
            containment and overlap checks can assume a forward extent.
        height : int | float, optional
            Vertical extent. Negative heights are flipped for the same reason
            as ``width``.
        """
        self.x = x
        self.y = y

        self.width = width
        self.height = height

        if self.width < 0:
            self.width *= -1
            self.x -= self.width

        if self.height < 0:
            self.height *= -1
            self.y -= self.height

    def point_in(self, x: int, y: int, include_borders=True) -> bool:
        """Report whether a coordinate falls inside the rectangle.

        Parser and editor code use this helper when deciding whether a tile,
        object, or pointer-derived coordinate belongs to a rectangular region.
        The border toggle lets adjacent regions choose inclusive or half-open
        behavior without rewriting the bound checks.

        Parameters
        ----------
        x : int
            Horizontal coordinate to test.
        y : int
            Vertical coordinate to test.
        include_borders : bool, optional
            When ``True``, points on the right or bottom edge count as inside.
            When ``False``, the check uses half-open bounds so callers can
            avoid double-counting adjacent rectangles.

        Returns
        -------
        bool
            ``True`` when the coordinate lies inside the rectangle according to
            the selected border policy.
        """
        if not include_borders:
            return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height
        else:
            return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def intersects(self, other: "Rect"):
        """Report whether two rectangles overlap by area.

        This keeps overlap policy in one place for geometry consumers that only
        need a yes-or-no answer before continuing placement or collision-style
        logic. The method is read-only: it interprets two normalized rectangle
        states and returns one overlap decision for higher-level workflow code.

        Parameters
        ----------
        other : Rect
            Rectangle to compare against this one.

        Returns
        -------
        bool
            ``True`` when the rectangles overlap. Touching edges alone do not
            count as an intersection because the comparison uses strict
            separation checks.
        """
        if other.x + other.width <= self.x:
            return False

        if other.y + other.height <= self.y:
            return False

        if other.x >= self.x + self.width:
            return False

        if other.y >= self.y + self.height:
            return False

        return True

    def contains(self, other: "Rect"):
        """Report whether this rectangle fully encloses another rectangle.

        The method reduces containment to the corner policy already defined by
        :meth:`point_in`, so higher-level code gets one consistent notion of
        whether a region sits entirely inside another. It does not mutate
        either rectangle; it turns stored bounds into a single containment
        verdict that callers can reuse in placement and selection flows after
        both rectangles have already been normalized into comparable bounds.

        Parameters
        ----------
        other : Rect
            Rectangle whose corners are tested against this rectangle.

        Returns
        -------
        bool
            ``True`` when both corners of ``other`` lie inside this rectangle
            under the inclusive border policy used by :meth:`point_in`.

        Notes
        -----
        Callers typically arrive here after both rectangles have already been
        normalized and after a broader workflow has decided containment, not
        mere overlap, is the next question to answer. The method then delegates
        both corner tests through :meth:`point_in` so region-selection and
        placement code reuse the same border policy that governs single-point
        membership checks elsewhere in the module.
        """
        return self.point_in(*other.top_left()) and self.point_in(*other.bottom_right())

    def size(self):
        """Expose the normalized width and height as one value object.

        Callers that only need extent, not position, can use this tuple form
        instead of unpacking the rectangle manually. That keeps size-only
        consumers decoupled from the rectangle's positional fields while still
        reading extent from the constructor-normalized rectangle state.

        Returns
        -------
        tuple[int | float, int | float]
            Width and height in that order.
        """
        return self.width, self.height

    def top(self):
        """Expose the normalized top edge for coordinate comparisons.

        This accessor keeps edge reads explicit in code that compares vertical
        bounds without unpacking the whole rectangle.

        Returns
        -------
        int | float
            Stored ``y`` origin.
        """
        return self.y

    def bottom(self):
        """Expose the normalized lower edge for vertical bound checks.

        Callers use the derived edge instead of recomputing ``y + height`` in
        every containment or placement path, so read-only geometry code can
        depend on one canonical lower-bound calculation sourced from the
        rectangle's normalized vertical state.

        Returns
        -------
        int | float
            ``y`` plus ``height`` after normalization.
        """
        return self.y + self.height

    def left(self):
        """Expose the normalized left edge for coordinate comparisons.

        This mirrors :meth:`top` so parser and model code can read bounds by
        intent instead of by raw field access alone.

        Returns
        -------
        int | float
            Stored ``x`` origin.
        """
        return self.x

    def right(self):
        """Expose the normalized right edge for horizontal bound checks.

        Using one accessor keeps the derived horizontal boundary consistent
        everywhere the rectangle participates in placement logic.

        Returns
        -------
        int | float
            ``x`` plus ``width`` after normalization.
        """
        return self.x + self.width

    def top_left(self):
        """Build the top-left corner as a reusable point value.

        Returning a :class:`Point` keeps corner-based code aligned with the
        same lightweight coordinate type used elsewhere in parser helpers.

        Returns
        -------
        Point
            Corner value that can be reused by containment and placement code.
        """
        return Point(self.x, self.y)

    def top_right(self):
        """Build the top-right corner as a reusable point value.

        Corner helpers let containment and placement code talk in coordinates
        without duplicating edge arithmetic.

        Returns
        -------
        Point
            Point positioned at the right edge and top edge of the rectangle.
        """
        return Point(self.x + self.width, self.y)

    def bottom_left(self):
        """Build the bottom-left corner as a reusable point value.

        The corner stays coupled to the rectangle's normalized bounds, which
        keeps downstream coordinate logic free of repeated offset math.

        Returns
        -------
        Point
            Point positioned at the left edge and bottom edge of the
            rectangle.
        """
        return Point(self.x, self.y + self.height)

    def bottom_right(self):
        """Build the bottom-right corner as a reusable point value.

        The method gives containment checks and external geometry code a single
        lower-right representation derived from normalized bounds, which keeps
        downstream coordinate flow anchored to the same edge calculation.

        Returns
        -------
        Point
            Point positioned at the lower-right corner of the rectangle.
        """
        return Point(self.x + self.width, self.y + self.height)

    def __iter__(self):
        """Yield rectangle fields in constructor order.

        Iteration keeps the rectangle easy to unpack when parser-side helpers
        need a lightweight serialized view without adding a custom export
        method.

        Returns
        -------
        iterator of int | float
            Iterator over ``(x, y, width, height)`` for tuple unpacking and
            light serialization.
        """
        return iter((self.x, self.y, self.width, self.height))

    def __mul__(self, other):
        """Scale a rectangle by a numeric factor.

        Scaling preserves the rectangle abstraction while letting callers move
        between coarse map coordinates and zoomed or expanded coordinate spaces
        with one operation.

        Parameters
        ----------
        other : int | float
            Scale factor applied to origin and size values.

        Returns
        -------
        Rect
            New scaled rectangle value.

        Raises
        ------
        TypeError
            If ``other`` is not numeric.
        """
        if not isinstance(other, (int, float)):
            raise TypeError("Rect can only be multiplied by an integer or float")

        return Rect(self.x * other, self.y * other, self.width * other, self.height * other)


class Point:
    """Store a lightweight coordinate pair for parser and editor helpers.

    The type gives low-level geometry code a named coordinate container that
    can move between rectangle helpers, parser data structures, and editor
    plumbing without collapsing immediately into anonymous tuples.

    Parameters
    ----------
    x : int | float
        Horizontal coordinate.
    y : int | float
        Vertical coordinate.

    Attributes
    ----------
    x : int | float
        Horizontal coordinate.
    y : int | float
        Vertical coordinate.

    Notes
    -----
    ``Point`` exists beside :class:`Rect` so geometry-aware helpers can return
    typed coordinate pairs instead of raw tuples while still staying detached
    from GUI geometry classes. That keeps parser and editor-adjacent code on a
    shared coordinate type even when no rectangle is involved.

    See Also
    --------
    Rect
        Rectangle helper that produces and consumes ``Point`` instances for
        corner and containment checks.
    """

    def __init__(self, x, y):
        """Store a coordinate pair without any framework dependency.

        The constructor intentionally does no coercion so parser and editor
        helpers can preserve whichever numeric coordinate type they already use.

        Parameters
        ----------
        x : int | float
            Horizontal coordinate.
        y : int | float
            Vertical coordinate.
        """
        self.x = x
        self.y = y

    def copy(self):
        """Duplicate the point for code that needs an independent value copy.

        The method avoids exposing mutability assumptions at call sites that
        want to branch from an existing coordinate.

        Returns
        -------
        Point
            New point with the same coordinates.
        """
        return Point(self.x, self.y)

    def __add__(self, other):
        """Add two points component-wise.

        This keeps coordinate composition inside the point abstraction so
        offsetting code stays readable and type-checked at the boundary.

        Parameters
        ----------
        other : Point
            Point whose coordinates are added to this point.

        Returns
        -------
        Point
            New point with summed coordinates.

        Raises
        ------
        TypeError
            If ``other`` is not a :class:`Point`.
        """
        if not isinstance(other, Point):
            raise TypeError("Point can only be added to another Point")

        return Point(self.x + other.x, self.y + other.y)

    def __iter__(self):
        """Yield the point coordinates in ``x, y`` order.

        Tuple-style iteration lets helpers pass points into unpacking-based
        APIs while keeping a named geometry type in the rest of the workflow.

        Returns
        -------
        iterator of int | float
            Iterator over ``(x, y)`` for tuple unpacking and helper calls.
        """
        return iter((self.x, self.y))
