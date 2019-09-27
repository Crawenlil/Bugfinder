from settings import *
from image_processors.abc.transformation import Transformation
from errors import TransformationError
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout, QLabel, QMessageBox

class GaussianBlur(Transformation):
    priority = 2
    process_type = GRAY
    KERNEL = 'krenel'
    def __init__(self, selected=False, kernel=(25,25)):
        super().__init__(selected)
        self.kernel = kernel

    def __eq__(self, other):
        return super().__eq__(other) and self.kernel==other.kernel
        
    @classmethod
    def from_json(cls, json):
        return cls(
            json['selected'],
            tuple(json['kernel'])
        )

    def transform(self, images, *args, **kwargs):
        if self.selected:
            if GRAY_IMAGE in images:
                images[GRAY_IMAGE] = self.image_service.gaussian_blur(images[GRAY_IMAGE], self.kernel)
                images[OUT_IMAGE] = GRAY_IMAGE
            else:
                raise TransformationError("Gaussian blur requires transformation grayscale image")
                
        return images

    def serialize(self):
        return {
            'name': 'GaussianBlur',
            'selected': self.selected,
            'kernel': self.kernel,
        }

    def gui(self, image_widget):
        super().gui(image_widget)
        self.group_box = QGroupBox()
        self.hbox = QHBoxLayout()
        self.group_box.setLayout(self.hbox)
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)
        self.group_box.toggled[bool].connect(self._checked_action_handler)
        self.group_box.setTitle("Gaussian blur")

        self.kernel_spin_box = self._create_spin_box(0, 500, self.kernel[0], self._kernel_value_changed_handler, step=2)

        self.hbox.addWidget(QLabel("kernel"))
        self.hbox.addWidget(self.kernel_spin_box)
        self.hbox.addStretch()
        return self.group_box

    def _kernel_value_changed_handler(self, value):
        self.kernel = (value, value)
