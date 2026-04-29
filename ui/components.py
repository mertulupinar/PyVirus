from PyQt5.QtWidgets import QPushButton, QProgressBar, QFrame, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor

class ModernButton(QPushButton):
    """Modern özelleştirilmiş buton."""
    
    def __init__(self, text: str, primary=False, danger=False, warning=False):
        super().__init__(text)
        self.setFixedHeight(40)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Determine colors
        if primary:
            bg_color = "#3b82f6"
            hover_color = "#2563eb"
            pressed_color = "#1d4ed8"
            text_color = "white"
        elif danger:
            bg_color = "#ef4444"
            hover_color = "#dc2626"
            pressed_color = "#b91c1c"
            text_color = "white"
        elif warning:
            bg_color = "#f59e0b"
            hover_color = "#d97706"
            pressed_color = "#b45309"
            text_color = "white"
        else:
            bg_color = "#374151"
            hover_color = "#4b5563"
            pressed_color = "#1f2937"
            text_color = "#f3f4f6"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: #1f2937;
                color: #6b7280;
            }}
        """)

class AnimatedProgressBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(10)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #374151;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                border-radius: 5px;
            }
        """)

def add_shadow(widget):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0, 0, 0, 60))
    widget.setGraphicsEffect(shadow)

class StatusCard(QFrame):
    def __init__(self, title, value, icon, color="#10b981"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedHeight(110)
        self.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 12px;
                border: 1px solid #374151;
            }
        """)
        add_shadow(self)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Header layout (Icon + Title)
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"color: {color}; font-size: 16px; background: transparent; border: none;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #9ca3af; font-size: 12px; font-weight: bold; border: none; background: transparent; letter-spacing: 0.5px;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"color: #f3f4f6; font-size: 28px; font-weight: 800; border: none; background: transparent;")
        
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        self.setLayout(layout)
        
        self.value_label = value_label
        
    def update_value(self, value):
        self.value_label.setText(str(value))

class Card(QFrame):
    """Genel amaçlı kart widget'ı"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            Card {
                background-color: #1f2937;
                border-radius: 12px;
                border: 1px solid #374151;
            }
        """)
        add_shadow(self)
