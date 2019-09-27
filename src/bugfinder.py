#!/usr/bin/env python3.4
import sys
from PyQt5.QtWidgets import QApplication 
from controllers.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow(app)
    main_window.setFixedSize(1280, 720)

    sys.exit(app.exec_())
