import uuid
from PyQt5.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QCheckBox, QRadioButton,
    QTextEdit, QComboBox, QListWidget, QTableWidget, QTableWidgetItem, QTabWidget, QWidget, QVBoxLayout,
    QGroupBox, QSlider, QScrollArea, QFrame, QAbstractItemView, QListView, QApplication
)
from PyQt5.QtCore import Qt, QPoint, QRect, QEvent
from PyQt5.QtGui import QColor, QFont, QCursor, QPalette

class DesignScrollArea(QScrollArea):
    """自定义滚动区域，用于显示'画布'文字"""
    def __init__(self, parent=None, ui_control=None):
        super().__init__(parent)
        self.ui_control = ui_control
        
        # 创建标签显示"画布"
        self.label_tag = QLabel("画布", self)
        self.label_tag.setAlignment(Qt.AlignCenter)
        self.label_tag.setAttribute(Qt.WA_TransparentForMouseEvents)  # 鼠标穿透
        self.label_tag.setStyleSheet("background-color: transparent; color: #555555; border: none;")
        self.label_tag.setFont(QFont("Microsoft YaHei", 14))
        self.label_tag.adjustSize()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 居中显示标签
        if self.label_tag:
            x = (self.width() - self.label_tag.width()) // 2
            y = (self.height() - self.label_tag.height()) // 2
            self.label_tag.move(x, y)
            
    def update_style(self):
        if self.ui_control:
            self.label_tag.setStyleSheet(f"background-color: transparent; color: {self.ui_control.fg_color.name()}; border: none;")
            font = QFont(self.ui_control.font.family(), 14)
            self.label_tag.setFont(font)
            self.label_tag.adjustSize()
            # Re-center
            x = (self.width() - self.label_tag.width()) // 2
            y = (self.height() - self.label_tag.height()) // 2
            self.label_tag.move(x, y)


class UIControl:
    """封装所有UI控件的属性和行为，统一管理"""

    PRESET_THEMES = {
    "自定义": {},
    "现代简约": {
    "QPushButton": {
        "bg_color": "#3B82F6", "fg_color": "#FFFFFF", "font_size": 10, "bold": True,
        "visual_style": "扁平", "border_radius": 8, "border_width": 0, "border_color": "transparent"
    },
    "QLabel": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 0, "border_width": 0, "border_color": "transparent"
    },
    "QLineEdit": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QTextEdit": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QComboBox": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QCheckBox": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 4, "border_width": 1, "border_color": "#9CA3AF"
    },
    "QRadioButton": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 10, "border_width": 1, "border_color": "#9CA3AF"
    },
    "QGroupBox": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": True,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QSlider": {
        # 优化：滑块前景色与按钮主色一致，形成视觉呼应
        "bg_color": "#E5E7EB", "fg_color": "#3B82F6", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 4, "border_width": 0, "border_color": "transparent"
    },
    "QTabWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QListWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QTableWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QScrollArea": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QFrame": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#E5E7EB"
    }
    },
    "商务专业": {
    "QPushButton": {
        "bg_color": "#1E40AF", "fg_color": "#FFFFFF", "font_size": 10, "bold": True,
        "visual_style": "扁平", "border_radius": 6, "border_width": 0, "border_color": "transparent"
    },
    "QLabel": {
        "bg_color": "#F3F4F6", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "默认", "border_radius": 0, "border_width": 0, "border_color": "transparent"
    },
    "QLineEdit": {
        "bg_color": "#FFFFFF", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#D1D5DB"
    },
    "QTextEdit": {
        "bg_color": "#FFFFFF", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#D1D5DB"
    },
    "QComboBox": {
        "bg_color": "#FFFFFF", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#D1D5DB"
    },
    "QCheckBox": {
        "bg_color": "#F3F4F6", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "默认", "border_radius": 3, "border_width": 1, "border_color": "#6B7280"
    },
    "QRadioButton": {
        "bg_color": "#F3F4F6", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "默认", "border_radius": 10, "border_width": 1, "border_color": "#6B7280"
    },
    "QGroupBox": {
        "bg_color": "#F3F4F6", "fg_color": "#111827", "font_size": 10, "bold": True,
        "visual_style": "默认", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QSlider": {
        "bg_color": "#E5E7EB", "fg_color": "#1E40AF", "font_size": 10, "bold": False,
        "visual_style": "默认", "border_radius": 4, "border_width": 0, "border_color": "transparent"
    },
    "QTabWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "默认", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QListWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#D1D5DB"
    },
    "QTableWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#D1D5DB"
    },
    "QScrollArea": {
        "bg_color": "#F3F4F6", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "默认", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QFrame": {
        "bg_color": "#F3F4F6", "fg_color": "#111827", "font_size": 10, "bold": False,
        "visual_style": "默认", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    }
    },
    "活力青春": {
    "QPushButton": {
        # 优化：降低玫红饱和度，避免刺眼，增强质感
        "bg_color": "#DB2777", "fg_color": "#FFFFFF", "font_size": 11, "bold": True,
        "visual_style": "扁平", "border_radius": 12, "border_width": 0, "border_color": "transparent"
    },
    "QLabel": {
        "bg_color": "#FDF2F8", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "默认", "border_radius": 0, "border_width": 0, "border_color": "transparent"
    },
    "QLineEdit": {
        "bg_color": "#FDF2F8", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "圆角", "border_radius": 12, "border_width": 2, "border_color": "#DB2777"
    },
    "QTextEdit": {
        "bg_color": "#FDF2F8", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "圆角", "border_radius": 12, "border_width": 2, "border_color": "#DB2777"
    },
    "QComboBox": {
        "bg_color": "#FDF2F8", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "圆角", "border_radius": 12, "border_width": 2, "border_color": "#DB2777"
    },
    "QCheckBox": {
        "bg_color": "#FDF2F8", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "默认", "border_radius": 6, "border_width": 2, "border_color": "#DB2777"
    },
    "QRadioButton": {
        "bg_color": "#FDF2F8", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "默认", "border_radius": 12, "border_width": 2, "border_color": "#DB2777"
    },
    "QGroupBox": {
        "bg_color": "#FCE7F3", "fg_color": "#1F2937", "font_size": 11, "bold": True,
        "visual_style": "圆角", "border_radius": 16, "border_width": 2, "border_color": "#DB2777"
    },
    "QSlider": {
        "bg_color": "#FBCFE8", "fg_color": "#DB2777", "font_size": 11, "bold": False,
        "visual_style": "默认", "border_radius": 6, "border_width": 0, "border_color": "transparent"
    },
    "QTabWidget": {
        "bg_color": "#FDF2F8", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "圆角", "border_radius": 16, "border_width": 2, "border_color": "#DB2777"
    },
    "QListWidget": {
        "bg_color": "#FDF2F8", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "圆角", "border_radius": 12, "border_width": 2, "border_color": "#DB2777"
    },
    "QTableWidget": {
        "bg_color": "#FDF2F8", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "圆角", "border_radius": 12, "border_width": 2, "border_color": "#DB2777"
    },
    "QScrollArea": {
        "bg_color": "#FCE7F3", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "圆角", "border_radius": 16, "border_width": 2, "border_color": "#DB2777"
    },
    "QFrame": {
        "bg_color": "#FCE7F3", "fg_color": "#1F2937", "font_size": 11, "bold": False,
        "visual_style": "圆角", "border_radius": 16, "border_width": 2, "border_color": "#DB2777"
    }
    },
    "暗黑模式": {
    "QPushButton": {
        # 优化：提高紫色亮度，增强暗黑模式下的辨识度
        "bg_color": "#A78BFA", "fg_color": "#1F2937", "font_size": 10, "bold": True,
        "visual_style": "扁平", "border_radius": 8, "border_width": 0, "border_color": "transparent"
    },
    "QLabel": {
        "bg_color": "#1F2937", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 0, "border_width": 0, "border_color": "transparent"
    },
    "QLineEdit": {
        "bg_color": "#374151", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#4B5563"
    },
    "QTextEdit": {
        "bg_color": "#374151", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#4B5563"
    },
    "QComboBox": {
        "bg_color": "#374151", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#4B5563"
    },
    "QCheckBox": {
        "bg_color": "#1F2937", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 4, "border_width": 1, "border_color": "#9CA3AF"
    },
    "QRadioButton": {
        "bg_color": "#1F2937", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 10, "border_width": 1, "border_color": "#9CA3AF"
    },
    "QGroupBox": {
        "bg_color": "#1F2937", "fg_color": "#F3F4F6", "font_size": 9, "bold": True,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#374151"
    },
    "QSlider": {
        "bg_color": "#4B5563", "fg_color": "#A78BFA", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 4, "border_width": 0, "border_color": "transparent"
    },
    "QTabWidget": {
        "bg_color": "#1F2937", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#374151"
    },
    "QListWidget": {
        "bg_color": "#374151", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#4B5563"
    },
    "QTableWidget": {
        "bg_color": "#374151", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 8, "border_width": 1, "border_color": "#4B5563"
    },
    "QScrollArea": {
        "bg_color": "#1F2937", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#374151"
    },
    "QFrame": {
        "bg_color": "#1F2937", "fg_color": "#F3F4F6", "font_size": 9, "bold": False,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#374151"
    }
    },
    "Material Design": {
    "QPushButton": {
        "bg_color": "#8B5CF6", "fg_color": "#FFFFFF", "font_size": 10, "bold": True,
        "visual_style": "扁平", "border_radius": 6, "border_width": 0, "border_color": "transparent"
    },
    "QLabel": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 0, "border_width": 0, "border_color": "transparent"
    },
    "QLineEdit": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QTextEdit": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QComboBox": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QCheckBox": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 3, "border_width": 2, "border_color": "#8B5CF6"
    },
    "QRadioButton": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 10, "border_width": 2, "border_color": "#8B5CF6"
    },
    "QGroupBox": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": True,
        "visual_style": "默认", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QSlider": {
        "bg_color": "#E5E7EB", "fg_color": "#8B5CF6", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 4, "border_width": 0, "border_color": "transparent"
    },
    "QTabWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QListWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QTableWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QScrollArea": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QFrame": {
        "bg_color": "#F9FAFB", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    }
    },
    "Fluent Design": {
    "QPushButton": {
        # 优化：调整为 Fluent 标志性的天蓝，更贴合设计语言
        "bg_color": "#0078D4", "fg_color": "#FFFFFF", "font_size": 10, "bold": True,
        "visual_style": "扁平", "border_radius": 6, "border_width": 0, "border_color": "transparent"
    },
    "QLabel": {
        "bg_color": "#F3F4F6", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 0, "border_width": 0, "border_color": "transparent"
    },
    "QLineEdit": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QTextEdit": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QComboBox": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QCheckBox": {
        "bg_color": "#F3F4F6", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 3, "border_width": 1, "border_color": "#9CA3AF"
    },
    "QRadioButton": {
        "bg_color": "#F3F4F6", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 10, "border_width": 1, "border_color": "#9CA3AF"
    },
    "QGroupBox": {
        "bg_color": "#F3F4F6", "fg_color": "#1F2937", "font_size": 9, "bold": True,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QSlider": {
        "bg_color": "#E5E7EB", "fg_color": "#0078D4", "font_size": 9, "bold": False,
        "visual_style": "默认", "border_radius": 4, "border_width": 0, "border_color": "transparent"
    },
    "QTabWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QListWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QTableWidget": {
        "bg_color": "#FFFFFF", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "描边", "border_radius": 6, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QScrollArea": {
        "bg_color": "#F3F4F6", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#E5E7EB"
    },
    "QFrame": {
        "bg_color": "#F3F4F6", "fg_color": "#1F2937", "font_size": 9, "bold": False,
        "visual_style": "圆角", "border_radius": 10, "border_width": 1, "border_color": "#E5E7EB"
    }
    }
    }
    
    @staticmethod
    def get_control_count(parent_canvas, control_type):
        """获取画布上指定类型控件的数量"""
        if parent_canvas is None or not hasattr(parent_canvas, 'controls'):
            return 0
        count = 0
        for control in parent_canvas.controls:
            if control.type == control_type:
                count += 1
        return count
    
    def __init__(self, control_type, parent_canvas):
        # 基础属性
        self.id = str(uuid.uuid4())[:8]  # 唯一标识
        self.type = control_type  # 控件类型（QPushButton/QLabel等）
        
        # 获取同类型控件数量
        control_count = self.get_control_count(parent_canvas, control_type)
        
        # 中文类型名称映射
        type_names = {
            "QPushButton": "按钮",
            "QLabel": "标签",
            "QLineEdit": "输入框",
            "QTextEdit": "文本框",
            "QComboBox": "下拉框",
            "QListWidget": "列表框",
            "QTableWidget": "表格",
            "QCheckBox": "复选框",
            "QRadioButton": "单选框",
            "QTabWidget": "选项卡",
            "QGroupBox": "标签容器",
            "QSlider": "滑块",
            "QScrollArea": "画布",
            "QFrame": "父容器"
        }
        
        # 设置中文名称
        chinese_type = type_names.get(control_type, control_type)
        self.name = f"{chinese_type}_{str(control_count + 1).zfill(3)}"  # 控件名称，如"按钮_001"
        self.text = chinese_type  # 显示文本
        
        # 根据控件类型设置默认尺寸
        if control_type == "QLabel":
            self.rect = QRect(100, 100, 50, 30)  # 标签默认尺寸
        elif control_type == "QPushButton":
            self.rect = QRect(100, 100, 50, 30)  # 按钮默认尺寸
        elif control_type == "QLineEdit":
            self.rect = QRect(100, 100, 150, 30)  # 输入框默认尺寸
        elif control_type == "QTextEdit":
            self.rect = QRect(100, 100, 150, 100)  # 文本框默认尺寸
        elif control_type == "QListWidget":
            self.rect = QRect(100, 100, 150, 100)  # 列表框默认尺寸
        elif control_type == "QTableWidget":
            self.rect = QRect(100, 100, 450, 70)  # 表格默认尺寸
        elif control_type == "QTabWidget":
            self.rect = QRect(100, 100, 300, 200)  # 选项卡默认尺寸
        elif control_type == "QGroupBox":
            self.rect = QRect(100, 100, 200, 150)  # 容器默认尺寸
        elif control_type == "QSlider":
            self.rect = QRect(100, 100, 100, 20)   # 滑块默认尺寸
        elif control_type == "QScrollArea":
            self.rect = QRect(100, 100, 200, 150)  # 画布默认尺寸
        elif control_type == "QFrame":
            self.rect = QRect(100, 100, 200, 150)  # 父容器默认尺寸
        else:
            self.rect = QRect(100, 100, 100, 40)  # 其他控件默认尺寸
        
        self.bg_color = QColor(255, 255, 255)  # 背景色
        self.fg_color = QColor(44, 62, 80)  # 文字色 (#2c3e50)
        self.font = QFont("Microsoft YaHei", 9)  # 字体
        self.use_style = True  # 是否使用QSS样式表
        self.preset_style = "默认风格"  # 当前使用的预设样式
        self.visual_style = "默认"  # 视觉风格: 默认, 扁平, 圆角, 描边, 渐变
        self.border_radius = 4 # 圆角半径
        self.border_width = 1 # 边框宽度
        self.border_color = QColor(224, 224, 224) # 边框颜色 (#e0e0e0)
        self.events = []  # 事件绑定列表，每个元素为 [事件名称, 回调函数]

        # 记录哪些属性被用户手动设置（用于全局预设样式覆盖逻辑）
        self.custom_properties = set()  # 存储被手动设置的属性名称

        # 控件特有属性
        self.checked = False  # 复选框/单选框选中状态
        self.read_only = False  # 输入框只读状态
        self.align = Qt.AlignCenter  # 文本对齐方式（默认居中）
        self.wrap_text = False  # 标签文本自动换行
        self.max_length = 0  # 输入框最大长度（0表示无限制）
        self.password_mode = False  # 输入框密码模式
        self.placeholder = ""  # 输入框占位符文本
        self.enabled = True  # 控件是否启用
        self.visible = True  # 控件是否可见
        self.locked = False  # 控件是否锁定
        self.show_bg_color = True  # 锁定时是否显示背景色
        
        # 滚动条设置
        self.h_scrollbar = True  # 水平滚动条 (True=AsNeeded, False=AlwaysOff)
        self.v_scrollbar = True  # 垂直滚动条 (True=AsNeeded, False=AlwaysOff)
        
        # QSlider特有属性
        self.slider_minimum = 0
        self.slider_maximum = 100
        self.slider_value = 0
        self.slider_orientation = 1  # 1=水平, 2=垂直
        
        # QTextEdit特有属性
        self.text_edit_read_only = False  # 文本框只读状态
        self.text_edit_placeholder = ""  # 文本框占位符文本
        self.text_edit_wrap_mode = 1  # 自动换行模式（0=不换行，1=按词换行，2=按字符换行）
        self.text_edit_alignment = 1  # 文本对齐方式（0=左对齐，1=居中，2=右对齐，默认居中）
        
        # QComboBox特有属性
        self.combo_editable = False  # 下拉框可编辑状态
        
        # QListWidget特有属性
        self.list_selection_mode = 0  # 列表框选择模式（0=单选，1=多选，2=扩展选择）
        self.list_items = ["列表项1", "列表项2", "列表项3"]  # 列表项内容
        self.list_edit_triggers = 0  # 编辑触发方式（0=不可编辑，1=双击编辑，2=选中编辑，3=任意编辑）
        self.list_alternating_row_colors = False  # 交替行颜色
        self.list_sorting_enabled = False  # 启用排序
        self.list_view_mode = 0  # 视图模式（0=列表模式，1=图标模式）
        self.list_drag_drop_mode = 0  # 拖拽模式（0=不可拖拽，1=内部拖拽，2=拖拽移动，3=拖拽复制）
        self.list_resize_mode = 0  # 调整大小模式（0=固定，1=自适应）
        self.list_movement = 0  # 移动模式（0=静态，1=自由，2=吸附）

        # QTableWidget特有属性
        self.table_row_count = 3  # 表格行数
        self.table_column_count = 3  # 表格列数
        self.table_data = [["单元格1", "单元格2", "单元格3"],
                          ["单元格4", "单元格5", "单元格6"],
                          ["单元格7", "单元格8", "单元格9"]]  # 表格数据
        self.table_headers = ["列1", "列2", "列3"]  # 表格列标题
        self.table_row_headers = ["行1", "行2", "行3"]  # 表格行标题
        self.table_column_widths = [100, 100, 100]  # 列宽
        self.table_row_heights = [30, 30, 30]  # 行高
        self.table_show_grid = True  # 显示网格
        self.table_selection_mode = 0  # 选择模式（0=单选，1=多选，2=整行选择，3=整列选择）
        self.table_edit_triggers = 0  # 编辑触发方式（0=不可编辑，1=双击编辑，2=选中编辑，3=任意编辑）
        self.table_alternating_row_colors = False  # 交替行颜色
        self.table_sorting_enabled = False  # 启用排序
        self.table_corner_button_enabled = True  # 角按钮启用

        # QTabWidget特有属性
        self.tab_position = 0  # 选项卡位置（0=北，1=南，2=西，3=东）
        self.tab_shape = 0  # 选项卡形状（0=圆角，1=三角）
        self.tab_closable = False  # 选项卡可关闭
        self.tab_movable = False  # 选项卡可移动
        self.tab_current_index = 0  # 当前选中的选项卡索引
        self.tab_titles = ["选项卡1", "选项卡2", "选项卡3"]  # 选项卡标题列表
        self.tab_count = 3  # 选项卡数量

        # 关联的UI对象
        self.parent_canvas = parent_canvas  # 画布对象
        self.widget = None  # 画布上的预览控件
        self.list_item = None  # 控件列表中的项

        # 父子关系管理
        self.parent = None  # 父控件（容器控件）
        self.parent_tab_index = -1 # 如果父控件是选项卡，记录所在的标签页索引
        self.children = []  # 子控件列表

    def create_widget(self):
        """创建画布上的预览控件"""
        # 根据类型创建控件
        if self.type == "QPushButton":
            self.widget = QPushButton(self.text, self.parent_canvas)
        elif self.type == "QLabel":
            self.widget = QLabel(self.text, self.parent_canvas)
        elif self.type == "QLineEdit":
            self.widget = QLineEdit(self.text, self.parent_canvas)
        elif self.type == "QCheckBox":
            self.widget = QCheckBox(self.text, self.parent_canvas)
        elif self.type == "QRadioButton":
            self.widget = QRadioButton(self.text, self.parent_canvas)
        elif self.type == "QTextEdit":
            self.widget = QTextEdit(self.parent_canvas)
        elif self.type == "QComboBox":
            self.widget = QComboBox(self.parent_canvas)
            self.widget.addItem("选项1")
            self.widget.addItem("选项2")
            self.widget.addItem("选项3")
        elif self.type == "QListWidget":
            self.widget = QListWidget(self.parent_canvas)
            # 添加默认列表项
            for item in self.list_items:
                self.widget.addItem(item)
        elif self.type == "QTableWidget":
            self.widget = QTableWidget(self.parent_canvas)
        elif self.type == "QTabWidget":
            self.widget = QTabWidget(self.parent_canvas)
            # 添加默认选项卡
            self.tab_widgets = []
            for i in range(self.tab_count):
                if i < len(self.tab_titles):
                    tab_widget = QWidget()
                    tab_widget.setObjectName(f"tab_widget_{self.id}_{i}")
                    tab_layout = QVBoxLayout(tab_widget)
                    tab_layout.setContentsMargins(0, 0, 0, 0)
                    tab_layout.setSpacing(0)
                    self.widget.addTab(tab_widget, self.tab_titles[i])
                    self.tab_widgets.append(tab_widget)
            if self.tab_current_index < self.tab_count:
                self.widget.setCurrentIndex(self.tab_current_index)
        elif self.type == "QGroupBox":
            self.widget = QGroupBox(self.parent_canvas)
        elif self.type == "QSlider":
            self.widget = QSlider(self.parent_canvas)
        elif self.type == "QScrollArea":
            self.widget = DesignScrollArea(self.parent_canvas, self)
        elif self.type == "QFrame":
            self.widget = QFrame(self.parent_canvas)
            self.widget.setFrameShape(QFrame.StyledPanel)
            self.widget.setFrameShadow(QFrame.Raised)
        else:
            return

        # 设置objectName以区分画布控件，避免受全局样式影响
        self.widget.setObjectName("design_canvas_widget")

        # 调用统一的更新方法应用所有属性和样式
        self.update_widget()
        self.widget.show()

        # 如果有父控件，需要将widget添加到父控件中
        if self.parent:
            self.attach_to_parent(self.parent)

        # 绑定事件
        if self.type != "QTabWidget":
            self.widget.mousePressEvent = lambda e: self.on_mouse_press(e)
            self.widget.mouseReleaseEvent = lambda e: self.on_mouse_release(e)
        
        self.widget.mouseMoveEvent = lambda e: self.on_mouse_move(e)

    def attach_to_parent(self, parent_control):
        """将控件挂载到父控件上（包括逻辑关系和UI关系）"""
        if not parent_control:
            return

        # 1. 建立逻辑关系（如果尚未建立）
        if self.parent != parent_control:
            self.parent = parent_control
            if self not in parent_control.children:
                parent_control.children.append(self)

        # 2. 建立UI关系
        if not self.widget:
            return
            
        # 特殊处理：如果父控件是主窗口，将Widget挂载到画布上
        if parent_control.type == "MainWindow":
            self.widget.setParent(self.parent_canvas)
            # 计算绝对坐标，考虑主窗口的标题栏高度
            abs_x = self.parent_canvas.main_window_props.x + self.rect.x()
            abs_y = self.parent_canvas.main_window_props.y + self.parent_canvas.main_window_props.title_height + self.rect.y()
            self.widget.setGeometry(abs_x, abs_y, self.rect.width(), self.rect.height())
            self.widget.show()
            return

        # 常规处理：挂载到父控件的Widget上
        if not parent_control.widget:
            return

        if parent_control.type == "QTabWidget":
            # 对于QTabWidget，添加到指定标签页
            tab_widget = parent_control.widget
            target_tab = None
            
            # 优先使用 parent_tab_index
            if self.parent_tab_index >= 0 and self.parent_tab_index < tab_widget.count():
                target_tab = tab_widget.widget(self.parent_tab_index)
            # 其次尝试使用当前选中的Tab（适用于新建控件时）
            elif tab_widget.count() > 0:
                target_tab = tab_widget.currentWidget()
                self.parent_tab_index = tab_widget.currentIndex()
            
            if target_tab:
                self.widget.setParent(target_tab)
                # 坐标转换：rect是相对于QTabWidget的，Widget是相对于Page的
                # 需要减去Page的偏移量（主要是TabBar高度）
                content_rect = parent_control.get_content_rect()
                local_rect = QRect(self.rect)
                local_rect.translate(0, -content_rect.y())
                self.widget.setGeometry(local_rect)
                self.widget.show()
        else:
            # 对于其他容器控件，直接添加到容器中
            self.widget.setParent(parent_control.widget)
            self.widget.setGeometry(self.rect)
            self.widget.show()

    def update_widget(self):
        """更新控件样式和属性（仅更新样式和属性，不涉及位置和大小）"""
        if not self.widget:
            return
        
        # 更新通用属性
        self.widget.setVisible(self.visible)
        self.widget.setEnabled(self.enabled)
        
        if self.locked:
            self.widget.setCursor(QCursor(Qt.ForbiddenCursor))
        else:
            self.widget.setCursor(QCursor(Qt.PointingHandCursor))
            
        # 更新控件特有属性 (Logic Properties)
        self.update_specific_properties()

        # 更新样式 (Visual Style)
        if self.use_style:
            self.update_stylesheet()
        else:
            self.update_native_style()
        
        # 确保控件可见
        self.widget.raise_()
        
    def update_geometry(self):
        """更新控件的位置和大小"""
        if not self.widget:
            return
            
        if self.parent and self.parent.type != "MainWindow":
            # 控件在普通父容器内
            content_rect = self.parent.get_content_rect()
            
            # 对于QTabWidget，需要特殊处理坐标
            if self.parent.type == "QTabWidget":
                # 坐标转换：rect是相对于QTabWidget的，Widget是相对于Page的
                # 需要减去Page的偏移量（主要是TabBar高度）
                local_rect = QRect(self.rect)
                local_rect.translate(0, -content_rect.y())
                self.widget.setGeometry(local_rect)
            else:
                # 对于其他容器控件（如QGroupBox），直接使用self.rect设置位置
                # 避免与attach_to_parent方法的处理逻辑不一致
                self.widget.setGeometry(self.rect)
        elif self.parent and self.parent.type == "MainWindow":
            # 控件在主窗口内，需要计算绝对坐标并加上标题栏高度
            abs_x = self.parent_canvas.main_window_props.x + self.rect.x()
            abs_y = self.parent_canvas.main_window_props.y + self.parent_canvas.main_window_props.title_height + self.rect.y()
            self.widget.setGeometry(abs_x, abs_y, self.rect.width(), self.rect.height())
        else:
            # 没有父容器
            self.widget.setGeometry(self.rect)

        # 特殊控件辅助组件更新
        if self.type == "QScrollArea" and isinstance(self.widget, DesignScrollArea):
            self.widget.update_style()

        # 5. 更新文本和滚动条
        # 注意：对于复杂控件（如列表、表格、Tab），不直接设置text
        if hasattr(self.widget, "setText") and self.type not in ["QListWidget", "QTableWidget", "QComboBox", "QTabWidget", "QTextEdit"]:
             self.widget.setText(self.text)
        elif hasattr(self.widget, "setPlaceholderText") and self.type not in ["QTextEdit"]: # QTextEdit handled in specific
             self.widget.setPlaceholderText(self.text)
             
        if self.parent_canvas:
            self.parent_canvas.update()
            
        if self.type in ["QScrollArea", "QTextEdit", "QListWidget", "QTableWidget", "QTreeWidget"]:
            policy_h = Qt.ScrollBarAsNeeded if self.h_scrollbar else Qt.ScrollBarAlwaysOff
            policy_v = Qt.ScrollBarAsNeeded if self.v_scrollbar else Qt.ScrollBarAlwaysOff
            if hasattr(self.widget, "setHorizontalScrollBarPolicy"):
                self.widget.setHorizontalScrollBarPolicy(policy_h)
            if hasattr(self.widget, "setVerticalScrollBarPolicy"):
                self.widget.setVerticalScrollBarPolicy(policy_v)

    def update_native_style(self):
        """应用原生样式（字体、颜色、背景）"""
        # 1. 清除样式表
        self.widget.setStyleSheet("")
        
        # 2. 设置字体
        # 强制创建新对象以确保刷新
        apply_font = QFont(self.font.family(), self.font.pointSize())
        apply_font.setBold(self.font.bold())
        apply_font.setItalic(self.font.italic())
        apply_font.setUnderline(self.font.underline())
        apply_font.setStrikeOut(self.font.strikeOut())
        self.widget.setFont(apply_font)
        
        # 3. 设置调色板 (颜色)
        palette = QApplication.palette(self.widget)
        palette.setColor(QPalette.Window, self.bg_color)
        palette.setColor(QPalette.WindowText, self.fg_color)
        palette.setColor(QPalette.Base, self.bg_color)
        palette.setColor(QPalette.Text, self.fg_color)
        palette.setColor(QPalette.Button, self.bg_color)
        palette.setColor(QPalette.ButtonText, self.fg_color)
        self.widget.setPalette(palette)
        
        # 4. 自动填充背景
        # 为按钮开启自动填充背景，确保按钮背景色能正确显示
        if self.type in ["QLabel", "QFrame", "QScrollArea", "QGroupBox", "QWidget", "QPushButton"]:
             self.widget.setAutoFillBackground(True)
        else:
             self.widget.setAutoFillBackground(False)

    def update_specific_properties(self):
        """更新控件特有属性"""
        if self.type == "QLabel":
            self.widget.setAlignment(self.align)
            self.widget.setWordWrap(self.wrap_text)
        elif self.type == "QLineEdit":
            self.widget.setReadOnly(self.read_only)
            self.widget.setEchoMode(QLineEdit.Password if self.password_mode else QLineEdit.Normal)
            if self.placeholder:
                self.widget.setPlaceholderText(self.placeholder)
            if self.max_length > 0:
                self.widget.setMaxLength(self.max_length)
        elif self.type == "QCheckBox" or self.type == "QRadioButton":
            self.widget.setChecked(self.checked)
        elif self.type == "QTextEdit":
            self.widget.setReadOnly(self.text_edit_read_only)
            if self.text_edit_placeholder:
                self.widget.setPlaceholderText(self.text_edit_placeholder)
            if self.text_edit_wrap_mode == 0:
                self.widget.setLineWrapMode(QTextEdit.NoWrap)
            elif self.text_edit_wrap_mode == 1:
                self.widget.setLineWrapMode(QTextEdit.WidgetWidth)
            elif self.text_edit_wrap_mode == 2:
                self.widget.setLineWrapMode(QTextEdit.FixedPixelWidth)
            if self.text_edit_alignment == 0:
                self.widget.setAlignment(Qt.AlignLeft)
            elif self.text_edit_alignment == 1:
                self.widget.setAlignment(Qt.AlignCenter)
            elif self.text_edit_alignment == 2:
                self.widget.setAlignment(Qt.AlignRight)
        elif self.type == "QPushButton":
            # 确保按钮文本正确更新
            if hasattr(self.widget, "setText"):
                self.widget.setText(self.text)
        elif self.type == "QComboBox":
            self.widget.setEditable(self.combo_editable)
        elif self.type == "QListWidget":
            if self.list_selection_mode == 0:
                self.widget.setSelectionMode(QListWidget.SingleSelection)
            elif self.list_selection_mode == 1:
                self.widget.setSelectionMode(QListWidget.MultiSelection)
            elif self.list_selection_mode == 2:
                self.widget.setSelectionMode(QListWidget.ExtendedSelection)
            
            # Edit Triggers
            if self.list_edit_triggers == 0:
                self.widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            elif self.list_edit_triggers == 1:
                self.widget.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
            elif self.list_edit_triggers == 2:
                self.widget.setEditTriggers(QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
            elif self.list_edit_triggers == 3:
                self.widget.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
            
            self.widget.setAlternatingRowColors(self.list_alternating_row_colors)
            self.widget.setSortingEnabled(self.list_sorting_enabled)
            
            if self.list_view_mode == 0:
                self.widget.setViewMode(QListView.ListMode)
            elif self.list_view_mode == 1:
                self.widget.setViewMode(QListView.IconMode)
            
            # Drag Drop
            if self.list_drag_drop_mode == 0:
                self.widget.setDragDropMode(QAbstractItemView.NoDragDrop)
            elif self.list_drag_drop_mode == 1:
                self.widget.setDragDropMode(QAbstractItemView.InternalMove)
            elif self.list_drag_drop_mode == 2:
                self.widget.setDragDropMode(QAbstractItemView.DragDrop)
            elif self.list_drag_drop_mode == 3:
                self.widget.setDragDropMode(QAbstractItemView.DropOnly)
                
            # Resize Mode
            if self.list_resize_mode == 0:
                self.widget.setResizeMode(QListView.Fixed)
            elif self.list_resize_mode == 1:
                self.widget.setResizeMode(QListView.Adjust)
                
            # Movement
            if self.list_movement == 0:
                self.widget.setMovement(QListView.Static)
            elif self.list_movement == 1:
                self.widget.setMovement(QListView.Free)
            elif self.list_movement == 2:
                self.widget.setMovement(QListView.Snap)

            # Update Items
            self.widget.clear()
            for item in self.list_items:
                self.widget.addItem(item)
                
        elif self.type == "QTableWidget":
            self.widget.setRowCount(self.table_row_count)
            self.widget.setColumnCount(self.table_column_count)
            self.widget.setHorizontalHeaderLabels(self.table_headers)
            self.widget.setVerticalHeaderLabels(self.table_row_headers)
            
            for col_idx, width in enumerate(self.table_column_widths):
                if col_idx < self.table_column_count:
                    self.widget.setColumnWidth(col_idx, width)
            for row_idx, height in enumerate(self.table_row_heights):
                if row_idx < self.table_row_count:
                    self.widget.setRowHeight(row_idx, height)
            
            self.widget.clearContents()
            for row in range(self.table_row_count):
                for col in range(self.table_column_count):
                    if row < len(self.table_data) and col < len(self.table_data[row]):
                        item = QTableWidgetItem(self.table_data[row][col])
                        item.setTextAlignment(Qt.AlignCenter)
                        self.widget.setItem(row, col, item)

            if self.table_selection_mode == 0:
                self.widget.setSelectionMode(QAbstractItemView.SingleSelection)
                self.widget.setSelectionBehavior(QAbstractItemView.SelectItems)
            elif self.table_selection_mode == 1:
                self.widget.setSelectionMode(QAbstractItemView.MultiSelection)
                self.widget.setSelectionBehavior(QAbstractItemView.SelectItems)
            elif self.table_selection_mode == 2:
                self.widget.setSelectionMode(QAbstractItemView.SingleSelection)
                self.widget.setSelectionBehavior(QAbstractItemView.SelectRows)
            elif self.table_selection_mode == 3:
                self.widget.setSelectionMode(QAbstractItemView.SingleSelection)
                self.widget.setSelectionBehavior(QAbstractItemView.SelectColumns)
            
            if self.table_edit_triggers == 0:
                self.widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            elif self.table_edit_triggers == 1:
                self.widget.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
            elif self.table_edit_triggers == 2:
                self.widget.setEditTriggers(QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
            elif self.table_edit_triggers == 3:
                self.widget.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
            
            self.widget.setAlternatingRowColors(self.table_alternating_row_colors)
            self.widget.setSortingEnabled(self.table_sorting_enabled)
            self.widget.setShowGrid(self.table_show_grid)
            self.widget.setCornerButtonEnabled(self.table_corner_button_enabled)

        elif self.type == "QTabWidget":
            if self.tab_position == 0: self.widget.setTabPosition(QTabWidget.North)
            elif self.tab_position == 1: self.widget.setTabPosition(QTabWidget.South)
            elif self.tab_position == 2: self.widget.setTabPosition(QTabWidget.West)
            elif self.tab_position == 3: self.widget.setTabPosition(QTabWidget.East)
            
            if self.tab_shape == 0: self.widget.setTabShape(QTabWidget.Rounded)
            elif self.tab_shape == 1: self.widget.setTabShape(QTabWidget.Triangular)
            
            self.widget.setTabsClosable(self.tab_closable)
            self.widget.setMovable(self.tab_movable)
            
            # Recreate tabs if count changes (basic logic from original)
            # Original code cleared and re-added. We should do same for consistency.
            if self.widget.count() != self.tab_count:
                # This is a bit destructive but matches original logic
                self.widget.clear()
                self.tab_widgets = []
                for i in range(self.tab_count):
                    if i < len(self.tab_titles):
                        tab_widget = QWidget()
                        tab_widget.setObjectName(f"tab_widget_{self.id}_{i}")
                        tab_layout = QVBoxLayout(tab_widget)
                        tab_layout.setContentsMargins(0, 0, 0, 0)
                        tab_layout.setSpacing(0)
                        self.widget.addTab(tab_widget, self.tab_titles[i])
                        self.tab_widgets.append(tab_widget)
                if self.tab_current_index < self.tab_count:
                    self.widget.setCurrentIndex(self.tab_current_index)
            else:
                # Just update titles
                for i in range(self.widget.count()):
                    if i < len(self.tab_titles):
                        self.widget.setTabText(i, self.tab_titles[i])
            
        elif self.type == "QGroupBox":
            self.widget.setTitle(self.text)
            
        elif self.type == "QSlider":
            self.widget.setOrientation(Qt.Horizontal if self.slider_orientation == 1 else Qt.Vertical)
            self.widget.setMinimum(self.slider_minimum)
            self.widget.setMaximum(self.slider_maximum)
            self.widget.setValue(self.slider_value)
        
        elif self.type == "QScrollArea":
            if isinstance(self.widget, DesignScrollArea):
                self.widget.update_style()

    def get_stylesheet(self):
        """生成QSS样式字符串"""
        # 基础颜色处理
        if self.locked and self.show_bg_color:
            bg_color_str = "rgba(200, 200, 200, 0.5)"
        else:
            bg_color_str = self.bg_color.name()
            
        fg_color_str = self.fg_color.name()
        
        # 根据视觉风格调整样式
        style_css = ""
        
        # 动态样式属性
        border_radius_str = f"{self.border_radius}px"
        border_width_str = f"{self.border_width}px"
        border_color_str = self.border_color.name()
        
        if self.type == "QPushButton":
            if self.visual_style == "扁平":
                style_css = f"""
                    QPushButton {{
                        background-color: {bg_color_str};
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: none;
                        border-radius: {border_radius_str};
                        padding: 4px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.bg_color.lighter(110).name()};
                    }}
                    QPushButton:pressed {{
                        background-color: {self.bg_color.darker(110).name()};
                    }}
                """
            elif self.visual_style == "圆角":
                style_css = f"""
                    QPushButton {{
                        background-color: {bg_color_str};
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: {border_width_str} solid {border_color_str};
                        border-radius: {border_radius_str};
                        padding: 4px 15px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.bg_color.lighter(110).name()};
                    }}
                    QPushButton:pressed {{
                        background-color: {self.bg_color.darker(110).name()};
                    }}
                """
            elif self.visual_style == "描边":
                style_css = f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: {border_width_str} solid {bg_color_str};
                        border-radius: {border_radius_str};
                        padding: 4px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {bg_color_str};
                        color: #FFFFFF;
                    }}
                    QPushButton:pressed {{
                        background-color: {self.bg_color.darker(110).name()};
                        color: #FFFFFF;
                    }}
                """
            elif self.visual_style == "渐变":
                style_css = f"""
                    QPushButton {{
                        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 {self.bg_color.lighter(120).name()}, stop:1 {self.bg_color.darker(110).name()});
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: {border_width_str} solid {self.bg_color.darker(130).name()};
                        border-radius: {border_radius_str};
                        padding: 4px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 {self.bg_color.lighter(130).name()}, stop:1 {self.bg_color.name()});
                    }}
                    QPushButton:pressed {{
                        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 {self.bg_color.darker(110).name()}, stop:1 {self.bg_color.darker(130).name()});
                    }}
                """
            else: # 默认
                style_css = f"""
                    QPushButton {{
                        background-color: {bg_color_str};
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: {border_width_str} solid {border_color_str};
                        border-radius: {border_radius_str};
                        padding: 4px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.bg_color.lighter(110).name()};
                    }}
                    QPushButton:pressed {{
                        background-color: {self.bg_color.darker(110).name()};
                    }}
                """
            
        elif self.type == "QLineEdit":
            if self.visual_style == "扁平":
                style_css = f"""
                    QLineEdit {{
                        background-color: {bg_color_str};
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: none;
                        border-bottom: {border_width_str} solid {border_color_str};
                        padding: 4px 6px;
                    }}
                    QLineEdit:focus {{
                        border-bottom: 2px solid #5c9aff;
                    }}
                """
            elif self.visual_style == "圆角":
                style_css = f"""
                    QLineEdit {{
                        background-color: {bg_color_str};
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: {border_width_str} solid {border_color_str};
                        border-radius: {border_radius_str};
                        padding: 4px 10px;
                    }}
                    QLineEdit:focus {{
                        border: 2px solid #5c9aff;
                    }}
                """
            else: # 默认
                style_css = f"""
                    QLineEdit {{
                        background-color: {bg_color_str};
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: {border_width_str} solid {border_color_str};
                        border-radius: {border_radius_str};
                        padding: 4px 6px;
                    }}
                    QLineEdit:focus {{
                        border: 2px solid #0066cc;
                    }}
                """
            
        elif self.type == "QLabel":
            # Label usually simple, but we can support border/radius
            border = "none"
            radius = "0px"
            padding = "2px"
            
            if self.visual_style == "描边":
                border = f"{border_width_str} solid {fg_color_str}"
                radius = f"{border_radius_str}"
                padding = "4px"
            elif self.visual_style == "圆角":
                radius = f"{border_radius_str}"
                padding = "4px"
            elif self.visual_style == "默认" and self.border_width > 0:
                 border = f"{border_width_str} solid {border_color_str}"
                 radius = f"{border_radius_str}"
            
            style_css = f"""
                QLabel {{
                    background-color: {bg_color_str};
                    color: {fg_color_str};
                    font-family: {self.font.family()};
                    font-size: {self.font.pointSize()}px;
                    border: {border};
                    border-radius: {radius};
                    padding: {padding};
                }}
            """
            
        elif self.type == "QGroupBox":
            # GroupBox styles
            if self.visual_style == "扁平":
                style_css = f"""
                    QGroupBox {{
                        background-color: {bg_color_str};
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: none;
                        border-top: {border_width_str} solid {border_color_str};
                        margin-top: 8px;
                    }}
                    QGroupBox::title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 0 3px;
                        left: 0px;
                        color: {fg_color_str};
                    }}
                """
            elif self.visual_style == "圆角":
                style_css = f"""
                    QGroupBox {{
                        background-color: {bg_color_str};
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: {border_width_str} solid {border_color_str};
                        border-radius: {border_radius_str};
                        margin-top: 8px;
                    }}
                    QGroupBox::title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 0 3px;
                        left: 10px;
                    }}
                """
            else: # 默认
                style_css = f"""
                    QGroupBox {{
                        background-color: transparent;
                        color: {fg_color_str};
                        font-family: {self.font.family()};
                        font-size: {self.font.pointSize()}px;
                        border: 1px solid #e0e0e0;
                        border-radius: 3px;
                        margin-top: 8px;
                    }}
                    QGroupBox::title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 0 3px;
                        left: 10px;
                        color: #5c9aff;
                    }}
                """

        # 其他控件使用原有逻辑，稍作修改以使用预计算的变量
        elif self.type == "QCheckBox":
            style_css = f"""
                QCheckBox {{
                    background-color: {bg_color_str};
                    color: {fg_color_str};
                    font-family: {self.font.family()};
                    font-size: {self.font.pointSize()}px;
                    border: none;
                    padding: 2px;
                    spacing: 5px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {border_color_str};
                    border-radius: 4px;
                    background-color: #ffffff;
                }}
                QCheckBox::indicator:hover {{
                    border: 2px solid #5c9aff;
                }}
                QCheckBox::indicator:checked {{
                    background-color: #5c9aff;
                    border: 2px solid #5c9aff;
                }}
            """
        elif self.type == "QRadioButton":
            style_css = f"""
                QRadioButton {{
                    background-color: {bg_color_str};
                    color: {fg_color_str};
                    font-family: {self.font.family()};
                    font-size: {self.font.pointSize()}px;
                    border: none;
                    padding: 2px;
                    spacing: 5px;
                }}
                QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 1px solid {border_color_str};
                    border-radius: 8px;
                    background-color: transparent;
                }}
                QRadioButton::indicator:checked {{
                    background-color: #5c9aff;
                    border: 1px solid #5c9aff;
                }}
            """
        elif self.type == "QTextEdit":
            style_css = f"""
                QTextEdit {{
                    background-color: {bg_color_str};
                    color: {fg_color_str};
                    font-family: {self.font.family()};
                    font-size: {self.font.pointSize()}px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 4px 6px;
                }}
                QTextEdit:focus {{
                    border: 2px solid #5c9aff;
                }}
            """
        elif self.type == "QComboBox":
            style_css = f"""
                QComboBox {{
                    background-color: {bg_color_str};
                    color: {fg_color_str};
                    font-family: {self.font.family()};
                    font-size: {self.font.pointSize()}px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 4px 6px;
                    min-height: 20px;
                }}
                QComboBox:hover {{
                    border: 2px solid #5c9aff;
                }}
                QComboBox::drop-down {{
                    border: none;
                }}
                QComboBox::down-arrow {{
                    width: 12px;
                    height: 12px;
                }}
            """
        elif self.type == "QListWidget":
            style_css = f"""
                QListWidget {{
                    background-color: {bg_color_str};
                    color: {fg_color_str};
                    font-family: {self.font.family()};
                    font-size: {self.font.pointSize()}px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 4px;
                    outline: none;
                }}
                QListWidget::item {{
                    padding: 6px 8px;
                    border-radius: 2px;
                }}
                QListWidget::item:selected {{
                    background-color: #e6f7ff;
                    color: #5c9aff;
                }}
                QListWidget::item:hover {{
                    background-color: #f5f7fa;
                }}
            """
        elif self.type == "QTableWidget":
            style_css = f"""
                QTableWidget {{
                    background-color: {bg_color_str};
                    color: {fg_color_str};
                    font-family: {self.font.family()};
                    font-size: {self.font.pointSize()}px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 4px;
                    gridline-color: #e0e0e0;
                }}
                QTableWidget::item {{
                    padding: 4px;
                    border-radius: 2px;
                }}
                QTableWidget::item:selected {{
                    background-color: #e6f7ff;
                    color: #5c9aff;
                }}
                QTableWidget::item:hover {{
                    background-color: #f5f7fa;
                }}
                QHeaderView::section {{
                    background-color: #f5f7fa;
                    color: #2c3e50;
                    padding: 4px;
                    border: 1px solid #e0e0e0;
                    font-weight: bold;
                }}
            """
        elif self.type == "QTabWidget":
            style_css = f"""
                QTabWidget {{
                    background-color: {bg_color_str};
                    color: {fg_color_str};
                    font-family: {self.font.family()};
                    font-size: {self.font.pointSize()}px;
                }}
                QTabWidget::pane {{
                    border: 1px solid #cccccc;
                    background-color: white;
                    border-radius: 2px;
                }}
                QTabBar::tab {{
                    background-color: #e0e0e0;
                    color: #333333;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }}
                QTabBar::tab:selected {{
                    background-color: {bg_color_str};
                    color: {fg_color_str};
                    border: 1px solid #999999;
                    border-bottom: none;
                }}
            """
        elif self.type == "QSlider":
            style_css = f"""
                QSlider::groove:horizontal {{
                    border: 1px solid #e0e0e0;
                    height: 8px;
                    background: #f0f0f0;
                    margin: 2px 0;
                    border-radius: 4px;
                }}
                QSlider::handle:horizontal {{
                    background: #5c9aff;
                    border: 1px solid #5c9aff;
                    width: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }}
            """
        elif self.type == "QScrollArea":
            bg_color_fixed = "#f0f0f0" if self.bg_color.name().upper() == "#FFFFFF" else self.bg_color.name()
            style_css = f"""
                QScrollArea {{
                    background-color: {bg_color_fixed};
                    border: 1px solid #dee2e6;
                }}
            """
        elif self.type == "QFrame":
            style_css = f"""
                QFrame {{
                    background-color: {bg_color_str};
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                }}
            """
        
        return style_css

    def update_stylesheet(self):
        """应用QSS样式"""
        style_css = self.get_stylesheet()
        if self.widget:
            self.widget.setStyleSheet(style_css)

    def get_content_rect(self):
        """获取控件的内容区域（相对于控件自身左上角）"""
        if self.type == "QTabWidget" and self.widget:
            try:
                tab_bar_height = self.widget.tabBar().height()
                # 如果高度为0（可能未显示），使用默认值
                if tab_bar_height <= 0:
                    tab_bar_height = 30
                return QRect(0, tab_bar_height, self.rect.width(), self.rect.height() - tab_bar_height)
            except:
                return QRect(0, 30, self.rect.width(), self.rect.height() - 30)
        elif self.type == "QGroupBox":
            # 容器控件有顶部标题栏，内容区域向下偏移15px
            return QRect(0, 15, self.rect.width(), self.rect.height() - 15)
        elif self.type == "QScrollArea":
             # 画布控件，内容区域就是整个区域
             return QRect(0, 0, self.rect.width(), self.rect.height())
        elif self.type == "QFrame":
             # 父容器控件，内容区域就是整个区域
             return QRect(0, 0, self.rect.width(), self.rect.height())
        else:
             # 默认情况下，内容区域就是整个区域
             return QRect(0, 0, self.rect.width(), self.rect.height())

    def on_mouse_press(self, event):
        """鼠标按下：选中控件+记录拖拽起始位置"""
        if self.locked:
            return
        self.parent_canvas.selected_control = self
        self.parent_canvas.main_window_selected_flag = False
        
        # 使用全局坐标记录起始点，避免控件移动导致的坐标系变化问题
        self.parent_canvas.drag_start_global = event.globalPos()
        self.parent_canvas.drag_start_rect = QRect(self.rect)
        
        self.parent_canvas.update_control_list()
        self.parent_canvas.control_selected.emit(self)
        self.parent_canvas.main_window_selected.emit(None)
        self.parent_canvas.update_selection_overlay()

    def on_mouse_move(self, event):
        """鼠标移动：拖拽控件"""
        if self.locked:
            return
        # 检查是否按住左键且当前控件被选中
        if self.parent_canvas.selected_control != self or event.buttons() != Qt.LeftButton:
            return
            
        # 确保有起始坐标记录
        if not hasattr(self.parent_canvas, 'drag_start_global'):
            return

        # 计算全局偏移量
        delta = event.globalPos() - self.parent_canvas.drag_start_global
        
        # 基于初始位置计算新位置
        start_rect = self.parent_canvas.drag_start_rect
        new_x = start_rect.x() + delta.x()
        new_y = start_rect.y() + delta.y()
        
        if self.parent and self.parent.widget:
            # 如果有父容器，限制在父容器的内容区域内部
            content_rect = self.parent.get_content_rect()
            
            # 限制边界
            min_x = content_rect.x()
            min_y = 0  # 相对于父容器的内容区域，Y坐标从0开始
            max_x = content_rect.width() - self.rect.width()
            max_y = content_rect.height() - self.rect.height()
            
            new_x = max(min_x, min(new_x, max_x))
            new_y = max(min_y, min(new_y, max_y))
            
            self.rect.moveTo(new_x, new_y)
            # 如果是QTabWidget，需要转换坐标
            if self.parent.type == "QTabWidget":
                self.widget.move(new_x, new_y)
            else:
                self.widget.move(new_x, new_y)
        else:
            # 限制在主窗口内容区域内，加上标题栏高度
            content_width = self.parent_canvas.main_window_props.width
            content_height = self.parent_canvas.main_window_props.height + self.parent_canvas.main_window_props.title_height  # 加上标题栏高度
            new_x = max(0, min(new_x, content_width - self.rect.width()))
            new_y = max(0, min(new_y, content_height - self.rect.height()))
            
            self.rect.moveTo(new_x, new_y)
            # 将相对坐标转换为绝对坐标来移动控件
            abs_x = self.parent_canvas.main_window_props.x + self.rect.x()
            abs_y = self.parent_canvas.main_window_props.y + self.parent_canvas.main_window_props.title_height + self.rect.y()
            self.widget.move(abs_x, abs_y)
            
        self.parent_canvas.update_selection_overlay()

    def on_mouse_release(self, event):
        """鼠标释放：结束拖拽"""
        if hasattr(self.parent_canvas, 'drag_start_global'):
            del self.parent_canvas.drag_start_global
        self.parent_canvas.control_selected.emit(self)

    def to_dict(self):
        """序列化为字典"""
        data = {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "text": self.text,
            "rect": [self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()],
            "bg_color": self.bg_color.name(),
            "fg_color": self.fg_color.name(),
            "font": {
                "family": self.font.family(),
                "pointSize": self.font.pointSize(),
                "bold": self.font.bold(),
                "italic": self.font.italic()
            },
            "use_style": self.use_style,
            "preset_style": self.preset_style,
            "visual_style": self.visual_style,
            "border_radius": self.border_radius,
            "border_width": self.border_width,
            "border_color": self.border_color.name(),
            "events": self.events,
            "checked": self.checked,
            "read_only": self.read_only,
            "align": int(self.align),
            "wrap_text": self.wrap_text,
            "max_length": self.max_length,
            "password_mode": self.password_mode,
            "placeholder": self.placeholder,
            "enabled": self.enabled,
            "visible": self.visible,
            "locked": self.locked,
            "show_bg_color": self.show_bg_color,
            "text_edit_read_only": self.text_edit_read_only,
            "text_edit_placeholder": self.text_edit_placeholder,
            "text_edit_wrap_mode": self.text_edit_wrap_mode,
            "text_edit_alignment": self.text_edit_alignment,
            "combo_editable": self.combo_editable,
            "list_selection_mode": self.list_selection_mode,
            "list_items": self.list_items,
            "list_edit_triggers": self.list_edit_triggers,
            "list_alternating_row_colors": self.list_alternating_row_colors,
            "list_sorting_enabled": self.list_sorting_enabled,
            "list_view_mode": self.list_view_mode,
            "list_drag_drop_mode": self.list_drag_drop_mode,
            "list_resize_mode": self.list_resize_mode,
            "list_movement": self.list_movement,
            "table_row_count": self.table_row_count,
            "table_column_count": self.table_column_count,
            "table_data": self.table_data,
            "table_headers": self.table_headers,
            "table_row_headers": self.table_row_headers,
            "table_column_widths": self.table_column_widths,
            "table_row_heights": self.table_row_heights,
            "table_show_grid": self.table_show_grid,
            "table_selection_mode": self.table_selection_mode,
            "table_edit_triggers": self.table_edit_triggers,
            "table_alternating_row_colors": self.table_alternating_row_colors,
            "table_sorting_enabled": self.table_sorting_enabled,
            "table_corner_button_enabled": self.table_corner_button_enabled,
            "tab_position": self.tab_position,
            "tab_shape": self.tab_shape,
            "tab_closable": self.tab_closable,
            "tab_movable": self.tab_movable,
            "tab_current_index": self.tab_current_index,
            "tab_titles": self.tab_titles,
            "tab_count": self.tab_count,
            "parent_id": self.parent.id if self.parent else None,
            "parent_tab_index": self.parent_tab_index,
            "slider_minimum": self.slider_minimum,
            "slider_maximum": self.slider_maximum,
            "slider_value": self.slider_value,
            "slider_orientation": self.slider_orientation
        }
        return data

    @classmethod
    def from_dict(cls, data, parent_canvas):
        """从字典反序列化"""
        control = cls(data["type"], parent_canvas)
        control.id = data.get("id", control.id)
        control.name = data.get("name", control.name)
        control.text = data.get("text", control.text)
        
        rect = data.get("rect", [100, 100, 100, 30])
        control.rect = QRect(rect[0], rect[1], rect[2], rect[3])
        
        control.bg_color = QColor(data.get("bg_color", "#FFFFFF"))
        control.fg_color = QColor(data.get("fg_color", "#000000"))
        
        font_data = data.get("font", {})
        control.font = QFont(font_data.get("family", "Microsoft YaHei"), font_data.get("pointSize", 9))
        control.font.setBold(font_data.get("bold", False))
        control.font.setItalic(font_data.get("italic", False))
        
        control.use_style = data.get("use_style", True)
        control.preset_style = data.get("preset_style", "自定义")
        control.visual_style = data.get("visual_style", "默认")
        control.border_radius = data.get("border_radius", 0)
        control.border_width = data.get("border_width", 1)
        control.border_color = QColor(data.get("border_color", "#999999"))

        control.events = data.get("events", [])
        control.checked = data.get("checked", False)
        control.read_only = data.get("read_only", False)
        control.align = Qt.Alignment(data.get("align", int(Qt.AlignCenter)))
        control.wrap_text = data.get("wrap_text", False)
        control.max_length = data.get("max_length", 0)
        control.password_mode = data.get("password_mode", False)
        control.placeholder = data.get("placeholder", "")
        control.enabled = data.get("enabled", True)
        control.visible = data.get("visible", True)
        control.locked = data.get("locked", False)
        control.show_bg_color = data.get("show_bg_color", True)
        control.h_scrollbar = data.get("h_scrollbar", True)
        control.v_scrollbar = data.get("v_scrollbar", True)
        
        # 特有属性
        control.slider_minimum = data.get("slider_minimum", 0)
        control.slider_maximum = data.get("slider_maximum", 100)
        control.slider_value = data.get("slider_value", 0)
        control.slider_orientation = data.get("slider_orientation", 1)

        control.text_edit_read_only = data.get("text_edit_read_only", False)
        control.text_edit_placeholder = data.get("text_edit_placeholder", "")
        control.text_edit_wrap_mode = data.get("text_edit_wrap_mode", 1)
        control.text_edit_alignment = data.get("text_edit_alignment", 1)
        
        control.combo_editable = data.get("combo_editable", False)
        
        control.list_selection_mode = data.get("list_selection_mode", 0)
        control.list_items = data.get("list_items", [])
        control.list_edit_triggers = data.get("list_edit_triggers", 0)
        control.list_alternating_row_colors = data.get("list_alternating_row_colors", False)
        control.list_sorting_enabled = data.get("list_sorting_enabled", False)
        control.list_view_mode = data.get("list_view_mode", 0)
        control.list_drag_drop_mode = data.get("list_drag_drop_mode", 0)
        control.list_resize_mode = data.get("list_resize_mode", 0)
        control.list_movement = data.get("list_movement", 0)
        
        control.table_row_count = data.get("table_row_count", 3)
        control.table_column_count = data.get("table_column_count", 3)
        control.table_data = data.get("table_data", [])
        control.table_headers = data.get("table_headers", [])
        control.table_row_headers = data.get("table_row_headers", [])
        control.table_column_widths = data.get("table_column_widths", [])
        control.table_row_heights = data.get("table_row_heights", [])
        control.table_show_grid = data.get("table_show_grid", True)
        control.table_selection_mode = data.get("table_selection_mode", 0)
        control.table_edit_triggers = data.get("table_edit_triggers", 0)
        control.table_alternating_row_colors = data.get("table_alternating_row_colors", False)
        control.table_sorting_enabled = data.get("table_sorting_enabled", False)
        control.table_corner_button_enabled = data.get("table_corner_button_enabled", True)
        
        control.tab_position = data.get("tab_position", 0)
        control.tab_shape = data.get("tab_shape", 0)
        control.tab_closable = data.get("tab_closable", False)
        control.tab_movable = data.get("tab_movable", False)
        control.tab_current_index = data.get("tab_current_index", 0)
        control.tab_titles = data.get("tab_titles", ["Tab 1", "Tab 2"])
        control.tab_count = data.get("tab_count", 2)
        
        control.parent_tab_index = data.get("parent_tab_index", -1)

        # parent_id 在外部处理连接
        return control
