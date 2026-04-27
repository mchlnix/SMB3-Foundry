"""World-map wrappers for SMB3 airship travel path points.

This module adapts the ROM-backed records that define airship travel paths into
selectable editor objects. The workflow is travel-set record -> ``MapObject``
wrapper -> shared world-map selection, drag, and redraw state, so path points
reuse the same editor tools as other overworld entities.

See Also
--------
foundry.game.gfx.objects.world_map.map_object
    Defines the shared position and drawing contract for world-map objects.
foundry.game.level.WorldMap
    Owns the overworld data that supplies these travel-point records.
"""

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPainter

from foundry.game.gfx.drawable import load_from_object_sprite_sheet
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.levels import WORLD_MAP_SCREEN_WIDTH

AIRSHIP_TRAVEL_POINT_1 = load_from_object_sprite_sheet(59, 2)
AIRSHIP_TRAVEL_POINT_2 = load_from_object_sprite_sheet(60, 2)
AIRSHIP_TRAVEL_POINT_3 = load_from_object_sprite_sheet(61, 2)
AIRSHIP_TRAVEL_POINT_4 = load_from_object_sprite_sheet(62, 2)
AIRSHIP_TRAVEL_POINT_5 = load_from_object_sprite_sheet(59, 3)
AIRSHIP_TRAVEL_POINT_6 = load_from_object_sprite_sheet(60, 3)

AIRSHIP_TRAVEL_POINTS = [
    AIRSHIP_TRAVEL_POINT_1,
    AIRSHIP_TRAVEL_POINT_2,
    AIRSHIP_TRAVEL_POINT_3,
    AIRSHIP_TRAVEL_POINT_4,
    AIRSHIP_TRAVEL_POINT_5,
    AIRSHIP_TRAVEL_POINT_6,
]


class AirshipTravelPoint(MapObject):
    """Model one waypoint in an overworld airship travel path.

    SMB3 groups these points into travel sets that define where an airship can
    move between encounters. The editor wraps each point as a selectable map
    object so path editing can use the same movement and drawing tools as other
    overworld objects.

    The data flow is airship-travel-set entry -> map object wrapper -> editor
    movement and rendering, with writes flowing back into the shared position
    record stored by the travel set.

    Parameters
    ----------
    pos : object
        Position record from the airship travel set.
    set_no : int
        Zero-based airship travel-set index.
    index : int
        Zero-based point index inside the travel set.

    Attributes
    ----------
    index : int
        Zero-based point index inside the travel set.
    name : str
        Editor-facing label derived from set and point number.
    pos : object
        Mutable position record stored in the ROM-backed travel set.
    set_no : int
        Zero-based airship travel-set index.

    Examples
    --------
    The world-map editor wraps one mutable travel-set position record and then
    updates that same record when a drag changes the waypoint::

        class DemoPos:
            def __init__(self, screen, x, y):
                self.screen = screen
                self.x = x
                self.y = y

            @property
            def xy(self):
                return (
                    self.screen * WORLD_MAP_SCREEN_WIDTH + self.x,
                    self.y,
                )

        pos = DemoPos(screen=1, x=3, y=5)
        point = AirshipTravelPoint(pos, set_no=0, index=2)
        point.set_position(20, 6)

        assert point.get_position() == (20, 6)
        assert (pos.screen, pos.x, pos.y) == (1, 4, 6)
    """

    def __init__(self, pos, set_no, index):
        """Wrap one ROM-backed airship travel position for editing.

        Construction preserves the mutable travel-set record so later drag
        operations can feed coordinates straight back into the same overworld
        path entry rather than copying that state into a second editor-only
        structure.

        Parameters
        ----------
        pos : object
            Mutable position record stored by the airship travel set.
        set_no : int
            Zero-based airship travel-set index.
        index : int
            Zero-based point index inside the travel set.
        """
        super(AirshipTravelPoint, self).__init__()

        self.pos = pos
        self.set_no = set_no
        self.index = index

        self.name = f"Airship Set #{set_no + 1} Point {index + 1}"

    def draw(self, painter: QPainter, block_length, transparent):
        """Draw the waypoint sprite at its world-map position.

        Rendering resolves the point index into the matching sprite-sheet image
        so path previews stay aligned with the same travel-set ordering used by
        the ROM-backed path record and the redraw workflow reads the same point
        state later used by selection and movement tools.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        block_length : int
            Rendered block size in pixels.
        transparent : bool
            Ignored transparency flag from the shared map-object API.
        """
        x, y = self.get_position()

        painter.drawImage(
            QPoint(x, y) * block_length,
            AIRSHIP_TRAVEL_POINTS[self.index].scaled(block_length, block_length),
        )

    def set_position(self, x, y):
        """Update the waypoint position in world-map coordinates.

        The method translates editor coordinates back into the split SMB3
        storage format of screen, column, and row so dragging a point updates
        the same record later serialized by the overworld model.

        Parameters
        ----------
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.

        Examples
        --------
        Dragging a waypoint updates the shared ROM-backed travel record in the
        split screen/column format used by the overworld data::

            class DemoPos:
                def __init__(self):
                    self.screen = 0
                    self.x = 0
                    self.y = 0

                @property
                def xy(self):
                    return (
                        self.screen * WORLD_MAP_SCREEN_WIDTH + self.x,
                        self.y,
                    )

            pos = DemoPos()
            point = AirshipTravelPoint(pos, set_no=0, index=0)
            point.set_position(WORLD_MAP_SCREEN_WIDTH + 2, 7)

            assert (pos.screen, pos.x, pos.y) == (1, 2, 7)
        """
        self.pos.x = x % WORLD_MAP_SCREEN_WIDTH
        self.pos.y = y
        self.pos.screen = x // WORLD_MAP_SCREEN_WIDTH

    def get_position(self) -> tuple[int, int]:
        """Normalized waypoint coordinates for shared map-object tools.

        The editor reads this normalized coordinate pair instead of the
        underlying screen-plus-column storage so selection and drag code can
        treat travel points like other world-map objects and keep coordinate
        state flowing through one shared API.

        Returns
        -------
        tuple[int, int]
            X and Y coordinates of the waypoint.
        """
        return self.pos.xy

    def change_type(self, new_type):
        """Ignore type changes for airship travel points.

        Parameters
        ----------
        new_type : int
            Ignored replacement type identifier.
        """
        pass
