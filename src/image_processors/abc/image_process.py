from settings import *
import importlib 
import pkgutil
from services.image_service import ImageService
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout, QLabel, QMessageBox
import image_processors

TYPES = [CLIP, COLOR, GRAY, BINARY, SPLIT]



class ImageProcess(object):
    SELECTED = 'selected'
    def __init__(self, selected):
        self.image_service = ImageService()
        self.selected = selected

    def __eq__(self, other):
        return self.selected == other.selected

    @classmethod
    def from_json(cls, json):
        for importer, name, ispkg in pkgutil.iter_modules(image_processors.__path__):
            module = importlib.import_module('image_processors.{0}'.format(name))
            image_process_class = getattr(module, json['name'], None)
            if image_process_class:
                return image_process_class.from_json(json)
                                                                                                      
    def process(self, images, *args, **kwargs):
        ''' 
        Images is a dict of images, override it's content only if necesary, might be usefull for other functions later.
        In image_out is stored pointer to output image, should be updated by each transformation.
        TODO: make it class -> list of images + attribute with image_out
        '''
        raise NotImplementedError("process method must be implemented")

    def serialize(self):
        raise NotImplementedError("serialize method must be implemented")

    def gui(self, image_widget):
        self.image_widget = image_widget

    def _checked_action_handler(self, checked):
        self.selected = checked

    def _create_double_spin_box(self, minimum, maximum, value, handler, step=1, suffix=''):
        spin_box = QDoubleSpinBox()
        spin_box.setMinimum(minimum)
        spin_box.setMaximum(maximum)
        spin_box.setValue(value)
        spin_box.setSingleStep(step)
        spin_box.setSuffix(suffix)
        spin_box.valueChanged[float].connect(handler)
        return spin_box

    def _create_spin_box(self, minimum, maximum, value, handler, step=1, suffix=''):
        spin_box = QSpinBox()
        spin_box.setMinimum(minimum)
        spin_box.setMaximum(maximum)
        spin_box.setValue(value)
        spin_box.setSingleStep(step)
        spin_box.setSuffix(suffix)
        spin_box.valueChanged[int].connect(handler)
        return spin_box

    def _set_grid_row(self, grid_layout, row, col, label, tooltip, widget):
        qlabel = QLabel(label)
        qlabel.setToolTip(tooltip)
        grid_layout.addWidget(QLabel(label), row, col)
        grid_layout.addWidget(widget, row, col+1)

