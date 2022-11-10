"""Board class."""
import logging
import math as m
import os
import sys
import time
from typing import List, Optional, NamedTuple, Dict

import matplotlib.pyplot as plt
from mpl_toolkits.axisartist import Axes
from mpl_toolkits.axisartist.grid_finder import MaxNLocator
from mpl_toolkits.axisartist.grid_helper_curvelinear import GridHelperCurveLinear

from database import Database, Tile, NEIGHBORS_COORD

logger = logging.getLogger("root")

DATA_FILE_NAME = 'DATA.csv'

COLOR_MAPPING: Dict[Tile.Edge, str] = {
    Tile.Edge.EMPTY: 'white',
    Tile.Edge.PLAIN: 'lightgreen',
    Tile.Edge.TREE: 'forestgreen',
    Tile.Edge.WEED: 'yellow',
    Tile.Edge.HOUSE: 'brown',
    Tile.Edge.RIVER: 'navy',
    Tile.Edge.RAIL: 'slategray',
    Tile.Edge.POND: 'deepskyblue',
    Tile.Edge.DOME: 'lightcoral',
}

EDGE_VALUE: Dict[Tile.Edge, int] = {
    Tile.Edge.DOME: 0,
    Tile.Edge.POND: 1,
    Tile.Edge.PLAIN: 2,
    Tile.Edge.TREE: 4,
    Tile.Edge.WEED: 4,
    Tile.Edge.HOUSE: 4,
    Tile.Edge.RIVER: 6,
    Tile.Edge.RAIL: 8,
}


class Board:
    """Factory ensuring the database coherence given the Dorfromantik rules."""

    def __init__(self):
        self._database: Database = Database()
        nb_tiles, avg_x, avg_y = 0, 0, 0
        logger.info("Loading Database...")
        with open(os.path.join(os.path.dirname(sys.argv[0]), DATA_FILE_NAME)) as file:
            for line in file:
                x, y, e0, e1, e2, e3, e4, e5 = [int(n) for n in line.split(';')]
                tile = self.place_tile(Tile(x, y, edges=[e0, e1, e2, e3, e4, e5]), show=False)
                if tile.state == tile.State.FULL:
                    avg_x += x
                    avg_y += y
                    nb_tiles += 1
        logger.info(f"Database loaded: {nb_tiles} tiles found.")
        self.m_x, self.m_y = avg_x / nb_tiles, avg_y / nb_tiles
        self.last_placement: Optional[Tile] = None

    @staticmethod
    def _tr(x, y):
        return x * 0.866, y + x * 0.5  # cos(pi/6) ~= 0.866025...

    @staticmethod
    def _inv_tr(x, y):
        return x / 0.866, y - x * 0.5  # cos(pi/6) ~= 0.866025...

    def render(self, fast_mode: bool = False):
        """Draw the board."""

        def _get_midpoint(t_x, t_y):
            return [(t_x[0] + t_y[0]) / 2, (t_x[1] + t_y[1]) / 2]

        t0 = time.time()
        # Determine aspect ratio
        x_min, x_max, y_min, y_max = 0, 0, 0, 0
        for tile in self._database.get_tiles():
            x, y = self._tr(*tile.get_pos())
            x_min, x_max, y_min, y_max = min(x, x_min), max(x, x_max), min(y, y_min), max(y, y_max)
        x_range, y_range = (x_max - x_min + 1) ** 2 / (y_max - y_min + 1), (x_max - x_min + 1)

        # Create canvas image
        grid_helper = GridHelperCurveLinear(
            (self._tr, self._inv_tr), grid_locator1=MaxNLocator(integer=True), grid_locator2=MaxNLocator(integer=True)
        )
        plt.figure(figsize=[x_range, y_range]).add_subplot(1, 1, 1, axes_class=Axes, grid_helper=grid_helper).grid()

        logger.info("Rendering board...")
        s = 0.5 / m.cos(m.pi / 6) - 2 * 0.01  # 0.01 is the width of the triangles' lines (probably)
        for tile in self._database.get_tiles():
            x, y = self._tr(*tile.get_pos())
            hexagon_coord = [[x + s, y], [x + s * m.cos(m.pi / 3), y + s * m.sin(m.pi / 3)],
                             [x + s * m.cos(m.pi * 2 / 3), y + s * m.sin(m.pi * 2 / 3)], [x - s, y],
                             [x + s * m.cos(-m.pi * 2 / 3), y + s * m.sin(-m.pi * 2 / 3)],
                             [x + s * m.cos(-m.pi / 3), y + s * m.sin(-m.pi / 3)], [x + s, y]]

            if fast_mode and len([t for t in tile.get_neighbors() if t and t.state == Tile.State.FULL]) == 6:
                if tile.state != Tile.State.EMPTY:
                    xs, ys = zip(*hexagon_coord)
                    plt.fill(xs, ys, color='gray')
                    continue

            # For each side of the hexagon
            for i in range(6):
                m1 = _get_midpoint(hexagon_coord[0 + i], [x, y])
                m2 = _get_midpoint(hexagon_coord[1 + i], [x, y])
                t_coord = [m1] + hexagon_coord[0 + i:2 + i] + [m2] + [m1]
                xs, ys = zip(*t_coord)
                if tile.state == Tile.State.EMPTY:
                    plt.plot(xs, ys, color='gray')
                elif tile.state == Tile.State.FULL:
                    getattr(tile, 'e' + str(i))
                    plt.fill(xs, ys, color=COLOR_MAPPING[getattr(tile, 'e' + str(i))])
            plt.text(x, y, f"{tile.get_pos()}", ha='center', va='center')

        plt.savefig(os.path.join(os.path.dirname(sys.argv[0]), 'board.png'))
        plt.close()
        t1 = time.time()
        logger.info(f"Board rendered | Time: {(t1 - t0):.2f}s.")

    def place_tile(self, new_tile: Tile, show: bool = True) -> Tile:
        """Add a tile to the board if allowed.

        :param new_tile: tile to place.
        :param show: logs boolean.
        :raise Exception: cannot add tile.
        """
        if new_tile.state == Tile.State.EMPTY:
            raise Exception(f"Cannot add tile {new_tile.get_pos()}: tile is empty")
        if not self._database.get_tile(*new_tile.get_pos()):
            raise Exception(f"Cannot add tile {new_tile.get_pos()}: not a valid slot")
        if self._database.get_tile(*new_tile.get_pos()).state != Tile.State.EMPTY:
            raise Exception(f"Cannot add tile {new_tile.get_pos()}: slot given not empty")
        if new_tile.Edge.EMPTY in new_tile.get_edges():
            raise Exception(f"Cannot add tile {new_tile.get_pos()}: edge given is empty")

        # Add eventual new slots and verify if edge matches
        for i in range(6):
            n_coord = new_tile.x + NEIGHBORS_COORD[i]["x"], new_tile.y + NEIGHBORS_COORD[i]["y"]
            n_tile = self._database.get_tile(*n_coord)
            if not n_tile:
                self._database.add_tile(Tile(*n_coord))
            elif show and n_tile.state == Tile.State.FULL and not self._edge_match(
                    getattr(new_tile, 'e' + str(i)), getattr(n_tile, 'e' + str((i + 3) % 6))
            ):
                logger.warning(f"Edge {i + 1} with {n_coord} does not match")
        db_tile = self._database.get_tile(*new_tile.get_pos())
        db_tile.e0, db_tile.e1, db_tile.e2, db_tile.e3, db_tile.e4, db_tile.e5 = new_tile.get_edges()
        db_tile.state = Tile.State.FULL
        self.last_placement = new_tile
        if show:
            logger.info(f"Tile {new_tile.get_pos()} placed")
            # Verify if neighbors are closed slots with no candidates seen before
            for n in [tile for tile in db_tile.get_neighbors() if tile.state == Tile.State.EMPTY]:
                if len([t for t in n.get_neighbors() if t is not None and t.state == Tile.State.FULL]) == 6:
                    n_c = self.find_candidate([getattr(n.get_neighbors()[j], 'e' + str((j + 3) % 6)) for j in range(6)])
                    if not n_c:
                        logger.warning(f"Warning: {n.get_pos()} closed but candidates found")
                    else:
                        logger.info(f"{n.get_pos()} closed, {len(n_c)} candidates found")
        return db_tile

    def undo(self):
        """Delete last tile placement."""
        if not self.last_placement:
            logger.warning("No last placement")
            return
        x, y = self.last_placement.get_pos()
        self._database.remove_tile(x, y)
        self._database.add_tile(Tile(x, y))
        self.last_placement = None
        logger.info(f"Last tile ({x, y}) removed from database")

    def save_data(self):
        """Save all tiles in a file."""
        with open(os.path.join(os.path.dirname(sys.argv[0]), DATA_FILE_NAME), 'w') as file:
            tiles = [tile for tile in self._database.get_tiles() if tile.state == tile.State.FULL]
            for tile in tiles:
                line = f"{tile.x};{tile.y};{tile.e0};{tile.e1};{tile.e2};{tile.e3};{tile.e4};{tile.e5}\n"
                file.write(line)
        logger.info(f"{len(tiles)} tiles saved successfully")

    def help_me(self, edges: List[Tile.Edge]) -> (list, list):
        """The core of the added value. It only considers empty slots with at least 2 neighbors fulfilled.
        If one edge doesn't match, the candidate is discarded for that slot (except 5/6 matches).

        :param list edges: list of edges of the tile.
        :return: matches with no conflict & 5/6 matches.
        """

        class _Match(NamedTuple):
            """Link data to a match."""
            tile: Tile
            n_neighbors: int
            value: float
            distance: float

        class _FiveOfSixMatch(NamedTuple):
            """Link data to a 5/6 match."""
            tile: Tile
            ideal_occurrence: int

        # List of all empty slots matching
        matches: List[_Match] = []
        five_of_six_matches: List[_FiveOfSixMatch] = []

        # For each slot
        for slot in [tile for tile in self._database.get_tiles() if tile.state == tile.State.EMPTY]:
            neighbors_num = len([t for t in slot.get_neighbors() if t is not None and t.state == Tile.State.FULL])
            if neighbors_num < 2:
                continue
            # For each rotation of the tile to place
            for i in range(self._rotations(edges)):
                candidate: Tile = Tile(slot.x, slot.y, edges[i:] + edges[:i])
                candidate_value = 0
                conflicts = 0
                for j, slot_n in enumerate(slot.get_neighbors()):
                    if slot_n and slot_n.state == Tile.State.FULL:
                        if not self._edge_match(
                                getattr(candidate, 'e' + str(j)), getattr(slot_n, 'e' + str((j + 3) % 6))
                        ):
                            conflicts += 1
                            if conflicts > 1:
                                break
                        # What is matched (from the existing tile and from the candidate)
                        candidate_value += EDGE_VALUE[getattr(slot_n, 'e' + str((j + 3) % 6))]
                        candidate_value += EDGE_VALUE[getattr(candidate, 'e' + str(j))]
                    else:
                        # What is left behind from the candidate
                        candidate_value -= EDGE_VALUE[getattr(candidate, 'e' + str(j))]
                # 5/6 matches
                if conflicts == 1 and neighbors_num == 6:
                    ideal_edges = [getattr(slot.get_neighbors()[j], 'e' + str((j + 3) % 6)) for j in range(6)]
                    five_of_six_matches.append(_FiveOfSixMatch(candidate, len(self.find_candidate(ideal_edges))))
                    continue
                if conflicts:
                    continue

                matches.append(_Match(
                    candidate, neighbors_num, float(str(candidate_value / neighbors_num)[:4]),
                    float(str(m.sqrt(sum(coord * coord for coord in self._tr(
                        candidate.x - self.m_x, candidate.y - self.m_y
                    ))))[:4])
                ))
        return matches, five_of_six_matches

    def find_candidate(self, edges: List[Tile.Edge]) -> list:
        """Says if the candidate given is already on the board or not.

        :return: list of matches coordinates.
        """
        matches: list = []
        for db_tile in [tile for tile in self._database.get_tiles() if tile.state == tile.State.FULL]:
            # Determine if the tile is symmetrical to avoid repetitions
            db_edges = db_tile.get_edges()
            for i in range(self._rotations(edges)):
                valid_tile = True
                for j in range(6):
                    if not self._edge_match(db_edges[j], edges[(i + j) % 6]):
                        valid_tile = False
                        break
                if valid_tile:
                    matches.append(db_tile.get_pos())
                    break
        return matches

    def find_tile(self, edges: List[Tile.Edge]) -> list:
        """Says if the tile given is already on the board or not.

        :return: list of matches coordinates.
        """
        matches: list = []
        for db_tile in [tile for tile in self._database.get_tiles() if tile.state == tile.State.FULL]:
            for i in range(self._rotations(edges)):
                if db_tile.get_edges() == edges[i:] + edges[:i]:
                    matches.append(db_tile.get_pos())
                    break
        return matches

    @staticmethod
    def _edge_match(e1: Tile.Edge, e2: Tile.Edge) -> bool:
        """Verify if edges match.

        :return: boolean.
        """
        if e1 == e2:
            return True
        if e1 > e2:
            e1, e2 = e2, e1
        if e2 == Tile.Edge.POND and e1 in [Tile.Edge.PLAIN, Tile.Edge.RIVER]:
            return True
        if e2 == Tile.Edge.DOME and e1 in [Tile.Edge.PLAIN, Tile.Edge.RIVER, Tile.Edge.RAIL, Tile.Edge.POND]:
            return True
        return False

    @staticmethod
    def _rotations(edges: List[Tile.Edge]) -> int:
        """Determine if the tile is symmetrical to avoid repetitions."""
        if edges == edges[1:] + edges[:1]:  # 60°
            return 1
        if edges == edges[2:] + edges[:2]:  # 120°
            return 2
        if edges == edges[3:] + edges[:3]:  # 180°
            return 3
        return 6

#    def count_occurrences(self):
#        """Says if the tile given is already on the board or not.

#        :return: occurrences.
#        """
#        for db_tile_ref in [tile for tile in self._database.get_tiles() if tile.state == tile.State.FULL]:
#            edges = db_tile_ref.get_edges()
#            matches: list = []
#            for db_tile in [tile for tile in self._database.get_tiles() if tile.state == tile.State.FULL]:
#                if db_tile.get_pos() == db_tile_ref.get_pos():
#                    continue
#                # Determine if the tile is symmetrical to avoid repetitions
#                db_edges = db_tile.get_edges()
#                for i in range(self._rotations(edges)):
#                    valid_tile = True
#                    for j in range(6):
#                        if not self._edge_match(db_edges[j], edges[(i + j) % 6]):
#                            valid_tile = False
#                            break
#                    if valid_tile:
#                        matches += [db_tile.get_pos()]
#                        break
#            if not matches:
#                print(db_tile_ref.get_pos())
