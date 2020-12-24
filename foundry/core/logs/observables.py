
import logging

from foundry import log_dir

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler = logging.FileHandler(f"{log_dir}/observable.log")
handler.setFormatter(formatter)
logger.addHandler(handler)