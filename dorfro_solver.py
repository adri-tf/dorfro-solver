"""Main file."""
import logging.config
import os
import sys

from PyQt5.QtWidgets import QApplication

from board import Board
from window import Window

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.conf"))


def main():
    """Main function."""
    board = Board()

    app = QApplication(sys.argv)
    win = Window(board)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# For 5/6 matches, consider exclusive edge matches
# Redo display output
