# import cv2
# import numpy as np

# def process_ecg_signal(img, target_size=(224, 224)):
#     if img is None:
#         return None
#     h, w = img.shape[:2]
#     cropped_img = img[int(h*0.20):int(h*0.95), :]
#     gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)    
#     _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#     kernel = np.ones((2, 2), np.uint8)
#     clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)    
#     dilated = cv2.dilate(clean, kernel, iterations=1)    
#     resized = cv2.resize(dilated, target_size, interpolation=cv2.INTER_AREA)    
#     if len(resized.shape) == 2:
#         resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
        
#     return resized

# def process_ecg_signal(img, target_size=(224, 224)):
#     """
#     Crop, grayscale, binarize, and resize ECG images.
#     Matches preprocessing used during training.
#     """
#     if img is None:
#         return None
    
#     h, w = img.shape[:2]
#     y_start = int(h * 0.20)
#     y_end = int(h * 0.95)
#     if y_end <= y_start:
#         y_end = h  

#     cropped_img = img[y_start:y_end, :]
#     gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
#     _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

#     kernel = np.ones((2, 2), np.uint8)
#     clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
#     dilated = cv2.dilate(clean, kernel, iterations=1)

#     resized = cv2.resize(dilated, target_size, interpolation=cv2.INTER_AREA)

#     if len(resized.shape) == 2:
#         resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)

#     return resized

# inference_transform = transforms.Compose([
#     transforms.ToPILImage(),
#     transforms.Resize((224, 224)),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)  
# ])

# def prepare_ecg_for_model(img):
#     """
#     Takes a raw OpenCV image, applies preprocessing + transform,
#     returns a tensor ready for the model.
#     """
#     processed = process_ecg_signal(img)
#     if processed is None:
#         return None
#     tensor = inference_transform(processed)
#     tensor = tensor.unsqueeze(0)  
#     return tensor
import cv2
import numpy as np
from torchvision import transforms
from PIL import Image

def process_ecg_signal(img, target_size=(224,224)):

    h, w = img.shape[:2]

    y_start = int(h * 0.20)
    y_end = int(h * 0.95)
    if y_end <= y_start: y_end = h_img
    cropped = img[y_start:y_end, :]

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    resized = cv2.resize(binary, target_size)

    resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)

    return resized


inference_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)
])

def prepare_ecg_for_model(img):
    processed = process_ecg_signal(img)
    tensor = inference_transform(processed).unsqueeze(0)  # Add batch dim
    return tensor.to(device)
