import sys
from PyQt5.QtWidgets import QApplication, QStyle
from ui.main_window import AntivirusApp

# Geriye dönük uyumluluk ve dışarıdan kullanım için exportlar (örn. test_antivirus.py)
from core.database import (
    load_virus_signatures, 
    save_virus_signatures, 
    update_virus_signatures, 
    remove_virus_signature,
    VIRUS_DB_FILE
)
from core.scanner import calculate_hash, scan_file, scan_file_parallel, scan_files_parallel
from core.quarantine import move_to_quarantine, QUARANTINE_FOLDER

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