from settings import *
from image_processors.abc.transformation import Transformation
from errors import TransformationError
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout, QLabel, QMessageBox

class Clip(Transformation):
    priority = 1
    process_type = CLIP
    def __init__(self, selected=False, gaussian_blur=(15, 15), lower_h=15, lower_s=0, lower_v=0, upper_h=165, upper_s=255, upper_v=255, canny_min=100, canny_max=100):
        super().__init__(selected)
        self.gaussian_blur = gaussian_blur
        self.lower_h = lower_h
        self.lower_s = lower_s
        self.lower_v = lower_v
        self.upper_h = upper_h
        self.upper_s = upper_s
        self.upper_v = upper_v
        self.canny_min = canny_min
        self.canny_max = canny_max

    def __eq__(self, other):
        return (super().__eq__(other) 
            and self.gaussian_blur == other.gaussian_blur
            and self.lower_h == other.lower_h
            and self.lower_s == other.lower_s
            and self.lower_v == other.lower_v
            and self.upper_h == other.upper_h
            and self.upper_s == other.upper_s
            and self.upper_v == other.upper_v
            and self.canny_min == other.canny_min
            and self.canny_max == other.canny_max
        )
        
    @classmethod
    def from_json(cls, json):
        return cls(
            json['selected'],
            tuple(json['gaussian_blur']),
            json['lower_h'],
            json['lower_s'],
            json['lower_v'],
            json['upper_h'],
            json['upper_s'],
            json['upper_v'],
            json['canny_min'],
            json['canny_max'],
        )

    def transform(self, images, *args, **kwargs):
        if self.selected:
            if COLOR_IMAGE in images:
                images[COLOR_IMAGE] = self.image_service.clip_and_rotate(
                    images[COLOR_IMAGE],
                    self.gaussian_blur,
                    (self.lower_h, self.lower_s, self.lower_v),
                    (self.upper_h, self.upper_s, self.upper_v),
                    self.canny_min,
                    self.canny_max
                )
                images[OUT_IMAGE] = COLOR_IMAGE
                images[CLIPPED_IMAGE] = images[COLOR_IMAGE]
            else:
                raise TransformationError("Clip requires color image")
        return images
   

    def serialize(self):
        return {
            'name': 'Clip',
            'selected': self.selected,
            'gaussian_blur': self.gaussian_blur,
            'lower_h': self.lower_h,
            'lower_s': self.lower_s,
            'lower_v': self.lower_v,
            'upper_h': self.upper_h,
            'upper_s': self.upper_s,
            'upper_v': self.upper_v,
            'canny_min': self.canny_min,
            'canny_max': self.canny_max,
        }

    def gui(self, image_widget):
        super().gui(image_widget)
        self.group_box = QGroupBox()
        self.grid_layout = QGridLayout()
        self.group_box.setLayout(self.grid_layout)
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)
        self.group_box.toggled[bool].connect(self._checked_action_handler)
        self.group_box.setTitle("Clip")

        self.gaussian_blur_spin_box = self._create_spin_box(0, 100, self.gaussian_blur[0], self._gaussian_blur_value_changed_handler, step=2)

        self.lower_h_spin_box = self._create_spin_box(0, 255, self.lower_h, self._lower_h_value_changed_handler)  
        self.lower_s_spin_box = self._create_spin_box(0, 255, self.lower_s, self._lower_s_value_changed_handler) 
        self.lower_v_spin_box = self._create_spin_box(0, 255, self.lower_v, self._lower_v_value_changed_handler) 
        self.upper_h_spin_box = self._create_spin_box(0, 255, self.upper_h, self._upper_h_value_changed_handler) 
        self.upper_s_spin_box = self._create_spin_box(0, 255, self.upper_s, self._upper_s_value_changed_handler) 
        self.upper_v_spin_box = self._create_spin_box(0, 255, self.upper_v, self._upper_v_value_changed_handler) 

        self.canny_min_spin_box = self._create_spin_box(0, 1000, self.canny_min, self._canny_min_value_changed_handler)
        self.canny_max_spin_box = self._create_spin_box(0, 1000, self.canny_max, self._canny_max_value_changed_handler)

        self._set_grid_row(self.grid_layout, 0, 0, "Gaussian blur", "Higher value means more blurred effect", self.gaussian_blur_spin_box)
        self._set_grid_row(self.grid_layout, 0, 2, "Canny min", "Canny lower threshold value", self.canny_min_spin_box)
        self._set_grid_row(self.grid_layout, 0, 4, "Canny max", "Canny lower threshold value", self.canny_max_spin_box)
        self._set_grid_row(self.grid_layout, 1, 0, "Lower hue", "Lower hue for image filtering", self.lower_h_spin_box)
        self._set_grid_row(self.grid_layout, 1, 2, "Lower saturation", "Lower saturation for image filtering", self.lower_s_spin_box)
        self._set_grid_row(self.grid_layout, 1, 4, "Lower value", "Lower value for image filtering", self.lower_v_spin_box)
        self._set_grid_row(self.grid_layout, 2, 0, "Upper hue", "Upper hue for image filtering", self.upper_h_spin_box)
        self._set_grid_row(self.grid_layout, 2, 2, "Upper saturation", "Upper saturation for image filtering", self.upper_s_spin_box)
        self._set_grid_row(self.grid_layout, 2, 4, "Upper value", "Upper value for image filtering", self.upper_v_spin_box)

        return self.group_box

    def _gaussian_blur_value_changed_handler(self, value):
        self.gaussian_blur = (value, value)

    def _lower_h_value_changed_handler(self, value):
        self.lower_h = value

    def _lower_s_value_changed_handler(self, value):
        self.lower_s = value

    def _lower_v_value_changed_handler(self, value):
        self.lower_v = value

    def _upper_h_value_changed_handler(self, value):
        self.upper_h = value

    def _upper_s_value_changed_handler(self, value):
        self.upper_s = value

    def _upper_v_value_changed_handler(self, value):
        self.upper_v = value

    def _canny_min_value_changed_handler(self, value):
        self.canny_min = value

    def _canny_max_value_changed_handler(self, value):
        self.canny_max = value
