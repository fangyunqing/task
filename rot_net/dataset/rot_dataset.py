# @Time    : 2023/05/29 11:25
# @Author  : fyq
# @File    : rot_dataset.py
# @Software: PyCharm

__author__ = 'fyq'

from pathlib import Path
from typing import Tuple, List, Optional

import torch
from PIL import Image
from torch import Tensor
from torch.utils.data import Dataset
from torchvision.transforms import Normalize
import numpy as np

from rot_net.util import DEFAULT_NORM, from_img


class RotDataset(Dataset[Tuple[Tensor, Tensor]]):

    def __init__(self,
                 image_paths: List[Path],
                 cls_num,
                 target_size=224,
                 norm: Optional[Normalize] = None):
        self.image_paths = image_paths
        self.cls_num = cls_num
        self.target_size = target_size
        self.norm = norm
        if self.norm is None:
            self.norm = DEFAULT_NORM
        self.size = len(self.image_paths)
        self.indices = torch.randint(cls_num, (self.size,), dtype=torch.long)

    def __getitem__(self, index) -> Tuple[Tensor, Tensor]:
        index_ts: Tensor = self.indices[index]

        img = Image.open(self.image_paths[index], formats=('JPEG', 'PNG', 'WEBP'))
        img = img.convert('RGB')
        img_ts = torch.from_numpy(np.array(img))
        img_ts = img_ts.view(img.height, img.width, 3)
        img_ts = img_ts.permute(2, 0, 1)
        img_ts = from_img(img_ts, index_ts.item() / self.cls_num, self.target_size)
        img_ts = self.norm(img_ts)

        return img_ts, index_ts

    def __len__(self):
        return self.size
