import logging
import logging.config
from pathlib import Path

from utils import read_json

PROJECT_DIR = Path(__file__).parent.parent


def setup_logging(
    save_dir: Path,
    log_config: Path = Path(f"{PROJECT_DIR}/logger/logger_config.json"),
    default_level: int = logging.INFO,
) -> None:
    """
    Setup logging configuration
    """
    if log_config.is_file():
        config = read_json(log_config)
        # modify logging paths based on run config
        for _, handler in config["handlers"].items():
            if "filename" in handler:
                handler["filename"] = str(save_dir / handler["filename"])

        logging.config.dictConfig(config)
    else:
        print(
            "Warning: logging configuration file is not found in {}.".format(log_config)
        )
        logging.basicConfig(level=default_level)
