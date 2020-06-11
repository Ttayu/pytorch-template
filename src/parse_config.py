import logging
import os
import shutil
from datetime import datetime
from functools import partial, reduce
from operator import getitem
from pathlib import Path
from typing import Optional

from logger import setup_logging
from utils import dump_code, dump_environment, read_json, write_json


class ConfigParser:
    def __init__(
        self, config, resume: Optional[Path] = None, modification=None, run_id=None
    ):
        """
        class to parse configuration json file. Handles hyperparameters for training, initializations of modules, checkpoint saving
        and logging module.
        :param config: Dict containing configurations, hyperparameters for training. contents of `config.json` file for example.
        :param resume: String, path to the checkpoint being loaded.
        :param modification: Dict keychain:value, specifying position values to be replaced from config dict.
        :param run_id: Unique Identifier for training processes. Used to save checkpoints and training log. Timestamp is being used as default
        """
        # load config file and apply modification
        self._config = _update_config(config, modification)
        self.resume = resume

        # set save_dir where trained model and log will be saved.
        save_dir = Path(self.config["trainer"]["save_dir"])

        exper_name = self.config["name"]
        if run_id is None:  # use timestamp as default run-id
            run_id = datetime.now().strftime(r"%m%d_%H%M%S")
        self._save_dir = save_dir / exper_name / run_id
        self._model_dir = self.save_dir / "models"
        self._log_dir = self.save_dir / "log"

        # make directory for saving checkpoints and log.
        exist_ok = True
        self._save_dir.mkdir(parents=True, exist_ok=exist_ok)
        self._model_dir.mkdir(parents=True, exist_ok=exist_ok)
        self._log_dir.mkdir(parents=True, exist_ok=exist_ok)

        # save updated config file to the checkpoint dir
        write_json(self.config, self.save_dir / "config.json")

        # save code to the checkpoint dir
        dump_code(self.save_dir)

        # save python environment
        dump_environment(self.save_dir)

        # configure logging module
        setup_logging(self.log_dir)
        self.log_levels = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}

        # copy log and model in the checkpoint begin.
        self._copy_checkpoint()

    @classmethod
    def from_args(cls, args, options=""):
        """
        Initialize this class from some cli arguments. Used in train, test.
        """
        for opt in options:
            args.add_argument(*opt.flags, default=None, type=opt.type)
        if not isinstance(args, tuple):
            args = args.parse_args()

        if args.device is not None:
            os.environ["CUDA_VISIBLE_DEVICES"] = args.device
        if args.resume is not None:
            # ./path/to/datetime/models/model.pth
            resume = Path(args.resume)
            # ./path/to/datetime/config.json
            cfg_fname = resume.parent.parent / "config.json"
        else:
            msg_no_cfg = "Configuration file need to be specified. Add '-c config.json', for example."
            assert args.config is not None, msg_no_cfg
            resume = None
            cfg_fname = Path(args.config)

        config = read_json(cfg_fname)
        if args.config and resume:
            # update new config for fine-tuning
            config.update(read_json(args.config))

        # parse custom cli options into dictionary
        modification = {
            opt.target: getattr(args, _get_opt_name(opt.flags)) for opt in options
        }
        return cls(config, resume, modification)

    def init_obj(self, name, module, *args, **kwargs):
        """
        Finds a function handle with the name given as 'type' in config, and returns the
        instance initialized with corresponding arguments given.

        `object = config.init_obj('name', module, a, b=1)`
        is equivalent to
        `object = module.name(a, b=1)`
        """
        module_name = self[name]["type"]
        module_args = dict(self[name]["args"])
        assert all(
            [k not in module_args for k in kwargs]
        ), "Overwriting kwargs given in config file is not allowed"
        module_args.update(kwargs)
        return getattr(module, module_name)(*args, **module_args)

    def init_ftn(self, name, module, *args, **kwargs):
        """
        Finds a function handle with the name given as 'type' in config, and returns the
        function with given arguments fixed with functools.partial.

        `function = config.init_ftn('name', module, a, b=1)`
        is equivalent to
        `function = lambda *args, **kwargs: module.name(a, *args, b=1, **kwargs)`.
        """
        module_name = self[name]["type"]
        module_args = dict(self[name]["args"])
        assert all(
            [k not in module_args for k in kwargs]
        ), "Overwriting kwargs given in config file is not allowed"
        module_args.update(kwargs)
        return partial(getattr(module, module_name), *args, **module_args)

    def _copy_checkpoint(self):
        def copy_trained_log():
            # experiment_name/run_id/models/model.pth
            # -> experiment_name/run_id/log
            trained_log_dir: Path = self.resume.parents[1] / "log"
            print(trained_log_dir)
            for trained_log in trained_log_dir.glob("*"):
                # skip tensorboard file because it is too large file.
                if "events" in trained_log.name:
                    continue
                shutil.copy(trained_log, self.log_dir / f"train_{trained_log.name}")

        def copy_resume():
            shutil.copy(self.resume, self.model_dir / self.resume.name)

        def copy_run_id():
            # experiment_name/run_id/models/model.pth
            run_id = self.resume.parents[1].name
            (self.save_dir / run_id).touch()

        if self.resume is None:
            return
        copy_trained_log()
        copy_resume()
        copy_run_id()

    def __getitem__(self, name):
        """Access items like ordinary dict."""
        return self.config[name]

    def get_logger(self, name, verbosity=2):
        msg_verbosity = "verbosity option {} is invalid. Valid options are {}.".format(
            verbosity, self.log_levels.keys()
        )
        assert verbosity in self.log_levels, msg_verbosity
        logger = logging.getLogger(name)
        logger.setLevel(self.log_levels[verbosity])
        return logger

    # setting read-only attributes
    @property
    def config(self):
        return self._config

    @property
    def save_dir(self):
        return self._save_dir

    @property
    def model_dir(self):
        return self._model_dir

    @property
    def log_dir(self):
        return self._log_dir


# helper functions to update config dict with custom cli options


def _update_config(config, modification):
    if modification is None:
        return config

    for k, v in modification.items():
        if v is not None:
            _set_by_path(config, k, v)
    return config


def _get_opt_name(flags):
    for flg in flags:
        if flg.startswith("--"):
            return flg.replace("--", "")
    return flags[0].replace("--", "")


def _set_by_path(tree, keys, value):
    """Set a value in a nested object in tree by sequence of keys."""
    keys = keys.split(";")
    _get_by_path(tree, keys[:-1])[keys[-1]] = value


def _get_by_path(tree, keys):
    """Access a nested object in tree by sequence of keys."""
    return reduce(getitem, keys, tree)
