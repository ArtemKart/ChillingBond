import logging
import logging.config

import yaml  # type: ignore [import-untyped]

from src import ROOTDIR


def setup_logging() -> None:

    config_path = ROOTDIR / "logging.yml"
    logs_dir = ROOTDIR / "logs"

    logs_dir.mkdir(exist_ok=True)

    with open(config_path) as f:
        config = yaml.safe_load(f)

        if "handlers" in config and "file" in config["handlers"]:
            log_file = str(logs_dir / "app.log")
            config["handlers"]["file"]["filename"] = log_file

        logging.config.dictConfig(config)
