#!/usr/bin/env python3.4
import unittest
from services.storage_service import StorageService
from models.pattern import Pattern
from models.settings import Settings
import numpy as np
import cv2

class StorageServiceTest(unittest.TestCase):

    def setUp(self):
        self.storage_service = StorageService()
        self.pattern_name = 'test_pattern'
        self.pattern = self.create_pattern(self.pattern_name)
        self.settings_name = 'test_settings'
        self.settings = Settings(self.settings_name)


    def create_pattern(self, pattern_name):
        bin_image = np.random.randint(2, size=(20, 10))
        bin_image[bin_image==1] = 255
        keypoints = [
            cv2.KeyPoint(5, 5, 2, -1, 0, 0, -1),
            cv2.KeyPoint(2, 2, 1, -1, 1, 1, -1) 
        ]
        descriptors = np.random.randint(256, size=(len(keypoints), 32))
        return Pattern(pattern_name, bin_image, keypoints, descriptors)

    def test_pattern(self):
        self.storage_service.save_pattern(self.pattern, overwrite=True) 
        pattern = self.storage_service.load_pattern(self.pattern_name)
        self.assertEqual(self.pattern, pattern)


    def test_settings(self):
        self.storage_service.save_settings(self.settings, overwrite=True) 
        settings = self.storage_service.load_settings(self.settings_name)
        self.assertEqual(self.settings, settings)




