from settings import *
from image_processors.abc.transformation import Transformation
from errors import TransformationError
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout, QLabel, QMessageBox

class LinearScaling(Transformation):
    priority = 3
    process_type = COLOR
    def __init__(self, selected=False, alpha=1.5, beta=50):
        super().__init__(selected)
        self.alpha = alpha
        self.beta = beta

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and self.alpha == other.alpha
            and self.beta == other.beta
        )
        
    @classmethod
    def from_json(cls, json):
        return cls(
            json['selected'],
            json['alpha'],
            json['beta']
        )

    def transform(self, images, *args, **kwargs):
        if self.selected:
            if COLOR_IMAGE in images:
                images[COLOR_IMAGE] = self.image_service.linear_scaling(images[COLOR_IMAGE], self.alpha, self.beta)
                images[OUT_IMAGE] = COLOR_IMAGE
            else:
                raise TransformationError("Contrast and brightness transformation requires color image")
        return images

    def serialize(self):
        return {
            'name': 'LinearScaling',
            'selected': self.selected,
            'alpha': self.alpha,
            'beta': self.beta,
        }

    def gui(self, image_widget):
        super().gui(image_widget)
        self.group_box = QGroupBox()
        self.hbox = QHBoxLayout()
        self.group_box.setLayout(self.hbox)
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)
        self.group_box.toggled[bool].connect(self._checked_action_handler)
        self.group_box.setTitle("Contrast and brightness")

        self.alpha_spin_box = self._create_double_spin_box(0, 2, self.alpha, self._alpha_value_changed_handler, step=0.1)
        self.beta_spin_box = self._create_spin_box(0, 100, self.beta, self._beta_value_changed_handler)

        self.hbox.addWidget(QLabel("alpha"))
        self.hbox.addWidget(self.alpha_spin_box)
        self.hbox.addWidget(QLabel("beta"))
        self.hbox.addWidget(self.beta_spin_box)
        self.hbox.addStretch()
        return self.group_box

    def _alpha_value_changed_handler(self, value):
        self.alpha = value

    def _beta_value_changed_handler(self, value):
        self.beta = value
