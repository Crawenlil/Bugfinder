import os
import sys
import shutil
import cv2
import numpy as np
import pickle
import json
from settings import *
from models.settings import Settings
from models.pattern import Pattern
from image_processors.abc.image_process import *
import importlib
import configparser

class StorageService(object):

    def __init__(self):
        self.config_parser = configparser.RawConfigParser()   

    def save_pattern(self, pattern, overwrite=False):
        directory = os.path.join(PATTERNS_DIR, pattern.name)
        if os.path.exists(directory):
            if overwrite:
                shutil.rmtree(directory)
            else:
                raise IOError("Pattern already exists")
        os.mkdir(directory)
        cv2.imwrite(os.path.join(directory, BINARY_FILENAME), pattern.image, [cv2.IMWRITE_JPEG_QUALITY, 100])
        with open(os.path.join(directory, KEYPOINTS_FILENAME), 'w') as f:
            json.dump(self._keypoints_to_json(pattern.keypoints), f)
        np.save(os.path.join(directory, DESCRIPTORS_FILENAME), pattern.descriptors)

    def load_pattern(self, name):
        directory = os.path.join(PATTERNS_DIR, name)
        pattern = Pattern(name)
        if os.path.exists(directory):
            pattern.image = cv2.imread(os.path.join(directory, BINARY_FILENAME), cv2.IMREAD_GRAYSCALE)
            with open(os.path.join(directory, KEYPOINTS_FILENAME), 'r') as f:
                pattern.keypoints = self._json_to_keypoints(json.load(f))
            pattern.descriptors = np.load(os.path.join(directory, DESCRIPTORS_FILENAME))
        return pattern

    def _keypoints_to_json(self, keypoints):
        return [{'class_id': kp.class_id, 'x': kp.pt[0], 'y': kp.pt[1], 'size': kp.size, 'angle': kp.angle, 'octave': kp.octave, 'response': kp.response} for kp in keypoints]

    def _json_to_keypoints(self, json_list):
        return [cv2.KeyPoint(kp['x'], kp['y'], kp['size'],kp['angle'], kp['response'], kp['octave'], kp['class_id']) for kp in json_list]
            
    def get_avaliable_pattern_names(self):
        return [PATTERN_COMBO_NAME] + [os.path.basename(f) for f in os.listdir(PATTERNS_DIR)]

    def get_avaliable_settings_names(self):
        return [SETTINGS_COMBO_NAME] + [os.path.basename(f) for f in os.listdir(SETTINGS_DIR)]

    def save_settings(self, settings, overwrite=False):
        settings_path = os.path.join(SETTINGS_DIR, settings.name)
        if os.path.exists(settings_path):
            if overwrite:
                os.remove(settings_path)
            else:
                raise IOError("Settings already exists")
        json_dict = {
            NAME: settings.name,
            IMAGE_PROCESSES: [image_process.serialize() for image_process in settings.image_processes()],
        }
        with open(settings_path, 'w') as f:
            json.dump(json_dict, f)

    def load_settings(self, settings_name):
        settings = None
        settings_path = os.path.join(SETTINGS_DIR, settings_name)
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                json_dict = json.load(f)
                image_processes = [ImageProcess.from_json(j) for j in json_dict[IMAGE_PROCESSES]]
                settings = Settings(settings_name, image_processes)
        return settings
            
    def next_image(self):
        self.config_parser.read(WORKDIR_PATH)
        directory = self.config_parser.get('bugfinder-config', 'processed_images_path')
        filename = sorted(os.listdir(directory))[0]
        filepath = os.path.join(directory, filename)
        img = cv2.imread(filepath, cv2.IMREAD_COLOR)
        if PROCESSED_IMAGES_PATH:
            os.rename(filepath, os.path.join(PROCESSED_IMAGES_PATH, filename))
        else:
            os.remove(filepath)
        return img


