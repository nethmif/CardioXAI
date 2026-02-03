import torch
import numpy as np
import cv2
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

class L1Wrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model
    def forward(self, x):
        return self.model(x)[0] 

class L2Wrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model
    def forward(self, x):
        return self.model(x)[1] 

def generate_heatmaps(model, input_tensor, rgb_img_float):

    target_layers = [model.backbone.features[-1]]
    
    cam_l1 = GradCAM(model=L1Wrapper(model), target_layers=target_layers)
    grayscale_cam_l1 = cam_l1(input_tensor=input_tensor)[0, :]
    
    cam_l2 = GradCAM(model=L2Wrapper(model), target_layers=target_layers)
    output_l2 = model(input_tensor)[1]
    target_category = torch.argmax(output_l2, dim=1).item()
    targets_l2 = [ClassifierOutputTarget(target_category)]
    grayscale_cam_l2 = cam_l2(input_tensor=input_tensor, targets=targets_l2)[0, :]
    vis_l1 = show_cam_on_image(rgb_img_float, grayscale_cam_l1, use_rgb=True)
    vis_l2 = show_cam_on_image(rgb_img_float, grayscale_cam_l2, use_rgb=True)
    vis_l1_bgr = cv2.cvtColor(vis_l1, cv2.COLOR_RGB2BGR)
    vis_l2_bgr = cv2.cvtColor(vis_l2, cv2.COLOR_RGB2BGR)

    return vis_l1_bgr, vis_l2_bgr