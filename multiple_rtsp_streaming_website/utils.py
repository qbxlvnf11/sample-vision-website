import cv2
import time
import threading
import yaml

def load_config(path="config.yaml"):
    
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config
