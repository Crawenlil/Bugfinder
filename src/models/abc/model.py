from image_processors.abc.transformation import Transformation
from image_processors.abc.split import Split
from image_processors import avaliable_image_processes

class Model(object):
    def __init__(self, name = None, image_processes=None):
        self.name = name
        if image_processes:
            self.transformations = [t for t in image_processes if isinstance(t, Transformation)]
            self.splits = [s for s in image_processes if isinstance(s, Split)]
        else:
            self.transformations = [t() for t in avaliable_image_processes if issubclass(t, Transformation)]
            self.splits = [s() for s in avaliable_image_processes if issubclass(s, Split)]

    def __eq__(self, other):
        return self.name == other.name and self.image_processes() == other.image_processes()

    def selected_split(self):
        splits = [s for s in self.splits if s.selected]
        return splits[0] if splits else None

    def selected_transformations(self):
        return filter(lambda t: t.selected, self.transformations)

    def image_processes(self):
        return self.transformations + self.splits

