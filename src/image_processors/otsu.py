from settings import *
from image_processors.abc.transformation import Transformation
from errors import TransformationError
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout, QLabel, QMessageBox

class OtsuBinarization(Transformation):
    priority = 1
    process_type = BINARY
    def __init__(self, selected=False):
        super().__init__(selected)
        
    @classmethod
    def from_json(cls, json):
        return cls(
            json['selected'],
        )

    def transform(self, images, *args, **kwargs):
        if self.selected:
            if GRAY_IMAGE in images:
                images[OUT_IMAGE] = BIN_IMAGE
                images[BIN_IMAGE] = self.image_service.otsu_binarization(images[GRAY_IMAGE])
            else:
                raise TransformationError("Otsu binarization requires grayscale image")
        return images

    def serialize(self):
        return {
            'name': 'OtsuBinarization',
            'selected': self.selected,
        }

    def gui(self, image_widget):
        super().gui(image_widget)
        self.widget = QWidget()
        self.hbox = QHBoxLayout()
        self.selected_checkbox = QCheckBox()
        self.selected_checkbox.setText("Otsu")
        self.selected_checkbox.stateChanged[int].connect(self.selected_action_handler)
        self.hbox.addWidget(self.selected_checkbox)
        self.widget.setLayout(self.hbox)
        return self.widget
    
    def selected_action_handler(self, value):
        self.selected = value == 2 # 2 is checked, 0 is unchecked
