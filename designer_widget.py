import sys
import os
import html
from project_manager import ProjectManager
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGroupBox, QPushButton, QLabel,
    QLineEdit, QTextEdit, QColorDialog, QVBoxLayout, QHBoxLayout,
    QSplitter, QMenuBar, QAction, QMessageBox, QInputDialog,
    QCheckBox, QRadioButton, QDialog, QScrollArea, QComboBox, QListWidget,
    QAbstractItemView, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget,
    QSlider, QFrame
)
from PyQt5.QtCore import Qt, QLocale, QTranslator, QLibraryInfo, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QTextOption, QFontMetrics

from ui_control import UIControl
from main_window_props import MainWindowProperties
from design_canvas import DesignCanvas
from control_hierarchy_panel import ControlHierarchyPanel
from property_panel import PropertyPanel
from component_library import ComponentLibrary


class DesignerWidget(QMainWindow):
    """
    单个设计器实例，继承自QMainWindow以便保留菜单栏和工具栏支持。
    将被嵌入到主窗口的Tab中。
    """
    # 信号定义
    status_message_changed = pyqtSignal(str)  # 状态栏消息信号
    project_saved = pyqtSignal()  # 项目保存信号

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置窗口标志为Widget，以便嵌入
        self.setWindowFlags(Qt.Widget)
        
        self.current_project_path = None
        self.init_ui()
        # 移除自身的状态栏创建，改为发送信号给主窗口（如果需要统一状态栏）
        # 或者保留自身状态栏（QMainWindow作为子控件时，自身状态栏显示在底部）
        self.create_status_bar() 
        self.bind_signals()

    def init_ui(self):
        """初始化主界面"""
        # 中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 整体布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # 1. 左侧区域（组件库 + 控件层级，垂直分割）
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.setHandleWidth(1)
        left_splitter.setStretchFactor(0, 0)
        left_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(left_splitter)

        # 1.1 组件库
        self.component_lib = ComponentLibrary()
        self.component_lib.setMinimumWidth(200)
        self.component_lib.setMaximumWidth(200)
        self.component_lib.setMinimumHeight(200)
        left_splitter.addWidget(self.component_lib)

        # 1.2 控件层级面板
        self.control_hierarchy_panel = ControlHierarchyPanel()
        self.control_hierarchy_panel.setMinimumWidth(200)
        self.control_hierarchy_panel.setMaximumWidth(200)
        self.control_hierarchy_panel.set_main_window(self)
        left_splitter.addWidget(self.control_hierarchy_panel)
        left_splitter.setSizes([200, 400])
        
        # 设置分割器不可折叠
        left_splitter.setCollapsible(0, False)
        left_splitter.setCollapsible(1, False)

        # 2. 右侧主区域（画布 + 属性面板，水平分割）
        right_splitter = QSplitter(Qt.Horizontal)
        right_splitter.setHandleWidth(1)
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 0)
        main_layout.addWidget(right_splitter)

        # 画布（用QGroupBox包裹）
        canvas_group = QGroupBox("画布")
        canvas_layout = QVBoxLayout()
        canvas_layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setMinimumSize(400, 400)
        
        # 创建画布并设置到滚动区域
        self.design_canvas = DesignCanvas()
        scroll_area.setWidget(self.design_canvas)
        
        canvas_layout.addWidget(scroll_area)
        canvas_group.setLayout(canvas_layout)
        right_splitter.addWidget(canvas_group)

        # 属性面板
        self.property_panel = PropertyPanel()
        self.property_panel.setMinimumWidth(280)
        self.property_panel.setMaximumWidth(280)
        self.property_panel.control_hierarchy_panel = self.control_hierarchy_panel
        right_splitter.addWidget(self.property_panel)
        right_splitter.setSizes([800, 280])
        
        # 初始显示主窗口属性
        self.property_panel.set_main_window(self.design_canvas.main_window_props)
        
        # 设置分割器折叠属性
        right_splitter.setCollapsible(0, True)
        right_splitter.setCollapsible(1, False)

        # 菜单栏
        self.create_menu()

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
    
    def update_status(self, message):
        """更新状态栏消息"""
        self.status_bar.showMessage(message)
        self.status_message_changed.emit(message) # 同时发送信号

    def create_menu(self):
        """创建菜单栏"""
        menu_bar = self.menuBar() # 获取QMainWindow自带的MenuBar
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        # 保存项目
        save_action = QAction("保存项目", self)
        save_action.triggered.connect(self.save_project)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        generate_action = QAction("生成代码文件", self)
        generate_action.triggered.connect(self.generate_code_to_file)
        file_menu.addAction(generate_action)
        
        generate_code_action = QAction("生成代码", self)
        generate_code_action.triggered.connect(self.generate_ui_code)
        file_menu.addAction(generate_code_action)
        
        # 注意：新建、打开、退出 现在由主窗口统一管理，或者作为Tab操作
        # 这里仅保留针对当前项目的操作

        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        delete_action = QAction("删除选中控件", self)
        delete_action.triggered.connect(self.design_canvas.delete_selected_control)
        edit_menu.addAction(delete_action)

        # 预览菜单
        preview_menu = menu_bar.addMenu("预览")
        preview_action = QAction("实时预览UI", self)
        preview_action.triggered.connect(self.preview_ui)
        preview_menu.addAction(preview_action)

    def bind_signals(self):
        """绑定所有信号槽"""
        # 组件库选中控件 → 进入绘制模式
        self.component_lib.component_selected.connect(self.design_canvas.start_drawing)
        # 绘制模式改变 → 更新状态栏和重置组件库选中
        self.design_canvas.drawing_mode_changed.connect(self.on_drawing_mode_changed)
        # 画布创建控件 → 添加到控件层级
        self.design_canvas.control_created.connect(self.control_hierarchy_panel.add_control)
        # 画布选中控件 → 更新属性面板
        self.design_canvas.control_selected.connect(self.property_panel.set_control)
        # 画布选中主窗口 → 更新属性面板
        self.design_canvas.main_window_selected.connect(self.property_panel.set_main_window)
        # 画布删除控件 → 从控件层级移除对应的项
        self.design_canvas.control_deleted.connect(self.control_hierarchy_panel.remove_control)
        # 控件层级选中 → 画布选中对应控件
        self.control_hierarchy_panel.control_selected.connect(self.on_control_hierarchy_selected)
        # 主窗口属性变更 → 更新画布
        self.property_panel.mw_x_spin.valueChanged.connect(self.on_main_window_prop_changed)
        self.property_panel.mw_y_spin.valueChanged.connect(self.on_main_window_prop_changed)
        self.property_panel.mw_w_spin.valueChanged.connect(self.on_main_window_prop_changed)
        self.property_panel.mw_h_spin.valueChanged.connect(self.on_main_window_prop_changed)
        self.property_panel.mw_title_edit.textChanged.connect(self.on_main_window_prop_changed)
        self.property_panel.mw_title_height_spin.valueChanged.connect(self.on_main_window_prop_changed)
        self.property_panel.mw_bg_color_btn.clicked.connect(self.on_main_window_prop_changed)
        self.property_panel.mw_title_color_btn.clicked.connect(self.on_main_window_prop_changed)
        self.property_panel.mw_title_text_color_btn.clicked.connect(self.on_main_window_prop_changed)
        self.property_panel.mw_use_style_group.buttonToggled.connect(lambda: self.on_main_window_prop_changed())

    def on_main_window_prop_changed(self):
        """主窗口属性变更：更新画布"""
        self.design_canvas.update()

    def on_control_hierarchy_selected(self, control_id):
        """控件层级选中事件：同步到画布"""
        control = self.design_canvas.get_control_by_id(control_id)
        if control:
            self.design_canvas.selected_control = control
            self.design_canvas.main_window_selected_flag = False
            self.design_canvas.update_control_list()
            self.property_panel.set_control(control)
    
    def on_drawing_mode_changed(self, is_drawing, control_type):
        """绘制模式改变事件：更新状态栏和重置组件库选中"""
        if is_drawing:
            # 进入绘制模式
            control_name = {"QPushButton": "按钮", "QLabel": "标签", "QLineEdit": "输入框", 
                          "QCheckBox": "复选框", "QRadioButton": "单选框"}.get(control_type, control_type)
            self.update_status(f"绘制模式：在画布上拖拽绘制{control_name}（按ESC取消）")
        else:
            # 退出绘制模式
            self.update_status("就绪")
            self.component_lib.reset_selection()

    def preview_ui(self):
        """实时预览UI"""
        # 创建预览对话框类
        class PreviewDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.event_callbacks = {}
                self.function_implementations = {}
            
            def add_event_callback(self, control_name, event_name, callback_code):
                """添加事件回调"""
                key = f"{control_name}_{event_name}"
                self.event_callbacks[key] = callback_code
            
            def setup_functions(self):
                """设置所有函数实现"""
                for key, callback_code in self.event_callbacks.items():
                    # 提取控件名和事件名
                    control_name, event_name = key.rsplit('_', 1)
                    # 提取函数名
                    if '(' in callback_code:
                        func_name = callback_code.split('(')[0].strip()
                    else:
                        func_name = callback_code.strip()
                    
                    if func_name and func_name not in self.function_implementations:
                        # 创建函数实现，打印控件名和事件名
                        self.function_implementations[func_name] = lambda fn=func_name, cn=control_name, en=event_name: (
                            print(f"事件触发 - 控件: {cn}, 事件: {en}, 函数: {fn}"),
                            QMessageBox.information(self, "事件触发", f"控件: {cn}\\n事件: {en}\\n函数: {fn}")
                        )
            
            def execute_event(self, control_name, event_name):
                """执行事件回调"""
                key = f"{control_name}_{event_name}"
                if key in self.event_callbacks:
                    callback_code = self.event_callbacks[key]
                    try:
                        # 提取函数名
                        if '(' in callback_code:
                            func_name = callback_code.split('(')[0].strip()
                        else:
                            func_name = callback_code.strip()
                        
                        # 执行函数
                        if func_name in self.function_implementations:
                            self.function_implementations[func_name]()
                    except Exception as e:
                        msg = QMessageBox(self)
                        msg.setIcon(QMessageBox.Critical)
                        msg.setWindowTitle("事件执行错误")
                        msg.setText(f"错误: {str(e)}\\n回调代码: {callback_code}")
                        msg.exec_()
        
        preview_dialog = PreviewDialog(self)
        # 使用画布中主窗口的预设标题
        mw_props = self.design_canvas.main_window_props
        preview_dialog.setWindowTitle(mw_props.title)
        # 客户区大小直接使用设定的大小，即为设计器中的"高度"（不含标题栏）
        # 加上标题栏后，实际窗口高度会增加
        preview_dialog.resize(mw_props.width, mw_props.height)
        
        if mw_props.use_style:
            preview_dialog.setStyleSheet(f"background-color: {mw_props.bg_color.name()};")
        else:
            preview_dialog.setStyleSheet("")

        def bind_events(widget, control):
            """绑定控件的所有事件"""
            for event_data in control.events:
                if not isinstance(event_data, list) or len(event_data) < 2:
                    continue
                event_name = event_data[0]
                callback = event_data[1]
                if not isinstance(callback, str):
                    callback = str(callback) if callback is not None else ""
                if event_name and callback:
                    if hasattr(widget, event_name):
                        signal = getattr(widget, event_name)
                        if hasattr(signal, 'connect'):
                            signal.connect(lambda checked=False, cn=control.name, en=event_name: preview_dialog.execute_event(cn, en))

        # 1. 第一遍：创建所有控件
        id_to_widget = {}
        id_to_tab_pages = {} # QTabWidget ID -> [PageWidget1, PageWidget2, ...]
        
        print(f"预览UI: 共有 {len(self.design_canvas.controls)} 个控件")
        for i, control in enumerate(self.design_canvas.controls):
            print(f"  控件 {i+1}: {control.type} - {control.name}")
            
            # 为每个事件注册回调代码
            for event_data in control.events:
                if not isinstance(event_data, list) or len(event_data) < 2:
                    continue
                event_name = event_data[0]
                callback = event_data[1]
                if not isinstance(callback, str):
                    callback = str(callback) if callback is not None else ""
                if event_name and callback:
                    preview_dialog.add_event_callback(control.name, event_name, callback)
            
            widget = None
            
            if control.type == "QPushButton":
                widget = QPushButton(control.text, preview_dialog)
            elif control.type == "QLabel":
                widget = QLabel(control.text, preview_dialog)
                widget.setWordWrap(control.wrap_text)
                widget.setAlignment(control.align)
                widget.setStyleSheet(f"""
                    background-color: {control.bg_color.name()};
                    color: {control.fg_color.name()};
                    font-family: {control.font.family()};
                    font-size: {control.font.pointSize()}px;
                """)
            elif control.type == "QLineEdit":
                widget = QLineEdit(control.text, preview_dialog)
                widget.setReadOnly(control.read_only)
                widget.setEchoMode(QLineEdit.Password if control.password_mode else QLineEdit.Normal)
                if control.max_length > 0:
                    widget.setMaxLength(control.max_length)
                if control.placeholder:
                    widget.setPlaceholderText(control.placeholder)
                widget.setStyleSheet(f"""
                    background-color: {control.bg_color.name()};
                    color: {control.fg_color.name()};
                    font-family: {control.font.family()};
                    font-size: {control.font.pointSize()}px;
                """)
            elif control.type == "QCheckBox":
                widget = QCheckBox(control.text, preview_dialog)
                widget.setChecked(control.checked)
                widget.setStyleSheet(f"""
                    background-color: {control.bg_color.name()};
                    color: {control.fg_color.name()};
                    font-family: {control.font.family()};
                    font-size: {control.font.pointSize()}px;
                """)
            elif control.type == "QRadioButton":
                widget = QRadioButton(control.text, preview_dialog)
                widget.setChecked(control.checked)
                widget.setStyleSheet(f"""
                    background-color: {control.bg_color.name()};
                    color: {control.fg_color.name()};
                    font-family: {control.font.family()};
                    font-size: {control.font.pointSize()}px;
                """)
            elif control.type == "QTextEdit":
                widget = QTextEdit(preview_dialog)
                widget.setReadOnly(control.text_edit_read_only)
                if control.text_edit_placeholder:
                    widget.setPlaceholderText(control.text_edit_placeholder)
                wrap_modes = [QTextOption.NoWrap, QTextOption.WordWrap, QTextOption.WrapAnywhere]
                widget.setWordWrapMode(wrap_modes[control.text_edit_wrap_mode])
                alignments = [Qt.AlignLeft, Qt.AlignCenter, Qt.AlignRight]
                widget.setAlignment(alignments[control.text_edit_alignment])
                widget.setStyleSheet(f"""
                    background-color: {control.bg_color.name()};
                    color: {control.fg_color.name()};
                    font-family: {control.font.family()};
                    font-size: {control.font.pointSize()}px;
                    border: 1px solid #d9d9d9;
                    border-radius: 3px;
                    padding: 4px 6px;
                """)
            elif control.type == "QComboBox":
                widget = QComboBox(preview_dialog)
                widget.setEditable(control.combo_editable)
                widget.addItem("选项1")
                widget.addItem("选项2")
                widget.addItem("选项3")
                widget.setStyleSheet(f"""
                    background-color: {control.bg_color.name()};
                    color: {control.fg_color.name()};
                    font-family: {control.font.family()};
                    font-size: {control.font.pointSize()}px;
                    border: 1px solid #d9d9d9;
                    border-radius: 3px;
                    padding: 4px 6px;
                """)
            elif control.type == "QListWidget":
                widget = QListWidget(preview_dialog)
                selection_modes = [QAbstractItemView.SingleSelection, QAbstractItemView.MultiSelection, QAbstractItemView.ExtendedSelection]
                widget.setSelectionMode(selection_modes[control.list_selection_mode])
                edit_triggers = [
                    QAbstractItemView.NoEditTriggers,
                    QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed,
                    QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed,
                    QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed
                ]
                widget.setEditTriggers(edit_triggers[control.list_edit_triggers])
                widget.setAlternatingRowColors(control.list_alternating_row_colors)
                widget.setSortingEnabled(control.list_sorting_enabled)
                from PyQt5.QtWidgets import QListView
                view_modes = [QListView.ListMode, QListView.IconMode]
                widget.setViewMode(view_modes[control.list_view_mode])
                drag_drop_modes = [
                    QAbstractItemView.NoDragDrop,
                    QAbstractItemView.InternalMove,
                    QAbstractItemView.DragDrop,
                    QAbstractItemView.DropOnly
                ]
                widget.setDragDropMode(drag_drop_modes[control.list_drag_drop_mode])
                resize_modes = [QListView.Fixed, QListView.Adjust]
                widget.setResizeMode(resize_modes[control.list_resize_mode])
                movements = [QListView.Static, QListView.Free, QListView.Snap]
                widget.setMovement(movements[control.list_movement])
                for item_text in control.list_items:
                    widget.addItem(item_text)
                widget.setStyleSheet(f"""
                    QListWidget {{
                        background-color: {control.bg_color.name()};
                        color: {control.fg_color.name()};
                        font-family: {control.font.family()};
                        font-size: {control.font.pointSize()}px;
                        border: 1px solid #d9d9d9;
                        border-radius: 3px;
                        padding: 4px;
                    }}
                    QListWidget::item {{
                        padding: 4px;
                        border-radius: 2px;
                    }}
                    QListWidget::item:selected {{
                        background-color: #e6f7ff;
                        color: #5c9aff;
                    }}
                    QListWidget::item:hover {{
                        background-color: #f5f7fa;
                    }}
                """)
            elif control.type == "QTableWidget":
                widget = QTableWidget(preview_dialog)
                widget.setRowCount(control.table_row_count)
                widget.setColumnCount(control.table_column_count)
                widget.setHorizontalHeaderLabels(control.table_headers)
                widget.setStyleSheet(f"""
                    QTableWidget {{
                        background-color: {control.bg_color.name()};
                        color: {control.fg_color.name()};
                        font-family: {control.font.family()};
                        font-size: {control.font.pointSize()}px;
                        border: 1px solid #d9d9d9;
                        border-radius: 3px;
                        gridline-color: #e0e0e0;
                    }}
                    QTableWidget::item {{
                        padding: 4px;
                        border: 1px solid #e0e0e0;
                    }}
                    QTableWidget::item:selected {{
                        background-color: #e6f7ff;
                        color: #5c9aff;
                    }}
                    QHeaderView::section {{
                        background-color: #f5f7fa;
                        padding: 4px;
                        border: 1px solid #e0e0e0;
                        font-weight: bold;
                    }}
                """)
                for row in range(control.table_row_count):
                    for col in range(control.table_column_count):
                        if row < len(control.table_data) and col < len(control.table_data[row]):
                            item = QTableWidgetItem(str(control.table_data[row][col]))
                            widget.setItem(row, col, item)
            elif control.type == "QTabWidget":
                widget = QTabWidget(preview_dialog)
                positions = [QTabWidget.North, QTabWidget.South, QTabWidget.West, QTabWidget.East]
                widget.setTabPosition(positions[control.tab_position])
                shapes = [QTabWidget.Rounded, QTabWidget.Triangular]
                widget.setTabShape(shapes[control.tab_shape])
                widget.setTabsClosable(control.tab_closable)
                widget.setMovable(control.tab_movable)
                
                widget.setStyleSheet(f"""
                    QTabWidget {{
                        background-color: {control.bg_color.name()};
                        color: {control.fg_color.name()};
                        font-family: {control.font.family()};
                        font-size: {control.font.pointSize()}px;
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
                        background-color: {control.bg_color.name()};
                        color: {control.fg_color.name()};
                        border: 1px solid #999999;
                        border-bottom: none;
                    }}
                """)
                
                pages = []
                for i in range(control.tab_count):
                    title = control.tab_titles[i] if i < len(control.tab_titles) else f"Tab {i+1}"
                    page = QWidget()
                    page.setStyleSheet("background-color: transparent;") 
                    widget.addTab(page, title)
                    pages.append(page)
                id_to_tab_pages[control.id] = pages
                
                if control.tab_current_index < control.tab_count:
                    widget.setCurrentIndex(control.tab_current_index)
            elif control.type == "QGroupBox":
                widget = QGroupBox(control.text, preview_dialog)
                widget.setStyleSheet(f"""
                    QGroupBox {{
                        background-color: transparent;
                        color: {control.fg_color.name()};
                        font-family: {control.font.family()};
                        font-size: {control.font.pointSize()}px;
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
                """)
            elif control.type == "QSlider":
                widget = QSlider(preview_dialog)
                widget.setOrientation(Qt.Horizontal if control.slider_orientation == 1 else Qt.Vertical)
                widget.setMinimum(control.slider_minimum)
                widget.setMaximum(control.slider_maximum)
                widget.setValue(control.slider_value)
                widget.setStyleSheet(f"""
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
                """)
            elif control.type == "QScrollArea":
                widget = QScrollArea(preview_dialog)
                widget.setWidgetResizable(True)
                container = QWidget()
                container.setStyleSheet("background-color: transparent;")
                widget.setWidget(container)
                
                # 画布默认使用
                bg_color = "#f5f7fa" if control.bg_color.name().upper() == "#FFFFFF" else control.bg_color.name()
                
                widget.setStyleSheet(f"""
                    QScrollArea {{
                        background-color: {bg_color};
                        border: 1px solid #e0e0e0;
                    }}
                """)
            elif control.type == "QFrame":
                widget = QFrame(preview_dialog)
                widget.setFrameShape(QFrame.StyledPanel)
                widget.setFrameShadow(QFrame.Raised)
                widget.setStyleSheet(f"""
                    QFrame {{
                        background-color: {control.bg_color.name()};
                        border: 1px solid #e0e0e0;
                        border-radius: 3px;
                    }}
                """)

            if widget:
                if control.use_style:
                    # 应用统一的样式表（包含视觉风格）
                    widget.setStyleSheet(control.get_stylesheet())
                else:
                    # 原生样式
                    widget.setStyleSheet("")
                    # 字体
                    widget.setFont(control.font)
                    # 颜色 (QPalette)
                    # 注意：预览窗口使用widget本身作为parent，需要从widget获取palette
                    # 但新创建的widget可能还没有正确的palette，或者需要强制更新
                    # 这里直接使用QApplication.palette(widget)确保基准正确
                    from PyQt5.QtWidgets import QApplication
                    from PyQt5.QtGui import QPalette
                    palette = QApplication.palette(widget)
                    palette.setColor(QPalette.Window, control.bg_color)
                    palette.setColor(QPalette.WindowText, control.fg_color)
                    palette.setColor(QPalette.Base, control.bg_color)
                    palette.setColor(QPalette.Text, control.fg_color)
                    palette.setColor(QPalette.Button, control.bg_color)
                    palette.setColor(QPalette.ButtonText, control.fg_color)
                    widget.setPalette(palette)
                    
                    # 自动填充背景
                    if control.type in ["QLabel", "QFrame", "QScrollArea", "QGroupBox", "QWidget"]:
                         widget.setAutoFillBackground(True)
                    else:
                         widget.setAutoFillBackground(False)

                # 通用属性设置
                widget.setGeometry(control.rect)
                widget.setEnabled(control.enabled)
                widget.setVisible(control.visible)
                
                # 设置滚动条策略
                if control.type in ["QScrollArea", "QTextEdit", "QListWidget", "QTableWidget", "QTreeWidget"]:
                    policy_h = Qt.ScrollBarAsNeeded if control.h_scrollbar else Qt.ScrollBarAlwaysOff
                    policy_v = Qt.ScrollBarAsNeeded if control.v_scrollbar else Qt.ScrollBarAlwaysOff
                    if hasattr(widget, "setHorizontalScrollBarPolicy"):
                        widget.setHorizontalScrollBarPolicy(policy_h)
                    if hasattr(widget, "setVerticalScrollBarPolicy"):
                        widget.setVerticalScrollBarPolicy(policy_v)
                
                bind_events(widget, control)
                id_to_widget[control.id] = widget

        # 2. 第二遍：处理父子关系和层级
        for control in self.design_canvas.controls:
            if control.id not in id_to_widget:
                continue
            
            widget = id_to_widget[control.id]
            
            if control.parent and control.parent.id in id_to_widget:
                parent_control = control.parent
                real_parent_widget = id_to_widget[parent_control.id]
                
                if parent_control.type == "QTabWidget":
                    pages = id_to_tab_pages.get(parent_control.id, [])
                    if 0 <= control.parent_tab_index < len(pages):
                        target_page = pages[control.parent_tab_index]
                        widget.setParent(target_page)
                        
                        tab_bar_height = real_parent_widget.tabBar().height()
                        if tab_bar_height <= 0: tab_bar_height = 30
                        
                        local_rect = QRect(control.rect)
                        local_rect.translate(0, -tab_bar_height)
                        widget.setGeometry(local_rect)
                        
                        if control.visible:
                            widget.show()
                elif parent_control.type == "QScrollArea":
                    scroll_content = real_parent_widget.widget()
                    widget.setParent(scroll_content)
                    
                    # 确保内容区域足够大
                    min_width = max(scroll_content.width(), control.rect.x() + control.rect.width() + 10)
                    min_height = max(scroll_content.height(), control.rect.y() + control.rect.height() + 10)
                    scroll_content.resize(min_width, min_height)
                    
                    widget.setGeometry(control.rect)
                    if control.visible:
                        widget.show()
                else:
                    widget.setParent(real_parent_widget)
                    if control.visible:
                        widget.show()
            else:
                pass

        # 设置所有函数实现
        preview_dialog.setup_functions()

        preview_dialog.exec_()

    def new_project(self):
        """新建项目初始化"""
        self.design_canvas.clear_canvas()
        self.current_project_path = None
        self.update_status("新建项目")

    def save_project(self):
        """保存项目"""
        if not self.current_project_path:
            # 默认保存到 projects 目录
            default_dir = os.path.join(os.getcwd(), "projects")
            if not os.path.exists(default_dir):
                os.makedirs(default_dir)
            
            # 使用当前标题作为默认文件名
            default_name = self.design_canvas.main_window_props.title
            if not default_name:
                default_name = "新项目"
                
            default_path = os.path.join(default_dir, f"{default_name}.pack")

            # 如果是新项目，需要另存为
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存项目", default_path, "项目文件 (*.pack);;JSON文件 (*.json)"
            )
            if not file_path:
                return
            
            # 确保有后缀
            if not file_path.endswith('.pack') and not file_path.endswith('.json'):
                file_path += '.pack'
        else:
            file_path = self.current_project_path
            
        if ProjectManager.save_project(file_path, self.design_canvas):
            self.current_project_path = file_path
            self.update_status(f"项目已保存: {file_path}")
            QMessageBox.information(self, "成功", "项目保存成功！")
            
            # 通知主窗口更新列表
            self.project_saved.emit()
        else:
            QMessageBox.critical(self, "错误", "项目保存失败！")

    def generate_code_to_file(self):
        """生成可运行的PyQt5代码并保存到文件（Qt5风格）"""
        if not self.design_canvas.controls:
            QMessageBox.warning(self, "警告", "画布中无控件！")
            return

        # 获取主窗口属性
        mw_props = self.design_canvas.main_window_props
        
        # 1. 构建父子关系映射
        children_map = {} # parent_id -> list of controls
        top_level_controls = []
        
        # 验证控件列表，确保parent引用有效
        valid_ids = {c.id for c in self.design_canvas.controls}
        
        for control in self.design_canvas.controls:
            has_parent = False
            if control.parent and control.parent.id in valid_ids:
                has_parent = True
                if control.parent.id not in children_map:
                    children_map[control.parent.id] = []
                children_map[control.parent.id].append(control)
            
            if not has_parent:
                top_level_controls.append(control)

        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 生成UI类文件名
        ui_file_name = "ui_mainwindow.py"
        main_file_name = "mainwindow.py"

        # 开始构建UI代码
        ui_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易语言风格UI - 自动生成的PyQt5 UI代码
生成时间: {timestamp}
"""
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, 
                             QLineEdit, QTextEdit, QCheckBox, QRadioButton, QComboBox, 
                             QListWidget, QTableWidget, QTabWidget, QGroupBox, QSlider, 
                             QScrollArea, QFrame, QAbstractItemView, QTableWidgetItem)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor, QPalette


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize({mw_props.width}, {mw_props.height})
        MainWindow.setWindowTitle("{mw_props.title}")
        MainWindow.setStyleSheet("background-color: {mw_props.bg_color.name()};")

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
'''

        # 定义递归生成函数
        def generate_widget_code(control, parent_var="self.centralwidget", indent_level=2):
            indent = "    " * indent_level
            c_code = ""
            var_name = f"self.{control.name}"
            
            # 1. 实例化
            c_code += f'{indent}{var_name} = {control.type}({parent_var})\n'
            c_code += f'{indent}{var_name}.setObjectName("{control.name}")\n'
            
            # 2. Geometry
            x, y, w, h = control.rect.x(), control.rect.y(), control.rect.width(), control.rect.height()
            if control.parent and control.parent.type == "QTabWidget":
                # Tab页内坐标修正：减去TabBar高度（估算30）
                y = max(0, y - 30)
            
            c_code += f'{indent}{var_name}.setGeometry(QRect({x}, {y}, {w}, {h}))\n'
            
            # 3. 样式表与外观
            if control.use_style:
                # 使用样式表
                style = control.get_stylesheet()
                if style:
                    style_str = style.replace('\n', ' ').replace('"', '\\"') # 压缩为一行并转义双引号
                    c_code += f'{indent}{var_name}.setStyleSheet("{style_str}")\n'
            else:
                # 使用原生样式 + 自定义属性
                c_code += f'{indent}{var_name}.setStyleSheet("")\n'
                
                # 字体
                font_family = control.font.family()
                font_size = control.font.pointSize()
                c_code += f'{indent}font = QFont("{font_family}", {font_size})\n'
                if control.font.bold(): c_code += f'{indent}font.setBold(True)\n'
                if control.font.italic(): c_code += f'{indent}font.setItalic(True)\n'
                if control.font.underline(): c_code += f'{indent}font.setUnderline(True)\n'
                if control.font.strikeOut(): c_code += f'{indent}font.setStrikeOut(True)\n'
                c_code += f'{indent}{var_name}.setFont(font)\n'
                
                # 颜色 (QPalette)
                bg_c = control.bg_color.name()
                fg_c = control.fg_color.name()
                
                c_code += f'{indent}pal = {var_name}.palette()\n'
                c_code += f'{indent}pal.setColor(QPalette.Window, QColor("{bg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.WindowText, QColor("{fg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.Base, QColor("{bg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.Text, QColor("{fg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.Button, QColor("{bg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.ButtonText, QColor("{fg_c}"))\n'
                c_code += f'{indent}{var_name}.setPalette(pal)\n'
                
                # 自动填充背景
                if control.type in ["QLabel", "QFrame", "QScrollArea", "QGroupBox", "QWidget"]:
                     c_code += f'{indent}{var_name}.setAutoFillBackground(True)\n'
                else:
                     c_code += f'{indent}{var_name}.setAutoFillBackground(False)\n'
            
            # 4. 基础属性
            if hasattr(control, 'text') and control.text:
                safe_text = control.text.replace('"', '\\"')
                if control.type in ["QLabel", "QPushButton", "QCheckBox", "QRadioButton", "QLineEdit"]:
                    c_code += f'{indent}{var_name}.setText("{safe_text}")\n'
                elif control.type == "QGroupBox":
                    c_code += f'{indent}{var_name}.setTitle("{safe_text}")\n'

            # 5. 特殊属性
            if control.type in ["QCheckBox", "QRadioButton"] and control.checked:
                c_code += f'{indent}{var_name}.setChecked(True)\n'
            
            if control.type == "QLineEdit":
                if control.read_only: c_code += f'{indent}{var_name}.setReadOnly(True)\n'
                if control.placeholder: 
                    safe_placeholder = control.placeholder.replace('"', '\\"')
                    c_code += f'{indent}{var_name}.setPlaceholderText("{safe_placeholder}")\n'
                if control.password_mode: c_code += f'{indent}{var_name}.setEchoMode(QLineEdit.Password)\n'
            
            if control.type == "QComboBox":
                 c_code += f'{indent}{var_name}.setEditable({control.combo_editable})\n'
                 c_code += f'{indent}{var_name}.addItems(["选项1", "选项2", "选项3"])\n'
            
            if control.type == "QListWidget":
                # List items
                safe_items = [str(item).replace('"', '\\"') for item in control.list_items]
                c_code += f'{indent}{var_name}.addItems({safe_items})\n'
                c_code += f'{indent}{var_name}.setAlternatingRowColors({control.list_alternating_row_colors})\n'
            
            if control.type == "QTableWidget":
                c_code += f'{indent}{var_name}.setRowCount({control.table_row_count})\n'
                c_code += f'{indent}{var_name}.setColumnCount({control.table_column_count})\n'
                safe_headers = [str(h).replace('"', '\\"') for h in control.table_headers]
                safe_v_headers = [str(h).replace('"', '\\"') for h in control.table_row_headers]
                c_code += f'{indent}{var_name}.setHorizontalHeaderLabels({safe_headers})\n'
                c_code += f'{indent}{var_name}.setVerticalHeaderLabels({safe_v_headers})\n'
                # Table Data
                for r in range(control.table_row_count):
                    for c in range(control.table_column_count):
                        if r < len(control.table_data) and c < len(control.table_data[r]):
                            val = str(control.table_data[r][c]).replace('"', '\\"')
                            c_code += f'{indent}{var_name}.setItem({r}, {c}, QTableWidgetItem("{val}"))\n'

            if control.type == "QSlider":
                orientation = "Qt.Horizontal" if control.slider_orientation == 1 else "Qt.Vertical"
                c_code += f'{indent}{var_name}.setOrientation({orientation})\n'
                c_code += f'{indent}{var_name}.setMinimum({control.slider_minimum})\n'
                c_code += f'{indent}{var_name}.setMaximum({control.slider_maximum})\n'
                c_code += f'{indent}{var_name}.setValue({control.slider_value})\n'

            # Enabled/Visible
            if not control.enabled: c_code += f'{indent}{var_name}.setEnabled(False)\n'
            if not control.visible: c_code += f'{indent}{var_name}.setVisible(False)\n'

            # 6. 容器递归处理
            if control.type == "QTabWidget":
                c_code += f'{indent}{var_name}.setTabPosition({control.tab_position})\n'
                # Tab Pages
                for i in range(control.tab_count):
                    page_var = f"{var_name}_Page{i+1}"
                    title = control.tab_titles[i] if i < len(control.tab_titles) else f"Page {i+1}"
                    safe_title = title.replace('"', '\\"')
                    c_code += f'{indent}{page_var} = QWidget()\n'
                    c_code += f'{indent}{page_var}.setObjectName("{page_var}")\n'
                    c_code += f'{indent}{page_var}.setStyleSheet("background-color: transparent;")\n'
                    c_code += f'{indent}{var_name}.addTab({page_var}, "{safe_title}")\n'
                    
                    # Children in this tab
                    if control.id in children_map:
                        for child in children_map[control.id]:
                            # 容错处理：如果索引无效，默认放到第一页
                            child_tab_idx = child.parent_tab_index
                            if child_tab_idx < 0 or child_tab_idx >= control.tab_count:
                                child_tab_idx = 0
                                
                            if child_tab_idx == i:
                                c_code += generate_widget_code(child, page_var, indent_level)
                                
            elif control.type == "QScrollArea":
                content_var = f"{var_name}_Content"
                c_code += f'{indent}{var_name}.setWidgetResizable(True)\n'
                c_code += f'{indent}{content_var} = QWidget()\n'
                c_code += f'{indent}{content_var}.setGeometry(QRect(0, 0, {control.rect.width()-2}, {control.rect.height()-2}))\n'
                c_code += f'{indent}{content_var}.setObjectName("{content_var}")\n'
                c_code += f'{indent}{var_name}.setWidget({content_var})\n'
                
                if control.id in children_map:
                    for child in children_map[control.id]:
                        c_code += generate_widget_code(child, content_var, indent_level)
            
            else:
                # GroupBox, Frame etc.
                if control.id in children_map:
                    for child in children_map[control.id]:
                        c_code += generate_widget_code(child, var_name, indent_level)

            return c_code

        # 生成所有顶层控件
        setup_body = ""
        for control in top_level_controls:
            setup_body += generate_widget_code(control, "self.centralwidget", 2)
        
        if not setup_body.strip():
            setup_body = "        pass\n"
        
        ui_code += setup_body

        # 生成主窗口类代码
        main_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易语言风格UI - 自动生成的PyQt5主窗口代码
生成时间: {timestamp}
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTranslator, QLibraryInfo
from ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # 设置UI
        self.setupUi(self)
        # 绑定事件
        self.bind_events()
    
    def bind_events(self):
'''
        has_events = False
        for control in self.design_canvas.controls:
            for event_data in control.events:
                if len(event_data) < 2: continue
                event_name, callback = event_data[0], event_data[1]
                
                # 检查回调函数名是否有效
                if event_name and callback and isinstance(callback, str):
                    func_name = callback.split('(')[0].strip() if '(' in callback else callback
                    func_name = func_name.strip()
                    if func_name:
                        main_code += f'        self.{control.name}.{event_name}.connect(self.{func_name})\n'
                        has_events = True
        
        if not has_events:
            main_code += "        pass\n"

        # 用户自定义函数
        main_code += '''
    # 用户自定义函数
'''
        user_functions = set()
        for control in self.design_canvas.controls:
            for event_data in control.events:
                if len(event_data) < 2: continue
                callback = event_data[1]
                if callback and isinstance(callback, str):
                    func_name = callback.split('(')[0].strip() if '(' in callback else callback
                    func_name = func_name.strip()
                    if func_name:
                        user_functions.add(func_name)
        
        for func_name in user_functions:
            main_code += f'''
    def {func_name}(self):
        """用户自定义函数: {func_name}"""
        print("执行函数: {func_name}")
        QMessageBox.information(self, "事件触发", "执行函数: {func_name}")
'''

        # Main block
        main_code += '''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 尝试加载中文字体和翻译
    translator = QTranslator()
    translations_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    if translator.load("qt_zh_CN.qm", translations_path):
        app.installTranslator(translator)
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
'''

        # 准备保存路径
        base_gen_dir = os.path.join(os.getcwd(), "代码生成")
        folder_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = os.path.join(base_gen_dir, folder_timestamp)
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 保存UI代码文件
        ui_file_path = os.path.join(save_dir, ui_file_name)
        with open(ui_file_path, "w", encoding="utf-8") as f:
            f.write(ui_code)
        
        # 保存主窗口代码文件
        main_file_path = os.path.join(save_dir, main_file_name)
        with open(main_file_path, "w", encoding="utf-8") as f:
            f.write(main_code)

        QMessageBox.information(self, "成功", f"UI代码已生成：\n\n目录: {save_dir}\n文件: {ui_file_name} 和 {main_file_name}\n\n可直接运行 mainwindow.py！")
        
        # 打开文件夹
        try:
            os.startfile(save_dir)
        except Exception as e:
            print(f"无法打开文件夹: {e}")
        return
    
    def generate_ui_code(self):
        """生成UI代码并在文本窗口中显示"""
        if not self.design_canvas.controls:
            QMessageBox.warning(self, "警告", "画布中无控件！")
            return

        # 获取主窗口属性
        mw_props = self.design_canvas.main_window_props
        
        # 1. 构建父子关系映射
        children_map = {} # parent_id -> list of controls
        top_level_controls = []
        
        # 验证控件列表，确保parent引用有效
        valid_ids = {c.id for c in self.design_canvas.controls}
        
        for control in self.design_canvas.controls:
            has_parent = False
            if control.parent and control.parent.id in valid_ids:
                has_parent = True
                if control.parent.id not in children_map:
                    children_map[control.parent.id] = []
                children_map[control.parent.id].append(control)
            
            if not has_parent:
                top_level_controls.append(control)

        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 开始构建代码
        code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易语言风格UI - 自动生成的PyQt5代码
生成时间: {timestamp}
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QLabel, 
                             QLineEdit, QTextEdit, QCheckBox, QRadioButton, QComboBox, 
                             QListWidget, QTableWidget, QTabWidget, QGroupBox, QSlider, 
                             QScrollArea, QFrame, QAbstractItemView, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QRect, QMetaObject, QCoreApplication, QTranslator, QLibraryInfo
from PyQt5.QtGui import QFont, QColor, QPalette

# UI类 - 负责UI控件初始化
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize({mw_props.width}, {mw_props.height})
        MainWindow.setWindowTitle("{mw_props.title}")
        MainWindow.setStyleSheet("background-color: {mw_props.bg_color.name()};")

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
'''

        # 定义递归生成函数
        def generate_widget_code(control, parent_var="self.centralwidget", indent_level=2):
            indent = "    " * indent_level
            c_code = ""
            var_name = f"self.{control.name}"
            
            # 1. 实例化
            c_code += f'{indent}{var_name} = {control.type}({parent_var})\n'
            c_code += f'{indent}{var_name}.setObjectName("{control.name}")\n'
            
            # 2. Geometry
            x, y, w, h = control.rect.x(), control.rect.y(), control.rect.width(), control.rect.height()
            if control.parent and control.parent.type == "QTabWidget":
                # Tab页内坐标修正：减去TabBar高度（估算30）
                y = max(0, y - 30)
            
            c_code += f'{indent}{var_name}.setGeometry(QRect({x}, {y}, {w}, {h}))\n'
            
            # 3. 样式表与外观
            if control.use_style:
                # 使用样式表
                style = control.get_stylesheet()
                if style:
                    style_str = style.replace('\n', ' ').replace('"', '\\"') # 压缩为一行并转义双引号
                    c_code += f'{indent}{var_name}.setStyleSheet("{style_str}")\n'
            else:
                # 使用原生样式 + 自定义属性
                c_code += f'{indent}{var_name}.setStyleSheet("")\n'
                
                # 字体
                font_family = control.font.family()
                font_size = control.font.pointSize()
                c_code += f'{indent}font = QFont("{font_family}", {font_size})\n'
                if control.font.bold(): c_code += f'{indent}font.setBold(True)\n'
                if control.font.italic(): c_code += f'{indent}font.setItalic(True)\n'
                if control.font.underline(): c_code += f'{indent}font.setUnderline(True)\n'
                if control.font.strikeOut(): c_code += f'{indent}font.setStrikeOut(True)\n'
                c_code += f'{indent}{var_name}.setFont(font)\n'
                
                # 颜色 (QPalette)
                bg_c = control.bg_color.name()
                fg_c = control.fg_color.name()
                
                c_code += f'{indent}pal = {var_name}.palette()\n'
                c_code += f'{indent}pal.setColor(QPalette.Window, QColor("{bg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.WindowText, QColor("{fg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.Base, QColor("{bg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.Text, QColor("{fg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.Button, QColor("{bg_c}"))\n'
                c_code += f'{indent}pal.setColor(QPalette.ButtonText, QColor("{fg_c}"))\n'
                c_code += f'{indent}{var_name}.setPalette(pal)\n'
                
                # 自动填充背景
                if control.type in ["QLabel", "QFrame", "QScrollArea", "QGroupBox", "QWidget"]:
                     c_code += f'{indent}{var_name}.setAutoFillBackground(True)\n'
                else:
                     c_code += f'{indent}{var_name}.setAutoFillBackground(False)\n'
            
            # 4. 基础属性
            if hasattr(control, 'text') and control.text:
                safe_text = control.text.replace('"', '\\"')
                if control.type in ["QLabel", "QPushButton", "QCheckBox", "QRadioButton", "QLineEdit"]:
                    c_code += f'{indent}{var_name}.setText("{safe_text}")\n'
                elif control.type == "QGroupBox":
                    c_code += f'{indent}{var_name}.setTitle("{safe_text}")\n'

            # 5. 特殊属性
            if control.type in ["QCheckBox", "QRadioButton"] and control.checked:
                c_code += f'{indent}{var_name}.setChecked(True)\n'
            
            if control.type == "QLineEdit":
                if control.read_only: c_code += f'{indent}{var_name}.setReadOnly(True)\n'
                if control.placeholder: 
                    safe_placeholder = control.placeholder.replace('"', '\\"')
                    c_code += f'{indent}{var_name}.setPlaceholderText("{safe_placeholder}")\n'
                if control.password_mode: c_code += f'{indent}{var_name}.setEchoMode(QLineEdit.Password)\n'
            
            if control.type == "QComboBox":
                 c_code += f'{indent}{var_name}.setEditable({control.combo_editable})\n'
                 c_code += f'{indent}{var_name}.addItems(["选项1", "选项2", "选项3"])\n'
            
            if control.type == "QListWidget":
                # List items
                safe_items = [str(item).replace('"', '\\"') for item in control.list_items]
                c_code += f'{indent}{var_name}.addItems({safe_items})\n'
                c_code += f'{indent}{var_name}.setAlternatingRowColors({control.list_alternating_row_colors})\n'
            
            if control.type == "QTableWidget":
                c_code += f'{indent}{var_name}.setRowCount({control.table_row_count})\n'
                c_code += f'{indent}{var_name}.setColumnCount({control.table_column_count})\n'
                safe_headers = [str(h).replace('"', '\\"') for h in control.table_headers]
                safe_v_headers = [str(h).replace('"', '\\"') for h in control.table_row_headers]
                c_code += f'{indent}{var_name}.setHorizontalHeaderLabels({safe_headers})\n'
                c_code += f'{indent}{var_name}.setVerticalHeaderLabels({safe_v_headers})\n'
                # Table Data
                for r in range(control.table_row_count):
                    for c in range(control.table_column_count):
                        if r < len(control.table_data) and c < len(control.table_data[r]):
                            val = str(control.table_data[r][c]).replace('"', '\\"')
                            c_code += f'{indent}{var_name}.setItem({r}, {c}, QTableWidgetItem("{val}"))\n'

            if control.type == "QSlider":
                orientation = "Qt.Horizontal" if control.slider_orientation == 1 else "Qt.Vertical"
                c_code += f'{indent}{var_name}.setOrientation({orientation})\n'
                c_code += f'{indent}{var_name}.setMinimum({control.slider_minimum})\n'
                c_code += f'{indent}{var_name}.setMaximum({control.slider_maximum})\n'
                c_code += f'{indent}{var_name}.setValue({control.slider_value})\n'

            # Enabled/Visible
            if not control.enabled: c_code += f'{indent}{var_name}.setEnabled(False)\n'
            if not control.visible: c_code += f'{indent}{var_name}.setVisible(False)\n'

            # 6. 容器递归处理
            if control.type == "QTabWidget":
                c_code += f'{indent}{var_name}.setTabPosition({control.tab_position})\n'
                # Tab Pages
                for i in range(control.tab_count):
                    page_var = f"{var_name}_Page{i+1}"
                    title = control.tab_titles[i] if i < len(control.tab_titles) else f"Page {i+1}"
                    safe_title = title.replace('"', '\\"')
                    c_code += f'{indent}{page_var} = QWidget()\n'
                    c_code += f'{indent}{page_var}.setObjectName("{page_var}")\n'
                    c_code += f'{indent}{page_var}.setStyleSheet("background-color: transparent;")\n'
                    c_code += f'{indent}{var_name}.addTab({page_var}, "{safe_title}")\n'
                    
                    # Children in this tab
                    if control.id in children_map:
                        for child in children_map[control.id]:
                            # 容错处理：如果索引无效，默认放到第一页
                            child_tab_idx = child.parent_tab_index
                            if child_tab_idx < 0 or child_tab_idx >= control.tab_count:
                                child_tab_idx = 0
                                
                            if child_tab_idx == i:
                                c_code += generate_widget_code(child, page_var, indent_level)
                                
            elif control.type == "QScrollArea":
                content_var = f"{var_name}_Content"
                c_code += f'{indent}{var_name}.setWidgetResizable(True)\n'
                c_code += f'{indent}{content_var} = QWidget()\n'
                c_code += f'{indent}{content_var}.setGeometry(QRect(0, 0, {control.rect.width()-2}, {control.rect.height()-2}))\n'
                c_code += f'{indent}{content_var}.setObjectName("{content_var}")\n'
                c_code += f'{indent}{var_name}.setWidget({content_var})\n'
                
                if control.id in children_map:
                    for child in children_map[control.id]:
                        c_code += generate_widget_code(child, content_var, indent_level)
            
            else:
                # GroupBox, Frame etc.
                if control.id in children_map:
                    for child in children_map[control.id]:
                        c_code += generate_widget_code(child, var_name, indent_level)

            return c_code

        # 生成所有顶层控件
        setup_body = ""
        for control in top_level_controls:
            setup_body += generate_widget_code(control, "self.centralwidget", 2)
        
        if not setup_body.strip():
            setup_body = "        pass\n"
        
        code += setup_body

        # 结束UI类定义
        code += '''

# 主窗口类 - 负责业务逻辑和信号事件处理
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # 设置UI
        self.setupUi(self)
        # 绑定事件
        self.bind_events()
    
    def bind_events(self):
'''
        has_events = False
        for control in self.design_canvas.controls:
            for event_data in control.events:
                if len(event_data) < 2: continue
                event_name, callback = event_data[0], event_data[1]
                
                # 检查回调函数名是否有效
                if event_name and callback and isinstance(callback, str):
                    func_name = callback.split('(')[0].strip() if '(' in callback else callback
                    func_name = func_name.strip()
                    if func_name:
                        code += f'        self.{control.name}.{event_name}.connect(self.{func_name})\n'
                        has_events = True
        
        if not has_events:
            code += "        pass\n"

        # 用户自定义函数
        code += '''
    # 用户自定义函数
'''
        user_functions = set()
        for control in self.design_canvas.controls:
            for event_data in control.events:
                if len(event_data) < 2: continue
                callback = event_data[1]
                if callback and isinstance(callback, str):
                    func_name = callback.split('(')[0].strip() if '(' in callback else callback
                    func_name = func_name.strip()
                    if func_name:
                        user_functions.add(func_name)
        
        for func_name in user_functions:
            code += f'''
    def {func_name}(self):
        """用户自定义函数: {func_name}"""
        print("执行函数: {func_name}")
        QMessageBox.information(self, "事件触发", "执行函数: {func_name}")
'''

        # Main block
        code += '''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 尝试加载中文字体和翻译
    translator = QTranslator()
    translations_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    if translator.load("qt_zh_CN.qm", translations_path):
        app.installTranslator(translator)
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
'''

        # 显示代码对话框
        dialog = self.CodeDisplayDialog(code, self)
        dialog.exec_()
    
    class CodeDisplayDialog(QDialog):
        """代码显示对话框，用于显示生成的代码并提供复制功能"""
        def __init__(self, code, parent=None):
            super().__init__(parent)
            self.setWindowTitle("生成的UI代码")
            # 设置固定大小，确保窗口不会无限扩展
            self.setFixedSize(800, 800)
            self.setModal(True)
            
            # 设置布局
            layout = QVBoxLayout(self)
            layout.setSpacing(10)
            layout.setContentsMargins(10, 10, 10, 10)
            
            # 代码显示区域 - 使用纯多行文本
            self.code_text = QTextEdit()
            self.code_text.setPlainText(code)
            self.code_text.setReadOnly(True)
            self.code_text.setFont(QFont("Consolas", 10))
            self.code_text.setLineWrapMode(QTextEdit.NoWrap)
            layout.addWidget(self.code_text, 1)
            
            # 按钮布局
            button_layout = QHBoxLayout()
            button_layout.setSpacing(10)
            
            # 复制按钮
            self.copy_btn = QPushButton("复制代码")
            self.copy_btn.clicked.connect(self.copy_code)
            button_layout.addWidget(self.copy_btn)
            
            # 保存按钮
            self.save_btn = QPushButton("保存到文件")
            self.save_btn.clicked.connect(self.save_code)
            button_layout.addWidget(self.save_btn)
            
            # 关闭按钮
            self.close_btn = QPushButton("关闭")
            self.close_btn.clicked.connect(self.close)
            button_layout.addWidget(self.close_btn)
            
            # 右对齐按钮
            button_layout.addStretch()
            layout.addLayout(button_layout)
        
        def copy_code(self):
            """复制代码到剪贴板"""
            code = self.code_text.toPlainText()
            clipboard = QApplication.clipboard()
            clipboard.setText(code)
            QMessageBox.information(self, "成功", "代码已复制到剪贴板！")
        
        def save_code(self):
            """保存代码到文件"""
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存代码文件", "", "Python Files (*.py);;All Files (*.*)"
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.code_text.toPlainText())
                    QMessageBox.information(self, "成功", f"代码已保存到：\n{file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")
    
    def keyPressEvent(self, event):
        """键盘事件：处理ESC键取消绘制模式"""
        if event.key() == Qt.Key_Escape:
            if self.design_canvas.drawing_mode:
                self.design_canvas.cancel_drawing()
        super().keyPressEvent(event)
