import os
from typing import Set, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtCore import QThread, pyqtSignal
from utils.logger import logger
from core.database import load_virus_signatures
from core.scanner import scan_file, scan_file_parallel

class ScanThread(QThread):
    """Asenkron dosya tarama thread'i."""
    progress = pyqtSignal(int)
    result = pyqtSignal(str, bool)  # Geriye dönük uyumluluk için
    batch_results = pyqtSignal(list) # UI donmalarını engellemek için toplu sonuç
    finished = pyqtSignal()

    def __init__(self, path: str, scan_type: str = 'directory', parallel: bool = True, max_workers: int = 4):
        super().__init__()
        self.path = path
        self.scan_type = scan_type
        self._is_running = True
        self.parallel = parallel
        self.max_workers = max_workers

    def run(self):
        logger.info(f"Tarama başlatıldı: {self.path} (Paralel: {self.parallel})")
        virus_signatures = load_virus_signatures()
        
        files = self._get_files()
        if not files:
            logger.warning("Taranacak dosya bulunamadı")
            self.finished.emit()
            return
        
        total_files = len(files)
        logger.info(f"Toplam {total_files} dosya taranacak")
        
        if self.parallel and total_files > 10:
            self._run_parallel_scan(files, virus_signatures, total_files)
        else:
            self._run_serial_scan(files, virus_signatures, total_files)
        
        logger.info("Tarama tamamlandı")
        self.finished.emit()
    
    def _run_serial_scan(self, files: List[str], virus_signatures: Set[str], total_files: int):
        batch = []
        for index, file_path in enumerate(files):
            if not self._is_running:
                break
            
            path, is_virus = scan_file(file_path, virus_signatures)
            batch.append((path, is_virus))
            self.result.emit(path, is_virus)
            
            if len(batch) >= 20:
                self.batch_results.emit(batch)
                batch = []
            
            progress_percent = int((index + 1) / total_files * 100)
            self.progress.emit(progress_percent)
            
        if batch:
            self.batch_results.emit(batch)

    def _run_parallel_scan(self, files: List[str], virus_signatures: Set[str], total_files: int):
        completed = 0
        batch = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(scan_file_parallel, file_path, virus_signatures): file_path 
                for file_path in files
            }
            
            for future in as_completed(future_to_file):
                if not self._is_running:
                    break
                
                try:
                    path, is_virus = future.result()
                    batch.append((path, is_virus))
                    self.result.emit(path, is_virus)
                    
                    completed += 1
                    
                    if len(batch) >= 20:
                        self.batch_results.emit(batch)
                        batch = []
                    
                    progress_percent = int(completed / total_files * 100)
                    self.progress.emit(progress_percent)
                except Exception as e:
                    file_path = future_to_file[future]
                    logger.error(f"Paralel tarama hatası: {file_path} - {e}")
                    batch.append((file_path, False))
                    self.result.emit(file_path, False)
                    completed += 1
                    
            if batch:
                self.batch_results.emit(batch)
                
            if not self._is_running:
                for f in future_to_file:
                    f.cancel()
    
    def _get_files(self) -> list:
        if self.scan_type == 'file':
            return [self.path] if os.path.isfile(self.path) else []
        elif self.scan_type == 'directory':
            return self._get_files_in_directory(self.path)
        return []
    
    def _get_files_in_directory(self, path: str) -> list:
        all_files = []
        try:
            for root, _, files in os.walk(path):
                for file in files:
                    if not self._is_running:
                        break
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
        except (OSError, PermissionError) as e:
            logger.error(f"Dizin taranamadı: {e}")
        
        return all_files
    
    def stop(self):
        self._is_running = False
