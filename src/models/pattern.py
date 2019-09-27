from models.abc.model import Model
import numpy as np


class Pattern(Model):
    def __init__(self, name=None, image=None, keypoints=[], descriptors=None, image_processes=[]):
        super().__init__(name, image_processes)
        self.image = image
        self.keypoints = keypoints
        self.descriptors = descriptors

    def __eq__(self, other):
        def keypoints_equal(kp1, kp2):
            return (
                kp1.class_id == kp2.class_id
                and kp1.pt[0] == kp2.pt[0]
                and kp1.pt[1] ==  kp2.pt[1]
                and kp1.size == kp2.size
                and kp1.angle == kp2.angle
                and kp1.octave == kp2.octave
                and kp1.response == kp2.response
            )

        if isinstance(other, self.__class__):
            for k1, k2 in zip(self.keypoints, other.keypoints):
                if not keypoints_equal:
                    return False
            if not np.array_equal(self.image, other.image):
                return False
            if not np.array_equal(self.descriptors, other.descriptors):
                return False
            return super().__eq__(other) and True
        return False

    

