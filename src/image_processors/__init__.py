import pkgutil
import importlib
import image_processors
import inspect
import image_processors.abc


abc_classes = set()
abstract_modules = list(pkgutil.iter_modules(image_processors.abc.__path__))
for _, name, _ in abstract_modules:
    module = importlib.import_module('image_processors.abc.{0}'.format(name))
    classes = [getattr(module, c) for c in dir(module) if inspect.isclass(getattr(module, c))]
    abc_classes |= set(c for c in classes if issubclass(c, image_processors.abc.image_process.ImageProcess))

image_process_classes = set()
for importer, name, ispkg in pkgutil.iter_modules(image_processors.__path__):
    if not ispkg:
        module = importlib.import_module('image_processors.{0}'.format(name))
        classes = [getattr(module, c) for c in dir(module) if inspect.isclass(getattr(module, c))]
        image_process_classes |= set(c for c in classes if issubclass(c, image_processors.abc.image_process.ImageProcess))
avaliable_image_processes = sorted([c for c in (image_process_classes - abc_classes)], key=lambda c: (c.process_type, c.priority))
