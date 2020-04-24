import torch
import torch.nn.functional as F
from torch.nn.modules.loss import _Loss


class NLL_Loss(_Loss):
    def __init__(self):
        super().__init__()

    def forward(self, output: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        return F.nll_loss(output, target)
