from typing import Optional, Tuple, Type

import torch
import torch.backends.cudnn as cudnn
from torch import nn


def check_apex_available() -> bool:
    """
    Checks if apex is available.
    """
    try:
        import apex  # noqa: F401
        from apex import amp  # noqa: F401

        return True
    except ImportError:
        return False


def assert_fp16_available() -> None:
    assert cudnn.enabled, "fp16 mode requires cudnn backend to be enabled."

    assert check_apex_available(), (
        "NVidia Apex package must be installed." "See https://github.com/NVIDIA/apex."
    )


def check_ddp_wrapped(model: nn.Module) -> bool:
    """
    Checks whether model is wrapped with DataParallel/DistributedDataParallel.
    """
    parallel_wrappers: Tuple[Type, ...] = (
        nn.DataParallel,
        nn.parallel.DistributedDataParallel,
    )

    # check whether Apex is installed and if it is.
    # add Apex's DistributedDataParallel to list of checked types
    try:
        from apex.parallel import DistributedDataParallel as apex_DDP  # noqa: F401

        parallel_wrappers = parallel_wrappers + (apex_DDP,)
    except ImportError:
        pass

    return isinstance(model, parallel_wrappers)


def check_torch_distributed_initialized() -> bool:
    """
    Checks if torch.distributed is availabel and initialized.
    """
    return torch.distributed.is_available() and torch.distributed.is_initialized()


def initialize_apex(
    model: nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None,
    **distributed_params
) -> Tuple[nn.Module, Optional[torch.optim.Optimizer]]:
    assert_fp16_available()
    import apex

    amp_params = {"opt_level": "O0"}
    for dp in distributed_params:
        amp_params[dp] = distributed_params[dp]
    amp_result = apex.amp.initialize(model, optimizer, **amp_params)
    if optimizer is None:
        model, optimizer = amp_result
    else:
        model = amp_result
    return model, optimizer
