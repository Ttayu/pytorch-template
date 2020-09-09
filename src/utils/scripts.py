import os
import subprocess
import sys
import warnings
from pathlib import Path
from shutil import copytree, ignore_patterns
from typing import Union

from .util import ensure_dir


def dump_code(save_dir: Union[str, Path]) -> None:
    save_dir = ensure_dir(save_dir)
    new_src_dir = "src"

    # src/project/__code__.py
    old_pro_dir = Path(__file__).parents[1]
    new_pro_dir = save_dir / new_src_dir / old_pro_dir.name

    copytree(old_pro_dir, new_pro_dir, ignore=ignore_patterns("*cache*"))


def list_pip_packages() -> str:
    result = ""
    with open(os.devnull, "w") as devnull:
        try:
            result = (
                subprocess.check_output("pip freeze".split(), stderr=devnull)
                .strip()
                .decode("utf-8")
            )
        except Exception:
            warnings.warn(
                f"Failed to freeze pip packages. "
                f"Continue experiment without pip packages dumping."
            )
    return result


def dump_environment(save_dir: Union[str, Path]) -> None:
    save_dir = ensure_dir(save_dir)
    pip_package = list_pip_packages()
    python_version = sys.version
    (save_dir / "pip-packages.txt").write_text(pip_package)
    (save_dir / "python_version.txt").write_text(python_version)
