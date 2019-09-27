import unittest
from services.image_service import ImageService
import numpy as np
import cv2

class ImageServiceTest(unittest.TestCase):

    def setUp(self):
        self.image_service = ImageService()
        self.color_rand_image = np.random.randint(256, size=(20, 20, 3)).astype(np.uint8)
        self.gray_rand_image = np.random.randint(256, size=(20, 20)).astype(np.uint8)
        self.bin_rand_image = np.random.randint(2, size=(20, 20)).astype(np.uint8)
        self.bin_rand_image[self.bin_rand_image == 1] = 255

        self.color_image=np.array([[[1,1,1], [1,1,1], [1,1,1]],
                                   [[2,2,2], [2,2,2], [2,2,2]],
                                   [[3,3,3], [3,3,3], [3,3,3]]]).astype(np.uint8)

        


    def test_brightness_eqalizer(self):
        img = self.image_service.brightness_equalizer(self.color_rand_image)
        self.assertEqual(img.shape, self.color_rand_image.shape)

    def test_linear_scaling(self):
        img = self.image_service.linear_scaling(self.color_image, 0, 0)
        np.testing.assert_equal(img, np.zeros(self.color_image.shape))

        img = self.image_service.linear_scaling(self.color_image, 1, 0)
        np.testing.assert_equal(img, self.color_image)

        img = self.image_service.linear_scaling(self.color_image, 2, 0)
        np.testing.assert_equal(img, self.color_image * 2)

        img = self.image_service.linear_scaling(self.color_image, 1, 10)
        np.testing.assert_equal(img, self.color_image + 10)

        img = self.image_service.linear_scaling(self.color_image, 1, 500)
        np.testing.assert_equal(img, np.full((3,3,3), 255, dtype=np.uint8))

    def test_otsu_binarization(self):
        self.assertFalse(np.all(np.in1d(self.gray_rand_image, [0, 255])))
        img = self.image_service.otsu_binarization(self.gray_rand_image)
        self.assertTrue(np.all(np.in1d(img, [0, 255])))

    def test_remove_background(self):
        red_image = np.array([[[0,0,255], [1,1,255], [2,2,255]],
                              [[3,3,255], [255,5,255], [4,4,255]],
                              [[5,5,255], [6,6,255], [7,7,255]]]).astype(np.uint8)
        expected_result = np.array([[[0,0,0], [0,0,0], [0,0,0]],
                                   [[0,0,0], [255,5,255], [0,0,0]],
                                   [[0,0,0], [0,0,0], [0,0,0]]]).astype(np.uint8)
        
        img = self.image_service.remove_background(red_image, (15, 0, 0), (165, 255,255))
        np.testing.assert_equal(img, expected_result)

    def test_clip_to_box(self):
        image = np.arange(300, dtype=np.uint8).reshape((10,10,3))
        result = np.array([[[50, 51, 52], [53, 54, 55], [56, 57, 58]],
                           [[80, 81, 82], [83, 84, 85], [86, 87, 88]],
                           [[110, 111, 112], [113, 114, 115], [116, 117, 118]]], dtype=np.uint8)
        box = np.array([[1,1], [4, 4], [1,4], [4,1]])
        img = self.image_service.clip_to_frame(image, box)

        np.testing.assert_equal(img, result)

    def test_add_affine_transform(self):
        M1 = np.array([[1,0,10], [0,1,5]])
        M2 = np.array([[1,0,5], [0,1,5]])
        M3 = np.array([[1,0,15], [0,1,10]])
        np.testing.assert_equal(self.image_service.add_affine_transform(M1, M2), M3)




        






