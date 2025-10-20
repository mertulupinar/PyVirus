import sys
import os
import hashlib
import json
import shutil
import csv
import logging
from datetime import datetime
from typing import Set, Optional, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QProgressBar,
                              QTableWidget, QTableWidgetItem, QFileDialog, 
                              QMessageBox, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QFrame, QAbstractItemView, QInputDialog, QStyle)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QCursor



VIRUS_DB_FILE = "./virus_signatures.json"
QUARANTINE_FOLDER = "quarantine"
LOG_FILE = "antivirus.log"

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('OxynosAV')

# Global cache için
_virus_signatures_cache: Optional[Set[str]] = None
_cache_timestamp: float = 0

def load_virus_signatures() -> Set[str]:
    """
    Virus imzalarını cache'den veya dosyadan yükler.
    Cache mekanizması ile performansı artırır.
    """
    global _virus_signatures_cache, _cache_timestamp
    
    # Cache kontrolü (dosya değişmişse yeniden yükle)
    if os.path.exists(VIRUS_DB_FILE):
        file_mtime = os.path.getmtime(VIRUS_DB_FILE)
        if _virus_signatures_cache is not None and _cache_timestamp >= file_mtime:
            logger.debug("Virus imzaları cache'den yüklendi")
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
    
        # Dosya yoksa boş set döndür
    logger.warning("Virus imza dosyası bulunamadı, boş set döndürülüyor")
    _virus_signatures_cache = set()
    _cache_timestamp = 0
    return _virus_signatures_cache

def save_virus_signatures(signatures: Set[str]) -> None:
    """İmzaları dosyaya kaydeder ve cache'i günceller."""
    global _virus_signatures_cache, _cache_timestamp
    
    try:
        with open(VIRUS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(signatures)), f, indent=2, ensure_ascii=False)
        
        # Cache'i güncelle
        _virus_signatures_cache = signatures.copy()
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

def calculate_hash(path: str, algorithm: str = 'md5') -> Optional[str]:
    """
    Dosyanın hash değerini hesaplar.
    Varsayılan olarak MD5 kullanır (virus signatures ile uyumlu).
    """
    hash_func = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()
    
    try:
        with open(path, "rb") as f:
            # Büyük dosyalar için optimize edilmiş chunk size (64KB)
            for chunk in iter(lambda: f.read(65536), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except (IOError, OSError, PermissionError):
        return None

def scan_file(path: str, virus_signatures: Optional[Set[str]] = None) -> Tuple[str, bool]:
    """
    Dosyayı tarar ve virüs olup olmadığını kontrol eder.
    virus_signatures parametresi ile imzalar tekrar yüklenmez.
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

# ======================
# Paralel Tarama Fonksiyonları
# ======================

def scan_file_parallel(file_path: str, virus_signatures: Set[str]) -> Tuple[str, bool]:
    """Paralel tarama için optimize edilmiş dosya tarama fonksiyonu."""
    try:
        return scan_file(file_path, virus_signatures)
    except Exception as e:
        logger.error(f"Dosya tarama hatası: {file_path} - {e}")
        return file_path, False

def scan_files_parallel(files: List[str], virus_signatures: Set[str], max_workers: int = 4) -> List[Tuple[str, bool]]:
    """
    Dosyaları paralel olarak tarar.
    max_workers: Aynı anda çalışacak thread sayısı (varsayılan 4)
    """
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

# ======================
# Tarama Thread'i
# ======================

class ScanThread(QThread):
    """Asenkron dosya tarama thread'i."""
    progress = pyqtSignal(int)
    result = pyqtSignal(str, bool)
    finished = pyqtSignal()

    def __init__(self, path: str, scan_type: str = 'directory', parallel: bool = True, max_workers: int = 4):
        super().__init__()
        self.path = path
        self.scan_type = scan_type
        self._is_running = True
        self.parallel = parallel  # Paralel tarama aktif mi
        self.max_workers = max_workers  # Thread sayısı

    def run(self):
        """Tarama işlemini başlatır."""
        logger.info(f"Tarama başlatıldı: {self.path} (Paralel: {self.parallel})")
        
        # Virus imzalarını bir kere yükle (performans optimizasyonu)
        virus_signatures = load_virus_signatures()
        
        files = self._get_files()
        if not files:
            logger.warning("Taranacak dosya bulunamadı")
            self.finished.emit()
            return
        
        total_files = len(files)
        logger.info(f"Toplam {total_files} dosya taranacak")
        
        if self.parallel and total_files > 10:
            # Paralel tarama (10'dan fazla dosya için)
            self._run_parallel_scan(files, virus_signatures, total_files)
        else:
            # Seri tarama
            self._run_serial_scan(files, virus_signatures, total_files)
        
        logger.info("Tarama tamamlandı")
        self.finished.emit()
    
    def _run_serial_scan(self, files: List[str], virus_signatures: Set[str], total_files: int):
        """Seri tarama modu."""
        for index, file_path in enumerate(files):
            if not self._is_running:
                break
            
            path, is_virus = scan_file(file_path, virus_signatures)
            self.result.emit(path, is_virus)
            
            progress_percent = int((index + 1) / total_files * 100)
            self.progress.emit(progress_percent)

    def _run_parallel_scan(self, files: List[str], virus_signatures: Set[str], total_files: int):
        """Paralel tarama modu."""
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(scan_file_parallel, file_path, virus_signatures): file_path 
                for file_path in files
            }
            
            for future in as_completed(future_to_file):
                if not self._is_running:
                    executor.shutdown(wait=False)
                    break
                
                try:
                    path, is_virus = future.result()
                    self.result.emit(path, is_virus)
                    
                    completed += 1
                    progress_percent = int(completed / total_files * 100)
                    self.progress.emit(progress_percent)
                except Exception as e:
                    file_path = future_to_file[future]
                    logger.error(f"Paralel tarama hatası: {file_path} - {e}")
                    self.result.emit(file_path, False)
    
    def _get_files(self) -> list:
        """Taranacak dosya listesini döndürür."""
        if self.scan_type == 'file':
            return [self.path] if os.path.isfile(self.path) else []
        elif self.scan_type == 'directory':
            return self._get_files_in_directory(self.path)
        return []
    
    def _get_files_in_directory(self, path: str) -> list:
        """Dizindeki tüm dosyaları recursive olarak toplar."""
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
        """Taramayı durdurur."""
        self._is_running = False

class ModernButton(QPushButton):
    """Modern özelleştirilmiş buton."""
    
    # Renk haritası - sınıf değişkeni olarak tanımla
    _COLOR_MAP = {
        "#4CAF50": ("#3d8b40", "#357a35"),  # (dark, darker)
        "#2196F3": ("#1976D2", "#1565C0"),
        "#FF9800": ("#F57C00", "#E65100"),
        "#f44336": ("#d32f2f", "#c62828")
    }
    
    def __init__(self, text: str, color: str = "#4CAF50", hover_color: str = "#45a049"):
        super().__init__(text)
        self.color = color
        self.hover_color = hover_color
        self.setFixedHeight(50)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(self._get_style())
    
    def _get_style(self) -> str:
        """Buton stilini oluşturur."""
        dark_color = self._darken_color(self.color)
        dark_hover = self._darken_color(self.hover_color)
        
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.color}, stop:1 {dark_color});
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.hover_color}, stop:1 {dark_hover});
            }}
            QPushButton:pressed {{
                background: {dark_hover};
            }}
        """
    
    def _darken_color(self, color: str) -> str:
        """Rengi koyulaştır."""
        if color in self._COLOR_MAP:
            return self._COLOR_MAP[color][0]
        # Fallback: manuel koyulaştırma
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        except ValueError:
            return "#333333"

class AnimatedProgressBar(QProgressBar):
    """Animasyonlu progress bar"""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(30)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 15px;
                text-align: center;
                background-color: #f0f0f0;
                font-size: 12px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:0.5 #45a049, stop:1 #4CAF50);
                border-radius: 13px;
                margin: 2px;
            }
        """)

class StatusCard(QFrame):
    """Durum kartı widget'ı"""
    def __init__(self, title, value, color="#4CAF50"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Başlık
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 12px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Değer
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        self.setLayout(layout)
        
        self.value_label = value_label
        
    def update_value(self, value):
        self.value_label.setText(str(value))

# ======================
# UI - AntivirusApp
# ======================

class AntivirusApp(QWidget):
    def __init__(self):
        super().__init__()
        self.scanned_files = 0
        self.infected_files = 0
        self.clean_files = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Oxynos Antivirus Scanner Pro")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        # Ana stil
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333;
            }
        """)
        
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık bölümü
        self.create_header(main_layout)
        
        # İstatistik kartları
        self.create_stats_section(main_layout)
        
        # Kontrol paneli
        self.create_control_panel(main_layout)
        
        # Progress bar
        self.create_progress_section(main_layout)
        
        # Sonuç tablosu
        self.create_results_section(main_layout)
        
        # Alt panel
        self.create_bottom_panel(main_layout)
        
        self.setLayout(main_layout)
        
        # İcon ayarla
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

    def create_header(self, layout):
        """Başlık bölümü oluştur"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        header_frame.setFixedHeight(120)
        
        header_layout = QHBoxLayout()
        
        # Logo/Icon bölümü
        icon_label = QLabel("🛡️")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setFixedSize(80, 80)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Başlık metinleri
        text_layout = QVBoxLayout()
        
        title_label = QLabel("Oxynos Antivirus Scanner Pro")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        subtitle_label = QLabel("Bilgisayarınızı güvende tutun")
        subtitle_label.setStyleSheet("color: #e8f5e8; font-size: 14px;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        text_layout.addStretch()
        
        # Durum göstergesi
        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignRight)
        
        status_label = QLabel("Sistem Durumu")
        status_label.setStyleSheet("color: white; font-size: 12px;")
        
        system_status = QLabel("✅ Korumalı")
        system_status.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(system_status)
        status_layout.addStretch()
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        header_layout.addLayout(status_layout)
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

    def create_stats_section(self, layout):
        """İstatistik kartları oluştur"""
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.scanned_card = StatusCard("Taranan Dosya", "0", "#2196F3")
        self.infected_card = StatusCard("Tehdit Bulundu", "0", "#f44336")
        self.clean_card = StatusCard("Temiz Dosya", "0", "#4CAF50")
        
        stats_layout.addWidget(self.scanned_card)
        stats_layout.addWidget(self.infected_card)
        stats_layout.addWidget(self.clean_card)
        
        layout.addLayout(stats_layout)

    def create_control_panel(self, layout):
        """Kontrol paneli oluştur"""
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 20px;
            }
        """)
        
        control_layout = QGridLayout()
        control_layout.setSpacing(15)
        
        # Ana tarama butonu
        self.scanButton = ModernButton("🔍 Dosya Tara", "#4CAF50", "#45a049")
        self.scanButton.clicked.connect(self.scanDirectory)
        
        control_layout.addWidget(self.scanButton, 0, 0, 1, 3)
        
        control_frame.setLayout(control_layout)
        layout.addWidget(control_frame)

    def create_progress_section(self, layout):
        """Progress bölümü oluştur"""
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        
        progress_layout = QVBoxLayout()
        
        # Durum etiketi
        self.status_label = QLabel("Tarama bekleniyor...")
        self.status_label.setStyleSheet("color: #666; font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        
        # Progress bar
        self.progressBar = AnimatedProgressBar()
        self.progressBar.setValue(0)
        
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progressBar)
        
        progress_frame.setLayout(progress_layout)
        layout.addWidget(progress_frame)

    def create_results_section(self, layout):
        """Sonuç tablosu oluştur"""
        results_frame = QFrame()
        results_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        
        results_layout = QVBoxLayout()
        
        # Başlık
        results_title = QLabel("Tarama Sonuçları")
        results_title.setStyleSheet("color: #333; font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        
        # Tablo
        self.resultTable = QTableWidget()
        self.resultTable.setColumnCount(2)
        self.resultTable.setHorizontalHeaderLabels(["📁 Dosya Yolu", "🔍 Durum"])
        
        # Tablo stilini ayarla
        self.resultTable.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #fafafa;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                border: none;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #333;
            }
        """)
        
        self.resultTable.setAlternatingRowColors(True)
        self.resultTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultTable.horizontalHeader().setStretchLastSection(True)
        self.resultTable.verticalHeader().setVisible(False)
        
        results_layout.addWidget(results_title)
        results_layout.addWidget(self.resultTable)
        
        results_frame.setLayout(results_layout)
        layout.addWidget(results_frame)

    def create_bottom_panel(self, layout):
        """Alt panel oluştur"""
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        
        bottom_layout = QGridLayout()
        bottom_layout.setSpacing(10)
        
        # İşlem butonları
        self.quarantineButton = ModernButton("🔒 Karantinaya Al", "#f44336", "#d32f2f")
        self.quarantineButton.clicked.connect(self.quarantineSelectedFile)
        
        self.addSignatureButton = ModernButton("➕ İmza Ekle", "#2196F3", "#1976D2")
        self.addSignatureButton.clicked.connect(self.addSignature)
        
        self.removeSignatureButton = ModernButton("➖ İmza Sil", "#FF9800", "#F57C00")
        self.removeSignatureButton.clicked.connect(self.removeSignature)
        
        self.saveReportButton = ModernButton("💾 Rapor Kaydet", "#4CAF50", "#45a049")
        self.saveReportButton.clicked.connect(self.saveReport)
        
        bottom_layout.addWidget(self.quarantineButton, 0, 0)
        bottom_layout.addWidget(self.addSignatureButton, 0, 1)
        bottom_layout.addWidget(self.removeSignatureButton, 0, 2)
        bottom_layout.addWidget(self.saveReportButton, 0, 3)
        
        bottom_frame.setLayout(bottom_layout)
        layout.addWidget(bottom_frame)

    # ======================
    # Tarama İşlemleri
    # ======================
    def scanDirectory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Dizin Seç")
        if not dir_path:
            return
        self.resultTable.setRowCount(0)
        self.progressBar.setValue(0)
        
        # İstatistikleri sıfırla
        self.scanned_files = 0
        self.infected_files = 0
        self.clean_files = 0
        self.update_stats()
        
        self.status_label.setText("Dizin taraması başlatılıyor...")

        self.scanThread = ScanThread(dir_path, 'directory')
        self.scanThread.result.connect(self.addScanResult)
        self.scanThread.progress.connect(self.updateProgressBar)
        self.scanThread.finished.connect(self.scanFinished)
        self.scanThread.start()

    def addScanResult(self, path, is_virus):
        row = self.resultTable.rowCount()
        self.resultTable.insertRow(row)

        file_item = QTableWidgetItem(path)
        status_item = QTableWidgetItem("Tehlikeli" if is_virus else "Temiz")

        if is_virus:
            file_item.setBackground(QColor(200, 0, 0))
            file_item.setForeground(QColor(Qt.white))
            status_item.setBackground(QColor(200, 0, 0))
            status_item.setForeground(QColor(Qt.white))
            self.infected_files += 1
        else:
            file_item.setBackground(QColor(0, 200, 0))
            file_item.setForeground(QColor(Qt.black))
            status_item.setBackground(QColor(0, 200, 0))
            status_item.setForeground(QColor(Qt.black))
            self.clean_files += 1

        self.resultTable.setItem(row, 0, file_item)
        self.resultTable.setItem(row, 1, status_item)
        
        self.scanned_files += 1
        self.update_stats()

    def update_stats(self):
        """İstatistik kartlarını güncelle"""
        self.scanned_card.update_value(self.scanned_files)
        self.infected_card.update_value(self.infected_files)
        self.clean_card.update_value(self.clean_files)

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.status_label.setText("Tarama tamamlandı!")
        else:
            self.status_label.setText(f"Tarama devam ediyor... %{value}")

    def scanFinished(self):
        self.progressBar.setValue(100)
        self.status_label.setText("Tarama tamamlandı!")

    # ======================
    # Karantina
    # ======================
    def quarantineSelectedFile(self):
        selected_row = self.resultTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen karantinaya alınacak dosyayı seçin.")
            return

        file_path_item = self.resultTable.item(selected_row, 0)
        status_item = self.resultTable.item(selected_row, 1)

        if not file_path_item or not status_item:
            return

        file_path = file_path_item.text()
        status = status_item.text()

        if status != "Tehlikeli":
            QMessageBox.information(self, "Bilgi", "Bu dosya temiz görünüyor, karantinaya alınmadı.")
            return

        try:
            quarantine_path = move_to_quarantine(file_path)
            status_item.setText("Karantinada")
            file_path_item.setBackground(QColor(180, 180, 180))
            file_path_item.setForeground(QColor(Qt.black))
            status_item.setBackground(QColor(180, 180, 180))
            status_item.setForeground(QColor(Qt.black))
            QMessageBox.information(self, "Başarılı", f"Dosya karantinaya alındı:\n{quarantine_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karantinaya alma başarısız:\n{str(e)}")

    # ======================
    # İmza İşlemleri
    # ======================
    def addSignature(self):
        """Yeni virus imzası ekler."""
        file_path, _ = QFileDialog.getOpenFileName(self, "İmza için Dosya Seç")
        if not file_path:
            return

        file_hash = calculate_hash(file_path, algorithm='md5')
        if file_hash:
            update_virus_signatures({file_hash})
            QMessageBox.information(self, "Başarılı", f"İmza eklendi:\n{file_hash}")
        else:
            QMessageBox.critical(self, "Hata", "Dosyanın hash değeri hesaplanamadı.")

    def removeSignature(self):
        signatures = list(load_virus_signatures())
        if not signatures:
            QMessageBox.information(self, "Bilgi", "Veritabanında imza bulunmamaktadır.")
            return

        signature, ok = QInputDialog.getItem(self, "İmza Sil", "Silinecek imzayı seçin:", signatures, 0, False)
        if ok and signature:
            if remove_virus_signature(signature):
                QMessageBox.information(self, "Başarılı", f"İmza silindi:\n{signature}")
            else:
                QMessageBox.critical(self, "Hata", "İmza silinemedi.")

    # ======================
    # 📊 Rapor Kaydetme
    # ======================
    def saveReport(self):
        """Tarama raporunu JSON veya CSV formatında kaydeder."""
        if self.resultTable.rowCount() == 0:
            QMessageBox.information(self, "Bilgi", "Kaydedilecek rapor bulunmamaktadır.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Raporu Kaydet", "", 
            "JSON Files (*.json);;CSV Files (*.csv)"
        )
        if not save_path:
            return

        try:
            # Sonuçları topla
            results = []
            for row in range(self.resultTable.rowCount()):
                file_item = self.resultTable.item(row, 0).text()
                status_item = self.resultTable.item(row, 1).text()
                results.append({"dosya": file_item, "durum": status_item})

            # Dosya formatına göre kaydet
            if save_path.endswith(".json"):
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            elif save_path.endswith(".csv"):
                with open(save_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["dosya", "durum"])
                    writer.writeheader()
                    writer.writerows(results)
            else:
                QMessageBox.warning(self, "Uyarı", "Dosya uzantısı desteklenmiyor (.json veya .csv seçin).")
                return

            QMessageBox.information(self, "Başarılı", f"Rapor kaydedildi:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor kaydedilemedi:\n{str(e)}")

# ======================
# Uygulama Çalıştırma
# ======================

def main():
    app = QApplication(sys.argv)
    
    # Uygulama ikonunu ayarla
    app.setWindowIcon(app.style().standardIcon(QStyle.SP_ComputerIcon))
    
    # Modern tema ayarları
    app.setStyle('Fusion')
    
    window = AntivirusApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()