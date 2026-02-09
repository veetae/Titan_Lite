import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "titanhq.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3),
        logging.StreamHandler()
    ]
)

def get_logger(name="TitanHQ"):
    return logging.getLogger(name)
