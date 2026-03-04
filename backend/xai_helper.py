# import torch
# import numpy as np
# import cv2
# from pytorch_grad_cam import GradCAM
# from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
# from pytorch_grad_cam.utils.image import show_cam_on_image

# class L1Wrapper(torch.nn.Module):
#     def __init__(self, model):
#         super().__init__()
#         self.model = model
#     def forward(self, x):
#         return self.model(x)[0] 

# class L2Wrapper(torch.nn.Module):
#     def __init__(self, model):
#         super().__init__()
#         self.model = model
#     def forward(self, x):
#         return self.model(x)[1] 

# def generate_heatmaps(model, input_tensor, rgb_img_float):

#     target_layers = [model.backbone.features[-1]]
    
#     cam_l1 = GradCAM(model=L1Wrapper(model), target_layers=target_layers)
#     grayscale_cam_l1 = cam_l1(input_tensor=input_tensor)[0, :]
    
#     cam_l2 = GradCAM(model=L2Wrapper(model), target_layers=target_layers)
#     output_l2 = model(input_tensor)[1]
#     target_category = torch.argmax(output_l2, dim=1).item()
#     targets_l2 = [ClassifierOutputTarget(target_category)]
#     grayscale_cam_l2 = cam_l2(input_tensor=input_tensor, targets=targets_l2)[0, :]
#     vis_l1 = show_cam_on_image(rgb_img_float, grayscale_cam_l1, use_rgb=True)
#     vis_l2 = show_cam_on_image(rgb_img_float, grayscale_cam_l2, use_rgb=True)
#     vis_l1_bgr = cv2.cvtColor(vis_l1, cv2.COLOR_RGB2BGR)
#     vis_l2_bgr = cv2.cvtColor(vis_l2, cv2.COLOR_RGB2BGR)

#     return vis_l1_bgr, vis_l2_bgr
import torch
import numpy as np
import cv2
import random
import matplotlib.pyplot as plt
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

class BinaryTarget:
    def __call__(self, model_output):
        return model_output

def generate_heatmaps(model, input_tensor, rgb_img_float, true_l2_label=None):
    """
    Generates GradCAM heatmaps for L1 and L2 outputs.
    Arguments:
        model: HierarchicalECGModel (trained)
        input_tensor: preprocessed ECG tensor (1, C, H, W)
        rgb_img_float: original image in float [0,1], shape (H,W,3)
        true_l2_label: optional int for L2 target
    Returns:
        vis_l1_bgr, vis_l2_bgr: visualized heatmaps in BGR format
    """
    target_layers = [model.backbone.features[-1]]

    cam_l1 = GradCAM(model=L1Wrapper(model), target_layers=target_layers)
    grayscale_cam_l1 = cam_l1(input_tensor=input_tensor, targets=[BinaryTarget()])[0, :]
    if grayscale_cam_l1.max() > 0:
        grayscale_cam_l1 = (grayscale_cam_l1 - grayscale_cam_l1.min()) / (grayscale_cam_l1.max() - grayscale_cam_l1.min() + 1e-8)

    cam_l2 = GradCAM(model=L2Wrapper(model), target_layers=target_layers)
    if true_l2_label is not None:
        targets_l2 = [ClassifierOutputTarget(true_l2_label)]
    else:
        output_l2 = model(input_tensor)[1]
        pred_l2 = output_l2.argmax(dim=1).item()
        targets_l2 = [ClassifierOutputTarget(pred_l2)]
    grayscale_cam_l2 = cam_l2(input_tensor=input_tensor, targets=targets_l2)[0, :]

    vis_l1 = show_cam_on_image(rgb_img_float, grayscale_cam_l1, use_rgb=True, image_weight=0.6)
    vis_l2 = show_cam_on_image(rgb_img_float, grayscale_cam_l2, use_rgb=True, image_weight=0.6)
    
    vis_l1_bgr = cv2.cvtColor(vis_l1, cv2.COLOR_RGB2BGR)
    vis_l2_bgr = cv2.cvtColor(vis_l2, cv2.COLOR_RGB2BGR)
    return vis_l1_bgr, vis_l2_bgr

def visualize_ecg(model, input_tensor, class_names_L2):
    model.eval()
    with torch.no_grad():
        out1, out2 = model(input_tensor)
        prob_l1 = torch.sigmoid(out1).item()
        pred_l1_text = "Myocardial Infarction" if prob_l1 > 0.5 else "Other Cardiac Conditions (Non-myocardial)"
        
        pred_l2_idx = out2.argmax(dim=1).item()
        pred_l2_text = class_names_L2[pred_l2_idx]

    rgb_img = input_tensor.squeeze(0).permute(1,2,0).cpu().numpy()
    rgb_img = (rgb_img * np.array([0.5, 0.5, 0.5])) + 0.5  
    rgb_img = np.clip(rgb_img, 0, 1)

    vis_l1, vis_l2 = generate_heatmaps(model, input_tensor, rgb_img)