import torch
import torch.nn as nn
from torchvision import models
class HierarchicalECGModel(nn.Module):
    def __init__(self):
        super(HierarchicalECGModel, self).__init__()
        self.backbone = models.efficientnet_b0(weights='DEFAULT')
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Identity()
        
        self.head_l1 = nn.Sequential(
            nn.Linear(num_features, 1),
            # nn.Sigmoid()
        )

        self.head_l2 = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 4)
        )

    def forward(self, x):
        features = self.backbone(x)
        l1_out = self.head_l1(features)
        l2_out = self.head_l2(features)
        return l1_out, l2_out

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = HierarchicalECGModel().to(device)