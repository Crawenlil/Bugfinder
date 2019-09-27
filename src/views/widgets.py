import cv2
from functools import partial
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QToolBox, QFrame, QGroupBox, QGraphicsView, QGraphicsScene, QLabel, QSpinBox, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtGui import QPen, QColor, QPainter, QImage, QPixmap

from image_processors import avaliable_image_processes
from image_processors.abc.image_process import ImageProcess, TYPES
from errors import TransformationError
from services.image_service import ImageService
from services.storage_service import StorageService
from models.settings import *
from decorators import wait_cursor
from matplotlib import pyplot as plt

class MainWidget(QGraphicsView):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.scene = QGraphicsScene(self)

        self.setScene(self.scene)

    def _cv2_image_to_pixmap(self):
        if self.cv2_out_image == COLOR_IMAGE:
            cv2_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2RGB)
        elif self.cv2_out_image == GRAY_IMAGE:
            cv2_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_GRAY2RGB)
        elif self.cv2_out_image == BIN_IMAGE:
            cv2_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_GRAY2RGB)
        height, width, chanels = cv2_image.shape
        return QPixmap.fromImage(QImage(cv2_image, width, height, width * chanels, QImage.Format_RGB888))

    def setImage(self, images):
        self.cv2_out_image = images[OUT_IMAGE]
        self.cv2_image = images[self.cv2_out_image]
        self.update_view()

    def update_view(self):
        self.scene.clear()
        self.scene.setSceneRect(0, 0, self.cv2_image.shape[1], self.cv2_image.shape[0])
        self.scene.addPixmap(self._cv2_image_to_pixmap())
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)


class ParametersWidget(QWidget):
    '''
    Abstract class that displays image on left pane and allows user to select image processes on right pane.
    Any class that inherits from ParametersWidget should implement draw function
    '''
    def __init__(self, parent, model):
        super().__init__()
        self.parent = parent
        self.model = model
        
        self.storage_service = StorageService()
        self.image_service = ImageService()
        self.image_widget = ImageWidget(self)
        self.model_box = self._create_model_box()

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.image_widget)
        self.hbox.addWidget(self.model_box)
        self.model_box.setMaximumWidth(550)
        self.setLayout(self.hbox)

    def setImage(self, image):
        self.cv2_image_orig = image
        self.image_widget.setImage(image)

    def draw(self, image):
        raise NotImplementedError("draw function must be implemented")


    def _create_model_box(self):
        model_frame = QFrame()
        model_vbox_layout = QVBoxLayout()
        model_frame.setLayout(model_vbox_layout)

        name_widget = self._create_name_widget()

        tool_box = self._create_image_processes_boxes()
        
        buttons_widget = self._create_buttons_widget()

        model_vbox_layout.addWidget(name_widget)
        model_vbox_layout.addWidget(tool_box)
        model_vbox_layout.addWidget(buttons_widget)
        return model_frame

    def _create_name_widget(self):
        name_widget = QWidget()
        name_hbox_layout = QHBoxLayout()
        name_widget.setLayout(name_hbox_layout)
        
        name_hbox_layout.addWidget(QLabel("{0} name".format(self.model_name.title())))
        name_text_edit = QLineEdit()
        name_text_edit.textEdited.connect(self._name_text_edited_handler)
        name_hbox_layout.addWidget(name_text_edit)
        return name_widget

    def _name_text_edited_handler(self, text):
        if text:
            self.save_button.setEnabled(True)
            self.model.name = text
            self.save_button.setToolTip("Saves {0} with given name".format(self.model_name))
        else:
            self.save_button.setEnabled(False)
            self.setToolTip("To save enter {0} name".format(self.model_name))

    def _create_image_processes_boxes(self):
        tool_box = QToolBox()
        for page in TYPES:
            qwidget = QWidget()
            vbox = QVBoxLayout()
            for image_process in self.model.transformations + self.model.splits:
                if image_process.process_type == page:
                    vbox.addWidget(image_process.gui(self.image_widget))
                
            vbox.addStretch()
            apply_button = QPushButton("Apply")
            apply_button.setToolTip("Apply changes and redraw image")
            apply_button.clicked.connect(self._apply_clicked_handler)
            hbox = QHBoxLayout()
            hbox.addStretch()
            hbox.addWidget(apply_button)
            vbox.addLayout(hbox)
            qwidget.setLayout(vbox)
            
            tool_box.addItem(qwidget, page[1]) 
        return tool_box


    def _create_buttons_widget(self):
        buttons_widget = QWidget()
        buttons_hbox_layout = QHBoxLayout()
        buttons_widget.setLayout(buttons_hbox_layout)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self._cancel_clicked_handler)
        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)
        self.save_button.setToolTip("To save enter model name")
        self.save_button.clicked.connect(self._save_clicked_handler)
        buttons_hbox_layout.addStretch()
        buttons_hbox_layout.addWidget(cancel_button)
        buttons_hbox_layout.addWidget(self.save_button)
        return buttons_widget

    def _apply_clicked_handler(self):
        #with wait_cursor():
        self.image_widget.update_view()




class SettingsWidget(ParametersWidget):
    def __init__(self, parent, model):
        self.model_name = "settings"
        super().__init__(parent, model)
    
    def draw(self, image):
        height, width = image.shape[:2]
        selected_split = self.model.selected_split()
        if selected_split:
            for line in selected_split.lines(image.shape[0], image.shape[1]):
                cv2.line(image, line[0], line[1], (255, 0, 0), 20)

    def _save_clicked_handler(self):
        self.storage_service.save_settings(self.model, overwrite=True)
        self.parent.settings_finished(self.model.name)

    def _cancel_clicked_handler(self):
        self.parent.settings_finished(None)

class PatternWidget(ParametersWidget):
    def __init__(self, parent, model):
        self.model_name = "pattern"
        super().__init__(parent, model)
    
    def draw(self, image):
        pass

    def _save_clicked_handler(self):
        images = self.transform_image()
        if images:
            self.model.keypoints, self.model.descriptors = self.image_service.extract_key_points_and_descriptors(images[GRAY_IMAGE])
            self.model.image = images[BIN_IMAGE]
            self.storage_service.save_pattern(self.model, overwrite=True)
            self.parent.pattern_finished(self.model.name)

    def _cancel_clicked_handler(self):
        self.parent.pattern_finished(None)

class ImageWidget(QGraphicsView):
    def __init__(self, parent):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.parent = parent

        self.setScene(self.scene)

    def setImage(self, cv2_image):
        self.cv2_image_orig = cv2_image
        self.transform_image()
        self.update_view()

    def update_view(self, transform=True):
        if transform:
            self.transform_image()
        self.scene.clear()
        self.scene.setSceneRect(0, 0, self.cv2_image.shape[1], self.cv2_image.shape[0])
        self.scene.addPixmap(self._cv2_image_to_pixmap())
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def _cv2_image_to_pixmap(self):
        if self.cv2_out_image == COLOR_IMAGE:
            cv2_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2RGB)
        elif self.cv2_out_image == GRAY_IMAGE:
            cv2_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_GRAY2RGB)
        elif self.cv2_out_image == BIN_IMAGE:
            cv2_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_GRAY2RGB)
        self.parent.draw(cv2_image)
        height, width, chanels = cv2_image.shape
        return QPixmap.fromImage(QImage(cv2_image, width, height, width * chanels, QImage.Format_RGB888))


    def transform_image(self):
        images = {}
        try:
            with wait_cursor():
                images = self.parent.image_service.transform_image(self.cv2_image_orig, self.parent.model)
            self.cv2_out_image = images[OUT_IMAGE]
            self.cv2_image = images[self.cv2_out_image]
        except TransformationError as e:
            message = QMessageBox(QMessageBox.Warning, "Warning", str(e))
            message.exec_()
        return images

    def resizeEvent(self, event):
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

