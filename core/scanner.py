import hashlib
import os
from typing import Set, Optional, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import logger
from core.database import load_virus_signatures

def calculate_hash(path: str, algorithm: str = 'md5') -> Optional[str]:
    """
    Dosyanın hash değerini hesaplar.
    Varsayılan olarak MD5 kullanır (virus signatures ile uyumlu).
    """
    hash_func = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()
    
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except (IOError, OSError, PermissionError):
        return None

def scan_file(path: str, virus_signatures: Optional[Set[str]] = None) -> Tuple[str, bool]:
    """
    Dosyayı tarar ve virüs olup olmadığını kontrol eder.
    """
    if virus_signatures is None:
        virus_signatures = load_virus_signatures()
    
    file_hash = calculate_hash(path)
    
    if file_hash is None:
        logger.debug(f"Hash hesaplanamadı: {path}")
        return path, False

    is_virus = file_hash in virus_signatures
    
    if is_virus:
        logger.warning(f"Virüs tespit edildi! Dosya: {path}, Hash: {file_hash}")
    else:
        logger.debug(f"Temiz dosya: {path}")
    
    return path, is_virus

def scan_file_parallel(file_path: str, virus_signatures: Set[str]) -> Tuple[str, bool]:
    try:
        return scan_file(file_path, virus_signatures)
    except Exception as e:
        logger.error(f"Dosya tarama hatası: {file_path} - {e}")
        return file_path, False

def scan_files_parallel(files: List[str], virus_signatures: Set[str], max_workers: int = 4) -> List[Tuple[str, bool]]:
    results = []
    total = len(files)
    
    logger.info(f"{total} dosya paralel tarama başlatılıyor ({max_workers} thread ile)")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(scan_file_parallel, file_path, virus_signatures): file_path 
            for file_path in files
        }
        
        for future in as_completed(future_to_file):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                file_path = future_to_file[future]
                logger.error(f"Thread hatası: {file_path} - {e}")
                results.append((file_path, False))
    
    logger.info(f"Paralel tarama tamamlandı: {len(results)} dosya tarandı")
    return results
