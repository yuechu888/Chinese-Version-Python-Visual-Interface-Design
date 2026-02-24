from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal


class ControlHierarchyPanel(QWidget):
    """控件层级面板：用树形结构显示控件的层级关系"""
    control_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.control_items = {}  # 控件ID到树项的映射
        self.main_window_item = None  # 主窗口树项

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 标题
        title_label = QLabel("控件层级")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #5c9aff; padding: 5px;")
        layout.addWidget(title_label)

        # 树形控件
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["控件名称", "类型"])
        self.tree_widget.setColumnWidth(0, 120)
        self.tree_widget.setColumnWidth(1, 80)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                font-size: 12px;
                border: none;
                background-color: transparent;
                color: #2c3e50;
            }
            QTreeWidget::item {
                padding: 4px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #e6f7ff;
                color: #5c9aff;
            }
            QTreeWidget::item:hover {
                background-color: #f5f7fa;
            }
            QHeaderView::section {
                background-color: #f5f7fa;
                color: #666666;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                padding: 6px;
                font-weight: bold;
            }
        """)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree_widget)

    def set_main_window(self, main_window):
        """设置主窗口作为根节点"""
        if self.main_window_item is None:
            self.main_window_item = QTreeWidgetItem(self.tree_widget)
            self.main_window_item.setText(0, "主窗口")
            self.main_window_item.setText(1, "Window")
            self.main_window_item.setExpanded(True)
            self.main_window_item.setData(0, Qt.UserRole, "main_window")

    def add_control(self, control, parent_control=None):
        """添加控件到树形结构"""
        # 如果没有指定父控件，则使用控件自身的parent属性
        if parent_control is None and control.parent:
            parent_control = control.parent
        
        if parent_control and parent_control.id in self.control_items:
            parent_item = self.control_items[parent_control.id]
        else:
            parent_item = self.main_window_item

        if parent_item is None:
            return

        item = QTreeWidgetItem(parent_item)
        item.setText(0, control.name)
        item.setText(1, control.type)
        item.setData(0, Qt.UserRole, control.id)
        
        self.control_items[control.id] = item
        control.tree_item = item

        parent_item.setExpanded(True)

    def remove_control(self, control):
        """从树中移除控件"""
        if control is None:
            # 清空非主窗口的所有子项
            if self.main_window_item:
                self.main_window_item.takeChildren()
            self.control_items.clear()
            return

        if control.id in self.control_items:
            item = self.control_items[control.id]
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                root_index = self.tree_widget.indexOfTopLevelItem(item)
                if root_index >= 0:
                    self.tree_widget.takeTopLevelItem(root_index)
            del self.control_items[control.id]
            control.tree_item = None

    def update_control_item(self, control):
        """更新控件树项文本"""
        if control.id in self.control_items:
            item = self.control_items[control.id]
            item.setText(0, control.name)
            item.setText(1, control.type)

    def on_item_clicked(self, item, column):
        """选中树项：同步选中画布控件"""
        control_id = item.data(0, Qt.UserRole)
        self.control_selected.emit(control_id)

    def clear(self):
        """清空树"""
        self.tree_widget.clear()
        self.control_items.clear()
