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

    def add_tile(self, tile: Tile) -> bool:
        """Add a tile to the database.

        :param tile:
        :raise Exception: tile already created.
        """
        for db_tile in self._tiles:
            if tile.x == db_tile.x and tile.y == db_tile.y:
                # raise Exception(f"Cannot add tile {tile.x, tile.y}: slot already created.")
                return False

        # For each neighbour of the tile
        for i in range(6):
            neighbor = self.get_tile(tile.x + NEIGHBORS_COORD[i]["x"], tile.y + NEIGHBORS_COORD[i]["y"])
            if neighbor:
                # Set the link between neighbor and tile
                setattr(neighbor, "n" + str((i + 3) % 6), tile)
                setattr(tile, "n" + str(i), neighbor)
            del neighbor

        self._tiles += [tile]
        return True

    def remove_tile(self, x: int, y: int) -> bool:
        """Remove a tile from database, if present.

        :param x: x coordinate.
        :param y: y coordinate
        :return: True if deleted, False otherwise.
        """
        for db_tile in self._tiles:
            if x == db_tile.x and y == db_tile.y:
                self._tiles.remove(db_tile)
                return True
        return False

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
