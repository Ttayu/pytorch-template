import sys
from pathlib import Path
from shutil import copy, copytree, ignore_patterns

# This script initializes new pytorch project with the template files.
# Run `python3 new_project.py ../MyNewProject` then new project named
# MyNewProject will be made
current_dir = Path()
assert (
    current_dir / "new_project.py"
).is_file(), "Script should be executed in the pytorch-template directory"
assert (
    len(sys.argv) == 2
), "Specify a name for the new project. Example: python3 new_project.py MyNewProject"

project_name = Path(sys.argv[1])
target_dir = current_dir / project_name
package_dir = target_dir / "src"
package_dir.mkdir(parents=True)

ignore = [
    ".git",
    "data",
    "saved",
    "new_project.py",
    "LICENSE",
    "README.md",
    "__pycache__",
    ".mypy_cache",
]

copytree(
    current_dir / "src",
    package_dir / project_name.name,
    ignore=ignore_patterns(*ignore),
)
(target_dir / "config").mkdir()
copy(current_dir / "config.json", target_dir / "config")
(target_dir / "datasets").mkdir()
(target_dir / "saved").mkdir()
copy(current_dir / ".gitignore", target_dir / "config")
copy(current_dir / ".flake8", target_dir / "config")

print("New project initialized at", target_dir.absolute().resolve())
