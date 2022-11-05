"""Window class."""
import logging
import math as m
from tkinter import Label, Entry, Button, Tk, SOLID, Frame, Canvas
from typing import Optional

from board import Board, COLOR_MAPPING
from database import Tile

logger = logging.getLogger("root")


class Window:
    """UI."""

    def __init__(self, board: Board):
        self._board: Board = board
        self._best_match: Optional[Tile] = None
        self._best_value: Optional[Tile] = None

        self.win = Tk()
        self.win.configure(bg='antique white')
        self.win.geometry('300x320')

        # Frame 1 (top left): input
        frame1 = Frame(self.win, bd=1, relief=SOLID, padx=5, pady=5)
        frame1.place_configure(x=0, y=0, width=150, height=200)

        self.x = Entry(frame1, width=15)
        self.y = Entry(frame1, width=15)
        self.e0 = Entry(frame1, width=15)
        self.e1 = Entry(frame1, width=15)
        self.e2 = Entry(frame1, width=15)
        self.e3 = Entry(frame1, width=15)
        self.e4 = Entry(frame1, width=15)
        self.e5 = Entry(frame1, width=15)

        Label(frame1, text="X:").grid(row=0)
        Label(frame1, text="Y:").grid(row=1)
        Label(frame1, text='1:').grid(row=2)
        Label(frame1, text='2:').grid(row=3)
        Label(frame1, text='3:').grid(row=4)
        Label(frame1, text='4:').grid(row=5)
        Label(frame1, text='5:').grid(row=6)
        Label(frame1, text='6:').grid(row=7)

        self.x.grid(row=0, column=1)
        self.y.grid(row=1, column=1)
        self.e0.grid(row=2, column=1)
        self.e1.grid(row=3, column=1)
        self.e2.grid(row=4, column=1)
        self.e3.grid(row=5, column=1)
        self.e4.grid(row=6, column=1)
        self.e5.grid(row=7, column=1)

        # Frame 2 (bottom): commands
        frame2 = Frame(self.win, bd=1, relief=SOLID, padx=5, pady=5)
        frame2.place_configure(x=0, y=200, width=300, height=120)

        Button(frame2, text='Help Me!', command=self._help_me).grid(column=1, row=9, padx=10, pady=5)
        Button(frame2, text='Place Tile', command=self._place_tile).grid(column=1, row=10, padx=10, pady=5)
        Button(frame2, text='Undo Move', command=self._board.undo).grid(column=1, row=11, padx=10, pady=5)
        Button(frame2, text='Find candidate', command=self._find_candidate).grid(column=2, row=9, padx=10, pady=5)
        Button(frame2, text='Best Match', command=self._place_best_match).grid(column=2, row=10, padx=10, pady=5)
        Button(frame2, text='Best Value', command=self._place_best_value).grid(column=2, row=11, padx=10, pady=5)
        Button(frame2, text='Find tile', command=self._find_tile).grid(column=3, row=9, padx=10, pady=5)
        Button(frame2, text='Render', command=self._board.render).grid(column=3, row=10, padx=10, pady=5)
        Button(frame2, text='Save', command=self._board.save_data).grid(column=3, row=11, padx=10, pady=5)

        # Frame 3 (top right): hexagon
        frame3 = Frame(self.win, bd=1, relief=SOLID)
        frame3.place_configure(x=150, y=0, width=150, height=160)

        self.canvas = Canvas(frame3)
        self.canvas.pack()

        # Frame 4 (below frame 3): < and > to rotate
        frame4 = Frame(self.win, bd=1, relief=SOLID)
        frame4.place_configure(x=150, y=160, width=150, height=40)

        Button(frame4, text='<', command=self._rotate_right).grid(column=1, row=1, padx=25, pady=5)
        Button(frame4, text='>', command=self._rotate_left).grid(column=2, row=1, padx=25, pady=5)

        self._rotations: int = 0

        self.win.mainloop()

    def _validate_coord(self) -> bool:
        """Verify if the X and Y coordinates are valid."""
        try:
            int(self.x.get())
        except ValueError:
            logger.warning("X must be an integer")
            return False
        try:
            int(self.y.get())
        except ValueError:
            logger.warning("Y must be an integer")
            return False
        return True

    def _validate_edges(self) -> bool:
        """Verify if all 6 edges are valid."""
        error = False
        for i_edge in range(6):
            try:
                Tile.Edge(int(getattr(self, 'e' + str(i_edge)).get()))
            except ValueError:
                error = True
                logger.warning(f"Edge {i_edge + 1}: '{getattr(self, 'e' + str(i_edge)).get()}' is not a valid edge")
        if error:
            return False
        return True

    def _help_me(self):
        self._reset_preview()
        if not self._validate_edges():
            return
        self._draw_hexagon()

        # Logging
        logger.info("------------")

        # Check if tile was seen before
        tile_occ = self._board.find_tile(
            [Tile.Edge(int(edge.get())) for edge in [self.e0, self.e1, self.e2, self.e3, self.e4, self.e5]]
        )
        if not tile_occ:
            logger.info("New tile")

        # Displaying best values for each matches
        matches, five_of_six_matches = self._board.help_me(
            [Tile.Edge(int(edge.get())) for edge in [self.e0, self.e1, self.e2, self.e3, self.e4, self.e5]]
        )
        if not matches:
            logger.info("Bruh")
            return None, None

        matches.sort(key=lambda t: (-t.value, t.distance))  # sort by value (descending) then distance
        for neighbors_num in range(1, 7):
            sub_list = [tmp_tile for tmp_tile in matches if tmp_tile.n_neighbors == neighbors_num]
            if not sub_list:
                continue
            if len(sub_list) > 10:
                info = [f"V:{temp_tile.value} E:{temp_tile.distance} {temp_tile.tile.get_pos()}"
                        for temp_tile in sub_list[:10]]
            else:
                info = [f"V:{temp_tile.value} E:{temp_tile.distance} {temp_tile.tile.get_pos()}"
                        for temp_tile in sub_list]
            logger.info("%s %s", neighbors_num, info)

        # Retrieving candidate with best value
        if len(matches) == 1 or matches[0].value != matches[1].value:
            logger.info(f"BV: M:{matches[0].n_neighbors} V:{matches[0].value} {matches[0].tile.get_pos()}")
        self._best_value = matches[0].tile  # always have a BV, but no logs if draw

        # Retrieving candidate with best match
        matches.sort(key=lambda t: (-t.n_neighbors))
        if len(matches) == 1 or matches[0].n_neighbors != matches[1].n_neighbors:
            logger.info(f"BM: M:{matches[0].n_neighbors} V:{matches[0].value} {matches[0].tile.get_pos()}")
        self._best_match = matches[0].tile  # always have a BM, but no logs if draw

        # 5/6 matches
        for match in five_of_six_matches:
            logger.info(f"5/6 Match: {match.tile.get_pos()} | Ideal occurrence: {match.ideal_occurrence}")

    def _place_tile(self):
        if self._validate_coord() and self._validate_edges():
            self._board.place_tile(Tile(int(self.x.get()), int(self.y.get()), [
                Tile.Edge(int(edge.get())) for edge in [self.e0, self.e1, self.e2, self.e3, self.e4, self.e5]
            ]))
            self._reset_preview()

    def _place_best_match(self):
        if self._best_match:
            self._board.place_tile(self._best_match)
            logger.info("Best Match placed")
            self._reset_preview()
        else:
            logger.info("No best tile retrieved")

    def _place_best_value(self):
        if self._best_value:
            self._board.place_tile(self._best_value)
            logger.info("Best Value placed")
            self._reset_preview()
        else:
            logger.info("No best tile retrieved")

    def _find_candidate(self):
        if self._validate_edges():
            matches = self._board.find_candidate(
                [Tile.Edge(int(edge.get())) for edge in [self.e0, self.e1, self.e2, self.e3, self.e4, self.e5]])
            if not matches:
                logger.info("Candidate not found in database.")
            elif len(matches) < 11:
                logger.info(f"Candidate found: {matches}.")
            else:
                logger.info(f"Candidate found: {len(matches)} matches.")
            self._draw_hexagon()

    def _find_tile(self):
        if self._validate_edges():
            matches = self._board.find_tile(
                [Tile.Edge(int(edge.get())) for edge in [self.e0, self.e1, self.e2, self.e3, self.e4, self.e5]])
            if not matches:
                logger.info("Tile not found in database.")
            elif len(matches) < 11:
                logger.info(f"Tile found: {matches}.")
            else:
                logger.info(f"Tile found: {len(matches)} matches.")
            self._draw_hexagon()

    def _draw_hexagon(self):
        x = 75
        y = 80
        w = 60

        # Y-axis is flipped
        hexagon_coord = [[x + w, y], [x + w * m.cos(-m.pi / 3), y + w * m.sin(-m.pi / 3)],
                         [x + w * m.cos(-m.pi * 2 / 3), y + w * m.sin(-m.pi * 2 / 3)], [x - w, y],
                         [x + w * m.cos(m.pi * 2 / 3), y + w * m.sin(m.pi * 2 / 3)],
                         [x + w * m.cos(m.pi / 3), y + w * m.sin(m.pi / 3)], [x + w, y]]

        for i in range(6):
            points = hexagon_coord[i] + hexagon_coord[i + 1] + [x] + [y]
            self.canvas.create_polygon(points, fill=COLOR_MAPPING[int(getattr(self, 'e' + str(i)).get())])

    def _rotate_left(self):
        if self._validate_edges():
            self._rotations += 1
            self.e0, self.e1, self.e2, self.e3, self.e4, self.e5 = self.e1, self.e2, self.e3, self.e4, self.e5, self.e0
            self._draw_hexagon()

    def _rotate_right(self):
        if self._validate_edges():
            self._rotations -= 1
            self.e0, self.e1, self.e2, self.e3, self.e4, self.e5 = self.e5, self.e0, self.e1, self.e2, self.e3, self.e4
            self._draw_hexagon()

    def _reset_preview(self):
        if self._rotations != 0:
            self.e0, self.e1, self.e2, self.e3, self.e4, self.e5 = [
                getattr(self, 'e' + str((i - self._rotations) % 6)) for i in range(6)
            ]
            self._rotations = 0
        self._best_match = None
        self._best_value = None

    def _save_exit(self):
        self._board.save_data()
        self.win.quit()
