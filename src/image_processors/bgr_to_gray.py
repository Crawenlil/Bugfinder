from settings import *
from errors import TransformationError
from image_processors.abc.transformation import Transformation
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout, QLabel, QMessageBox

class BgrToGray(Transformation):
    priority = 1
    process_type = GRAY
    def __init__(self, selected=False):
        super().__init__(selected)

    @classmethod
    def from_json(cls, json):
        return cls(
            json['selected']
        )

    def transform(self, images, *args, **kwargs):
        if self.selected:
            if COLOR_IMAGE in images:
                images[OUT_IMAGE] = GRAY_IMAGE
                images[GRAY_IMAGE] = self.image_service.bgr_to_gray(images[COLOR_IMAGE])
            else:
                raise TransformationError("RGB to gray transformation requires color image")
        return images

    def serialize(self):
        return {
            'name': 'BgrToGray',
            'selected': self.selected,
        }
    
    def gui(self, image_widget):
        super().gui(image_widget)
        self.widget = QWidget()
        self.hbox = QHBoxLayout()
        self.selected_checkbox = QCheckBox()
        self.selected_checkbox.setText("RGB to gray")
        self.selected_checkbox.stateChanged[int].connect(self.selected_action_handler)
        self.hbox.addWidget(self.selected_checkbox)
        self.widget.setLayout(self.hbox)
        return self.widget
    
    def selected_action_handler(self, value):
        self.selected = value == 2 # 2 is checked, 0 is unchecked

