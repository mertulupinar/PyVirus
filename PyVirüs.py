import sys,os,hashlib,json,shutil,csv
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ======================
# Created by Oxynos 
# ======================

VIRUS_DB_FILE = "./virus_signatures"
QUARANTINE_FOLDER = "quarantine"

def load_virus_signatures():
    """
    Virus imzalarını yükler.
    Eğer JSON dosyası varsa ordan yükler,
    eğer TXT dosyası varsa satır satır okuyup sete dönüştürür.
    """
    # Öncelikle .json var mı diye kontrol et
    json_file = VIRUS_DB_FILE + ".json"
    txt_file = VIRUS_DB_FILE + ".txt"

    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            return set(json.load(f))

    elif os.path.exists(txt_file):
        with open(txt_file, "r", encoding="utf-8") as f:
            # Boş satırları at ve hashleri topla
            return set(line.strip() for line in f if line.strip())

    else:
        # Dosya yoksa boş set döndür
        return set()

def save_virus_signatures(signatures):
    with open(VIRUS_DB_FILE, "w") as f:
        json.dump(list(signatures), f, indent=4)

def update_virus_signatures(new_signatures):
    signatures = load_virus_signatures()
    signatures.update(new_signatures)
    save_virus_signatures(signatures)

def remove_virus_signature(signature):
    signatures = load_virus_signatures()
    if signature in signatures:
        signatures.remove(signature)
        save_virus_signatures(signatures)
        return True
    return False

def calculate_sha256(path):
    hash_sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return None

def scan_file(path):
    file_hash = calculate_sha256(path)
    virus_signatures = load_virus_signatures()

    if file_hash is None:
        return path, False

    is_virus = file_hash in virus_signatures
    return path, is_virus

def move_to_quarantine(file_path):
    if not os.path.exists(QUARANTINE_FOLDER):
        os.makedirs(QUARANTINE_FOLDER)
    filename = os.path.basename(file_path)
    quarantine_path = os.path.join(QUARANTINE_FOLDER, filename)
    shutil.move(file_path, quarantine_path)
    return quarantine_path

# ======================
# Tarama Thread'i
# ======================

class ScanThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str, bool)
    finished = pyqtSignal()

    def __init__(self, path, scan_type='directory'):
        super().__init__()
        self.path = path
        self.scan_type = scan_type

    def run(self):
        files = []
        if self.scan_type == 'file':
            files = [self.path]
        elif self.scan_type == 'directory':
            files = self.get_files_in_directory(self.path)

        total_files = len(files) or 1

        for index, file_path in enumerate(files):
            path, is_virus = scan_file(file_path)
            self.result.emit(path, is_virus)
            progress_percent = int((index + 1) / total_files * 100)
            self.progress.emit(progress_percent)

        self.finished.emit()

    def get_files_in_directory(self, path):
        all_files = []
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        return all_files

class ModernButton(QPushButton):
    """Modern özelleştirilmiş buton"""
    def __init__(self, text, color="#4CAF50", hover_color="#45a049"):
        super().__init__(text)
        self.color = color
        self.hover_color = hover_color
        self.setFixedHeight(50)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(self.get_style())
        
    def get_style(self):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.color}, stop:1 {self.darken_color(self.color)});
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.hover_color}, stop:1 {self.darken_color(self.hover_color)});
            }}
            QPushButton:pressed {{
                background: {self.darken_color(self.hover_color)};
            }}
        """
    
    def darken_color(self, color):
        """Rengi koyulaştır"""
        color_map = {
            "#4CAF50": "#3d8b40",
            "#45a049": "#357a35",
            "#2196F3": "#1976D2",
            "#1976D2": "#1565C0",
            "#FF9800": "#F57C00",
            "#F57C00": "#E65100",
            "#f44336": "#d32f2f",
            "#d32f2f": "#c62828"
        }
        return color_map.get(color, "#333333")

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
        file_path, _ = QFileDialog.getOpenFileName(self, "İmza için Dosya Seç")
        if not file_path:
            return

        file_hash = calculate_sha256(file_path)
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
        if self.resultTable.rowCount() == 0:
            QMessageBox.information(self, "Bilgi", "Kaydedilecek rapor bulunmamaktadır.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Raporu Kaydet", "", "JSON Files (*.json);;CSV Files (*.csv)")
        if not file_path:
            return

        try:
            results = []
            for row in range(self.resultTable.rowCount()):
                file_path_item = self.resultTable.item(row, 0).text()
                status_item = self.resultTable.item(row, 1).text()
                results.append({"dosya": file_path_item, "durum": status_item})

            if file_path.endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)
            elif file_path.endswith(".csv"):
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["dosya", "durum"])
                    writer.writeheader()
                    writer.writerows(results)
            else:
                QMessageBox.warning(self, "Uyarı", "Dosya uzantısı desteklenmiyor (.json veya .csv seçin).")
                return

            QMessageBox.information(self, "Başarılı", f"Rapor kaydedildi:\n{file_path}")
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