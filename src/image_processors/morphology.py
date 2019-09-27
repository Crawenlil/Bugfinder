from settings import *
from image_processors.abc.transformation import Transformation
from errors import TransformationError
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout, QLabel, QMessageBox


class MorphologyOpening(Transformation):
    priority = 3
    process_type = BINARY
    KERNEL = 'krenel'
    def __init__(self, selected=False, kernel=(10,10)):
        super().__init__(selected)
        self.kernel = kernel

    def __eq__(self, other):
        return super().__eq__(other) and self.kernel == other.kernel
        
    @classmethod
    def from_json(cls, json):
        return cls(
            json['selected'],
            tuple(json[MorphologyOpening.KERNEL])
        )

    def transform(self, images, *args, **kwargs):
        if self.selected:
            if BIN_IMAGE in images:
                images[BIN_IMAGE] = self.image_service.morphology_opening(images[BIN_IMAGE], self.kernel)
                images[OUT_IMAGE] = BIN_IMAGE
            else:
                raise TransformationError("Morphology - opening transformation requires binary image")
        return images

    def serialize(self):
        return {
            'name': 'MorphologyOpening',
            'selected': self.selected,
            MorphologyOpening.KERNEL: self.kernel,
        }

    def gui(self, image_widget):
        super().gui(image_widget)
        self.group_box = QGroupBox()
        self.hbox = QHBoxLayout()
        self.group_box.setLayout(self.hbox)
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)
        self.group_box.toggled[bool].connect(self._checked_action_handler)
        self.group_box.setTitle("Morphology - opening")

        self.kernel_spin_box = self._create_spin_box(0, 500, self.kernel[0], self._kernel_value_changed_handler, step=1)
        self.hbox.addWidget(QLabel("kernel"))
        self.hbox.addWidget(self.kernel_spin_box)
        self.hbox.addStretch()
        return self.group_box

    def _kernel_value_changed_handler(self, value):
        self.kernel = (value, value)


class MorphologyClosing(Transformation):
    priority = 2
    process_type = BINARY
    KERNEL = 'krenel'
    def __init__(self, selected=False, kernel=(10,10)):
        super().__init__(selected)
        self.kernel = kernel
        
    def __eq__(self, other):
        return super().__eq__(other) and self.kernel == other.kernel

    @classmethod
    def from_json(cls, json):
        return cls(
            json['selected'],
            tuple(json[MorphologyOpening.KERNEL])
        )

    def transform(self, images, *args, **kwargs):
        if self.selected:
            if BIN_IMAGE in images:
                images[BIN_IMAGE] = self.image_service.morphology_closing(images[BIN_IMAGE], self.kernel)
                images[OUT_IMAGE] = BIN_IMAGE
            else:
                raise TransformationError("Morphology - closing transformation requires binary image")
        return images

    def serialize(self):
        return {
            'name': 'MorphologyClosing',
            'selected': self.selected,
            MorphologyClosing.KERNEL: self.kernel,
        }

    def gui(self, image_widget):
        super().gui(image_widget)
        self.group_box = QGroupBox()
        self.hbox = QHBoxLayout()
        self.group_box.setLayout(self.hbox)
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)
        self.group_box.toggled[bool].connect(self._checked_action_handler)
        self.group_box.setTitle("Morphology - closing")

        self.kernel_spin_box = self._create_spin_box(0, 500, self.kernel[0], self._kernel_value_changed_handler, step=1)
        self.hbox.addWidget(QLabel("kernel"))
        self.hbox.addWidget(self.kernel_spin_box)
        self.hbox.addStretch()
        return self.group_box

    def _kernel_value_changed_handler(self, value):
        self.kernel = (value, value)

    
