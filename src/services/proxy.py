from collections import OrderedDict
import numpy as np
from src.services.detected_service import ModelDetection


class ModelDetectionProxy:
    def __init__(self, model_detection: ModelDetection):
        self.model_detection = model_detection
        self.cache = OrderedDict()
        self.cache_size = 500

    def detect(self, image: np.ndarray):
        image_hash = hash(image.tobytes())
        
        # si esta en la caché, lo devolvemos
        if image_hash in self.cache:
            self.cache.move_to_end(image_hash)
            return self.cache[image_hash]

        # Si no está en la caché, realizar la detección
        detections = self.model_detection.detect(image)
        self.cache[image_hash] = detections

        # Limitar el tamaño de la caché
        if len(self.cache) > self.cache_size:
            # eliminamos el elemento más antiguo
            self.cache.popitem(last=False)

        return detections