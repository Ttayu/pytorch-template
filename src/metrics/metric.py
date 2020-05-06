import torch


def accuracy(output: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    assert output.shape[0] == target.shape[0]
    with torch.no_grad():
        pred = torch.argmax(output, dim=1)
        correct = 0
        correct += torch.sum(pred == target).item()
    return correct / len(target)


def top_k_acc(output: torch.Tensor, target: torch.Tensor, k: int = 3) -> torch.Tensor:
    assert output.shape[0] == target.shape[0]
    with torch.no_grad():
        pred = torch.topk(output, k, dim=1)[1]
        correct = 0
        for i in range(k):
            correct += torch.sum(pred[:, i] == target).item()
    return correct / len(target)
