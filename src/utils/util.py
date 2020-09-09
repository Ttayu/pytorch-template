import json
from collections import OrderedDict
from itertools import repeat
from pathlib import Path
from typing import Dict, Union

import pandas as pd


def ensure_dir(dirname: Union[str, Path]) -> Path:
    dirname = Path(dirname)
    if not dirname.is_dir():
        dirname.mkdir(parents=True, exist_ok=False)
    return dirname


def ensure_path(path: Union[str, Path]) -> Path:
    return Path(path)


def read_json(fname):
    fname = Path(fname)
    with fname.open("rt") as handle:
        return json.load(handle, object_hook=OrderedDict)


def write_json(content, fname):
    fname = Path(fname)
    with fname.open("wt") as handle:
        json.dump(content, handle, indent=4, sort_keys=False)


def inf_loop(data_loader):
    """ wrapper function for endless data loader. """
    for loader in repeat(data_loader):
        yield from loader


class MetricTracker:
    def __init__(self, *keys, writer=None):
        self.writer = writer
        self._data = pd.DataFrame(index=keys, columns=["total", "counts", "average"])
        self.reset()

    def reset(self) -> None:
        for col in self._data.columns:
            self._data[col].values[:] = 0

    def update(self, key: str, value: Union[int, float], n: int = 1) -> None:
        if self.writer is not None:
            self.writer.add_scalar(key, value)
        self._data.total[key] += value * n
        self._data.counts[key] += n
        self._data.average[key] = self._data.total[key] / self._data.counts[key]

    def avg(self, key: str) -> float:
        return self._data.average[key]

    def result(self) -> Dict[str, Union[int, float]]:
        return dict(self._data.average)
