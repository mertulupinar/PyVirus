import sys
import json
import csv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QFrame, QTableWidget, QTableWidgetItem, QFileDialog, 
                              QMessageBox, QAbstractItemView, QInputDialog, QStyle, QHeaderView)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QFont, QIcon

from ui.components import ModernButton, AnimatedProgressBar, StatusCard, Card, add_shadow
from ui.threads import ScanThread
from core.database import load_virus_signatures, update_virus_signatures, remove_virus_signature
from core.scanner import calculate_hash
from core.quarantine import move_to_quarantine

class AntivirusApp(QWidget):
    def __init__(self):
        super().__init__()
        self.scanned_files = 0
        self.infected_files = 0
        self.clean_files = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PyVirus Pro - Security Center")
        self.setGeometry(100, 100, 1000, 750)
        self.setMinimumSize(900, 650)
        
        # Dark theme base styling
        self.setStyleSheet("""
            QWidget {
                background-color: #111827;
                font-family: 'Segoe UI', Inter, Arial, sans-serif;
                color: #f3f4f6;
            }
            QMessageBox {
                background-color: #1f2937;
            }
            QMessageBox QLabel {
                color: #f3f4f6;
                background: transparent;
            }
            QMessageBox QPushButton {
                background-color: #374151;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #4b5563;
            }
            QInputDialog {
                background-color: #1f2937;
            }
            QInputDialog QLabel {
                color: #f3f4f6;
                background: transparent;
            }
            QLineEdit {
                background-color: #374151;
                color: #f3f4f6;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        self.create_header(main_layout)
        self.create_stats_section(main_layout)
        self.create_scan_section(main_layout)
        self.create_results_section(main_layout)
        self.create_bottom_panel(main_layout)
        
        self.setLayout(main_layout)

    def create_header(self, layout):
        header_layout = QHBoxLayout()
        
        # Left side: Logo and Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title_label = QLabel("PyVirus Pro")
        title_label.setStyleSheet("color: #f3f4f6; font-size: 28px; font-weight: 800; letter-spacing: 1px; background: transparent;")
        
        subtitle_label = QLabel("Advanced Threat Protection System")
        subtitle_label.setStyleSheet("color: #9ca3af; font-size: 13px; font-weight: 500; background: transparent;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Right side: System Status
        status_card = Card()
        status_card.setFixedSize(180, 60)
        status_card.setStyleSheet(status_card.styleSheet() + "Card { background-color: #1f2937; }")
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(15, 0, 15, 0)
        
        status_icon = QLabel("🛡️")
        status_icon.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        
        status_text_layout = QVBoxLayout()
        status_text_layout.setAlignment(Qt.AlignCenter)
        status_text_layout.setSpacing(2)
        
        status_lbl = QLabel("SYSTEM STATUS")
        status_lbl.setStyleSheet("color: #9ca3af; font-size: 10px; font-weight: bold; background: transparent; border: none;")
        
        self.system_status = QLabel("Secure")
        self.system_status.setStyleSheet("color: #10b981; font-size: 14px; font-weight: 800; background: transparent; border: none;")
        
        status_text_layout.addWidget(status_lbl)
        status_text_layout.addWidget(self.system_status)
        
        status_layout.addWidget(status_icon)
        status_layout.addLayout(status_text_layout)
        status_card.setLayout(status_layout)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(status_card)
        
        layout.addLayout(header_layout)

    def create_stats_section(self, layout):
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.scanned_card = StatusCard("SCANNED FILES", "0", "📁", "#3b82f6")
        self.infected_card = StatusCard("THREATS DETECTED", "0", "⚠️", "#ef4444")
        self.clean_card = StatusCard("CLEAN FILES", "0", "✅", "#10b981")
        
        stats_layout.addWidget(self.scanned_card)
        stats_layout.addWidget(self.infected_card)
        stats_layout.addWidget(self.clean_card)
        
        layout.addLayout(stats_layout)

    def create_scan_section(self, layout):
        scan_card = Card()
        scan_layout = QVBoxLayout()
        scan_layout.setContentsMargins(25, 25, 25, 25)
        scan_layout.setSpacing(20)
        
        top_layout = QHBoxLayout()
        
        info_layout = QVBoxLayout()
        self.status_label = QLabel("Ready to scan your system")
        self.status_label.setStyleSheet("color: #e5e7eb; font-size: 16px; font-weight: 600; background: transparent; border: none;")
        
        self.detail_label = QLabel("Select a directory to begin the malware scan.")
        self.detail_label.setStyleSheet("color: #9ca3af; font-size: 13px; background: transparent; border: none;")
        
        info_layout.addWidget(self.status_label)
        info_layout.addWidget(self.detail_label)
        
        self.scanButton = ModernButton("Scan Directory", primary=True)
        self.scanButton.setFixedWidth(200)
        self.scanButton.clicked.connect(self.scanDirectory)
        
        top_layout.addLayout(info_layout)
        top_layout.addStretch()
        top_layout.addWidget(self.scanButton)
        
        self.progressBar = AnimatedProgressBar()
        self.progressBar.setValue(0)
        
        scan_layout.addLayout(top_layout)
        scan_layout.addWidget(self.progressBar)
        
        scan_card.setLayout(scan_layout)
        layout.addWidget(scan_card)

    def create_results_section(self, layout):
        results_card = Card()
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(20, 20, 20, 20)
        results_layout.setSpacing(10)
        
        results_title = QLabel("Scan Results")
        results_title.setStyleSheet("color: #f3f4f6; font-size: 16px; font-weight: 600; background: transparent; border: none;")
        
        self.resultTable = QTableWidget()
        self.resultTable.setColumnCount(2)
        self.resultTable.setHorizontalHeaderLabels(["File Path", "Status"])
        self.resultTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.resultTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.resultTable.setColumnWidth(1, 150)
        
        self.resultTable.setStyleSheet("""
            QTableWidget {
                background-color: #111827;
                color: #d1d5db;
                border: 1px solid #374151;
                border-radius: 8px;
                gridline-color: #374151;
                outline: none;
            }
            QTableWidget::item {
                padding: 5px 10px;
                border-bottom: 1px solid #1f2937;
            }
            QTableWidget::item:selected {
                background-color: #374151;
                color: white;
            }
            QHeaderView::section {
                background-color: #1f2937;
                color: #9ca3af;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #374151;
                border-right: 1px solid #374151;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                text-align: left;
            }
            QScrollBar:vertical {
                border: none;
                background: #111827;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #374151;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4b5563;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.resultTable.setAlternatingRowColors(False)
        self.resultTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultTable.verticalHeader().setVisible(False)
        self.resultTable.setShowGrid(False)
        self.resultTable.setFocusPolicy(Qt.NoFocus)
        
        results_layout.addWidget(results_title)
        results_layout.addWidget(self.resultTable)
        
        results_card.setLayout(results_layout)
        layout.addWidget(results_card)

    def create_bottom_panel(self, layout):
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        self.quarantineButton = ModernButton("Quarantine Selected", danger=True)
        self.quarantineButton.clicked.connect(self.quarantineSelectedFile)
        
        self.addSignatureButton = ModernButton("Add Signature")
        self.addSignatureButton.clicked.connect(self.addSignature)
        
        self.removeSignatureButton = ModernButton("Remove Signature")
        self.removeSignatureButton.clicked.connect(self.removeSignature)
        
        self.saveReportButton = ModernButton("Save Report", warning=True)
        self.saveReportButton.clicked.connect(self.saveReport)
        
        bottom_layout.addWidget(self.quarantineButton)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.addSignatureButton)
        bottom_layout.addWidget(self.removeSignatureButton)
        bottom_layout.addWidget(self.saveReportButton)
        
        layout.addLayout(bottom_layout)

    def scanDirectory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if not dir_path:
            return
            
        self.resultTable.setRowCount(0)
        self.progressBar.setValue(0)
        
        self.scanned_files = 0
        self.infected_files = 0
        self.clean_files = 0
        self.update_stats()
        
        self.status_label.setText("Scanning in progress...")
        self.detail_label.setText(f"Scanning: {dir_path}")
        self.scanButton.setEnabled(False)
        
        self.system_status.setText("Scanning")
        self.system_status.setStyleSheet("color: #f59e0b; font-size: 14px; font-weight: 800; background: transparent; border: none;")
        
        self.resultTable.setSortingEnabled(False)
        
        self.scanThread = ScanThread(dir_path, 'directory')
        self.scanThread.batch_results.connect(self.addScanResultsBatch)
        self.scanThread.progress.connect(self.updateProgressBar)
        self.scanThread.finished.connect(self.scanFinished)
        self.scanThread.start()

    def addScanResultsBatch(self, results):
        current_row = self.resultTable.rowCount()
        self.resultTable.setRowCount(current_row + len(results))
        
        font = QFont()
        font.setWeight(QFont.Bold)

        for i, (path, is_virus) in enumerate(results):
            row = current_row + i
            
            file_item = QTableWidgetItem(path)
            
            if is_virus:
                status_item = QTableWidgetItem("⚠️ Infected")
                status_item.setForeground(QColor("#ef4444"))
                status_item.setFont(font)
                file_item.setForeground(QColor("#ef4444"))
                self.infected_files += 1
            else:
                status_item = QTableWidgetItem("✅ Clean")
                status_item.setForeground(QColor("#10b981"))
                file_item.setForeground(QColor("#d1d5db"))
                self.clean_files += 1

            self.resultTable.setItem(row, 0, file_item)
            self.resultTable.setItem(row, 1, status_item)
            self.scanned_files += 1
            
        self.update_stats()

    def update_stats(self):
        self.scanned_card.update_value(self.scanned_files)
        self.infected_card.update_value(self.infected_files)
        self.clean_card.update_value(self.clean_files)

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)

    def scanFinished(self):
        self.progressBar.setValue(100)
        self.status_label.setText("Scan Complete")
        self.detail_label.setText(f"Finished scanning. Found {self.infected_files} threats.")
        self.resultTable.setSortingEnabled(True)
        self.scanButton.setEnabled(True)
        
        if self.infected_files > 0:
            self.system_status.setText("Threats Found")
            self.system_status.setStyleSheet("color: #ef4444; font-size: 14px; font-weight: 800; background: transparent; border: none;")
        else:
            self.system_status.setText("Secure")
            self.system_status.setStyleSheet("color: #10b981; font-size: 14px; font-weight: 800; background: transparent; border: none;")

    def quarantineSelectedFile(self):
        selected_row = self.resultTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select an infected file to quarantine.")
            return

        file_path_item = self.resultTable.item(selected_row, 0)
        status_item = self.resultTable.item(selected_row, 1)

        if not file_path_item or not status_item:
            return

        file_path = file_path_item.text()
        status = status_item.text()

        if "Infected" not in status:
            QMessageBox.information(self, "Info", "This file is clean.")
            return

        try:
            quarantine_path = move_to_quarantine(file_path)
            status_item.setText("🔒 Quarantined")
            status_item.setForeground(QColor("#f59e0b"))
            file_path_item.setForeground(QColor("#6b7280"))
            
            font = QFont()
            font.setStrikeOut(True)
            file_path_item.setFont(font)
            
            QMessageBox.information(self, "Success", f"File moved to quarantine:\n{quarantine_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to quarantine:\n{str(e)}")

    def addSignature(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File for Signature")
        if not file_path:
            return

        file_hash = calculate_hash(file_path, algorithm='md5')
        if file_hash:
            update_virus_signatures({file_hash})
            QMessageBox.information(self, "Success", f"Signature added:\n{file_hash}")
        else:
            QMessageBox.critical(self, "Error", "Could not calculate file hash.")

    def removeSignature(self):
        signatures = list(load_virus_signatures())
        if not signatures:
            QMessageBox.information(self, "Info", "Database is empty.")
            return

        signature, ok = QInputDialog.getItem(self, "Remove Signature", "Select signature:", signatures, 0, False)
        if ok and signature:
            if remove_virus_signature(signature):
                QMessageBox.information(self, "Success", f"Signature removed:\n{signature}")
            else:
                QMessageBox.critical(self, "Error", "Could not remove signature.")

    def saveReport(self):
        if self.resultTable.rowCount() == 0:
            QMessageBox.information(self, "Info", "No scan results to save.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "", 
            "JSON Files (*.json);;CSV Files (*.csv)"
        )
        if not save_path:
            return

        try:
            results = []
            for row in range(self.resultTable.rowCount()):
                file_item = self.resultTable.item(row, 0).text()
                status_item = self.resultTable.item(row, 1).text()
                status = "Infected" if "Infected" in status_item else ("Quarantined" if "Quarantined" in status_item else "Clean")
                results.append({"file": file_item, "status": status})

            if save_path.endswith(".json"):
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            elif save_path.endswith(".csv"):
                with open(save_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["file", "status"])
                    writer.writeheader()
                    writer.writerows(results)
            else:
                QMessageBox.warning(self, "Warning", "Unsupported file format. Use .json or .csv")
                return

            QMessageBox.information(self, "Success", f"Report saved:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save report:\n{str(e)}")
