# @Time    : 2023/05/29 13:57
# @Author  : fyq
# @File    : train.py
# @Software: PyCharm

__author__ = 'fyq'

import math
import os
import sys
import time
from pathlib import Path

import torch
from torch import Tensor
from torch.nn import CrossEntropyLoss
from torch.utils.data import DataLoader
from tqdm import tqdm

from rot_net.dataset import RotDataset
from rot_net.module import RotNetR
from rot_net.util import from_google_street

if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cls_num = 180
    model = RotNetR(cls_num=cls_num).to(device)

    dataset_path = Path(r"F:\pythonProject\task\rot_net\image\street")
    image_paths = from_google_street(dataset_path)
    spilt_index = math.ceil(len(image_paths) * 0.8)
    train_paths = image_paths[0: spilt_index]
    test_paths = image_paths[spilt_index:]

    # 数据集
    train_dataset = RotDataset(image_paths=train_paths,
                               cls_num=cls_num)
    test_dataset = RotDataset(image_paths=test_paths,
                              cls_num=cls_num)

    # 数据加载器
    num_workers = os.cpu_count()
    batch_size = 64
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        shuffle=True,
        drop_last=True,
    )
    test_dataloader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        drop_last=True,
    )

    # 优化器
    lr = 0.01
    momentum = 0.9
    epochs = 64
    steps = 256
    optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=momentum)
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=lr, pct_start=0.25, epochs=epochs, steps_per_epoch=steps
    )

    # 损失
    loss_func = CrossEntropyLoss()

    best_val_loss = sys.maxsize
    for epoch_idx in range(epochs):

        start_t = time.perf_counter()
        total_train_loss = 0.0
        tqdm.write(f"Epoch#{epoch_idx}. Training process.")
        model.train()

        with tqdm(total=steps) as bar:
            for data_index, data in enumerate(train_dataloader):
                inputs, labels = data[0].to(device), data[1].to(device)
                optimizer.zero_grad()
                predict: Tensor = model(inputs)
                loss: Tensor = loss_func(predict, labels)
                loss.backward()
                optimizer.step()

                total_train_loss += loss.cpu().item()
                bar.update(1)

                if data_index + 1 == steps:
                    break

        train_loss = total_train_loss / steps

        tqdm.write(f"Epoch#{epoch_idx}. Validating process.")
        model.eval()

        total_val_loss = 0.0
        eval_batch_count = 0
        with torch.no_grad():
            for inputs, labels in tqdm(test_dataloader):
                inputs: Tensor = inputs.to(device=device)
                labels: Tensor = labels.to(device=device)

                predict: Tensor = model(inputs)

                total_val_loss += loss_func(predict, labels).cpu().item()
                eval_batch_count += 1

        val_loss = total_val_loss / eval_batch_count

        t_cost = time.perf_counter() - start_t
        tqdm.write(f"Epoch#{epoch_idx}. "
                   f"time_cost: {t_cost:.2f} s. "
                   f"train_loss: {train_loss:.8f}. "
                   f"val_loss: {val_loss:.8f}." 
                   f"train lr is {optimizer.state_dict()['param_groups'][0]['lr']}.")

        scheduler.step()

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "model/best.pth")
