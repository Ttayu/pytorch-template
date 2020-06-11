import os
from typing import Optional

import numpy as np

import torch
import torch.backends.cudnn as cudnn


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def prepare_cudnn(
    deterministic: Optional[bool] = None, benchmark: Optional[bool] = None
) -> None:
    if not torch.cuda.is_available():
        return
    if deterministic is None:
        deterministic = os.environ.get("CUDNN_DETERMINISTIC", "True") == "True"
    cudnn.deterministic = deterministic
    if benchmark is None:
        benchmark = os.environ.get("CUDNN_BENCHMARK", "True") == "True"
    cudnn.benchmark = benchmark


def detach(tensor: torch.Tensor) -> np.ndarray:
    return tensor.detach().cpu().numpy()
