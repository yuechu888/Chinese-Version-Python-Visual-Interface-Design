from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QToolButton, QScrollArea, QApplication
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QPoint
from PyQt5.QtGui import QDrag


class CollapsibleSection(QWidget):
    """可收缩的分组"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.expanded = True
        self.content_widget = None
        self.content_layout = None
        self.init_ui(title)
    
    def init_ui(self, title):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏
        self.header = QToolButton()
        self.header.setStyleSheet("""
            QToolButton {
                background-color: #f5f7fa;
                border: none;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                font-weight: 600;
                color: #2c3e50;
                text-align: left;
            }
            QToolButton:hover {
                background-color: #e6f7ff;
                color: #5c9aff;
            }
            QToolButton:pressed {
                background-color: #d6efff;
            }
        """)
        self.header.setText(title)
        self.header.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.header.setArrowType(Qt.DownArrow)
        self.header.clicked.connect(self.toggle)
        layout.addWidget(self.header)
        
        # 内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 5, 0, 5)
        self.content_layout.setSpacing(5)
        layout.addWidget(self.content_widget)
    
    def add_component(self, button):
        """添加组件按钮"""
        self.content_layout.addWidget(button)
    
    def toggle(self):
        """切换展开/收缩状态"""
        self.expanded = not self.expanded
        
        if self.expanded:
            self.content_widget.show()
            self.header.setArrowType(Qt.DownArrow)
        else:
            self.content_widget.hide()
            self.header.setArrowType(Qt.RightArrow)


class LibraryButton(QPushButton):
    """支持双击信号和拖拽的按钮"""
    doubleClicked = pyqtSignal()
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.drag_start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_start_pos:
            # 检查拖动距离，避免轻微抖动导致点击失效
            if (event.pos() - self.drag_start_pos).manhattanLength() > QApplication.startDragDistance():
                self.start_drag()
                return
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

    def start_drag(self):
        """开始拖拽"""
        control_type = self.property("control_type")
        if not control_type:
            return

        # 创建拖拽数据
        mime_data = QMimeData()
        mime_data.setText(control_type)

        # 启动拖拽
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setHotSpot(self.drag_start_pos)
        drag.exec_(Qt.CopyAction)



class ComponentLibrary(QWidget):
    """组件库：提供可拖拽的控件模板"""
    component_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.control_buttons = {}
        self.selected_button = None
        self.sections = {}
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.setMinimumWidth(200)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #2c3e50;
            }
        """)

        # 标题
        title_label = QLabel("组件库")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #5c9aff;
            padding: 10px 0;
            border-bottom: 2px solid #f0f0f0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f5f7fa;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #d0d0d0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #b0b0b0;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)
        
        # 添加分类
        self.add_section(scroll_layout, "基本控件", [
            ("按钮", "QPushButton"),
            ("标签", "QLabel"),
            ("输入框", "QLineEdit"),
            ("复选框", "QCheckBox"),
            ("单选框", "QRadioButton"),
            ("滑块", "QSlider")
        ])
        
        self.add_section(scroll_layout, "高级控件", [
            ("文本框", "QTextEdit"),
            ("下拉框", "QComboBox"),
            ("列表框", "QListWidget"),
            ("表格", "QTableWidget"),
            ("选项卡", "QTabWidget")
        ])
        
        self.add_section(scroll_layout, "容器控件", [
            ("标签容器", "QGroupBox"),
            ("画布", "QScrollArea"),
            ("父容器", "QFrame")
        ])
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
    
    def add_section(self, layout, title, components):
        """添加可收缩分组"""
        section = CollapsibleSection(title)
        self.sections[title] = section
        
        for name, type_ in components:
            btn = LibraryButton(name)
            btn.setProperty("control_type", type_)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px 12px;
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    text-align: left;
                    color: #555555;
                }
                QPushButton:hover {
                    background-color: #fff0f6; /* 浅粉色背景 */
                    border-color: #ff85c0;
                    color: #ff85c0;
                }
                QPushButton[selected="true"] {
                    background-color: #e6f7ff;
                    color: #5c9aff;
                    border-color: #5c9aff;
                    font-weight: bold;
                }
            """)
            btn.setMinimumHeight(45)
            # 双击高亮并发送选中信号（进入绘制模式）
            btn.doubleClicked.connect(lambda t=type_, b=btn: self.on_component_activate(t, b))
            
            section.add_component(btn)
            self.control_buttons[type_] = btn
        
        layout.addWidget(section)

    def on_component_highlight(self, control_type, button):
        """点击组件：仅高亮"""
        # 取消之前选中的按钮
        if self.selected_button:
            self.selected_button.setProperty("selected", False)
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)
        
        # 高亮当前按钮
        button.setProperty("selected", True)
        button.style().unpolish(button)
        button.style().polish(button)
        self.selected_button = button

    def on_component_activate(self, control_type, button):
        """双击组件：高亮并进入绘制模式"""
        self.on_component_highlight(control_type, button)
        # 发送信号
        self.component_selected.emit(control_type)
        
    def on_component_click(self, control_type, button):
        """兼容旧接口"""
        self.on_component_activate(control_type, button)
    
    def reset_selection(self):
        """重置选中状态"""
        if self.selected_button:
            self.selected_button.setProperty("selected", False)
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)
            self.selected_button = None
