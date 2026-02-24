from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal


class ControlListPanel(QWidget):
    """控件列表面板：显示所有已创建的控件，支持选中/删除"""
    control_selected = pyqtSignal(str)
    control_deleted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 标题
        title_label = QLabel("当前控件列表")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)

        # 控件列表（竖向排列）
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 12px;")
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("删除选中")
        self.delete_btn.clicked.connect(self.on_delete_click)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

    def add_control(self, control):
        """添加控件到列表"""
        item = QListWidgetItem(f"{control.name} ({control.type})")
        item.setData(Qt.UserRole, control.id)
        control.list_item = item
        self.list_widget.addItem(item)

    def remove_control(self, control):
        """从列表中移除控件"""
        if control.list_item:
            row = self.list_widget.row(control.list_item)
            self.list_widget.takeItem(row)
            control.list_item = None

    def update_control_item(self, control):
        """更新控件列表项文本"""
        if control.list_item:
            control.list_item.setText(f"{control.name} ({control.type})")

    def on_item_clicked(self, item):
        """选中列表项：同步选中画布控件"""
        control_id = item.data(Qt.UserRole)
        self.control_selected.emit(control_id)

    def on_delete_click(self):
        """删除选中控件"""
        self.control_deleted.emit()

    def clear(self):
        """清空列表"""
        self.list_widget.clear()
