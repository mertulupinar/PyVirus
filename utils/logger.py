import logging
import os

LOG_FILE = "antivirus.log"

def setup_logger():
    # Loglama konfigürasyonu
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('Mert Ulupınar')

logger = setup_logger()
