import cv2
import numpy as np
from torchvision import transforms
from PIL import Image
import torch
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def process_ecg_signal(img, target_size=(224, 224)):
    h_img, w_img = img.shape[:2]
    y_start = int(h_img * 0.20)
    y_end = int(h_img * 0.95)
    if y_end <= y_start: y_end = h_img
    cropped = img[y_start:y_end, :]

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    resized = cv2.resize(binary, target_size, interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)

inference_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)
])

def prepare_ecg_for_model(img):
    processed = process_ecg_signal(img)
    plt.imshow(processed)
    plt.title("Processed ECG sent to model")
    plt.show()
    tensor = inference_transform(processed).unsqueeze(0)
    return tensor.to(device)