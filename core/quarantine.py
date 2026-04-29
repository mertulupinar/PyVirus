import os
import shutil
from utils.logger import logger

QUARANTINE_FOLDER = "quarantine"

def move_to_quarantine(file_path: str) -> str:
    """Dosyayı karantina klasörüne taşır."""
    os.makedirs(QUARANTINE_FOLDER, exist_ok=True)
    
    filename = os.path.basename(file_path)
    quarantine_path = os.path.join(QUARANTINE_FOLDER, filename)
    
    # Aynı isimde dosya varsa benzersiz isim oluştur
    counter = 1
    base, ext = os.path.splitext(filename)
    while os.path.exists(quarantine_path):
        quarantine_path = os.path.join(QUARANTINE_FOLDER, f"{base}_{counter}{ext}")
        counter += 1
    
    shutil.move(file_path, quarantine_path)
    logger.info(f"Dosya karantinaya alındı: {file_path} -> {quarantine_path}")
    return quarantine_path
