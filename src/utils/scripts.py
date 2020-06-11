from pathlib import Path
from shutil import copytree, ignore_patterns
from typing import Union

from .util import ensure_path


def dump_code(save_dir: Union[str, Path]):
    save_dir = ensure_path(save_dir)
    new_src_dir = "src"

    # src/project/__code__.py
    old_pro_dir = Path(__file__).parents[1]
    new_pro_dir = save_dir / new_src_dir / old_pro_dir.name

    copytree(old_pro_dir, new_pro_dir, ignore=ignore_patterns("*cache*"))
