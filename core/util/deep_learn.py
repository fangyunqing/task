# @Time    : 2023/06/13 10:07
# @Author  : fyq
# @File    : deep_learn.py
# @Software: PyCharm

__author__ = 'fyq'

import torch
from PIL import Image

from rot_net.module import RotNetR
from rot_net.util.helper import process_captcha

import matplotlib.pyplot as plt


def rot_net_captcha(image_path: str,
                    model_path: str,
                    debug: bool = False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = RotNetR(train=False, cls_num=180)
    model.load_state_dict(torch.load(str(model_path)))
    model = model.to(device=device)
    model.eval()

    img = Image.open(image_path)
    img_ts = process_captcha(img)
    img_ts = img_ts.to(device=device)

    predict = model.predict(img_ts)
    angle = round(predict * 360, 2)

    if debug:
        img = img.rotate(
            -angle, resample=Image.Resampling.BILINEAR, fillcolor=(255, 255, 255)
        )  # use neg degree to recover the img
        plt.figure("debug")
        plt.imshow(img)
        plt.show()

    return angle
