import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QMessageBox, QWidget, QVBoxLayout, QTabBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from home_panel import HomePanel
from designer_widget import DesignerWidget
from project_manager import ProjectManager

class UnifiedMainWindow(QMainWindow):
    """统一的主窗口，包含选项卡界面"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("月初UI - 设计器--测试--绿泡泡:qycl96888")
        self.resize(1350, 1000)
        
        # 初始化UI
        self.init_ui()
        self.apply_global_styles()
        
    def apply_global_styles(self):
        """应用全局柔和白蓝粉主题样式"""
        # 配色方案：
        # 背景：#f5f7fa (柔和灰白)
        # 面板：#ffffff (纯白)
        # 文字：#2c3e50 (深灰蓝)
        # 主色(蓝)：#5c9aff
        # 辅色(粉)：#ff85c0
        # 边框：#e0e0e0
        
        light_stylesheet = """
        /* 全局基础 */
        QMainWindow, QWidget {
            background-color: #f5f7fa;
            color: #2c3e50;
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            font-size: 9pt;
        }
        
        /* 避免全局 QWidget 选择器影响 QMessageBox 的内部布局，特别是当它们没有 objectName 时 */
        /* 但为了保持统一，我们在下面专门为 QMessageBox 覆盖样式 */
        
        /* 选项卡样式 */
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            background: #ffffff;
            border-radius: 4px;
        }
        QTabWidget::tab-bar {
            left: 5px;
        }
        QTabBar::tab {
            background: #eef2f6;
            color: #666666;
            border: 1px solid #e0e0e0;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            min-width: 100px;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            color: #5c9aff;
            border-bottom: 1px solid #ffffff; /* 与pane融合 */
            font-weight: bold;
        }
        QTabBar::tab:hover:!selected {
            background: #ffffff;
            color: #5c9aff;
        }
        
        /* 滚动条样式 */
        QScrollBar:vertical {
            border: none;
            background: #f5f7fa;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #d0d0d0;
            min-height: 20px;
            border-radius: 5px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover {
            background: #b0b0b0;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            border: none;
            background: #f5f7fa;
            height: 10px;
            margin: 0px;
        }
        QScrollBar::handle:horizontal {
            background: #d0d0d0;
            min-width: 20px;
            border-radius: 5px;
            margin: 2px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #b0b0b0;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* 分割器样式 */
        QSplitter::handle {
            background-color: #e0e0e0;
        }
        QSplitter::handle:hover {
            background-color: #5c9aff;
        }
        
        /* 菜单栏样式 */
        QMenuBar {
            background-color: #ffffff;
            color: #2c3e50;
            border-bottom: 1px solid #e0e0e0;
        }
        QMenuBar::item {
            background: transparent;
            padding: 8px 12px;
        }
        QMenuBar::item:selected {
            background: #f0f7ff;
            color: #5c9aff;
        }
        QMenu {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 4px;
        }
        QMenu::item {
            padding: 6px 24px;
            color: #2c3e50;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #f0f7ff;
            color: #5c9aff;
        }
        
        /* 输入框和列表样式 */
        QLineEdit:not(#design_canvas_widget), QTextEdit:not(#design_canvas_widget), QPlainTextEdit:not(#design_canvas_widget), QSpinBox:not(#design_canvas_widget), QDoubleSpinBox:not(#design_canvas_widget), QComboBox:not(#design_canvas_widget) {
            background-color: #ffffff;
            border: 1px solid #d9d9d9;
            color: #2c3e50;
            padding: 6px;
            border-radius: 4px;
        }
        QLineEdit:not(#design_canvas_widget):focus, QTextEdit:not(#design_canvas_widget):focus, QPlainTextEdit:not(#design_canvas_widget):focus, QSpinBox:not(#design_canvas_widget):focus, QComboBox:not(#design_canvas_widget):focus {
            border: 1px solid #5c9aff;
            background-color: #ffffff;
        }
        
        QListWidget:not(#design_canvas_widget), QTreeWidget:not(#design_canvas_widget), QTableWidget:not(#design_canvas_widget) {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            color: #2c3e50;
            outline: none;
        }
        QListWidget:not(#design_canvas_widget)::item:selected, QTreeWidget:not(#design_canvas_widget)::item:selected, QTableWidget:not(#design_canvas_widget)::item:selected {
            background-color: #e6f7ff;
            color: #5c9aff;
            border: none;
        }
        QListWidget:not(#design_canvas_widget)::item:hover, QTreeWidget:not(#design_canvas_widget)::item:hover, QTableWidget:not(#design_canvas_widget)::item:hover {
            background-color: #f5f7fa;
        }
        
        /* 按钮样式 - 排除画布控件 */
        QPushButton:not(#design_canvas_widget) {
            background-color: #5c9aff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
        }
        QPushButton:not(#design_canvas_widget):hover {
            background-color: #7ab0ff;
        }
        QPushButton:not(#design_canvas_widget):pressed {
            background-color: #4a88e0;
        }
        QPushButton:not(#design_canvas_widget):disabled {
            background-color: #f0f0f0;
            color: #bbbbbb;
        }
        
        /* 辅助按钮(粉色) */
        QPushButton[role="secondary"] {
            background-color: #ff85c0;
        }
        QPushButton[role="secondary"]:hover {
            background-color: #ff9cc9;
        }
        
        /* GroupBox样式 */
        QGroupBox:not(#design_canvas_widget) {
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin-top: 24px;
            font-weight: bold;
            background-color: #ffffff;
        }
        QGroupBox:not(#design_canvas_widget)::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            left: 10px;
            color: #5c9aff;
        }
        
        /* Tooltip */
        QToolTip {
            border: 1px solid #e0e0e0;
            background-color: #ffffff;
            color: #2c3e50;
            padding: 4px;
        }

        /* 弹窗样式修正 */
        QDialog, QMessageBox, QInputDialog {
            background-color: #f5f7fa;
        }
        
        QDialog QLabel, QMessageBox QLabel {
            background-color: transparent;
            color: #2c3e50;
        }
        
        /* 确保弹窗按钮可见 - 统一使用白底黑字，避免背景色问题 */
        QMessageBox QPushButton, QInputDialog QPushButton, QDialogButtonBox QPushButton {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #d9d9d9;
            border-radius: 4px;
            padding: 6px 20px;
            min-width: 60px;
            min-height: 24px;
        }
        
        QMessageBox QPushButton:hover, QInputDialog QPushButton:hover, QDialogButtonBox QPushButton:hover {
            background-color: #e6f7ff;
            color: #5c9aff;
            border-color: #5c9aff;
        }
        
        /* 默认按钮使用白底蓝字+加粗边框，确保在任何情况下都可见 */
        QMessageBox QPushButton:default, QInputDialog QPushButton:default {
            background-color: #ffffff;
            color: #5c9aff;
            border: 2px solid #5c9aff;
        }
        
        QMessageBox QPushButton:default:hover, QInputDialog QPushButton:default:hover {
            background-color: #5c9aff;
            color: white;
        }
        """
        self.setStyleSheet(light_stylesheet)

    def init_ui(self):
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)
        
        # 添加首页（启动台）
        self.home_panel = HomePanel()
        self.home_panel.new_project_requested.connect(self.create_new_project_tab)
        self.home_panel.open_project_requested.connect(self.open_project_tab)
        
        # 首页Tab不可关闭（或者可以关闭但不能全部关闭？）
        # 这里设置为不可关闭
        self.tab_widget.addTab(self.home_panel, "首页")
        
        # 隐藏首页的关闭按钮
        self.tab_widget.tabBar().setTabButton(0, QTabBar.RightSide, None)
        
    def create_new_project_tab(self, project_name="新项目"):
        """创建新项目Tab（并立即保存为空白文件）"""
        
        # 1. 确定保存路径
        # 获取当前选中的文件夹路径（从HomePanel获取不太方便，这里简化为默认 projects 目录）
        # 更好的做法是HomePanel传过来，或者这里默认到 projects
        default_dir = os.path.join(os.getcwd(), "projects")
        if not os.path.exists(default_dir):
            os.makedirs(default_dir)
            
        # 尝试在当前显示的文件夹下创建（如果有）
        current_folder = self.home_panel.project_list.currentItem()
        if current_folder:
            folder_path = current_folder.data(Qt.UserRole)
            if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
                default_dir = folder_path

        file_path = os.path.join(default_dir, f"{project_name}.pack")
        
        # 如果文件已存在，自动重命名
        counter = 1
        base_path = file_path
        while os.path.exists(file_path):
            file_path = f"{base_path[:-5]}_{counter}.pack"
            counter += 1
            
        # 2. 创建并初始化设计器
        designer = DesignerWidget()
        designer.new_project() 
        designer.design_canvas.main_window_props.title = project_name
        designer.property_panel.set_main_window(designer.design_canvas.main_window_props)
        
        # 3. 立即保存文件
        if ProjectManager.save_project(file_path, designer.design_canvas):
            designer.current_project_path = file_path
            designer.update_status(f"项目已创建: {file_path}")
            # 刷新首页列表
            self.home_panel.load_projects()
        else:
            QMessageBox.critical(self, "错误", f"无法创建项目文件: {file_path}")
            designer.deleteLater()
            return

        # 4. 连接保存信号
        designer.project_saved.connect(self.home_panel.load_projects)
        designer.project_saved.connect(self.update_tab_title)
        
        # 5. 添加到Tab
        # 获取最终的文件名作为标题
        final_name = os.path.basename(file_path).replace('.pack', '')
        index = self.tab_widget.addTab(designer, final_name)
        self.tab_widget.setCurrentIndex(index)
        
    def open_project_tab(self, file_path):
        """打开项目Tab"""
        # 检查是否已经打开
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, DesignerWidget) and widget.current_project_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return

        # 创建设计器
        designer = DesignerWidget()
        
        # 加载项目
        # 修正：支持.pack文件
        if ProjectManager.load_project(file_path, designer.design_canvas):
            designer.current_project_path = file_path
            designer.property_panel.set_main_window(designer.design_canvas.main_window_props)
            designer.update_status(f"已打开项目: {file_path}")
            
            # 连接保存信号
            designer.project_saved.connect(self.home_panel.load_projects)
            designer.project_saved.connect(self.update_tab_title)
            
            # 获取文件名作为标题
            file_name = os.path.basename(file_path).replace('.pack', '').replace('.json', '')
            index = self.tab_widget.addTab(designer, file_name)
            self.tab_widget.setCurrentIndex(index)
        else:
            QMessageBox.critical(self, "错误", "项目文件加载失败！")
            designer.deleteLater()

    def close_tab(self, index):
        """关闭Tab"""
        widget = self.tab_widget.widget(index)
        
        # 首页不能关闭
        if widget == self.home_panel:
            return
            
        # 如果是设计器，检查是否需要保存
        if isinstance(widget, DesignerWidget):
            # 这里可以添加保存提示逻辑
            # reply = QMessageBox.question(...)
            pass
            
        self.tab_widget.removeTab(index)
        widget.deleteLater()
        
        # 如果关闭了设计器，刷新首页的项目列表（可能有新保存的项目）
        self.home_panel.load_projects()

    def update_tab_title(self):
        """更新Tab标题"""
        designer = self.sender()
        if not designer or not isinstance(designer, DesignerWidget) or not designer.current_project_path:
            return
        
        index = self.tab_widget.indexOf(designer)
        if index != -1:
            file_name = os.path.basename(designer.current_project_path).replace('.pack', '').replace('.json', '')
            self.tab_widget.setTabText(index, file_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnifiedMainWindow()
    window.show()
    sys.exit(app.exec_())
