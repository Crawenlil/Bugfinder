from settings import *
from image_processors.abc.split import Split
from errors import TransformationError
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout, QLabel, QMessageBox

class Grid(Split):
    priority = 1
    process_type = SPLIT
    def __init__(self, selected=False, x_offset=0, y_offset=0, x_between=0, y_between=0, pcb_width=0, pcb_height=0, n_rows=0, n_cols=0):
        super().__init__(selected)
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.x_between = x_between
        self.y_between = y_between
        self.pcb_width = pcb_width
        self.pcb_height = pcb_height
        self.n_rows = n_rows
        self.n_cols = n_cols

    def __eq__(self, other):
        return (
            super().__eq__(other) 
            and self.x_offset == other.x_offset
            and self.y_offset == other.y_offset
            and self.x_between == other.x_between
            and self.y_between == other.y_between
            and self.pcb_width == other.pcb_width
            and self.pcb_height == other.pcb_height
            and self.n_rows == other.n_rows
            and self.n_cols == other.n_cols
        )

    @classmethod
    def from_json(cls, json):
        return cls(
            json['selected'],
            json['x_offset'],
            json['y_offset'],
            json['x_between'],
            json['y_between'],
            json['pcb_width'],
            json['pcb_height'],
            json['n_rows'],
            json['n_cols'],
        )

    def split(self, images):
        height, width = images[images[OUT_IMAGE]].shape[:2]
        y_margin = self.pcb_height / 10
        x_margin = self.pcb_width / 10
        margin = min(x_margin, y_margin)
        slices = []
        for r in range(self.n_rows):
            y1 = self.y_offset + r*(self.pcb_height + self.y_between)
            y2 = y1 + self.pcb_height
            for c in range(self.n_cols):
                x1 = self.x_offset + c*(self.pcb_width + self.x_between)
                x2 = x1 + self.pcb_width
                slices.append((max(y1-margin, 0), min(y2+margin,height), max(x1-margin, 0), min(x2+margin, width)))
        return slices

    def serialize(self):
        return {
            'name': 'Grid',
            'selected': self.selected,
            'x_offset': self.x_offset,
            'y_offset': self.y_offset,
            'x_between': self.x_between,
            'y_between': self.y_between,
            'pcb_width': self.pcb_width,
            'pcb_height': self.pcb_height,
            'n_rows': self.n_rows,
            'n_cols': self.n_cols,
        }

    def lines(self, height, width):
        lines = []
        for r in range(self.n_rows):
            y1 = self.y_offset + r*(self.pcb_height + self.y_between)
            y2 = self.y_offset + self.pcb_height + r*(self.pcb_height + self.y_between)
            lines.append(((0,y1), (width, y1)))
            lines.append(((0, y2), (width, y2)))
        for c in range(self.n_cols):
            x1 = self.x_offset + c*(self.pcb_width + self.x_between)
            x2 = self.x_offset + self.pcb_width + c*(self.pcb_width + self.x_between)
            lines.append(((x1,0), (x1, height)))
            lines.append(((x2,0), (x2, height)))
        return lines

    def gui(self, image_widget):
        super().gui(image_widget)
        self.group_box = QGroupBox(GRID)
        grid_layout = QGridLayout()
        self.group_box.setLayout(grid_layout) 
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)
        self.group_box.toggled[bool].connect(self._checked_action_handler)

        self._set_grid_row(grid_layout, 0, 0, "Y offset", "Vertical distance from top to first pcb", self._create_spin_box(0, 1000000, 0, self._y_offset_value_changed_handler, step=1, suffix=" px"))
        self._set_grid_row(grid_layout, 0, 2, "X offset", "Horizontal distance from top to first pcb", self._create_spin_box(0, 1000000, 0, self._x_offset_value_changed_handler, step=1, suffix=" px"))
        self._set_grid_row(grid_layout, 1, 0, "Y pcbs margin", "Vertical distance between pcbs", self._create_spin_box(0, 10000, 0, self._y_between_value_changed_handler, step=1, suffix=" px"))
        self._set_grid_row(grid_layout, 1, 2, "X pcbs margin", "Horizontal distance between pcbs", self._create_spin_box(0, 10000, 0, self._x_between_value_changed_handler, step=1, suffix=" px"))
        self._set_grid_row(grid_layout, 2, 0, "Pcb height", "Single pcb vertical dimension", self._create_spin_box(0, 1000000, 0, self._pcb_height_value_changed_handler, step=1, suffix=" px"))
        self._set_grid_row(grid_layout, 2, 2, "Pcb width", "Single pcb horizontal dimension", self._create_spin_box(0, 1000000, 0, self._pcb_width_value_changed_handler, step=1, suffix=" px"))
        self._set_grid_row(grid_layout, 3, 0, "Rows", "Number of rows", self._create_spin_box(0, 1000, 0, self._n_rows_value_changed_handler))
        self._set_grid_row(grid_layout, 3, 2, "Columns", "Number of columns", self._create_spin_box(0, 1000, 0, self._n_cols_value_changed_handler))

        return self.group_box

    def _checked_action_handler(self, checked):
        super()._checked_action_handler(checked)
        self.image_widget.update_view(transform=False)

    def _x_offset_value_changed_handler(self, value):
        self.x_offset = value
        self.image_widget.update_view(transform=False)

    def _y_offset_value_changed_handler(self, value):
        self.y_offset = value
        self.image_widget.update_view(transform=False)

    def _x_between_value_changed_handler(self, value):
        self.x_between = value
        self.image_widget.update_view(transform=False)

    def _y_between_value_changed_handler(self, value):
        self.y_between = value
        self.image_widget.update_view(transform=False)

    def _pcb_width_value_changed_handler(self, value):
        self.pcb_width = value
        self.image_widget.update_view(transform=False)

    def _pcb_height_value_changed_handler(self, value):
        self.pcb_height = value
        self.image_widget.update_view(transform=False)

    def _n_rows_value_changed_handler(self, value):
        self.n_rows = value
        self.image_widget.update_view(transform=False)

    def _n_cols_value_changed_handler(self, value):
        self.n_cols = value
        self.image_widget.update_view(transform=False)
