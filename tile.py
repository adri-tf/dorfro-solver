"""Tile object"""
from enum import IntEnum
from typing import List, Optional


class Tile:
    """Tile object."""

    class Edge(IntEnum):
        """Edges of the tile."""
        EMPTY = 0
        PLAIN = 1
        TREE = 2
        WEED = 3
        HOUSE = 4
        RIVER = 5
        RAIL = 6
        POND = 7
        DOME = 8

    class State(IntEnum):
        """State of the tile."""
        EMPTY = 0
        FULL = 1

    def __init__(self, x: int, y: int, edges: List['Tile.Edge'] = None):
        self.x = int(x)
        self.y = int(y)

        self.state: Tile.State = Tile.State.EMPTY

        self.n0: Optional['Tile'] = None
        self.n1: Optional['Tile'] = None
        self.n2: Optional['Tile'] = None
        self.n3: Optional['Tile'] = None
        self.n4: Optional['Tile'] = None
        self.n5: Optional['Tile'] = None

        if edges:
            if len(edges) != 6:
                raise Exception("Cannot initialize Tile: assign all 6 edges or none")
            else:
                self.e0: 'Tile.Edge' = edges[0]
                self.e1: 'Tile.Edge' = edges[1]
                self.e2: 'Tile.Edge' = edges[2]
                self.e3: 'Tile.Edge' = edges[3]
                self.e4: 'Tile.Edge' = edges[4]
                self.e5: 'Tile.Edge' = edges[5]
                self.state = Tile.State.FULL
        else:
            self.e0 = Tile.Edge.EMPTY
            self.e1 = Tile.Edge.EMPTY
            self.e2 = Tile.Edge.EMPTY
            self.e3 = Tile.Edge.EMPTY
            self.e4 = Tile.Edge.EMPTY
            self.e5 = Tile.Edge.EMPTY

    def get_pos(self) -> (int, int):
        """Retrieve the coordinates of the tile."""
        return self.x, self.y

    def get_edges(self) -> List['Tile.Edge']:
        """Retrieve the edges of the tile."""
        return [self.e0, self.e1, self.e2, self.e3, self.e4, self.e5]

    def get_neighbors(self) -> List[Optional['Tile']]:
        """Retrieve the neighbors of the tile."""
        return [self.n0, self.n1, self.n2, self.n3, self.n4, self.n5]
