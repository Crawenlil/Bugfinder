# -*- coding: utf-8 -*-
import os
import cv2
from views.widgets import MainWidget, SettingsWidget, PatternWidget
from services.image_service import ImageService
from services.storage_service import StorageService
from settings import *
from models.settings import Settings
from models.pattern import Pattern
from decorators import wait_cursor

from PyQt5.QtWidgets import QMainWindow, QWidget, QMenuBar, QMenu, QAction, QToolBar, QStackedWidget, QFileDialog, QComboBox, QColorDialog, QLabel
from PyQt5.QtGui import QIcon, QColor

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.showMaximized()
        self.image_service = ImageService()
        self.storage_service = StorageService()
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.showMaximized()

        self.main_widget = MainWidget(self)
        self.settings_widget = SettingsWidget(self, Settings())
        self.pattern_widget = PatternWidget(self, Pattern())

        self.stacked_widget.addWidget(self.main_widget)
        self.stacked_widget.addWidget(self.pattern_widget)
        self.stacked_widget.addWidget(self.settings_widget)

        self.setCentralWidget(self.stacked_widget)

        self.selected_pattern_name = None
        self.selected_settings_name = None
        self.pattern = None
        self.settings = None
        self._create_actions()
        self._set_menu_bar()
        self._set_tool_bar()
        self.errors_color = QColor(255,0,0)

    def _create_actions(self):
        self.new_pattern_action = QAction(QIcon(os.path.join(ICONS_DIR, 'add.png')), "New pattern", self)
        self.new_pattern_action.triggered.connect(self._new_pattern_action_handler)

        self.new_settings_action = QAction(QIcon(os.path.join(ICONS_DIR, 'settings.png')), "New settings", self)
        self.new_settings_action.triggered.connect(self._new_settings_action_handler)

        self.next_image_action = QAction(QIcon(os.path.join(ICONS_DIR, 'next')), "Next image", self)
        self.next_image_action.triggered.connect(self._next_image_action_handler)
        self.next_image_action.setEnabled(False)

        self.errors_color_action = QAction(QIcon(os.path.join(ICONS_DIR, 'color.png')), "Errors marker", self)
        self.errors_color_action.triggered.connect(self._errors_color_action_handler)

        self.exit_action = QAction('Exit', self)
        self.exit_action.triggered.connect(self.app.quit)


    def _create_pattern_combo(self):
        self.pattern_combo = QComboBox(self)
        avaliable_pcbs = self.storage_service.get_avaliable_pattern_names()
        for name in avaliable_pcbs:
            self.pattern_combo.addItem(name)

        self.pattern_combo.activated[str].connect(self._selected_pattern_action_handler)

    def _create_settings_combo(self):
        self.settings_combo = QComboBox(self)
        avaliable_settings_names = self.storage_service.get_avaliable_settings_names()
        for name in avaliable_settings_names:
            self.settings_combo.addItem(name)

        self.settings_combo.activated[str].connect(self._selected_settings_action_handler)

    def _set_menu_bar(self):
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu('File')

        menu_file.addAction(self.new_pattern_action)
        menu_file.addAction(self.exit_action)

    def _set_tool_bar(self):
        self._create_pattern_combo()
        self._create_settings_combo()
        self.tool_bar = self.addToolBar('Tools')
    
        self.tool_bar.addWidget(self.pattern_combo)
        self.tool_bar.addAction(self.new_pattern_action)
        self.tool_bar.addSeparator()

        self.tool_bar.addWidget(self.settings_combo)
        self.tool_bar.addAction(self.new_settings_action)
        self.tool_bar.addAction(self.errors_color_action)
        self.tool_bar.addSeparator()

        self.tool_bar.addAction(self.next_image_action)

    def _new_pattern_action_handler(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["All Files (*)", "Images (*.png *.jpg)"])
        file_dialog.selectNameFilter("Images (*.png *.jpg)")
        if file_dialog.exec_():
            filename = file_dialog.selectedFiles()[0]
            with wait_cursor():
                image_orig = cv2.imread(filename, cv2.IMREAD_COLOR)
                self.stacked_widget.removeWidget(self.pattern_widget)
                self.settings_widget = PatternWidget(self, Pattern())
                self.stacked_widget.addWidget(self.pattern_widget)
                self.stacked_widget.setCurrentWidget(self.pattern_widget)
                self.pattern_widget.setImage(image_orig) 
                self.pattern_widget.update()

    def _new_settings_action_handler(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["All Files (*)", "Images (*.png *.jpg)"])
        file_dialog.selectNameFilter("Images (*.png *.jpg)")
        if file_dialog.exec_():
            filename = file_dialog.selectedFiles()[0]
            with wait_cursor():
                image_orig = cv2.imread(filename, cv2.IMREAD_COLOR)
                self.stacked_widget.removeWidget(self.settings_widget)
                self.settings_widget = SettingsWidget(self, Settings())
                self.stacked_widget.addWidget(self.settings_widget)
                self.stacked_widget.setCurrentWidget(self.settings_widget)
                self.settings_widget.setImage(image_orig) 
                self.settings_widget.update()

    def _next_image_action_handler(self):
        #all requirements met, don't check again
        image_orig = self.storage_service.next_image()
        if image_orig != None:
            with wait_cursor():
                images = self.image_service.transform_image(image_orig, self.settings)
                images = self.image_service.compare(self.pattern, images, self.settings)
                bgr = [
                    self.errors_color.blue(),
                    self.errors_color.green(),
                    self.errors_color.red()
                ]
                images = self.image_service.mark_errors(images, bgr)
                self.stacked_widget.removeWidget(self.main_widget)
                self.main_widget = MainWidget(self)
                self.stacked_widget.addWidget(self.main_widget)
                self.stacked_widget.setCurrentWidget(self.main_widget)
                self.main_widget.setImage(images)

    def _errors_color_action_handler(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.errors_color = color

    def _selected_pattern_action_handler(self, name):
        self.selected_pattern_name = name
        self.pattern = self.storage_service.load_pattern(self.selected_pattern_name)
        self._toggle_next_image_action()
    
    def _selected_settings_action_handler(self, name):
        self.selected_settings_name = name
        self.settings = self.storage_service.load_settings(self.selected_settings_name)    
        self._toggle_next_image_action()

    def _toggle_next_image_action(self):
        if self.selected_pattern_name and self.selected_pattern_name != PATTERN_COMBO_NAME and self.selected_settings_name and self.selected_settings_name != SETTINGS_COMBO_NAME:
            self.next_image_action.setEnabled(True)
        else:
            self.next_image_action.setEnabled(False)

    ### PUBLIC METHODS ###

    def pattern_finished(self, pattern_name):
        if pattern_name:
            self.pattern_combo.clear()
            avaliable_pattern_names = self.storage_service.get_avaliable_pattern_names()
            for name in avaliable_pattern_names:
                self.pattern_combo.addItem(name)
            index = self.pattern_combo.findText(pattern_name);
            self.pattern_combo.setCurrentIndex(index)
            self.selected_pattern_name = pattern_name
            self._toggle_next_image_action()
        self.stacked_widget.setCurrentWidget(self.main_widget)

    def settings_finished(self, settings_name):
        if settings_name:
            self.settings_combo.clear()
            avaliable_settings_names = self.storage_service.get_avaliable_settings_names()
            for name in avaliable_settings_names:
                self.settings_combo.addItem(name)
            index = self.settings_combo.findText(settings_name);
            self.settings_combo.setCurrentIndex(index)
            self.selected_settings_name = name
            self._toggle_next_image_action()
        self.stacked_widget.setCurrentWidget(self.main_widget)
