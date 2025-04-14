import cv2
import numpy as np
import base64
import random
from ultralytics import YOLO
class ModelDetection:

    def __init__(self, model_path='best.pt'):
        self.model = YOLO(model_path)
        self.colors = [tuple([random.randint(0, 255) for _ in range(3)]) for _ in range(100)]

    def detect(self, image: np.ndarray):

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.model([img_rgb], imgsz=640, conf=0.1)
        return self.results_to_json(results)
    
    def draw_boxes(self, image: np.ndarray, detections: list):
        # Dibujar las cajas delimitadoras en la imagen
        for bbox in detections:
            label = f'{bbox["class_name"]} {bbox["confidence"]:.2f}'
            self.plot_one_box(bbox['bbox'], image, label=label, color=self.colors[int(bbox['class'])], line_thickness=3)
        return image

    def encode_image(self, image: np.ndarray):
        # Codificar la imagen en base64
        _, im_arr = cv2.imencode('.jpg', image)
        return base64.b64encode(im_arr.tobytes()).decode('utf-8')
    
    def results_to_json(self, results):
        output = []
        for result in results:
            boxes = result.boxes.xyxy
            classes = result.boxes.cls
            confidences = result.boxes.conf

            result_data = []
            for box, cls, conf in zip(boxes, classes, confidences):
                result_data.append({
                    "class": int(cls),
                    "class_name": self.model.names[int(cls)],
                    "bbox": [int(x) for x in box[:4].tolist()],
                    "confidence": float(conf)
                })
            output.append(result_data)
        return output
    
    def plot_one_box(self, x, im, color=(128, 128, 128), label=None, line_thickness=3):
        tl = line_thickness or round(0.002 * (im.shape[0] + im.shape[1]) / 2) + 1
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        cv2.rectangle(im, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        if label:
            tf = max(tl - 1, 1)
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(im, c1, c2, color, -1, cv2.LINE_AA)
            cv2.putText(im, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)