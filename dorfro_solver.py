"""Main file."""
import logging.config
import os
import sys

from PyQt5.QtWidgets import QApplication

from window import MainWidget

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.conf"))


def main():
    """Main function."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = MainWidget()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
