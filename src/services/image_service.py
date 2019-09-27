import cv2
import numpy as np
from matplotlib import pyplot as plt
from math import sqrt
from settings import *

from errors import TransformationError


class ImageService:
    def __init__(self):
        self.detector = cv2.ORB_create(nfeatures=10000)
        #self.detector = cv2.xfeatures2d.SIFT_create()

    def bgr_to_gray(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def brightness_equalizer(self, bgr_image, clip_limit=0.7, tile_grid_size=(10,10)):
        lab_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab_image)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l = clahe.apply(l)
        lab_image = cv2.merge((l,a,b))
        return cv2.cvtColor(lab_image, cv2.COLOR_LAB2BGR)

    def linear_scaling(self, image, alpha, beta):
        '''
        Alpha - contrast controll, set 1.0 to 2.0 
        Beta - brightnewss control, set 0 to 100
        '''
        img = image.astype(np.float32, copy=False)
        img *= alpha
        img += beta
        np.clip(img, 0, 255, out=img)
        img = img.astype(np.uint8, copy=False)
        return img

    def gaussian_blur(self, image, kernel=(5,5)):
        if kernel[0] % 2 == 0 or kernel[1] % 2 == 0:
            raise TransformationError("Gaussian kernel must have odd dimension")
        return cv2.GaussianBlur(image, kernel, 0)

    def otsu_binarization(self, image, inv_binary_thresh=False):
        thresh = cv2.THRESH_BINARY_INV if inv_binary_thresh else cv2.THRESH_BINARY
        _, img = cv2.threshold(image, 0, 255, thresh + cv2.THRESH_OTSU)
        return img

    def extract_key_points_and_descriptors(self, image):
        kp, des = self.detector.detectAndCompute(image, None)
        return kp, des

    def clip_and_rotate(self, image, gaussian_blur=(15,15), lower=(15,0,0), upper=(165,255,255), canny_min=100, canny_max=100):
        img = self.remove_background(image, lower, upper)
        gray = self.bgr_to_gray(img)
        gray_blurred = self.gaussian_blur(gray, gaussian_blur)
        rectangle = self.find_rectangle(gray_blurred, canny_min, canny_max)
        box = cv2.boxPoints(rectangle)
        M, width, height = self.rotate_and_translate_affine(img, rectangle[2])
        image = cv2.warpAffine(image, M, (width, height))
        box = cv2.transform(np.array([box]), M)[0]
        image = self.clip_to_frame(image, box)
        return image
        

    def remove_background(self, image, lower, upper):
        img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([lower])
        upper = np.array([upper])
        mask = cv2.inRange(img, lower, upper)
        img = cv2.bitwise_and(img, img, mask=mask)
        return cv2.cvtColor(img, cv2.COLOR_HSV2BGR)


    def find_rectangle(self, gray, cannyMinValue, cannyMaxValue):
        edges = cv2.Canny(gray,cannyMinValue, cannyMaxValue)
        hull = cv2.convexHull(np.column_stack((np.nonzero(edges)[::-1])).reshape(-1,1,2).astype(np.int32)) # get x, y vectors of non zero points, stack them into array
        rect = cv2.minAreaRect(hull) 
        return rect

    def rotate_and_translate_affine(self, image, angle):
        h,w = image.shape[:2]
        if h > w and abs(angle) < 45:
            angle += 90
        center = (w//2, h//2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
 
        M[0, 2] += (nW / 2) - center[0]
        M[1, 2] += (nH / 2) - center[1]
        return M, nW, nH

    def clip_to_frame(self, image, box):
        xs, ys = box[:,0], box[:,1]
        x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)
        size = (x2 - x1, y2 - y1)
        center = x1 + size[0] /2, y1 + size[1]/2
        return cv2.getRectSubPix(image, size, center)


    def ransac(self, pts1, pts2, iters=100, maxerror=5):
        '''
        pts1 - source image points, Nx1x2
        pts2 - destination image points, Nx1x2
        iters - number of ransac iterations
        maxerror - max distance in pixels between points
        '''

        def calculate_model(s_indexes):
            result = None
            try:
                s_index_1, s_index_2, s_index_3 = s_indexes
                x1,y1 = pts1[s_index_1]
                u1,v1 = pts2[s_index_1]
                x2,y2 = pts1[s_index_2]
                u2,v2 = pts2[s_index_2]
                x3,y3 = pts1[s_index_3]
                u3,v3 = pts2[s_index_3]
                tmp = np.matrix([[x1,y1,1,0,0,0],
                                 [x2,y2,1,0,0,0],
                                 [x3,y3,1,0,0,0],
                                 [0,0,0,x1,y1,1],
                                 [0,0,0,x2,y2,1],
                                 [0,0,0,x3,y3,1]]).I
                tmp = tmp * np.matrix([u1,u2,u3,v1,v2,v3]).T
                result = np.array([[tmp.item(0), tmp.item(1), tmp.item(2)],
                                  [tmp.item(3), tmp.item(4), tmp.item(5)]])
            except np.linalg.LinAlgError:
                pass
            return result

        def model_error(model, i):
            x1,y1 = pts1[i]
            x2,y2 = pts2[i] 
            p1 = model.dot(np.array([[x1],[y1],[1]]))
            p2 = np.array([[x2],[y2]])
            return np.linalg.norm(p1-p2)

        #RANSAC
        pts_size = pts1.shape[0]
        bestmodel = None
        bestscore = 0
        for i in range(iters):
            model = None
            while model is None:
                s_indexes = np.random.choice(pts_size, 3, replace=False)
                model = calculate_model(s_indexes)
            score = 0
            for p in range(pts_size):
                error = model_error(model, p)
                if error < maxerror:
                    score += 1
            if score > bestscore:
                bestscore = score
                bestmodel = model
        return bestmodel



    def add_affine_transform(self, M, newM):
        ''' result = newM.dot(M) '''
        # We need to add [0,0,1] row to make 2x3 matrices 3x3, then after multiplying return again 2x3
        return np.vstack([newM, [0,0,1]]).dot(np.vstack([M, [0,0,1]]))[:2] 

    def morphology_closing(self, image, kernel):
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, np.ones((kernel), np.uint8))

    def morphology_opening(self, image, kernel):
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, np.ones((kernel), np.uint8))


    def extract_matches(self, des1, des2):
        index_params= dict(
            algorithm = 6, # FLANN_INDEX_LSH
            table_number = 12, # 6
            key_size = 20,     # 12
            multi_probe_level = 2 # 1
        )

        search_params = dict(checks=50)  

        flann = cv2.FlannBasedMatcher(index_params,search_params)
        all_matches = flann.knnMatch(des1, des2, k=2)

        all_matches = filter(lambda pair: len(pair) == 2, all_matches)
        matches = []
        for m,n in all_matches:
            if m.distance < 0.7*n.distance:
                matches.append(m)
        return matches

    def transform_image(self, image, model):
        images = {
            COLOR_IMAGE: image,
            CLIPPED_IMAGE: image,
            OUT_IMAGE: COLOR_IMAGE
        }
        for transformation in model.transformations:
            images = transformation.transform(images) 
        return images

    def compare(self, pattern, images, settings):
        frame_height, frame_width = images[COLOR_IMAGE].shape[:2]
        frame_mask = np.zeros((frame_height, frame_width), np.uint8)
        pattern_height, pattern_width = pattern.image.shape[0:2]
        selected_split = settings.selected_split()
        points = selected_split.split(images) if selected_split else [(0, frame_height, 0, frame_width)]
        for y1, y2, x1, x2 in points:
            pcb_gray =  np.array(images[GRAY_IMAGE][y1:y2, x1:x2])
            pcb_bin =  np.array(images[BIN_IMAGE][y1:y2, x1:x2])
            pcb_height, pcb_width = pcb_gray.shape[0:2]

            

            pcb_keypoints, pcb_descriptors = self.extract_key_points_and_descriptors(pcb_gray)
            matches = self.extract_matches(pattern.descriptors, pcb_descriptors)
            #img3 = cv2.drawMatches(pattern.image,pattern.keypoints,pcb_bin,pcb_keypoints,matches, flags=2, outImg = None)
            #plt.imshow(img3), plt.show()
            pattern_points = np.float32([pattern.keypoints[m.queryIdx].pt for m in matches]).reshape(-1,2)
            pcb_points = np.float32([pcb_keypoints[m.trainIdx].pt for m in matches]).reshape(-1,2)

            M_pcb_translate = np.float32([[1,0,x1], [0,1,y1]])
            M_pcb_to_pattern = self.ransac(pcb_points, pattern_points, iters=1000, maxerror=2)
            M_pattern_to_pcb = cv2.invertAffineTransform(M_pcb_to_pattern)
            M_xor_to_frame = self.add_affine_transform(M_pattern_to_pcb, M_pcb_translate)

            transformed_pcb = cv2.warpAffine(pcb_bin, M_pcb_to_pattern, (pattern_width, pattern_height))
            _, transformed_pcb = cv2.threshold(transformed_pcb, 127, 255, cv2.THRESH_BINARY)
            #plt.subplot(1,3,1)
            #plt.title("Orig"), plt.imshow(pcb_bin, 'gray', interpolation='none')
            #plt.subplot(1,3,2)
            #plt.title("transformed_pcb"), plt.imshow(transformed_pcb, 'gray', interpolation='none')
            #plt.subplot(1,3,3)
            #plt.title("pattern"), plt.imshow(pattern.image, 'gray', interpolation='none'), plt.show()

            xor_img = cv2.bitwise_xor(transformed_pcb, pattern.image)
            frame_mask = cv2.bitwise_or(cv2.warpAffine(xor_img, M_xor_to_frame, (frame_width, frame_height)), frame_mask)

        _, frame_mask = cv2.threshold(frame_mask, 127, 255, cv2.THRESH_BINARY)

        #plt.title("After xor"), plt.imshow(frame_mask, 'gray', interpolation='none'), plt.show()

        frame_mask = self.morphology_opening(frame_mask, (20, 20))
        #plt.title("After morphology"), plt.imshow(frame_mask, 'gray', interpolation='none'), plt.show()

        images[OUT_IMAGE] = BIN_IMAGE
        images[BIN_IMAGE] = frame_mask
        return images


    def mark_errors(self, images, color):

        def circle(kernel_size):
            assert kernel_size % 2 == 1
            circle_kernel = np.zeros((kernel_size, kernel_size), np.uint8)
            center = kernel_size / 2
            y, x = np.ogrid[-center:center+1, -center:center+1]
            index = x**2 + y**2 <= center**2
            circle_kernel[:,:][index] = 255
            return circle_kernel

        # plt.title("Bin image"), plt.imshow(images[BIN_IMAGE], 'gray', interpolation='none'), plt.show()
        outlines = cv2.dilate(images[BIN_IMAGE], circle(101), iterations=1)
        # plt.title("Dialate"), plt.imshow(outlines, 'gray', interpolation='none'), plt.show()
        outlines = cv2.morphologyEx(outlines, cv2.MORPH_GRADIENT, circle(41)) #difference between dialation and erosion
        outlines_inv = cv2.bitwise_not(outlines)
        # plt.title("Outlines_inv"), plt.imshow(outlines_inv, 'gray', interpolation='none'), plt.show()
        color_image = images[CLIPPED_IMAGE]
        color_image = cv2.bitwise_and(color_image, color_image, mask=outlines_inv)
        # plt.title("Color image"), plt.imshow(cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)), plt.show()
        red_outlines = cv2.cvtColor(outlines, cv2.COLOR_GRAY2BGR)
        # plt.title("Red outlines 1"), plt.imshow(cv2.cvtColor(red_outlines, cv2.COLOR_BGR2RGB)), plt.show()
        red_outlines[np.where(outlines==255)] = color
        # plt.title("Red outlines 2"), plt.imshow(cv2.cvtColor(red_outlines, cv2.COLOR_BGR2RGB)), plt.show()
        images[OUT_IMAGE] = COLOR_IMAGE
        images[COLOR_IMAGE] = cv2.add(color_image, red_outlines)
        # plt.title("Final"), plt.imshow(cv2.cvtColor(images[COLOR_IMAGE], cv2.COLOR_BGR2RGB)), plt.show()
        return images














