import cv2
import numpy as np

def process_ecg_signal(img, target_size=(224, 224)):
    if img is None:
        return None
    h, w = img.shape[:2]
    cropped_img = img[int(h*0.20):int(h*0.95), :]
    gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)    
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)    
    dilated = cv2.dilate(clean, kernel, iterations=1)    
    resized = cv2.resize(dilated, target_size, interpolation=cv2.INTER_AREA)    
    if len(resized.shape) == 2:
        resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
        
    return resized