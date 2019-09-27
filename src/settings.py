import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
ICONS_DIR = os.path.join(ROOT_DIR, 'icons')
PATTERNS_DIR = os.path.join(DATA_DIR, 'patterns')
SETTINGS_DIR = os.path.join(DATA_DIR, 'settings')
BINARY_FILENAME = 'binary.png'
KEYPOINTS_FILENAME = 'keypoints.pickle'
DESCRIPTORS_FILENAME = 'descriptors.npy'
WORKDIR_PATH = os.path.join(DATA_DIR, 'config.txt')
PROCESSED_IMAGES_PATH = '/home/leszek/PWR/BugFinder/sample_data/test'

CLIP = (1, 'Clip')
COLOR = (2, 'Color')
GRAY = (3, 'Gray')
BINARY = (4, 'Binary')
SPLIT = (5, 'Split')

#CONST STRINGS FOR GUI:
NAME = 'Name'
GRID = 'Grid'
PATTERN_COMBO_NAME = '--select pattern--'
SETTINGS_COMBO_NAME = '--select settings--'

#CONSTS
IMAGE_PROCESSES = 'image_processes'
TRANSFORMATIONS = 'transformations'
SPLITS = 'splits'
PATTERN = 'pattern'
COLOR_IMAGE = 'color_image'
CLIPPED_IMAGE = 'clipped_image'
GRAY_IMAGE = 'gray_image'
BIN_IMAGE = 'bin_image'
OUT_IMAGE = 'out_image'
