from torchvision import datasets, transforms

from base import BaseDataLoader


class MnistDataLoader(BaseDataLoader):
    """
    MNIST data loading demo using BaseDataLoader
    """

    def __init__(
        self,
        data_dir: str,
        batch_size: int,
        shuffle: bool = True,
        validation_split: float = 0.0,
        num_workers: int = 1,
        training: bool = True,
        pin_memory: bool = False,
        drop_last: bool = False,
    ):
        trsfm = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
        )
        self.data_dir = data_dir
        self.dataset = datasets.MNIST(
            self.data_dir, train=training, download=True, transform=trsfm
        )
        super().__init__(
            self.dataset,
            validation_split,
            batch_size,
            shuffle,
            num_workers,
            pin_memory,
            drop_last,
        )
