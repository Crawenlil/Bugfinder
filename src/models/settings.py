from models.abc.model import Model

from settings import *


class Settings(Model):
    def __init__(self, name=None, image_processes=[]):
        super().__init__(name, image_processes)


