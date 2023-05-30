# @Time    : 2023/05/29 9:15
# @Author  : fyq
# @File    : rot_net_r.py
# @Software: PyCharm

__author__ = 'fyq'

import torch.nn as nn
from torch import Tensor
from torchvision import models


class RotNetR(nn.Module):

    def __init__(self, cls_num, train: bool = True):
        super(RotNetR, self).__init__()
        self.cls_num = cls_num

        weights = models.RegNet_Y_3_2GF_Weights.DEFAULT if train else None
        self.backbone = models.regnet_y_3_2gf(weights=weights)

        fc_channels = self.backbone.fc.in_features
        del self.backbone.fc
        self.backbone.fc = nn.Linear(fc_channels, cls_num)

        if train:
            nn.init.kaiming_normal_(self.backbone.fc.weight)
            nn.init.zeros_(self.backbone.fc.bias)

    def forward(self, x: Tensor) -> Tensor:
        return self.backbone.forward(x)

    def predict(self, img_ts: Tensor) -> float:
        img_ts = img_ts.unsqueeze_(0)
        angle = float(self.backbone.forward(img_ts).cpu().argmax(1).item()) / self.cls_num
        return angle
