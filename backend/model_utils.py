# import torch
# import torch.nn as nn
# from torchvision import models
# class HierarchicalECGModel(nn.Module):
#     def __init__(self):
#         super(HierarchicalECGModel, self).__init__()
#         self.backbone = models.efficientnet_b0(weights='DEFAULT')
#         num_features = self.backbone.classifier[1].in_features
#         self.backbone.classifier = nn.Identity()
        
#         self.head_l1 = nn.Sequential(
#             nn.Linear(num_features, 1),
#             # nn.Sigmoid()
#         )

#         self.head_l2 = nn.Sequential(
#             nn.Linear(num_features, 512),
#             nn.BatchNorm1d(512),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(512, 4)
#         )

#     def forward(self, x):
#         features = self.backbone(x)
#         l1_out = self.head_l1(features)
#         l2_out = self.head_l2(features)
#         return l1_out, l2_out
# class HierarchicalECGModel(nn.Module):
#     def __init__(self):
#         super(HierarchicalECGModel, self).__init__()
#         self.backbone = models.efficientnet_b0(weights='DEFAULT')
#         num_features = self.backbone.classifier[1].in_features 
#         self.backbone.classifier = nn.Identity() 

#         for param in self.backbone.parameters():
#             param.requires_grad = False

#         total_layers = len(list(self.backbone.features))
#         for i in range(int(total_layers * 0.7), total_layers):
#             for param in self.backbone.features[i].parameters():
#                 param.requires_grad = True

#         self.l1_hidden = nn.Sequential(
#             nn.Linear(num_features, 256), 
#             nn.BatchNorm1d(256),
#             nn.LeakyReLU(0.1),
#             nn.Dropout(0.3)
#         )

#         self.head_l1 = nn.Linear(256, 1) 

#         self.feature_gate = nn.Sequential(
#             nn.Linear(256, 512),
#             nn.LeakyReLU(0.1),
#             nn.Linear(512, num_features),
#             nn.Sigmoid()
#         )

#         self.head_l2 = nn.Sequential(
#             nn.Linear(num_features, 512), 
#             nn.BatchNorm1d(512),
#             nn.LeakyReLU(0.1),
#             nn.Dropout(0.3), 
#             nn.Linear(512, 4)
#         )

#     def forward(self, x):
#         features = self.backbone(x)                 
#         l1_latent = self.l1_hidden(features) 
#         l1_out = self.head_l1(l1_latent) 
#         gate = self.feature_gate(l1_latent)
#         gated_features = features * gate         
#         l2_out = self.head_l2(gated_features)
#         return l1_out, l2_out
import torch
import torch.nn as nn
from torchvision import models

class HierarchicalECGModel(nn.Module):
    def __init__(self):
        super(HierarchicalECGModel, self).__init__()
        self.backbone = models.efficientnet_b0(weights='DEFAULT')
        num_features = self.backbone.classifier[1].in_features 
        self.backbone.classifier = nn.Identity() 

        for param in self.backbone.parameters():
            param.requires_grad = False

        total_layers = len(list(self.backbone.features))
        for i in range(int(total_layers * 0.7), total_layers):
            for param in self.backbone.features[i].parameters():
                param.requires_grad = True

        self.l1_hidden = nn.Sequential(
            nn.Linear(num_features, 256), 
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.3)
        )

        self.head_l1 = nn.Linear(256, 1) 

        self.feature_gate = nn.Sequential(
            nn.Linear(256, 512),
            nn.LeakyReLU(0.1),
            nn.Linear(512, num_features),
            nn.Sigmoid()
        )

        self.head_l2 = nn.Sequential(
            nn.Linear(num_features, 512), 
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.3), 
            nn.Linear(512, 4)
        )

    def forward(self, x):
        features = self.backbone(x)                 
        l1_latent = self.l1_hidden(features) 
        l1_out = self.head_l1(l1_latent) 
        gate = self.feature_gate(l1_latent)
        gated_features = features * gate         
        l2_out = self.head_l2(gated_features)
        return l1_out, l2_out
    
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = HierarchicalECGModel().to(device)