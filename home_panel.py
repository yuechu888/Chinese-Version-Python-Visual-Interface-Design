import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QListWidgetItem, QPushButton, QLabel, QGridLayout,
    QScrollArea, QMessageBox, QFrame, QSplitter, QInputDialog, QMenu
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QRect
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap, QPainter, QBrush, QPen, QCursor

# from main_window import EasyLanguageUI # 移除循环引用
from project_manager import ProjectManager

class CircularButton(QPushButton):
    """圆形大按钮"""
    def __init__(self, text, color, icon_text="+", icon_path=None, parent=None):
        super().__init__(parent)
        self.text_label = text
        self.color = QColor(color)
        self.icon_text = icon_text
        self.icon_path = icon_path
        self.setFixedSize(120, 140)  # 包含文字的高度
        self.setCursor(Qt.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆形背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(10, 10, 100, 100)
        
        # 绘制中间的图标或符号
        if self.icon_path and os.path.exists(self.icon_path):
            # 尝试使用 QIcon 获取高分辨率图片 (针对ico文件)
            icon = QIcon(self.icon_path)
            pixmap = icon.pixmap(200, 200)
            
            if pixmap.isNull():
                 pixmap = QPixmap(self.icon_path)

            if not pixmap.isNull():
                # 使用路径裁剪为圆形，并填满
                from PyQt5.QtGui import QPainterPath
                path = QPainterPath()
                path.addEllipse(10, 10, 100, 100)
                
                painter.save()
                painter.setClipPath(path)
                
                # 开启平滑缩放
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                
                # 强制将图片绘制到整个圆形区域 (10, 10, 100, 100)
                # 这会将图片拉伸以填满该区域
                painter.drawPixmap(QRect(10, 10, 100, 100), pixmap)
                
                painter.restore()
            else:
                # 图片加载失败，回退到文字
                self._draw_icon_text(painter)
        else:
            # 绘制文字符号
            self._draw_icon_text(painter)
            
        # 绘制右上角的小加号 (装饰) - 仅在没有图标时显示，或者作为装饰一直显示？
        # 这里假设如果是项目按钮，不需要右上角加号，除非是特殊按钮
        if self.icon_text == "+":
             painter.setPen(QPen(QColor("#00aaff"), 3))
             font_small = QFont("Arial", 20, QFont.Bold)
             painter.setFont(font_small)
             painter.drawText(80, 10, 30, 30, Qt.AlignCenter, "+")
        
        # 绘制下方的文字
        painter.setPen(QPen(Qt.black)) # 修改为黑色以适应浅色背景
        font_text = QFont("Microsoft YaHei", 10)
        painter.setFont(font_text)
        painter.drawText(0, 115, 120, 25, Qt.AlignCenter, self.text_label)

    def _draw_icon_text(self, painter):
        painter.setPen(QPen(Qt.white, 3))
        font = QFont("Arial", 40, QFont.Bold)
        painter.setFont(font)
        painter.drawText(10, 10, 100, 100, Qt.AlignCenter, self.icon_text)

class HomePanel(QWidget):
    """启动台/首页面板"""
    # 修复：信号参数定义必须在类级别，且与emit参数匹配
    new_project_requested = pyqtSignal(str) 
    open_project_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #f5f7fa;")
        
        self.projects_dir = os.path.join(os.getcwd(), "projects")
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)
            
        self.init_ui()
        self.load_projects()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. 左侧侧边栏
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("background-color: #ffffff; border-right: 1px solid #e0e0e0;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部标题
        title_label = QLabel("  项目列表")
        title_label.setFixedHeight(50)
        title_label.setStyleSheet("color: #5c9aff; font-size: 16px; font-weight: bold; background-color: #ffffff; border-bottom: 2px solid #f0f0f0;")
        sidebar_layout.addWidget(title_label)
        
        # 项目列表控件
        self.project_list = QListWidget()
        self.project_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: none;
                color: #2c3e50;
                font-size: 14px;
            }
            QListWidget::item {
                height: 40px;
                padding-left: 10px;
            }
            QListWidget::item:selected {
                background-color: #e6f7ff;
                color: #5c9aff;
                border-left: 3px solid #5c9aff;
            }
            QListWidget::item:hover {
                background-color: #f5f7fa;
            }
        """)
        self.project_list.itemClicked.connect(self.on_project_clicked)
        sidebar_layout.addWidget(self.project_list)
        
        main_layout.addWidget(self.sidebar)
        
        # 2. 右侧内容区
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setStyleSheet("background-color: #f5f7fa; border: none;")
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #f5f7fa;")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(20)
        
        # 顶部工具栏/状态栏模拟
        header_layout = QHBoxLayout()
        welcome_label = QLabel("欢迎使用月初UI设计器")
        welcome_label.setStyleSheet("color: #2c3e50; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)
        
        # 大按钮区域
        self.grid_layout = QGridLayout()
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.setSpacing(30)
        
        content_layout.addLayout(self.grid_layout)
        content_layout.addStretch()
        
        self.content_area.setWidget(self.content_widget)
        main_layout.addWidget(self.content_area)

    def load_projects(self):
        """加载项目列表（侧边栏显示文件夹）"""
        self.project_list.clear()
        
        # 扫描projects目录
        if os.path.exists(self.projects_dir):
            # 获取所有子文件夹
            dirs = [d for d in os.listdir(self.projects_dir) if os.path.isdir(os.path.join(self.projects_dir, d))]
            # 排序
            dirs.sort()
            
            # 添加"我的项目"（根目录）
            root_item = QListWidgetItem("我的项目")
            root_item.setIcon(QIcon(self.create_color_icon("#007acc")))
            root_item.setData(Qt.UserRole, self.projects_dir)
            self.project_list.addItem(root_item)
            
            # 添加子文件夹
            for d in dirs:
                item = QListWidgetItem(d)
                item.setIcon(QIcon(self.create_color_icon("#f56a00")))
                item.setData(Qt.UserRole, os.path.join(self.projects_dir, d))
                self.project_list.addItem(item)
            
            # 默认选中第一个
            if self.project_list.count() > 0:
                self.project_list.setCurrentRow(0)
                self.on_folder_clicked(self.project_list.item(0))

    def on_folder_clicked(self, item):
        """点击文件夹，加载该文件夹下的项目到右侧Grid"""
        folder_path = item.data(Qt.UserRole)
        self.update_grid_view(folder_path)

    def update_grid_view(self, folder_path):
        """更新右侧Grid视图"""
        # 清空现有Grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 重新添加基础按钮
        self.new_btn = CircularButton("新建项目", "#ff85c0", "+") # 使用粉色
        self.new_btn.clicked.connect(self.new_project)
        self.grid_layout.addWidget(self.new_btn, 0, 0)
        
        self.help_btn = CircularButton("使用帮助", "#5c9aff", "?") # 使用蓝色
        self.help_btn.clicked.connect(lambda: QMessageBox.information(self, "帮助", "点击'新建项目'开始设计UI。\n保存的项目将显示在左侧列表。"))
        self.grid_layout.addWidget(self.help_btn, 0, 1)

        if not folder_path or not os.path.exists(folder_path):
            return

        # 扫描该文件夹下的.pack文件
        files = [f for f in os.listdir(folder_path) if f.endswith('.pack')]
        # 按修改时间排序
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
        
        # 填充Grid
        grid_row = 0
        grid_col = 2 # 从第3列开始（0, 1 被占用）
        max_col = 5
        
        for f in files:
            full_path = os.path.join(folder_path, f)
            file_name = f.replace('.pack', '')
            
            # 生成随机颜色或固定颜色
            import random
            colors = ["#faad14", "#52c41a", "#f56a00", "#722ed1", "#eb2f96", "#1890ff"]
            btn_color = colors[hash(file_name) % len(colors)]
            
            # 使用 doro.ico 作为图标
            icon_path = os.path.join(os.getcwd(), "doro.ico")
            
            btn = CircularButton(file_name, btn_color, icon_text="", icon_path=icon_path)
            # 使用闭包捕获path
            btn.clicked.connect(lambda checked, path=full_path: self.open_project_requested.emit(path))
            
            # 绑定右键菜单（用于删除）
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, path=full_path, name=file_name: self.show_project_context_menu(pos, path, name))
            
            self.grid_layout.addWidget(btn, grid_row, grid_col)
            grid_col += 1
            if grid_col >= max_col:
                grid_col = 0
                grid_row += 1

    def show_project_context_menu(self, pos, file_path, project_name):
        """显示项目右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #d9d9d9;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px;
                color: #2c3e50;
            }
            QMenu::item:selected {
                background-color: #e6f7ff;
                color: #5c9aff;
            }
        """)
        
        delete_action = menu.addAction("删除项目")
        
        # 映射全局坐标
        global_pos = self.sender().mapToGlobal(pos)
        action = menu.exec_(global_pos)
        
        if action == delete_action:
            self.delete_project(file_path, project_name)

    def delete_project(self, file_path, project_name):
        """删除项目"""
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除项目 '{project_name}' 吗？\n此操作不可恢复！",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(file_path)
                # 刷新列表
                # 获取当前选中的文件夹
                current_item = self.project_list.currentItem()
                if current_item:
                    self.on_folder_clicked(current_item)
                else:
                    self.load_projects()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败: {str(e)}")

    def create_color_icon(self, color_str):
        """创建简单的颜色块图标"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(color_str))
        return pixmap

    def new_project(self):
        """发出新建项目请求"""
        name, ok = QInputDialog.getText(self, "新建项目", "请输入项目名称:", text="新项目")
        if ok and name:
            self.new_project_requested.emit(name)
        
    def on_project_clicked(self, item):
        """点击左侧列表项的处理"""
        if item:
            self.on_folder_clicked(item)

    def on_current_item_changed(self, current, previous):
        """当前选项改变时处理"""
        if current:
            self.on_folder_clicked(current)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePanel()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())
