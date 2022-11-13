"""Window"""
import logging
import math as m
import os.path
from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow

from board import Board, COLOR_MAPPING
from tile import Tile

logger = logging.getLogger("root")


class Window(QMainWindow):
    """Window."""

    def __init__(self, board: Board):
        super().__init__()

        # Window settings
        self.setWindowTitle("Dorfro-solver")
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.jpg")))
        self._width, self._height = 300, 360
        self.setFixedSize(self._width, self._height)
        self.setGeometry(int((1920 - self._width) / 2), 30, self._width, self._height)

        # Variables
        self._board: Board = board
        self._rotations = 0
        self._best_match: Optional[Tile] = None
        self._best_value: Optional[Tile] = None

        # Inputs
        self._inputWidget = QtWidgets.QWidget(self)
        self._inputWidget.setGeometry(0, 0, 150, 200)
        self._inputForm = QtWidgets.QFormLayout(self._inputWidget)
        self._inputForm.setContentsMargins(5, 5, 5, 5)

        self._xLabel, self._x = QtWidgets.QLabel("X", self._inputWidget), QtWidgets.QLineEdit(self._inputWidget)
        self._yLabel, self._y = QtWidgets.QLabel("Y", self._inputWidget), QtWidgets.QLineEdit(self._inputWidget)
        self._e0Label, self._e0 = QtWidgets.QLabel("1", self._inputWidget), QtWidgets.QLineEdit(self._inputWidget)
        self._e1Label, self._e1 = QtWidgets.QLabel("2", self._inputWidget), QtWidgets.QLineEdit(self._inputWidget)
        self._e2Label, self._e2 = QtWidgets.QLabel("3", self._inputWidget), QtWidgets.QLineEdit(self._inputWidget)
        self._e3Label, self._e3 = QtWidgets.QLabel("4", self._inputWidget), QtWidgets.QLineEdit(self._inputWidget)
        self._e4Label, self._e4 = QtWidgets.QLabel("5", self._inputWidget), QtWidgets.QLineEdit(self._inputWidget)
        self._e5Label, self._e5 = QtWidgets.QLabel("6", self._inputWidget), QtWidgets.QLineEdit(self._inputWidget)

        self._inputForm.setWidget(0, QtWidgets.QFormLayout.LabelRole, self._xLabel)
        self._inputForm.setWidget(0, QtWidgets.QFormLayout.FieldRole, self._x)
        self._inputForm.setWidget(1, QtWidgets.QFormLayout.LabelRole, self._yLabel)
        self._inputForm.setWidget(1, QtWidgets.QFormLayout.FieldRole, self._y)
        self._inputForm.setWidget(2, QtWidgets.QFormLayout.LabelRole, self._e0Label)
        self._inputForm.setWidget(2, QtWidgets.QFormLayout.FieldRole, self._e0)
        self._inputForm.setWidget(3, QtWidgets.QFormLayout.LabelRole, self._e1Label)
        self._inputForm.setWidget(3, QtWidgets.QFormLayout.FieldRole, self._e1)
        self._inputForm.setWidget(4, QtWidgets.QFormLayout.LabelRole, self._e2Label)
        self._inputForm.setWidget(4, QtWidgets.QFormLayout.FieldRole, self._e2)
        self._inputForm.setWidget(5, QtWidgets.QFormLayout.LabelRole, self._e3Label)
        self._inputForm.setWidget(5, QtWidgets.QFormLayout.FieldRole, self._e3)
        self._inputForm.setWidget(6, QtWidgets.QFormLayout.LabelRole, self._e4Label)
        self._inputForm.setWidget(6, QtWidgets.QFormLayout.FieldRole, self._e4)
        self._inputForm.setWidget(7, QtWidgets.QFormLayout.LabelRole, self._e5Label)
        self._inputForm.setWidget(7, QtWidgets.QFormLayout.FieldRole, self._e5)

        # Buttons
        self._buttonsWidget = QtWidgets.QWidget(self)
        self._buttonsWidget.setGeometry(0, 200, 300, 160)
        self._gridLayout = QtWidgets.QGridLayout(self._buttonsWidget)
        self._gridLayout.setContentsMargins(5, 5, 5, 5)

        self._pushButton0 = QtWidgets.QPushButton("Help Me!", self._buttonsWidget)
        self._pushButton1 = QtWidgets.QPushButton("Place Tile!", self._buttonsWidget)
        self._pushButton2 = QtWidgets.QPushButton("Undo", self._buttonsWidget)
        self._pushButton3 = QtWidgets.QPushButton("Best Match", self._buttonsWidget)
        self._pushButton4 = QtWidgets.QPushButton("Best Value", self._buttonsWidget)
        self._pushButton5 = QtWidgets.QPushButton("Find candidate", self._buttonsWidget)
        self._pushButton6 = QtWidgets.QPushButton("Find tile", self._buttonsWidget)
        self._pushButton7 = QtWidgets.QPushButton("Fast Render", self._buttonsWidget)
        self._pushButton8 = QtWidgets.QPushButton("Full Render", self._buttonsWidget)
        self._pushButton9 = QtWidgets.QPushButton("Save", self._buttonsWidget)

        self._pushButton0.clicked.connect(self._help_me)
        self._pushButton1.clicked.connect(self._place_tile)
        self._pushButton2.clicked.connect(self._board.undo)
        self._pushButton3.clicked.connect(self._place_best_match)
        self._pushButton4.clicked.connect(self._place_best_value)
        self._pushButton5.clicked.connect(self._find_candidate)
        self._pushButton6.clicked.connect(self._find_tile)
        self._pushButton7.clicked.connect(self._render_fast)
        self._pushButton8.clicked.connect(self._board.render)
        self._pushButton9.clicked.connect(self._board.save_data)

        self._gridLayout.addWidget(self._pushButton0, 0, 0, 1, 1)
        self._gridLayout.addWidget(self._pushButton1, 1, 0, 1, 1)
        self._gridLayout.addWidget(self._pushButton2, 2, 0, 1, 1)
        self._gridLayout.addWidget(self._pushButton3, 0, 1, 1, 1)
        self._gridLayout.addWidget(self._pushButton4, 1, 1, 1, 1)
        self._gridLayout.addWidget(self._pushButton5, 2, 1, 1, 1)
        self._gridLayout.addWidget(self._pushButton6, 3, 1, 1, 1)
        self._gridLayout.addWidget(self._pushButton7, 0, 2, 1, 1)
        self._gridLayout.addWidget(self._pushButton8, 1, 2, 1, 1)
        self._gridLayout.addWidget(self._pushButton9, 2, 2, 1, 1)

        # Rotation buttons
        self.tileWidget = QtWidgets.QWidget(self)
        self.tileWidget.setGeometry(150, 150, 150, 50)
        self.gridLayout = QtWidgets.QGridLayout(self.tileWidget)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)

        self.pushButtonL = QtWidgets.QPushButton(self.tileWidget)
        self.pushButtonR = QtWidgets.QPushButton(self.tileWidget)
        self.pushButtonL.setText("↻")
        self.pushButtonR.setText("↺")
        self.pushButtonL.clicked.connect(self._rotate_left)
        self.pushButtonR.clicked.connect(self._rotate_right)
        self.gridLayout.addWidget(self.pushButtonL, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.pushButtonR, 0, 1, 1, 1)

    def paintEvent(self, event):
        """Overriden function called automatically when initiating the widget and using repaint()."""
        x = 225
        y = 75
        w = 60
        hexagon_coord = [[x + w, y], [x + w * m.cos(-m.pi / 3), y + w * m.sin(-m.pi / 3)],
                         [x + w * m.cos(-m.pi * 2 / 3), y + w * m.sin(-m.pi * 2 / 3)], [x - w, y],
                         [x + w * m.cos(m.pi * 2 / 3), y + w * m.sin(m.pi * 2 / 3)],
                         [x + w * m.cos(m.pi / 3), y + w * m.sin(m.pi / 3)], [x + w, y]]

        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(Qt.white, 2, Qt.SolidLine))
        if self._validate_edges(logs=False):
            for i in range(6):
                painter.setBrush(
                    QtGui.QBrush(QColor(COLOR_MAPPING[Tile.Edge(int(getattr(self, '_e' + str(i)).text()))]),
                                 Qt.SolidPattern))
                polygon = QtGui.QPolygon([
                    QtCore.QPoint(x, y),
                    QtCore.QPoint(int(hexagon_coord[i][0]), int(hexagon_coord[i][1])),
                    QtCore.QPoint(int(hexagon_coord[i + 1][0]), int(hexagon_coord[i + 1][1])),
                ])

                painter.drawPolygon(polygon)
                painter.drawPolygon(polygon)
        else:
            for i in range(6):
                painter.setBrush(QtGui.QBrush(Qt.white, Qt.SolidPattern))

                polygon = QtGui.QPolygon([
                    QtCore.QPoint(x, y),
                    QtCore.QPoint(int(hexagon_coord[i][0]), int(hexagon_coord[i][1])),
                    QtCore.QPoint(int(hexagon_coord[i + 1][0]), int(hexagon_coord[i + 1][1])),
                ])

                painter.drawPolygon(polygon)
                painter.drawPolygon(polygon)

    def _validate_coord(self) -> bool:
        """Verify if the X and Y coordinates are valid."""
        try:
            int(self._x.text())
        except ValueError:
            logger.warning("X must be an integer")
            return False
        try:
            int(self._y.text())
        except ValueError:
            logger.warning("Y must be an integer")
            return False
        return True

    def _validate_edges(self, logs: bool = True) -> bool:
        """Verify if all 6 edges are valid."""
        error = False
        for i_edge in range(6):
            try:
                Tile.Edge(int(getattr(self, '_e' + str(i_edge)).text()))
            except ValueError:
                error = True
                if logs:
                    logger.warning(
                        f"Edge {i_edge + 1}: '{getattr(self, '_e' + str(i_edge)).text()}' is not a valid edge")
        if error:
            return False
        return True

    def _help_me(self):
        self._reset_preview()
        if not self._validate_edges():
            return
        self.repaint()

        # Logging
        logger.info("------------")

        # Check if tile was seen before
        tile_occ = self._board.find_tile(
            [Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]]
        )
        if not tile_occ:
            logger.info("New tile")

        # Displaying best values for each matches
        matches, five_of_six_matches = self._board.help_me(
            [Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]]
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
            self._board.place_tile(Tile(int(self._x.text()), int(self._y.text()), [
                Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]
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
                [Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]])
            if not matches:
                logger.info("Candidate not found in database.")
            elif len(matches) < 11:
                logger.info(f"Candidate found: {matches}.")
            else:
                logger.info(f"Candidate found: {len(matches)} matches.")
            self.update()

    def _find_tile(self):
        if self._validate_edges():
            matches = self._board.find_tile(
                [Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]])
            if not matches:
                logger.info("Tile not found in database.")
            elif len(matches) < 11:
                logger.info(f"Tile found: {matches}.")
            else:
                logger.info(f"Tile found: {len(matches)} matches.")
            self.update()

    def _rotate_left(self):
        if self._validate_edges():
            self._rotations += 1
            (self._e0, self._e1, self._e2, self._e3, self._e4, self._e5) = (
                self._e1, self._e2, self._e3, self._e4, self._e5, self._e0)
            self.update()

    def _rotate_right(self):
        if self._validate_edges():
            self._rotations -= 1
            (self._e0, self._e1, self._e2, self._e3, self._e4, self._e5) = (
                self._e5, self._e0, self._e1, self._e2, self._e3, self._e4)
            self.update()

    def _reset_preview(self):
        if self._rotations != 0:
            self._e0, self._e1, self._e2, self._e3, self._e4, self._e5 = [
                getattr(self, '_e' + str((i - self._rotations) % 6)) for i in range(6)
            ]
            self._rotations = 0
        self._best_match = None
        self._best_value = None

    def _render_fast(self):
        self._board.render(fast_mode=True)
