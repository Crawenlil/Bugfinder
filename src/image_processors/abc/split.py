from image_processors.abc.image_process import ImageProcess

class Split(ImageProcess):

    def process(self, images, *args, **kwargs):
        return images

    def lines(self):
        '''
        Returns lines to be displayed on image during settings configuration
        returned list must be in format: lines() -> [((x0, y0), (x1, y1)), ... ((xn, yn), (xn+1, yn+1))]
        '''
        raise NotImplementedError("lines method must be implemented")

    def split(self, images, *args, **kwargs):
        raise NotImplementedError("transform method must be implemented")

