"""Database."""
from typing import List, Optional, Dict

from tile import Tile

NEIGHBORS_COORD: Dict[int, Dict[str, int]] = {
    0: {"x": +1, "y": +0},
    1: {"x": +0, "y": +1},
    2: {"x": -1, "y": +1},
    3: {"x": -1, "y": +0},
    4: {"x": +0, "y": -1},
    5: {"x": +1, "y": -1},
}


class Database:
    """Contains all the tiles."""

    def __init__(self):
        self._tiles: List[Tile] = [Tile(0, 0)]

    def add_tile(self, tile: Tile) -> None:
        """Add a tile to the database.

        :param tile: tile to add.
        :raise Exception: tile already created.
        """
        for db_tile in self._tiles:
            if tile.get_pos() == db_tile.get_pos():
                raise Exception(f"Cannot add tile {tile.get_pos()}: slot already created.")

        # Update neighbors
        for i in range(6):
            neighbor = self.get_tile(tile.x + NEIGHBORS_COORD[i]["x"], tile.y + NEIGHBORS_COORD[i]["y"])
            if neighbor:
                setattr(neighbor, "n" + str((i + 3) % 6), tile)
                setattr(tile, "n" + str(i), neighbor)
            del neighbor

        self._tiles += [tile]

    def remove_tile(self, x: int, y: int) -> None:
        """Remove a tile from database, if present.

        :param x: x coordinate.
        :param y: y coordinate
        :raise Exception: tile not found.
        """
        for db_tile in self._tiles:
            if db_tile.get_pos() == (x, y):
                self._tiles.remove(db_tile)
                return
        raise Exception(f"Tile {x, y} not found")

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Retrieve a tile by its coordinates.

        :param x: x coordinate.
        :param y: y coordinate.
        :return: tile if found, None otherwise.
        """
        for db_tile in self._tiles:
            if x == db_tile.x and y == db_tile.y:
                return db_tile
        return None

    def get_tiles(self) -> List[Tile]:
        """Return all the tiles of the database.

        :return: all the tiles.
        """
        return self._tiles
