from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.yaml")


# Use the model
results =model.train(data="coco128.yaml", epochs=3)