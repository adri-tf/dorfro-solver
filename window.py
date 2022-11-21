"""Window"""
import logging
import math as m
import os.path
from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from board import Board, COLOR_MAPPING
from tile import Tile

logger = logging.getLogger("root")


class MainWidget(QtWidgets.QWidget):
    """Window."""

    def __init__(self):
        super().__init__()

        # Text display (declared now for board logs)
        self._textDisplay = QtWidgets.QTextEdit()
        self._textDisplay.ensureCursorVisible()
        self._textDisplay.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self._cursor = self._textDisplay.textCursor()
        self._textDisplay.setTextCursor(self._cursor)
        self._textDisplay.setReadOnly(True)
        self._textDisplay.setStyleSheet("background-color: rgb(43, 43, 43); font-family: Consolas; font-size: 15px;")

        # Variables
        self._board = Board(self._logger)
        self._rotations = 0
        self._best_match: Optional[Tile] = None
        self._best_value: Optional[Tile] = None

        # Window settings
        width, height = 1080, 360
        self.setGeometry(int((1920 - width) / 2), 30, width, height)
        self.setMinimumSize(450, 400)
        self.setWindowTitle("Dorfro-solver")
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.jpg")))
        self.setStyleSheet("color: white; background-color: rgb(60, 63, 65);")

        # Inputs
        input_form_widget = QtWidgets.QWidget()
        input_form_layout = QtWidgets.QFormLayout(input_form_widget)

        x_label, self._x = QtWidgets.QLabel("X", input_form_widget), QtWidgets.QLineEdit(input_form_widget)
        y_label, self._y = QtWidgets.QLabel("Y", input_form_widget), QtWidgets.QLineEdit(input_form_widget)
        e0_label, self._e0 = QtWidgets.QLabel("1", input_form_widget), QtWidgets.QLineEdit(input_form_widget)
        e1_label, self._e1 = QtWidgets.QLabel("2", input_form_widget), QtWidgets.QLineEdit(input_form_widget)
        e2_label, self._e2 = QtWidgets.QLabel("3", input_form_widget), QtWidgets.QLineEdit(input_form_widget)
        e3_label, self._e3 = QtWidgets.QLabel("4", input_form_widget), QtWidgets.QLineEdit(input_form_widget)
        e4_label, self._e4 = QtWidgets.QLabel("5", input_form_widget), QtWidgets.QLineEdit(input_form_widget)
        e5_label, self._e5 = QtWidgets.QLabel("6", input_form_widget), QtWidgets.QLineEdit(input_form_widget)

        self._x.setStyleSheet("background-color: rgb(69, 73, 74);")
        self._y.setStyleSheet("background-color: rgb(69, 73, 74);")
        self._e0.setStyleSheet(" background-color: rgb(69, 73, 74);")
        self._e1.setStyleSheet(" background-color: rgb(69, 73, 74);")
        self._e2.setStyleSheet(" background-color: rgb(69, 73, 74);")
        self._e3.setStyleSheet(" background-color: rgb(69, 73, 74);")
        self._e4.setStyleSheet(" background-color: rgb(69, 73, 74);")
        self._e5.setStyleSheet(" background-color: rgb(69, 73, 74);")

        input_form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, x_label)
        input_form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self._x)
        input_form_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, y_label)
        input_form_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self._y)
        input_form_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, e0_label)
        input_form_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self._e0)
        input_form_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, e1_label)
        input_form_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self._e1)
        input_form_layout.setWidget(4, QtWidgets.QFormLayout.LabelRole, e2_label)
        input_form_layout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self._e2)
        input_form_layout.setWidget(5, QtWidgets.QFormLayout.LabelRole, e3_label)
        input_form_layout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self._e3)
        input_form_layout.setWidget(6, QtWidgets.QFormLayout.LabelRole, e4_label)
        input_form_layout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self._e4)
        input_form_layout.setWidget(7, QtWidgets.QFormLayout.LabelRole, e5_label)
        input_form_layout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self._e5)

        # Buttons
        buttons_widget = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QGridLayout(buttons_widget)

        push_button0 = QtWidgets.QPushButton("Help Me!", buttons_widget)
        push_button1 = QtWidgets.QPushButton("Place Tile!", buttons_widget)
        push_button2 = QtWidgets.QPushButton("Undo", buttons_widget)
        push_button3 = QtWidgets.QPushButton("Best Match", buttons_widget)
        push_button4 = QtWidgets.QPushButton("Best Value", buttons_widget)
        push_button5 = QtWidgets.QPushButton("Find candidate", buttons_widget)
        push_button6 = QtWidgets.QPushButton("Find tile", buttons_widget)
        push_button7 = QtWidgets.QPushButton("Fast Render", buttons_widget)
        push_button8 = QtWidgets.QPushButton("Full Render", buttons_widget)
        push_button9 = QtWidgets.QPushButton("Save", buttons_widget)

        push_button0.clicked.connect(self._help_me)
        push_button1.clicked.connect(self._place_tile)
        push_button2.clicked.connect(self._board.undo)
        push_button3.clicked.connect(self._place_best_match)
        push_button4.clicked.connect(self._place_best_value)
        push_button5.clicked.connect(self._find_candidate)
        push_button6.clicked.connect(self._find_tile)
        push_button7.clicked.connect(self._render_fast)
        push_button8.clicked.connect(self._board.render)
        push_button9.clicked.connect(self._board.save_data)

        buttons_layout.addWidget(push_button0, 0, 0, 1, 1)
        buttons_layout.addWidget(push_button1, 1, 0, 1, 1)
        buttons_layout.addWidget(push_button2, 2, 0, 1, 1)
        buttons_layout.addWidget(push_button3, 0, 1, 1, 1)
        buttons_layout.addWidget(push_button4, 1, 1, 1, 1)
        buttons_layout.addWidget(push_button5, 2, 1, 1, 1)
        buttons_layout.addWidget(push_button6, 3, 1, 1, 1)
        buttons_layout.addWidget(push_button7, 0, 2, 1, 1)
        buttons_layout.addWidget(push_button8, 1, 2, 1, 1)
        buttons_layout.addWidget(push_button9, 2, 2, 1, 1)

        # Rotation buttons
        rot_buttons_widget = QtWidgets.QWidget()
        rot_buttons_layout = QtWidgets.QGridLayout(rot_buttons_widget)

        push_button_l = QtWidgets.QPushButton(rot_buttons_widget)
        push_button_r = QtWidgets.QPushButton(rot_buttons_widget)
        push_button_l.setText("↻")
        push_button_r.setText("↺")
        push_button_l.clicked.connect(self._rotate_left)
        push_button_r.clicked.connect(self._rotate_right)
        rot_buttons_layout.addWidget(push_button_l, 0, 0, 1, 1)
        rot_buttons_layout.addWidget(push_button_r, 0, 1, 1, 1)

        # Window arrangement
        main_layout = QtWidgets.QHBoxLayout(self)  # ||
        layout_1 = QtWidgets.QVBoxLayout()  # =
        layout_11 = QtWidgets.QHBoxLayout()  # ||
        layout_112 = QtWidgets.QVBoxLayout()  # =

        layout_1.addLayout(layout_11)
        layout_1.addWidget(buttons_widget)
        layout_1.addStretch(1)

        layout_11.addWidget(input_form_widget)
        layout_11.addLayout(layout_112)

        layout_112.addStretch()
        layout_112.addWidget(rot_buttons_widget)

        main_layout.addLayout(layout_1)
        main_layout.addWidget(self._textDisplay, 1)

    def paintEvent(self, event):
        """Overriden function called automatically when initiating the widget and using repaint()."""
        x = 247
        y = 100
        w = 60
        hexagon_coord = [[x + w, y], [x + w * m.cos(-m.pi / 3), y + w * m.sin(-m.pi / 3)],
                         [x + w * m.cos(-m.pi * 2 / 3), y + w * m.sin(-m.pi * 2 / 3)], [x - w, y],
                         [x + w * m.cos(m.pi * 2 / 3), y + w * m.sin(m.pi * 2 / 3)],
                         [x + w * m.cos(m.pi / 3), y + w * m.sin(m.pi / 3)], [x + w, y]]

        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(Qt.lightGray, 2, Qt.SolidLine))
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

    def _logger(self, string: str):
        """Logs for python and Qt window."""
        logger.info(string)
        self._cursor.insertText(string + "\n")
        self._textDisplay.moveCursor(QtGui.QTextCursor.End)

    def _validate_coord(self) -> bool:
        """Verify if the X and Y coordinates are valid."""
        try:
            int(self._x.text())
        except ValueError:
            self._logger("X must be an integer")
            return False
        try:
            int(self._y.text())
        except ValueError:
            self._logger("Y must be an integer")
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
                    self._logger(f"Edge {i_edge + 1}: '{getattr(self, '_e' + str(i_edge)).text()}' is not a valid edge")
        if error:
            return False
        return True

    def _help_me(self):
        self._reset_preview()
        if not self._validate_edges():
            return
        self.repaint()

        # Displaying best values for each matches
        matches, five_of_six_matches = self._board.help_me(
            [Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]]
        )
        if not matches:
            self._logger("Bruh")
            return

        result_table, neighbors_num = [], []
        matches.sort(key=lambda t: (-t.value, t.distance))  # sort by value (descending) then distance
        for n_m in range(7, 1, -1):
            sub_list = [tmp_tile for tmp_tile in matches if tmp_tile.n_neighbors == n_m]
            if not sub_list:
                continue
            neighbors_num.append(n_m)
            if len(sub_list) > 15:
                result_table.append(
                    [
                        f"V:{temp_tile.value} E:{temp_tile.distance} {temp_tile.tile.get_pos()}"
                        for temp_tile in sub_list[:15]
                    ]
                )
            else:
                result_table.append(
                    [f"V:{temp_tile.value} E:{temp_tile.distance} {temp_tile.tile.get_pos()}" for temp_tile in sub_list]
                )

        # Create empty slots for a proper table
        results_length = max(len(l_match) for l_match in result_table)
        for line in result_table:
            line += [''] * (results_length - len(line))

        self._logger("#" * (30 * len(result_table) + 1))

        # Transpose the table
        result_table = [
            [result_table[j][i] for j in range(len(result_table))] for i in range(len(result_table[0]) - 1, -1, -1)
        ]

        for line in result_table:
            display = "|"
            for match in line:
                if not match:
                    display += "\t|"
                else:
                    display += "  " + match + "\t|"
            self._logger(repr(display.expandtabs(30))[1:-1])

        values = "-"
        for n in neighbors_num:
            values += " - - - - - - -" + str(n) + "- - - - - - - -"
        self._logger(values)

        # 5/6 matches
        for match in five_of_six_matches:
            self._logger(f"5/6 Match: {match.tile.get_pos()} | Ideal occurrence: {match.ideal_occurrence}")

        # Retrieving candidate with best value
        if len(matches) == 1 or matches[0].value != matches[1].value:
            self._logger(f"BV: M:{matches[0].n_neighbors} V:{matches[0].value} {matches[0].tile.get_pos()}")
        self._best_value = matches[0].tile  # always have a BV, but no logs if draw

        # Retrieving candidate with best match
        matches.sort(key=lambda t: (-t.n_neighbors))
        if len(matches) == 1 or matches[0].value != matches[1].value:
            self._logger(f"BM: M:{matches[0].n_neighbors} V:{matches[0].value} {matches[0].tile.get_pos()}")
        self._best_match = matches[0].tile  # always have a BM, but no logs if draw

        # Check if tile was seen before
        tile_occ = self._board.find_tile(
            [Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]]
        )
        if not tile_occ:
            self._logger("New tile")

    def _place_tile(self):
        if self._validate_coord() and self._validate_edges():
            self._board.place_tile(Tile(int(self._x.text()), int(self._y.text()), [
                Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]
            ]))
            self._reset_preview()

    def _place_best_match(self):
        if self._best_match:
            self._board.place_tile(self._best_match)
            self._logger("Best Match placed")
            self._reset_preview()
        else:
            self._logger("No best tile retrieved")

    def _place_best_value(self):
        if self._best_value:
            self._board.place_tile(self._best_value)
            self._logger("Best Value placed")
            self._reset_preview()
        else:
            self._logger("No best tile retrieved")

    def _find_candidate(self):
        if self._validate_edges():
            matches = self._board.find_candidate(
                [Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]])
            if not matches:
                self._logger("Candidate not found in database.")
            elif len(matches) < 11:
                self._logger(f"Candidate found: {matches}.")
            else:
                self._logger(f"Candidate found: {len(matches)} matches.")
            self.update()

    def _find_tile(self):
        if self._validate_edges():
            matches = self._board.find_tile(
                [Tile.Edge(int(edge.text())) for edge in [self._e0, self._e1, self._e2, self._e3, self._e4, self._e5]])
            if not matches:
                self._logger("Tile not found in database.")
            elif len(matches) < 11:
                self._logger(f"Tile found: {matches}.")
            else:
                self._logger(f"Tile found: {len(matches)} matches.")
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
