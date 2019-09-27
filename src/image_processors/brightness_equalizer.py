from settings import *
from errors import TransformationError
from image_processors.abc.transformation import Transformation
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout, QLabel, QMessageBox

class BrightnessEqualizer(Transformation):
    priority = 2
    process_type = COLOR
    def __init__(self, selected=False, clip_limit=0.7, tile_grid_size=(10,10)):
        super().__init__(selected)
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size

    def __eq__(self, other):
        return super().__eq__(other) and self.clip_limit == other.clip_limit and self.tile_grid_size == other.tile_grid_size
        
    @classmethod
    def from_json(cls, json):
        return cls(
            json['selected'],
            json['clip_limit'],
            tuple(json['tile_grid_size'])
        )

    def transform(self, images, *args, **kwargs):
        if self.selected:
            if COLOR_IMAGE in images:
                images[OUT_IMAGE] = COLOR_IMAGE
                images[COLOR_IMAGE] = self.image_service.brightness_equalizer(images[COLOR_IMAGE], self.clip_limit, self.tile_grid_size)
            else:
                raise TransformationError("Brightness equalizer transformation requires color image")
        return images

    def serialize(self):
        return {
            'name': 'BrightnessEqualizer',
            'selected': self.selected,
            'clip_limit': self.clip_limit,
            'tile_grid_size': self.tile_grid_size,
        }

    def gui(self, image_widget):
        super().gui(image_widget)
        self.group_box = QGroupBox()
        self.hbox = QHBoxLayout()
        self.group_box.setLayout(self.hbox)
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)
        self.group_box.toggled[bool].connect(self._checked_action_handler)
        self.group_box.setTitle("Brightness equalization")

        self.clip_limit_spin_box = self._create_double_spin_box(0, 1, self.clip_limit, self._clip_limit_value_changed_handler, step=0.05)

        self.tile_grid_size_spin_box = self._create_spin_box(0, 500, self.tile_grid_size[0], self._tile_grid_size_value_changed_handler)
        self.hbox.addWidget(QLabel("clip limit"))
        self.hbox.addWidget(self.clip_limit_spin_box)
        self.hbox.addWidget(QLabel("tile grid size"))
        self.hbox.addWidget(self.tile_grid_size_spin_box)
        self.hbox.addStretch()
        return self.group_box

    def _clip_limit_value_changed_handler(self, value):
        self.clip_limit = value

    def _tile_grid_size_value_changed_handler(self, value):
        self.tile_grid_size = (value, value)

