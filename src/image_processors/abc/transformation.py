from image_processors.abc.image_process import *


class Transformation(ImageProcess):

    def process(self, images, *args, **kwargs):
        return self.transform(images, *args, **kwargs)

    def transform(self, images, *args, **kwargs):
        raise NotImplementedError("transform method must be implemented")
