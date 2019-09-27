from contextlib import contextmanager
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication 

@contextmanager
def wait_cursor():
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        yield
    except Exception as e:
        QApplication.restoreOverrideCursor()
        raise e
    finally:
        QApplication.restoreOverrideCursor()
