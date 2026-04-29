import json
import os
import threading
from typing import Set, Optional
from utils.logger import logger

VIRUS_DB_FILE = "./virus_signatures.json"

_virus_signatures_cache: Optional[Set[str]] = None
_cache_timestamp: float = 0
_db_lock = threading.Lock()

def load_virus_signatures() -> Set[str]:
    """
    Virus imzalarını cache'den veya dosyadan yükler.
    Thread-safe implementation.
    """
    global _virus_signatures_cache, _cache_timestamp
    
    with _db_lock:
        if os.path.exists(VIRUS_DB_FILE):
            file_mtime = os.path.getmtime(VIRUS_DB_FILE)
            if _virus_signatures_cache is not None and _cache_timestamp >= file_mtime:
                return _virus_signatures_cache
            
            try:
                with open(VIRUS_DB_FILE, "r", encoding="utf-8") as f:
                    _virus_signatures_cache = set(json.load(f))
                    _cache_timestamp = file_mtime
                    logger.info(f"{len(_virus_signatures_cache)} virus imzası yüklendi")
                    return _virus_signatures_cache
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Virus imza dosyası yüklenemedi: {e}")
                return set()
        
        logger.warning("Virus imza dosyası bulunamadı, boş set döndürülüyor")
        _virus_signatures_cache = set()
        _cache_timestamp = 0
        return _virus_signatures_cache

def save_virus_signatures(signatures: Set[str]) -> None:
    """İmzaları dosyaya kaydeder ve cache'i günceller."""
    global _virus_signatures_cache, _cache_timestamp
    
    with _db_lock:
        try:
            with open(VIRUS_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(sorted(list(signatures)), f, indent=2, ensure_ascii=False)
            
            _virus_signatures_cache = set(signatures)
            _cache_timestamp = os.path.getmtime(VIRUS_DB_FILE)
            logger.info(f"{len(signatures)} virus imzası kaydedildi")
        except IOError as e:
            logger.error(f"İmza dosyası kaydedilemedi: {e}")

def update_virus_signatures(new_signatures: Set[str]) -> None:
    """Yeni imzaları mevcut imzalara ekler."""
    signatures = load_virus_signatures()
    old_count = len(signatures)
    signatures.update(new_signatures)
    new_count = len(signatures) - old_count
    save_virus_signatures(signatures)
    logger.info(f"{new_count} yeni virus imzası eklendi")

def remove_virus_signature(signature: str) -> bool:
    """Belirtilen imzayı siler."""
    signatures = load_virus_signatures()
    if signature in signatures:
        signatures.remove(signature)
        save_virus_signatures(signatures)
        logger.info(f"Virus imzası silindi: {signature[:16]}...")
        return True
    logger.warning(f"Silinmek istenen imza bulunamadı: {signature[:16]}...")
    return False
