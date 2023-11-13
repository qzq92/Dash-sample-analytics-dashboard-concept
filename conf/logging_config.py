import logging
import os
from datetime import datetime
import yaml


def setup_logging() -> None:
    """Function that facilitates logging setup for python program.
    """
    with open("logging.yml", "r", encoding="utf-8") as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

     # Based on logger.yml handlers.
    file_handler_list = [
        "info_file_handler",
        "error_file_handler",
    ]

    for file_handler_type in file_handler_list:
        # Assumes of the format logs/info.log or similar structure
        # base, extension = os.path.splitext(filename)
        level_info_name = config_dict["handlers"][file_handler_type]["level"]
        # Get current run date in ddmmyyyy format
        today = datetime.today()
        today_str = today.strftime("%d/%m/%Y").replace("/", "")
        # Construct the required format

        # Make parent folder containing submodule name if avail, regardless of existence as long submodule_name.is not None
        log_dir_for_submodule = "logs"
        log_filename = f"{today_str}_{level_info_name.lower()}.log"

        orig_log_file = config_dict["handlers"][file_handler_type]["filename"]
        # Delete default configure log filepaths to prevent unnecessary confusion between generated logs
        if os.path.isfile(orig_log_file):
            os.remove(orig_log_file)
        # Construct relevant logfile name based on kedro logger structure and update config path
        rel_logfile_path = os.path.join(log_dir_for_submodule, log_filename)
        config_dict["handlers"][file_handler_type]["filename"] = rel_logfile_path

    # Apply the configuration change assuming it has config
    try:
        logging.config.dictConfig(config_dict)
    except KeyError:
        pass