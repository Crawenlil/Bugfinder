import unittest
from image_processors.grid import Grid
import numpy as np
import cv2

class ImageProcessTest(unittest.TestCase):

    def test_lines_offset(self):
        grid = Grid(selected=True, x_offset=10, y_offset=10, x_between=0, y_between=0, pcb_width=15, pcb_height=15, n_rows=2, n_cols=2)
        lines = [
            ((0, 10), (100, 10)),
            ((0, 25), (100, 25)),
            ((0, 25), (100, 25)),
            ((0, 40), (100, 40)),
            ((10, 0), (10, 100)),
            ((25, 0), (25, 100)),
            ((25, 0), (25, 100)),
            ((40, 0), (40, 100))
        ]
        self.assertListEqual(grid.lines(100, 100), lines)

    def test_lines_between(self):
        grid = Grid(selected=True, x_offset=0, y_offset=0, x_between=10, y_between=10, pcb_width=15, pcb_height=15, n_rows=2, n_cols=2)
        lines = [
            ((0, 0), (100, 0)),
            ((0, 15), (100, 15)),
            ((0, 25), (100, 25)),
            ((0, 40), (100, 40)),
            ((0, 0), (0, 100)),
            ((15, 0), (15, 100)),
            ((25, 0), (25, 100)),
            ((40, 0), (40, 100))
        ]
        self.assertListEqual(grid.lines(100, 100), lines)

    def test_lines_n(self):
        grid = Grid(selected=True, x_offset=0, y_offset=0, x_between=0, y_between=0, pcb_width=15, pcb_height=15, n_rows=3, n_cols=2)
        lines = [
            ((0, 0), (100, 0)),
            ((0, 15), (100, 15)),
            ((0, 15), (100, 15)),
            ((0, 30), (100, 30)),
            ((0, 30), (100, 30)),
            ((0, 45), (100, 45)),
            ((0, 0), (0, 100)),
            ((15, 0), (15, 100)),
            ((15, 0), (15, 100)),
            ((30, 0), (30, 100))
        ]
        self.assertListEqual(grid.lines(100, 100), lines)

    def test_lines(self):
        grid = Grid(selected=True, x_offset=10, y_offset=10, x_between=100, y_between=100, pcb_width=400, pcb_height=400, n_rows=2, n_cols=2)
        lines = [
            ((0, 10), (1000, 10)),
            ((0, 410), (1000, 410)),
            ((0, 510), (1000, 510)),
            ((0, 910), (1000, 910)),
            ((10, 0), (10, 1000)),
            ((410, 0), (410, 1000)), 
            ((510, 0),(510, 1000)),
            ((910, 0), (910, 1000))
        ]
        self.assertListEqual(grid.lines(1000, 1000), lines)




