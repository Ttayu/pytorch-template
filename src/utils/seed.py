import random

import numpy as np
import torch


def set_global_seed(seed: int) -> None:
    """
    Sets random seed for reproducibility into PyTorch, Numpy and Random.
    """
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)
