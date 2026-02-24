from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QSpinBox, QColorDialog, QCheckBox, QComboBox, QScrollArea, QListWidget, QTableWidget, QTableWidgetItem, QDialog, QToolButton,
    QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
from ui_control import UIControl
from table_editor_dialog import TableEditorDialog
from event_editor_dialog import EventEditorDialog
from design_canvas import get_control_parent_bounds, get_control_absolute_rect


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
                border-radius: 4px;
                padding: 8px 12px;
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
        self.content_layout.setContentsMargins(0, 8, 0, 8)
        self.content_layout.setSpacing(8)
        layout.addWidget(self.content_widget)
    
    def add_widget(self, widget):
        """添加控件到内容区域"""
        self.content_layout.addWidget(widget)
    
    def toggle(self):
        """切换展开/收缩状态"""
        self.expanded = not self.expanded
        
        if self.expanded:
            self.content_widget.show()
            self.header.setArrowType(Qt.DownArrow)
        else:
            self.content_widget.hide()
            self.header.setArrowType(Qt.RightArrow)


class PropertyPanel(QWidget):
    """属性面板：编辑控件的基础属性、样式、事件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_control = None
        self.current_main_window = None
        self.control_hierarchy_panel = None
        self.updating_list_items = False
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setMinimumWidth(320)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f5f7fa;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #d0d0d0;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #b0b0b0;
            }
            QLabel {
                color: #2c3e50;
            }
        """)

        # 移除空状态提示标签

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.layout.addWidget(self.scroll_area)

        # 创建滚动内容容器
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)
        self.scroll_area.setWidget(self.scroll_content)

        # 控件属性面板内容（初始隐藏）
        self.control_property_content = QWidget()
        self.control_property_layout = QVBoxLayout(self.control_property_content)
        self.control_property_layout.setContentsMargins(0, 0, 0, 0)
        self.control_property_layout.setSpacing(8)
        self.scroll_layout.addWidget(self.control_property_content)
        self.control_property_content.hide()

        # 1. 基础属性组
        self.basic_section = CollapsibleSection("📌 基础属性")
        self.control_property_layout.addWidget(self.basic_section)
        # 组件类型
        type_widget = QWidget()
        type_layout = QHBoxLayout(type_widget)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(8)
        type_label = QLabel("组件类型")
        type_label.setFixedWidth(80)
        type_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.type_value_label = QLabel("")
        self.type_value_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_value_label)
        type_layout.addStretch()
        self.basic_section.add_widget(type_widget)
        
        # 所属父容器
        self.parent_combo, self.parent_combo_widget = self.add_property_combobox("所属父容器", [], self.on_parent_changed)
        self.basic_section.add_widget(self.parent_combo_widget)

        # 名称
        self.name_edit, self.name_edit_widget = self.add_property_lineedit("控件名称", self.on_name_changed)
        self.basic_section.add_widget(self.name_edit_widget)
        # 显示文本
        self.text_edit, self.text_edit_widget = self.add_property_lineedit("显示文本", self.on_text_changed)
        self.basic_section.add_widget(self.text_edit_widget)
        # 显示组件
        self.visible_checkbox, self.visible_widget = self.add_property_checkbox("显示组件", self.on_visible_changed, True)
        self.basic_section.add_widget(self.visible_widget)
        # 锁定组件
        self.locked_checkbox, self.locked_widget = self.add_property_checkbox("锁定组件", self.on_locked_changed, False)
        self.basic_section.add_widget(self.locked_widget)
        # 显示背景色
        self.show_bg_color_checkbox, self.show_bg_color_widget = self.add_property_checkbox("显示背景色", self.on_show_bg_color_changed, True)
        self.basic_section.add_widget(self.show_bg_color_widget)
        # 位置大小
        self.add_position_size_properties_to_section(self.basic_section)

        # 2. 样式与外观属性组
        self.style_section = CollapsibleSection("🎨 样式与外观")
        self.control_property_layout.addWidget(self.style_section)
        
        # 是否使用样式
        self.use_style_group, self.use_style_widget = self.add_property_radio_group("样式模式", "样式表", "原生", self.on_use_style_changed, True)
        self.style_section.add_widget(self.use_style_widget)
        
        # 预设样式
        self.preset_style_combo, self.preset_style_widget = self.add_property_combobox("预设风格", list(UIControl.PRESET_THEMES.keys()), self.on_preset_style_changed)
        self.style_section.add_widget(self.preset_style_widget)
        # 将默认值设为"现代简约"
        self.preset_style_combo.blockSignals(True)
        self.preset_style_combo.setCurrentText("现代简约")
        self.preset_style_combo.blockSignals(False)

        # 视觉风格
        self.visual_style_combo, self.visual_style_widget = self.add_property_combobox("视觉风格", ["默认", "扁平", "圆角", "描边", "渐变"], self.on_visual_style_changed)
        self.style_section.add_widget(self.visual_style_widget)

        # 圆角半径
        self.border_radius_spin, self.border_radius_widget = self.add_property_spinbox("圆角半径", 0, 100, self.on_border_radius_changed)
        self.style_section.add_widget(self.border_radius_widget)

        # 边框宽度
        self.border_width_spin, self.border_width_widget = self.add_property_spinbox("边框宽度", 0, 20, self.on_border_width_changed)
        self.style_section.add_widget(self.border_width_widget)

        # 边框颜色
        self.border_color_widget = QWidget()
        border_color_layout = QHBoxLayout(self.border_color_widget)
        border_color_layout.setContentsMargins(0, 0, 0, 0)
        border_color_layout.setSpacing(8)
        self.border_color_label = QLabel("边框颜色")
        self.border_color_label.setFixedWidth(80)
        self.border_color_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.border_color_btn = QPushButton()
        self.border_color_btn.setFixedSize(36, 36)
        self.border_color_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
            QPushButton:hover {
                border: 1px solid #4dabf7;
            }
        """)
        self.border_color_btn.clicked.connect(self.on_border_color_click)
        border_color_layout.addWidget(self.border_color_label)
        border_color_layout.addWidget(self.border_color_btn)
        border_color_layout.addStretch()
        self.style_section.add_widget(self.border_color_widget)

        # 背景色
        bg_color_widget = QWidget()
        bg_color_layout = QHBoxLayout(bg_color_widget)
        bg_color_layout.setContentsMargins(0, 0, 0, 0)
        bg_color_layout.setSpacing(8)
        self.bg_color_label = QLabel("背景色")
        self.bg_color_label.setFixedWidth(80)
        self.bg_color_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(36, 36)
        self.bg_color_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
            QPushButton:hover {
                border: 1px solid #4dabf7;
            }
        """)
        self.bg_color_btn.clicked.connect(self.on_bg_color_click)
        bg_color_layout.addWidget(self.bg_color_label)
        bg_color_layout.addWidget(self.bg_color_btn)
        bg_color_layout.addStretch()
        self.style_section.add_widget(bg_color_widget)
        
        # 文字色
        fg_color_widget = QWidget()
        fg_color_layout = QHBoxLayout(fg_color_widget)
        fg_color_layout.setContentsMargins(0, 0, 0, 0)
        fg_color_layout.setSpacing(8)
        self.fg_color_label = QLabel("文字色")
        self.fg_color_label.setFixedWidth(80)
        self.fg_color_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.fg_color_btn = QPushButton()
        self.fg_color_btn.setFixedSize(36, 36)
        self.fg_color_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
            QPushButton:hover {
                border: 1px solid #4dabf7;
            }
        """)
        self.fg_color_btn.clicked.connect(self.on_fg_color_click)
        fg_color_layout.addWidget(self.fg_color_label)
        fg_color_layout.addWidget(self.fg_color_btn)
        fg_color_layout.addStretch()
        self.style_section.add_widget(fg_color_widget)

        # 字体选择
        font_widget = QWidget()
        font_layout = QHBoxLayout(font_widget)
        font_layout.setContentsMargins(0, 0, 0, 0)
        font_layout.setSpacing(8)
        font_label = QLabel("字体")
        font_label.setFixedWidth(80)
        font_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.font_combo = QComboBox()
        self.font_combo.addItems(["微软雅黑", "宋体", "黑体", "楷体", "仿宋"])
        self.font_combo.setMinimumHeight(36)
        self.font_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QComboBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTAgMkw2IDhMMTIgMlIiIHN0cm9rZT0iIzY3NTc1NyIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=);
            }
        """)
        self.font_combo.currentIndexChanged.connect(self.on_font_changed)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)
        font_layout.addStretch()
        self.style_section.add_widget(font_widget)
        # 字号
        size_widget = QWidget()
        size_layout = QHBoxLayout(size_widget)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setSpacing(8)
        size_label = QLabel("字号")
        size_label.setFixedWidth(80)
        size_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(12)
        self.size_spin.setMinimumHeight(36)
        self.size_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        self.size_spin.valueChanged.connect(self.on_font_size_changed)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        self.style_section.add_widget(size_widget)
        # 粗体
        self.bold_checkbox, self.bold_widget = self.add_property_checkbox("粗体", self.on_bold_changed)
        self.style_section.add_widget(self.bold_widget)
        # 斜体
        self.italic_checkbox, self.italic_widget = self.add_property_checkbox("斜体", self.on_italic_changed)
        self.style_section.add_widget(self.italic_widget)
        # 下划线
        self.underline_checkbox, self.underline_widget = self.add_property_checkbox("下划线", self.on_underline_changed)
        self.style_section.add_widget(self.underline_widget)
        # 删除线
        self.strikethrough_checkbox, self.strikethrough_widget = self.add_property_checkbox("删除线", self.on_strikethrough_changed)
        self.style_section.add_widget(self.strikethrough_widget)
        # 文本对齐
        self.align_combobox, self.align_widget = self.add_property_combobox("文本对齐", ["左对齐", "居中", "右对齐"], self.on_align_changed)
        self.style_section.add_widget(self.align_widget)
        # 自动换行
        self.wrap_text_checkbox, self.wrap_text_widget = self.add_property_checkbox("自动换行", self.on_wrap_text_changed)
        self.style_section.add_widget(self.wrap_text_widget)



        # 3. 控件特有属性组
        self.control_specific_section = CollapsibleSection("⚙️ 控件特有属性")
        self.control_property_layout.addWidget(self.control_specific_section)
        
        # 选中状态（复选框/单选框）
        self.checked_checkbox, self.checked_widget = self.add_property_checkbox("选中状态", self.on_checked_changed)
        self.control_specific_section.add_widget(self.checked_widget)
        self.checked_widget.hide()
        
        # 只读状态（输入框）
        self.read_only_checkbox, self.read_only_widget = self.add_property_checkbox("只读状态", self.on_read_only_changed)
        self.control_specific_section.add_widget(self.read_only_widget)
        self.read_only_widget.hide()
        
        # 密码模式（输入框）
        self.password_mode_checkbox, self.password_mode_widget = self.add_property_checkbox("密码模式", self.on_password_mode_changed)
        self.control_specific_section.add_widget(self.password_mode_widget)
        self.password_mode_widget.hide()
        
        # 最大长度（输入框）
        self.max_length_spin, self.max_length_widget = self.add_property_spinbox("最大长度", 0, 10000, self.on_max_length_changed, "无限制")
        self.control_specific_section.add_widget(self.max_length_widget)
        self.max_length_widget.hide()
        
        # 占位符文本（输入框）
        self.placeholder_edit, self.placeholder_widget = self.add_property_lineedit("占位符文本", self.on_placeholder_changed)
        self.control_specific_section.add_widget(self.placeholder_widget)
        self.placeholder_widget.hide()
        
        # 只读状态（QTextEdit）
        self.text_edit_read_only_checkbox, self.text_edit_read_only_widget = self.add_property_checkbox("只读状态", self.on_text_edit_read_only_changed)
        self.control_specific_section.add_widget(self.text_edit_read_only_widget)
        self.text_edit_read_only_widget.hide()
        
        # 占位符文本（QTextEdit）
        self.text_edit_placeholder_edit, self.text_edit_placeholder_widget = self.add_property_lineedit("占位符文本", self.on_text_edit_placeholder_changed)
        self.control_specific_section.add_widget(self.text_edit_placeholder_widget)
        self.text_edit_placeholder_widget.hide()
        
        # 可编辑状态（QComboBox）
        self.combo_editable_checkbox, self.combo_editable_widget = self.add_property_checkbox("可编辑", self.on_combo_editable_changed)
        self.control_specific_section.add_widget(self.combo_editable_widget)
        self.combo_editable_widget.hide()
        
        # 选择模式（QListWidget）
        self.list_selection_mode_combobox, self.list_selection_mode_widget = self.add_property_combobox("选择模式", ["单选", "多选", "扩展选择"], self.on_list_selection_mode_changed)
        self.control_specific_section.add_widget(self.list_selection_mode_widget)
        self.list_selection_mode_widget.hide()
        
        # 列表项内容（QListWidget）
        self.list_items_widget = QWidget()
        self.list_items_layout = QVBoxLayout(self.list_items_widget)
        self.list_items_layout.setContentsMargins(0, 0, 0, 0)
        self.list_items_layout.setSpacing(8)
        
        list_items_label = QLabel("列表项内容：")
        list_items_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.list_items_layout.addWidget(list_items_label)
        
        # 列表项显示和编辑区域
        self.list_items_listwidget = QListWidget()
        self.list_items_listwidget.setMinimumHeight(200)
        self.list_items_listwidget.setMaximumHeight(300)
        self.list_items_listwidget.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: #ffffff;
                padding: 4px;
            }
            QListWidget:focus {
                border: 1px solid #4dabf7;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #e7f5ff;
                color: #1971c2;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        self.list_items_listwidget.itemChanged.connect(self.on_list_item_changed)
        self.list_items_listwidget.currentRowChanged.connect(self.on_list_item_selected)
        self.list_items_layout.addWidget(self.list_items_listwidget)
        
        # 操作按钮区域
        self.list_items_buttons_widget = QWidget()
        self.list_items_buttons_layout = QHBoxLayout(self.list_items_buttons_widget)
        self.list_items_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.list_items_buttons_layout.setSpacing(6)
        
        button_style = """
            QPushButton {
                background-color: transparent;
                color: #495057;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #ced4da;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QPushButton:disabled {
                background-color: transparent;
                color: #adb5bd;
                border: 1px solid #dee2e6;
            }
        """
        
        # 添加按钮
        self.list_items_add_btn = QPushButton("添加")
        self.list_items_add_btn.setMinimumHeight(32)
        self.list_items_add_btn.setStyleSheet(button_style)
        self.list_items_add_btn.clicked.connect(self.on_list_item_add)
        self.list_items_buttons_layout.addWidget(self.list_items_add_btn)
        
        # 删除按钮
        self.list_items_del_btn = QPushButton("删除")
        self.list_items_del_btn.setMinimumHeight(32)
        self.list_items_del_btn.setStyleSheet(button_style)
        self.list_items_del_btn.clicked.connect(self.on_list_item_delete)
        self.list_items_del_btn.setEnabled(False)
        self.list_items_buttons_layout.addWidget(self.list_items_del_btn)
        
        # 上移按钮
        self.list_items_up_btn = QPushButton("上移")
        self.list_items_up_btn.setMinimumHeight(32)
        self.list_items_up_btn.setStyleSheet(button_style)
        self.list_items_up_btn.clicked.connect(self.on_list_item_move_up)
        self.list_items_up_btn.setEnabled(False)
        self.list_items_buttons_layout.addWidget(self.list_items_up_btn)
        
        # 下移按钮
        self.list_items_down_btn = QPushButton("下移")
        self.list_items_down_btn.setMinimumHeight(32)
        self.list_items_down_btn.setStyleSheet(button_style)
        self.list_items_down_btn.clicked.connect(self.on_list_item_move_down)
        self.list_items_down_btn.setEnabled(False)
        self.list_items_buttons_layout.addWidget(self.list_items_down_btn)
        
        self.list_items_layout.addWidget(self.list_items_buttons_widget)
        self.control_specific_section.add_widget(self.list_items_widget)
        self.list_items_widget.hide()
        
        # 编辑触发方式（QListWidget）
        self.list_edit_triggers_combobox, self.list_edit_triggers_widget = self.add_property_combobox("编辑触发", ["不可编辑", "双击编辑", "选中编辑", "任意编辑"], self.on_list_edit_triggers_changed)
        self.control_specific_section.add_widget(self.list_edit_triggers_widget)
        self.list_edit_triggers_widget.hide()
        
        # 交替行颜色（QListWidget）
        self.list_alternating_row_colors_checkbox, self.list_alternating_row_colors_widget = self.add_property_checkbox("交替行颜色", self.on_list_alternating_row_colors_changed)
        self.control_specific_section.add_widget(self.list_alternating_row_colors_widget)
        self.list_alternating_row_colors_widget.hide()
        
        # 启用排序（QListWidget）
        self.list_sorting_enabled_checkbox, self.list_sorting_enabled_widget = self.add_property_checkbox("启用排序", self.on_list_sorting_enabled_changed)
        self.control_specific_section.add_widget(self.list_sorting_enabled_widget)
        self.list_sorting_enabled_widget.hide()
        
        # 视图模式（QListWidget）
        self.list_view_mode_combobox, self.list_view_mode_widget = self.add_property_combobox("视图模式", ["列表模式", "图标模式"], self.on_list_view_mode_changed)
        self.control_specific_section.add_widget(self.list_view_mode_widget)
        self.list_view_mode_widget.hide()
        
        # 拖拽模式（QListWidget）
        self.list_drag_drop_mode_combobox, self.list_drag_drop_mode_widget = self.add_property_combobox("拖拽模式", ["不可拖拽", "内部拖拽", "拖拽移动", "拖拽复制"], self.on_list_drag_drop_mode_changed)
        self.control_specific_section.add_widget(self.list_drag_drop_mode_widget)
        self.list_drag_drop_mode_widget.hide()
        
        # 调整大小模式（QListWidget）
        self.list_resize_mode_combobox, self.list_resize_mode_widget = self.add_property_combobox("调整大小", ["固定", "自适应"], self.on_list_resize_mode_changed)
        self.control_specific_section.add_widget(self.list_resize_mode_widget)
        self.list_resize_mode_widget.hide()
        
        # 移动模式（QListWidget）
        self.list_movement_combobox, self.list_movement_widget = self.add_property_combobox("移动模式", ["静态", "自由", "吸附"], self.on_list_movement_changed)
        self.control_specific_section.add_widget(self.list_movement_widget)
        self.list_movement_widget.hide()
        
        # 自动换行模式（QTextEdit）
        self.text_edit_wrap_mode_combobox, self.text_edit_wrap_mode_widget = self.add_property_combobox("自动换行", ["不换行", "按词换行", "按字符换行"], self.on_text_edit_wrap_mode_changed)
        self.control_specific_section.add_widget(self.text_edit_wrap_mode_widget)
        self.text_edit_wrap_mode_widget.hide()
        
        # 文本对齐（QTextEdit）
        self.text_edit_alignment_combobox, self.text_edit_alignment_widget = self.add_property_combobox("文本对齐", ["左对齐", "居中", "右对齐"], self.on_text_edit_alignment_changed)
        self.control_specific_section.add_widget(self.text_edit_alignment_widget)
        self.text_edit_alignment_widget.hide()
        
        # 表格数据（QTableWidget）
        self.table_data_widget = QWidget()
        self.table_data_layout = QVBoxLayout(self.table_data_widget)
        self.table_data_layout.setContentsMargins(0, 0, 0, 0)
        self.table_data_layout.addWidget(QLabel("表格数据："))
        self.table_data_edit_btn = QPushButton("编辑表格数据")
        self.table_data_edit_btn.setMinimumHeight(36)
        self.table_data_edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4dabf7;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #339af0;
            }
            QPushButton:pressed {
                background-color: #228be6;
            }
        """)
        self.table_data_edit_btn.clicked.connect(self.on_table_data_edit_click)
        self.table_data_layout.addWidget(self.table_data_edit_btn)
        self.control_specific_section.add_widget(self.table_data_widget)
        self.table_data_widget.hide()
        
        # 显示网格（QTableWidget）
        self.table_show_grid_checkbox, self.table_show_grid_widget = self.add_property_checkbox("显示网格", self.on_table_show_grid_changed)
        self.control_specific_section.add_widget(self.table_show_grid_widget)
        self.table_show_grid_widget.hide()
        
        # 选择模式（QTableWidget）
        self.table_selection_mode_combobox, self.table_selection_mode_widget = self.add_property_combobox("选择模式", ["单选单元格", "多选单元格", "整行选择", "整列选择"], self.on_table_selection_mode_changed)
        self.control_specific_section.add_widget(self.table_selection_mode_widget)
        self.table_selection_mode_widget.hide()
        
        # 编辑触发方式（QTableWidget）
        self.table_edit_triggers_combobox, self.table_edit_triggers_widget = self.add_property_combobox("编辑触发", ["不可编辑", "双击编辑", "选中编辑", "任意编辑"], self.on_table_edit_triggers_changed)
        self.control_specific_section.add_widget(self.table_edit_triggers_widget)
        self.table_edit_triggers_widget.hide()
        
        # 交替行颜色（QTableWidget）
        self.table_alternating_row_colors_checkbox, self.table_alternating_row_colors_widget = self.add_property_checkbox("交替行颜色", self.on_table_alternating_row_colors_changed)
        self.control_specific_section.add_widget(self.table_alternating_row_colors_widget)
        self.table_alternating_row_colors_widget.hide()
        
        # 启用排序（QTableWidget）
        self.table_sorting_enabled_widget = QWidget()
        self.table_sorting_enabled_layout = QHBoxLayout(self.table_sorting_enabled_widget)
        self.table_sorting_enabled_layout.setContentsMargins(0, 0, 0, 0)
        self.table_sorting_enabled_layout.addWidget(QLabel("启用排序："))
        self.table_sorting_enabled_checkbox = QCheckBox()
        self.table_sorting_enabled_checkbox.stateChanged.connect(self.on_table_sorting_enabled_changed)
        self.table_sorting_enabled_layout.addWidget(self.table_sorting_enabled_checkbox)
        self.table_sorting_enabled_layout.addStretch()
        self.control_specific_section.add_widget(self.table_sorting_enabled_widget)
        self.table_sorting_enabled_widget.hide()
        
        # 角按钮启用（QTableWidget）
        self.table_corner_button_enabled_widget = QWidget()
        self.table_corner_button_enabled_layout = QHBoxLayout(self.table_corner_button_enabled_widget)
        self.table_corner_button_enabled_layout.setContentsMargins(0, 0, 0, 0)
        self.table_corner_button_enabled_layout.addWidget(QLabel("角按钮："))
        self.table_corner_button_enabled_checkbox = QCheckBox()
        self.table_corner_button_enabled_checkbox.setChecked(True)
        self.table_corner_button_enabled_checkbox.stateChanged.connect(self.on_table_corner_button_enabled_changed)
        self.table_corner_button_enabled_layout.addWidget(self.table_corner_button_enabled_checkbox)
        self.table_corner_button_enabled_layout.addStretch()
        self.control_specific_section.add_widget(self.table_corner_button_enabled_widget)
        self.table_corner_button_enabled_widget.hide()
        
        # 选项卡位置（QTabWidget）
        self.tab_position_combobox, self.tab_position_widget = self.add_property_combobox("选项卡位置", ["上", "下", "左", "右"], self.on_tab_position_changed)
        self.control_specific_section.add_widget(self.tab_position_widget)
        self.tab_position_widget.hide()
        
        # 选项卡形状（QTabWidget）
        self.tab_shape_combobox, self.tab_shape_widget = self.add_property_combobox("选项卡形状", ["圆角", "三角"], self.on_tab_shape_changed)
        self.control_specific_section.add_widget(self.tab_shape_widget)
        self.tab_shape_widget.hide()
        
        # 选项卡可关闭（QTabWidget）
        self.tab_closable_checkbox, self.tab_closable_widget = self.add_property_checkbox("可关闭", self.on_tab_closable_changed)
        self.control_specific_section.add_widget(self.tab_closable_widget)
        self.tab_closable_widget.hide()
        
        # 选项卡可移动（QTabWidget）
        self.tab_movable_checkbox, self.tab_movable_widget = self.add_property_checkbox("可移动", self.on_tab_movable_changed)
        self.control_specific_section.add_widget(self.tab_movable_widget)
        self.tab_movable_widget.hide()
        
        # 选项卡数量（QTabWidget）
        self.tab_count_widget = QWidget()
        self.tab_count_layout = QHBoxLayout(self.tab_count_widget)
        self.tab_count_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_count_layout.addWidget(QLabel("选项卡数量："))
        self.tab_count_spinbox = QSpinBox()
        self.tab_count_spinbox.setMinimum(1)
        self.tab_count_spinbox.setMaximum(20)
        self.tab_count_spinbox.valueChanged.connect(self.on_tab_count_changed)
        self.tab_count_layout.addWidget(self.tab_count_spinbox)
        self.tab_count_layout.addStretch()
        self.control_specific_section.add_widget(self.tab_count_widget)
        self.tab_count_widget.hide()
        
        # 选项卡标题（QTabWidget）
        self.tab_titles_widget = QWidget()
        self.tab_titles_layout = QVBoxLayout(self.tab_titles_widget)
        self.tab_titles_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_titles_layout.addWidget(QLabel("选项卡标题（每行一个）："))
        self.tab_titles_edit = QTextEdit()
        self.tab_titles_edit.setMaximumHeight(100)
        self.tab_titles_edit.textChanged.connect(self.on_tab_titles_changed)
        self.tab_titles_layout.addWidget(self.tab_titles_edit)
        self.control_specific_section.add_widget(self.tab_titles_widget)
        self.tab_titles_widget.hide()

        # 滑块属性（QSlider）
        self.slider_prop_widget = QWidget()
        self.slider_prop_layout = QVBoxLayout(self.slider_prop_widget)
        self.slider_prop_layout.setContentsMargins(0, 0, 0, 0)
        self.slider_prop_layout.setSpacing(8)
        
        # 最小值
        self.slider_min_spin, self.slider_min_widget = self.add_property_spinbox("最小值", -9999, 9999, self.on_slider_min_changed)
        self.slider_prop_layout.addWidget(self.slider_min_widget)
        
        # 最大值
        self.slider_max_spin, self.slider_max_widget = self.add_property_spinbox("最大值", -9999, 9999, self.on_slider_max_changed)
        self.slider_prop_layout.addWidget(self.slider_max_widget)
        
        # 当前值
        self.slider_val_spin, self.slider_val_widget = self.add_property_spinbox("当前值", -9999, 9999, self.on_slider_val_changed)
        self.slider_prop_layout.addWidget(self.slider_val_widget)
        
        # 方向
        self.slider_orient_combo, self.slider_orient_widget = self.add_property_combobox("方向", ["水平", "垂直"], self.on_slider_orient_changed)
        self.slider_prop_layout.addWidget(self.slider_orient_widget)
        
        self.control_specific_section.add_widget(self.slider_prop_widget)
        self.slider_prop_widget.hide()

        # 4. 事件属性组
        self.event_section = CollapsibleSection("⚡ 事件属性")
        self.control_property_layout.addWidget(self.event_section)
        
        # 事件表格显示
        self.event_table = QTableWidget()
        self.event_table.setColumnCount(3)
        self.event_table.setHorizontalHeaderLabels(["事件名", "函数名", "操作"])
        self.event_table.horizontalHeader().setStretchLastSection(False)
        self.event_table.setColumnWidth(2, 60)
        self.event_table.setMinimumHeight(100)
        self.event_table.setMaximumHeight(200)
        self.event_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #e7f5ff;
                color: #1971c2;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #dee2e6;
                font-weight: 500;
                color: #495057;
            }
        """)
        self.event_section.add_widget(self.event_table)
        
        # 编辑按钮
        self.event_edit_btn = QPushButton("编辑事件绑定")
        self.event_edit_btn.setMinimumHeight(36)
        self.event_edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4dabf7;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #339af0;
            }
            QPushButton:pressed {
                background-color: #228be6;
            }
        """)
        self.event_edit_btn.clicked.connect(self.on_event_edit_click)
        self.event_section.add_widget(self.event_edit_btn)

        # 主窗口属性面板内容（初始隐藏）
        self.main_window_property_content = QWidget()
        self.main_window_layout = QVBoxLayout(self.main_window_property_content)
        self.main_window_layout.setContentsMargins(12, 12, 12, 12)
        self.main_window_layout.setSpacing(10)
        self.scroll_layout.addWidget(self.main_window_property_content)
        self.main_window_property_content.hide()

        # 主窗口基础属性组
        self.add_main_window_section("📌 基础属性")
        # 窗口名称
        self.mw_name_edit = self.add_main_window_property_lineedit("窗口名称", self.on_mw_name_changed)
        # 窗口标题
        self.mw_title_edit = self.add_main_window_property_lineedit("窗口标题", self.on_mw_title_changed)
        # 位置大小
        self.add_main_window_position_size_properties()

        # 主窗口样式属性组
        self.add_main_window_section("🎨 样式属性")
        
        # 启用样式
        self.mw_use_style_group, self.mw_use_style_widget = self.add_property_radio_group("样式模式", "样式表", "原生", self.on_mw_use_style_changed, True)
        self.main_window_layout.addWidget(self.mw_use_style_widget)

        # 背景色
        self.mw_bg_color_btn, self.mw_bg_color_widget = self.add_main_window_property_button("背景色", self.on_mw_bg_color_click)
        self.mw_bg_color_label = QLabel("#f0f0f0")
        self.mw_bg_color_label.setStyleSheet("color: #6c757d; font-size: 12px; padding-left: 105px;")
        self.main_window_layout.addWidget(self.mw_bg_color_label)
        # 标题栏颜色
        self.mw_title_color_btn, self.mw_title_color_widget = self.add_main_window_property_button("标题栏色", self.on_mw_title_color_click)
        self.mw_title_color_label = QLabel("#0066cc")
        self.mw_title_color_label.setStyleSheet("color: #6c757d; font-size: 12px; padding-left: 105px;")
        self.main_window_layout.addWidget(self.mw_title_color_label)
        # 标题文字颜色
        self.mw_title_text_color_btn, self.mw_title_text_color_widget = self.add_main_window_property_button("标题文字色", self.on_mw_title_text_color_click)
        self.mw_title_text_color_label = QLabel("#ffffff")
        self.mw_title_text_color_label.setStyleSheet("color: #6c757d; font-size: 12px; padding-left: 105px;")
        self.main_window_layout.addWidget(self.mw_title_text_color_label)
        # 标题栏高度
        self.mw_title_height_spin, self.mw_title_height_widget = self.add_main_window_spinbox("标题栏高度", 20, 50, self.on_mw_title_height_changed)

        # 全局预设样式属性组
        self.add_main_window_section("🌐 全局预设样式")
        
        # 是否使用全局预设样式
        self.mw_use_global_style_checkbox, self.mw_use_global_style_widget = self.add_main_window_property_checkbox("启用全局样式", self.on_mw_use_global_style_changed, False)
        
        # 全局预设样式选择
        self.mw_global_preset_style_combo, self.mw_global_preset_style_widget = self.add_main_window_property_combobox("全局预设风格", list(UIControl.PRESET_THEMES.keys()), self.on_mw_global_preset_style_changed)
        # 将默认值设为"现代简约"
        self.mw_global_preset_style_combo.blockSignals(True)
        self.mw_global_preset_style_combo.setCurrentText("现代简约")
        self.mw_global_preset_style_combo.blockSignals(False)

    def add_property_radio_group(self, label_text, option1_text, option2_text, callback, initial_value=True):
        """添加带标签的单选按钮组"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setFixedWidth(80)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(15)
        
        rb1 = QRadioButton(option1_text)
        rb2 = QRadioButton(option2_text)
        
        group = QButtonGroup(widget)
        group.addButton(rb1, 1)
        group.addButton(rb2, 0)
        
        if initial_value:
            rb1.setChecked(True)
        else:
            rb2.setChecked(True)
            
        style = """
            QRadioButton {
                color: #495057;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 9px;
                border: 2px solid #dee2e6;
                background-color: white;
            }
            QRadioButton::indicator:hover {
                border-color: #4dabf7;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #4dabf7;
                background-color: white;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSI2IiBjeT0iNiIgcj0iNCIgZmlsbD0iIzRkYWJmNyIvPjwvc3ZnPg==);
            }
        """
        rb1.setStyleSheet(style)
        rb2.setStyleSheet(style)
        
        # 连接信号
        # 注意：这里我们只在按钮状态改变且为选中时触发回调，传递True(样式表)或False(原生)
        group.buttonToggled.connect(lambda btn, checked: callback(group.checkedId() == 1) if checked else None)
        
        radio_layout.addWidget(rb1)
        radio_layout.addWidget(rb2)
        radio_layout.addStretch()
        
        layout.addWidget(label)
        layout.addLayout(radio_layout)
        
        return group, widget

    def add_property_checkbox(self, label_text, callback, checked=False):
        """添加带标签的复选框"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(80)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        checkbox.setMinimumHeight(36)
        checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                color: #495057;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #4dabf7;
            }
            QCheckBox::indicator:checked {
                background-color: #4dabf7;
                border: 2px solid #4dabf7;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMiA2TDUgOUwxMCAzIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
        """)
        checkbox.stateChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(checkbox)
        layout.addStretch()
        return checkbox, widget

    def add_property_combobox(self, label_text, items, callback):
        """添加带标签的下拉框"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(80)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        combobox = QComboBox()
        combobox.setMinimumHeight(36)
        combobox.addItems(items)
        combobox.setStyleSheet("""
            QComboBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QComboBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTAgMkw2IDhMMTIgMlIiIHN0cm9rZT0iIzY3NTc1NyIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=);
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dee2e6;
                background-color: #ffffff;
                selection-background-color: #e7f5ff;
                selection-color: #1971c2;
            }
        """)
        combobox.currentIndexChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(combobox)
        layout.addStretch()
        return combobox, widget

    def add_property_spinbox(self, label_text, min_val, max_val, callback, special_value_text=None):
        """添加带标签的数字输入框"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(80)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setMinimumHeight(36)
        if special_value_text:
            spin.setSpecialValueText(special_value_text)
        spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: transparent;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: transparent;
            }
        """)
        spin.valueChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(spin)
        return spin, widget

    def add_property_lineedit(self, label_text, callback):
        """添加带标签的单行输入框"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(80)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        edit = QLineEdit()
        edit.setMinimumHeight(36)
        edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QLineEdit:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        edit.textChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(edit)
        return edit, widget

    def add_position_size_properties_to_section(self, section):
        """添加位置和大小属性到指定分组"""
        # X坐标
        x_widget = QWidget()
        x_layout = QHBoxLayout(x_widget)
        x_layout.setContentsMargins(0, 0, 0, 0)
        x_layout.setSpacing(8)
        x_label = QLabel("X坐标")
        x_label.setFixedWidth(80)
        x_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.setMinimumHeight(36)
        self.x_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        self.x_spin.valueChanged.connect(self.on_x_changed)
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.x_spin)
        x_layout.addStretch()
        section.add_widget(x_widget)

        # Y坐标
        y_widget = QWidget()
        y_layout = QHBoxLayout(y_widget)
        y_layout.setContentsMargins(0, 0, 0, 0)
        y_layout.setSpacing(8)
        y_label = QLabel("Y坐标")
        y_label.setFixedWidth(80)
        y_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.setMinimumHeight(36)
        self.y_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        self.y_spin.valueChanged.connect(self.on_y_changed)
        y_layout.addWidget(y_label)
        y_layout.addWidget(self.y_spin)
        y_layout.addStretch()
        section.add_widget(y_widget)

        # 宽度
        w_widget = QWidget()
        w_layout = QHBoxLayout(w_widget)
        w_layout.setContentsMargins(0, 0, 0, 0)
        w_layout.setSpacing(8)
        w_label = QLabel("宽度")
        w_label.setFixedWidth(80)
        w_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.w_spin = QSpinBox()
        self.w_spin.setRange(10, 9999)
        self.w_spin.setMinimumHeight(36)
        self.w_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        self.w_spin.valueChanged.connect(self.on_w_changed)
        w_layout.addWidget(w_label)
        w_layout.addWidget(self.w_spin)
        w_layout.addStretch()
        section.add_widget(w_widget)

        # 高度
        h_widget = QWidget()
        h_layout = QHBoxLayout(h_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(8)
        h_label = QLabel("高度")
        h_label.setFixedWidth(80)
        h_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.h_spin = QSpinBox()
        self.h_spin.setRange(10, 9999)
        self.h_spin.setMinimumHeight(36)
        self.h_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        self.h_spin.valueChanged.connect(self.on_h_changed)
        h_layout.addWidget(h_label)
        h_layout.addWidget(self.h_spin)
        h_layout.addStretch()
        section.add_widget(h_widget)

    def add_property_button(self, label_text, callback):
        """添加带标签的颜色选择按钮"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(80)
        label.setStyleSheet("color: #cccccc; font-weight: 500;")
        btn = QPushButton()
        btn.setFixedSize(70, 36)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
            }
            QPushButton:hover {
                border: 1px solid #007acc;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
        """)
        btn.clicked.connect(callback)
        layout.addWidget(label)
        layout.addWidget(btn)
        layout.addStretch()
        return btn

    def update_button_color(self, btn, color):
        """更新颜色按钮的背景色"""
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                border: 1px solid #5c9aff;
            }}
            QPushButton:pressed {{
                background-color: {color.name()};
            }}
        """)

    def add_main_window_section(self, title):
        """添加主窗口属性分组标题"""
        label = QLabel(title)
        label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 600;
                color: #5c9aff;
                padding: 8px 0;
                border-bottom: 2px solid #f0f0f0;
                margin-top: 16px;
            }
        """)
        self.main_window_layout.addWidget(label)

    def add_main_window_property_lineedit(self, label_text, callback):
        """添加主窗口带标签的单行输入框"""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(100)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        edit = QLineEdit()
        edit.setMinimumHeight(36)
        edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QLineEdit:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        edit.textChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(edit)
        self.main_window_layout.addLayout(layout)
        return edit

    def add_main_window_position_size_properties(self):
        """添加主窗口位置和大小属性"""
        # X坐标
        x_layout = QHBoxLayout()
        x_layout.setSpacing(8)
        x_label = QLabel("X坐标")
        x_label.setFixedWidth(100)
        x_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.mw_x_spin = QSpinBox()
        self.mw_x_spin.setRange(0, 2000)
        self.mw_x_spin.setMinimumHeight(36)
        self.mw_x_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        self.mw_x_spin.valueChanged.connect(self.on_mw_x_changed)
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.mw_x_spin)
        self.main_window_layout.addLayout(x_layout)

        # Y坐标
        y_layout = QHBoxLayout()
        y_layout.setSpacing(8)
        y_label = QLabel("Y坐标")
        y_label.setFixedWidth(100)
        y_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.mw_y_spin = QSpinBox()
        self.mw_y_spin.setRange(0, 2000)
        self.mw_y_spin.setMinimumHeight(36)
        self.mw_y_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        self.mw_y_spin.valueChanged.connect(self.on_mw_y_changed)
        y_layout.addWidget(y_label)
        y_layout.addWidget(self.mw_y_spin)
        self.main_window_layout.addLayout(y_layout)

        # 宽度
        w_layout = QHBoxLayout()
        w_layout.setSpacing(8)
        w_label = QLabel("宽度")
        w_label.setFixedWidth(100)
        w_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.mw_w_spin = QSpinBox()
        self.mw_w_spin.setRange(200, 9999)
        self.mw_w_spin.setMinimumHeight(36)
        self.mw_w_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        self.mw_w_spin.valueChanged.connect(self.on_mw_w_changed)
        w_layout.addWidget(w_label)
        w_layout.addWidget(self.mw_w_spin)
        self.main_window_layout.addLayout(w_layout)

        # 高度
        h_layout = QHBoxLayout()
        h_layout.setSpacing(8)
        h_label = QLabel("高度")
        h_label.setFixedWidth(100)
        h_label.setStyleSheet("color: #495057; font-weight: 500;")
        self.mw_h_spin = QSpinBox()
        self.mw_h_spin.setRange(200, 9999)
        self.mw_h_spin.setMinimumHeight(36)
        self.mw_h_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        self.mw_h_spin.valueChanged.connect(self.on_mw_h_changed)
        h_layout.addWidget(h_label)
        h_layout.addWidget(self.mw_h_spin)
        self.main_window_layout.addLayout(h_layout)

    def add_main_window_property_checkbox(self, label_text, callback, checked=False):
        """添加主窗口带标签的复选框"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(100)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        checkbox.setMinimumHeight(36)
        checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                color: #495057;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #4dabf7;
            }
            QCheckBox::indicator:checked {
                background-color: #4dabf7;
                border: 2px solid #4dabf7;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMiA2TDUgOUwxMCAzIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
        """)
        checkbox.stateChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(checkbox)
        layout.addStretch()
        self.main_window_layout.addWidget(widget)
        return checkbox, widget

    def add_main_window_property_button(self, label_text, callback):
        """添加主窗口带标签的按钮"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(100)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        btn = QPushButton()
        btn.setFixedSize(70, 36)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #dee2e6;
                border-radius: 6px;
            }
            QPushButton:hover {
                border: 2px solid #4dabf7;
            }
            QPushButton:pressed {
                background-color: #e7f5ff;
            }
        """)
        btn.clicked.connect(callback)
        layout.addWidget(label)
        layout.addWidget(btn)
        self.main_window_layout.addWidget(widget)
        return btn, widget

    def add_main_window_property_combobox(self, label_text, items, callback):
        """添加主窗口带标签的下拉框"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(100)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        combobox = QComboBox()
        combobox.setMinimumHeight(36)
        combobox.addItems(items)
        combobox.setStyleSheet("""
            QComboBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QComboBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTAgMkw2IDhMMTIgMlIiIHN0cm9rZT0iIzY3NTc1NyIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=);
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dee2e6;
                background-color: #ffffff;
                selection-background-color: #e7f5ff;
                selection-color: #1971c2;
            }
        """)
        combobox.currentIndexChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(combobox)
        layout.addStretch()
        self.main_window_layout.addWidget(widget)
        return combobox, widget


    def add_main_window_spinbox(self, label_text, min_val, max_val, callback):
        """添加主窗口带标签的数字输入框"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(100)
        label.setStyleSheet("color: #495057; font-weight: 500;")
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setMinimumHeight(36)
        spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #495057;
            }
            QSpinBox:focus {
                border: 1px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        spin.valueChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(spin)
        self.main_window_layout.addWidget(widget)
        return spin, widget

    def set_control(self, control):
        """设置当前编辑的控件"""
        # 如果没有选择到控件，自动切换到显示主窗口属性
        if not control:
            # 获取主窗口属性（从当前显示的控件或主窗口中获取）
            if self.current_control:
                main_window_props = self.current_control.parent_canvas.main_window_props
            elif self.current_main_window:
                main_window_props = self.current_main_window
            else:
                # 如果都没有，隐藏面板
                self.control_property_content.hide()
                self.main_window_property_content.hide()
                return
            
            # 显示主窗口属性
            self.set_main_window(main_window_props)
            return
        
        # 有控件选中，显示控件属性
        self.current_control = control
        self.current_main_window = None
        
        # 确保控件属性面板显示
        self.control_property_content.show()
        self.main_window_property_content.hide()

        # 计算主窗口内容区域大小
        content_width = control.parent_canvas.main_window_props.width
        content_height = control.parent_canvas.main_window_props.height  # height 本身就是内容区域高度，无需减去标题栏高度

        # 填充基础属性
        self.type_value_label.setText(control.type)
        self.name_edit.setText(control.name)
        self.text_edit.setText(control.text)
        self.visible_checkbox.setChecked(getattr(control, 'visible', True))
        self.locked_checkbox.setChecked(getattr(control, 'locked', False))
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.w_spin.blockSignals(True)
        self.h_spin.blockSignals(True)
        self.x_spin.setValue(control.rect.x())
        self.y_spin.setValue(control.rect.y())
        self.w_spin.setValue(control.rect.width())
        self.h_spin.setValue(control.rect.height())
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)
        self.w_spin.blockSignals(False)
        self.h_spin.blockSignals(False)

        # 填充字体属性
        font_names = ["微软雅黑", "宋体", "黑体", "楷体", "仿宋"]
        if control.font.family() in font_names:
            self.font_combo.setCurrentIndex(font_names.index(control.font.family()))
        else:
            self.font_combo.setCurrentIndex(0)
        self.size_spin.setValue(control.font.pointSize())
        self.bold_checkbox.setChecked(control.font.bold())
        self.italic_checkbox.setChecked(control.font.italic())
        self.underline_checkbox.setChecked(control.font.underline())
        self.strikethrough_checkbox.setChecked(control.font.strikeOut())

        # 更新SpinBox范围
        self.x_spin.setRange(0, max(0, content_width - control.rect.width()))
        self.y_spin.setRange(0, max(0, content_height - control.rect.height()))
        self.w_spin.setRange(10, max(10, content_width - control.rect.x()))
        self.h_spin.setRange(10, max(10, content_height - control.rect.y()))

        # 填充样式属性
        if control.use_style:
            self.use_style_group.button(1).setChecked(True)
        else:
            self.use_style_group.button(0).setChecked(True)
        self.update_control_style_visibility()
        self.preset_style_combo.blockSignals(True)
        # 如果控件当前预设样式为空或不在列表中，尝试设为"现代简约"或保持"自定义"
        current_preset = control.preset_style
        if not current_preset or current_preset not in UIControl.PRESET_THEMES:
             current_preset = "自定义"
        self.preset_style_combo.setCurrentText(current_preset)
        self.preset_style_combo.blockSignals(False)
        self.visual_style_combo.blockSignals(True)
        self.visual_style_combo.setCurrentText(control.visual_style)
        self.visual_style_combo.blockSignals(False)
        
        # 填充边框属性
        self.border_radius_spin.setValue(control.border_radius)
        self.border_width_spin.setValue(control.border_width)
        self.update_button_color(self.border_color_btn, control.border_color)
        
        self.bg_color_label.setText(control.bg_color.name())
        self.fg_color_label.setText(control.fg_color.name())
        self.update_button_color(self.bg_color_btn, control.bg_color)
        self.update_button_color(self.fg_color_btn, control.fg_color)

        # 填充事件属性
        self.update_event_list()

        # 更新父容器列表
        self.update_parent_combo()

        # 处理"显示背景色"属性的可见性（仅QLabel显示）
        self.show_bg_color_widget.setVisible(control.type == "QLabel")

        # 根据控件类型显示特有属性
        self.show_control_specific_properties(control.type)
        
        # 填充控件特有属性
        if control.type == "QCheckBox" or control.type == "QRadioButton":
            self.checked_checkbox.setChecked(control.checked)
        if control.type == "QLineEdit":
            self.read_only_checkbox.setChecked(control.read_only)
            self.password_mode_checkbox.setChecked(control.password_mode)
            self.max_length_spin.setValue(control.max_length)
            self.placeholder_edit.setText(control.placeholder)
        if control.type == "QLabel":
            self.align_combobox.setCurrentIndex(0 if control.align == Qt.AlignLeft else (1 if control.align == Qt.AlignCenter else 2))
            self.wrap_text_checkbox.setChecked(control.wrap_text)
        if control.type == "QTextEdit":
            self.text_edit_read_only_checkbox.setChecked(control.text_edit_read_only)
            self.text_edit_placeholder_edit.setText(control.text_edit_placeholder)
            self.text_edit_wrap_mode_combobox.setCurrentIndex(control.text_edit_wrap_mode)
            self.text_edit_alignment_combobox.setCurrentIndex(control.text_edit_alignment)
        if control.type == "QComboBox":
            self.combo_editable_checkbox.setChecked(control.combo_editable)
        if control.type == "QListWidget":
            self.list_selection_mode_combobox.setCurrentIndex(control.list_selection_mode)
            self.updating_list_items = True
            self.list_items_listwidget.clear()
            from PyQt5.QtWidgets import QListWidgetItem
            for item_text in control.list_items:
                item = QListWidgetItem(item_text)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.list_items_listwidget.addItem(item)
            self.updating_list_items = False
            self.list_edit_triggers_combobox.setCurrentIndex(control.list_edit_triggers)
            self.list_alternating_row_colors_checkbox.setChecked(control.list_alternating_row_colors)
            self.list_sorting_enabled_checkbox.setChecked(control.list_sorting_enabled)
            self.list_view_mode_combobox.setCurrentIndex(control.list_view_mode)
            self.list_drag_drop_mode_combobox.setCurrentIndex(control.list_drag_drop_mode)
            self.list_resize_mode_combobox.setCurrentIndex(control.list_resize_mode)
            self.list_movement_combobox.setCurrentIndex(control.list_movement)
        if control.type == "QTableWidget":
            self.table_show_grid_checkbox.setChecked(control.table_show_grid)
            self.table_selection_mode_combobox.setCurrentIndex(control.table_selection_mode)
            self.table_edit_triggers_combobox.setCurrentIndex(control.table_edit_triggers)
            self.table_alternating_row_colors_checkbox.setChecked(control.table_alternating_row_colors)
            self.table_sorting_enabled_checkbox.setChecked(control.table_sorting_enabled)
            self.table_corner_button_enabled_checkbox.setChecked(control.table_corner_button_enabled)
        if control.type == "QTabWidget":
            self.tab_position_combobox.setCurrentIndex(control.tab_position)
            self.tab_shape_combobox.setCurrentIndex(control.tab_shape)
            self.tab_closable_checkbox.setChecked(control.tab_closable)
            self.tab_movable_checkbox.setChecked(control.tab_movable)
            self.tab_count_spinbox.setValue(control.tab_count)
            self.tab_titles_edit.setPlainText("\n".join(control.tab_titles))
        if control.type == "QSlider":
            self.slider_min_spin.setValue(control.slider_minimum)
            self.slider_max_spin.setValue(control.slider_maximum)
            self.slider_val_spin.setValue(control.slider_value)
            self.slider_orient_combo.setCurrentIndex(control.slider_orientation - 1)

    def show_control_specific_properties(self, control_type):
        """根据控件类型显示特有属性"""
        # 先隐藏所有特有属性
        self.checked_widget.hide()
        self.read_only_widget.hide()
        self.password_mode_widget.hide()
        self.max_length_widget.hide()
        self.placeholder_widget.hide()
        self.align_widget.hide()
        self.wrap_text_widget.hide()
        self.text_edit_read_only_widget.hide()
        self.text_edit_placeholder_widget.hide()
        self.text_edit_wrap_mode_widget.hide()
        self.text_edit_alignment_widget.hide()
        self.combo_editable_widget.hide()
        self.list_selection_mode_widget.hide()
        self.list_items_widget.hide()
        self.list_edit_triggers_widget.hide()
        self.list_alternating_row_colors_widget.hide()
        self.list_sorting_enabled_widget.hide()
        self.list_view_mode_widget.hide()
        self.list_drag_drop_mode_widget.hide()
        self.list_resize_mode_widget.hide()
        self.list_movement_widget.hide()
        self.table_data_widget.hide()
        self.table_show_grid_widget.hide()
        self.table_selection_mode_widget.hide()
        self.table_edit_triggers_widget.hide()
        self.table_alternating_row_colors_widget.hide()
        self.table_sorting_enabled_widget.hide()
        self.table_corner_button_enabled_widget.hide()
        self.tab_position_widget.hide()
        self.tab_shape_widget.hide()
        self.tab_closable_widget.hide()
        self.tab_movable_widget.hide()
        self.tab_count_widget.hide()
        self.tab_titles_widget.hide()
        self.slider_prop_widget.hide()
        
        # 根据控件类型显示相应属性
        if control_type == "QCheckBox" or control_type == "QRadioButton":
            self.checked_widget.show()
        elif control_type == "QLineEdit":
            self.read_only_widget.show()
            self.password_mode_widget.show()
            self.max_length_widget.show()
            self.placeholder_widget.show()
        elif control_type == "QLabel":
            self.align_widget.show()
            self.wrap_text_widget.show()
        elif control_type == "QTextEdit":
            self.text_edit_read_only_widget.show()
            self.text_edit_placeholder_widget.show()
            self.text_edit_wrap_mode_widget.show()
            self.text_edit_alignment_widget.show()
        elif control_type == "QComboBox":
            self.combo_editable_widget.show()
        elif control_type == "QListWidget":
            self.list_selection_mode_widget.show()
            self.list_items_widget.show()
            self.list_edit_triggers_widget.show()
            self.list_alternating_row_colors_widget.show()
            self.list_sorting_enabled_widget.show()
            self.list_view_mode_widget.show()
            self.list_drag_drop_mode_widget.show()
            self.list_resize_mode_widget.show()
            self.list_movement_widget.show()
        elif control_type == "QTableWidget":
            self.table_data_widget.show()
            self.table_show_grid_widget.show()
            self.table_selection_mode_widget.show()
            self.table_edit_triggers_widget.show()
            self.table_alternating_row_colors_widget.show()
            self.table_sorting_enabled_widget.show()
            self.table_corner_button_enabled_widget.show()
        elif control_type == "QTabWidget":
            self.tab_position_widget.show()
            self.tab_shape_widget.show()
            self.tab_closable_widget.show()
            self.tab_movable_widget.show()
            self.tab_count_widget.show()
            self.tab_titles_widget.show()
        elif control_type == "QSlider":
            self.slider_prop_widget.show()


    def set_main_window(self, main_window_props):
        """设置当前编辑的主窗口"""
        # 保持属性面板显示状态，除非明确传入None且没有当前主窗口
        if not main_window_props and not self.current_main_window:
            self.control_property_content.hide()
            self.main_window_property_content.hide()
            return
            
        # 如果传入None但有当前主窗口，保持当前主窗口不变
        if not main_window_props and self.current_main_window:
            main_window_props = self.current_main_window
        
        self.current_main_window = main_window_props
        self.current_control = None
        
        # 确保主窗口属性面板显示
        self.control_property_content.hide()
        self.main_window_property_content.show()

        # 填充基础属性
        self.mw_name_edit.setText(main_window_props.name)
        self.mw_title_edit.setText(main_window_props.title)
        self.mw_x_spin.setValue(main_window_props.x)
        self.mw_y_spin.setValue(main_window_props.y)
        self.mw_w_spin.setValue(main_window_props.width)
        self.mw_h_spin.setValue(main_window_props.height)

        # 填充样式属性
        if getattr(main_window_props, 'use_style', True):
            self.mw_use_style_group.button(1).setChecked(True)
        else:
            self.mw_use_style_group.button(0).setChecked(True)
        self.update_mw_style_visibility()
        
        self.mw_bg_color_label.setText(main_window_props.bg_color.name())
        self.mw_title_color_label.setText(main_window_props.title_color.name())
        self.mw_title_text_color_label.setText(main_window_props.title_text_color.name())
        self.mw_title_height_spin.setValue(main_window_props.title_height)
        self.update_button_color(self.mw_bg_color_btn, main_window_props.bg_color)
        self.update_button_color(self.mw_title_color_btn, main_window_props.title_color)
        self.update_button_color(self.mw_title_text_color_btn, main_window_props.title_text_color)

        # 填充全局预设样式属性
        design_canvas = main_window_props.canvas
        if design_canvas:
            self.mw_use_global_style_checkbox.setChecked(design_canvas.global_use_style)
            self.mw_global_preset_style_combo.setCurrentText(design_canvas.global_preset_style)
            self.update_mw_global_style_visibility()

    # -------------------------- 控件属性变更回调 --------------------------
    def on_name_changed(self, text):
        if self.current_control and text:
            self.current_control.name = text
            if self.control_hierarchy_panel:
                self.control_hierarchy_panel.update_control_item(self.current_control)

    def on_text_changed(self, text):
        if self.current_control:
            self.current_control.text = text
            self.current_control.update_widget()

    def on_visible_changed(self, state):
        if self.current_control:
            self.current_control.visible = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_locked_changed(self, state):
        if self.current_control:
            self.current_control.locked = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_show_bg_color_changed(self, state):
        if self.current_control:
            self.current_control.show_bg_color = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_h_scrollbar_changed(self, state):
        if self.current_control:
            self.current_control.h_scrollbar = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_v_scrollbar_changed(self, state):
        if self.current_control:
            self.current_control.v_scrollbar = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_x_changed(self, value):
        if self.current_control:
            if self.current_control.parent and self.current_control.parent.type != "MainWindow":
                parent_bounds = get_control_parent_bounds(self.current_control, self.current_control.parent_canvas.main_window_props)
                parent_abs_rect = get_control_absolute_rect(self.current_control.parent, self.current_control.parent_canvas.main_window_props)
                max_x = parent_bounds.right() - parent_abs_rect.x() - self.current_control.rect.width()
                value = max(0, min(value, max_x))
            else:
                content_width = self.current_control.parent_canvas.main_window_props.width
                value = max(0, min(value, content_width - self.current_control.rect.width()))
            self.current_control.rect.setX(value)
            self.current_control.update_widget()

    def on_y_changed(self, value):
        if self.current_control:
            if self.current_control.parent and self.current_control.parent.type != "MainWindow":
                parent_bounds = get_control_parent_bounds(self.current_control, self.current_control.parent_canvas.main_window_props)
                parent_abs_rect = get_control_absolute_rect(self.current_control.parent, self.current_control.parent_canvas.main_window_props)
                max_y = parent_bounds.bottom() - parent_abs_rect.y() - self.current_control.rect.height()
                value = max(0, min(value, max_y))
            else:
                content_height = self.current_control.parent_canvas.main_window_props.height  # height 本身就是内容区域高度，无需减去标题栏高度
                value = max(0, min(value, content_height - self.current_control.rect.height()))
            self.current_control.rect.setY(value)
            self.current_control.update_widget()

    def on_w_changed(self, value):
        if self.current_control:
            if self.current_control.parent and self.current_control.parent.type != "MainWindow":
                parent_bounds = get_control_parent_bounds(self.current_control, self.current_control.parent_canvas.main_window_props)
                parent_abs_rect = get_control_absolute_rect(self.current_control.parent, self.current_control.parent_canvas.main_window_props)
                max_w = parent_bounds.right() - parent_abs_rect.x() - self.current_control.rect.x()
                value = max(10, min(value, max_w))
            else:
                content_width = self.current_control.parent_canvas.main_window_props.width
                value = max(10, min(value, content_width - self.current_control.rect.x()))
            self.current_control.rect.setWidth(value)
            self.current_control.update_widget()

    def on_h_changed(self, value):
        if self.current_control:
            if self.current_control.parent and self.current_control.parent.type != "MainWindow":
                parent_bounds = get_control_parent_bounds(self.current_control, self.current_control.parent_canvas.main_window_props)
                parent_abs_rect = get_control_absolute_rect(self.current_control.parent, self.current_control.parent_canvas.main_window_props)
                max_h = parent_bounds.bottom() - parent_abs_rect.y() - self.current_control.rect.y()
                value = max(10, min(value, max_h))
            else:
                content_height = self.current_control.parent_canvas.main_window_props.height  # height 本身就是内容区域高度，无需减去标题栏高度
                value = max(10, min(value, content_height - self.current_control.rect.y()))
            self.current_control.rect.setHeight(value)
            self.current_control.update_widget()

    def on_use_style_changed(self, use_style):
        if self.current_control:
            self.current_control.use_style = use_style
            self.update_control_style_visibility()
            self.current_control.update_widget()

    def on_preset_style_changed(self, index):
        if self.current_control:
            preset_name = self.preset_style_combo.currentText()
            self.current_control.preset_style = preset_name
            
            # 应用预设主题值（根据控件类型）
            theme_data = UIControl.PRESET_THEMES.get(preset_name, {})
            if theme_data:
                # 根据控件类型获取对应的样式数据
                control_type = self.current_control.type
                style_data = theme_data.get(control_type, {})
                if style_data:
                    # 1. 颜色和字体
                    if "bg_color" in style_data:
                        self.current_control.bg_color = QColor(style_data["bg_color"])
                    if "fg_color" in style_data:
                        self.current_control.fg_color = QColor(style_data["fg_color"])
                    if "font_size" in style_data:
                        self.current_control.font.setPointSize(style_data["font_size"])
                    if "bold" in style_data:
                        self.current_control.font.setBold(style_data["bold"])
                    
                    # 2. 边框和视觉风格
                    if "visual_style" in style_data:
                        self.current_control.visual_style = style_data["visual_style"]
                    if "border_radius" in style_data:
                        self.current_control.border_radius = style_data["border_radius"]
                    if "border_width" in style_data:
                        self.current_control.border_width = style_data["border_width"]
                    if "border_color" in style_data:
                        self.current_control.border_color = QColor(style_data["border_color"])

                    # 更新UI显示
                    # 颜色按钮和标签
                    self.bg_color_label.setText(self.current_control.bg_color.name())
                    self.update_button_color(self.bg_color_btn, self.current_control.bg_color)
                    self.fg_color_label.setText(self.current_control.fg_color.name())
                    self.update_button_color(self.fg_color_btn, self.current_control.fg_color)
                    
                    # 字体控件
                    self.size_spin.blockSignals(True)
                    self.size_spin.setValue(self.current_control.font.pointSize())
                    self.size_spin.blockSignals(False)
                    self.bold_checkbox.blockSignals(True)
                    self.bold_checkbox.setChecked(self.current_control.font.bold())
                    self.bold_checkbox.blockSignals(False)
                    
                    # 视觉风格控件
                    self.visual_style_combo.blockSignals(True)
                    self.visual_style_combo.setCurrentText(self.current_control.visual_style)
                    self.visual_style_combo.blockSignals(False)
                    
                    # 边框控件
                    self.border_radius_spin.blockSignals(True)
                self.border_radius_spin.setValue(self.current_control.border_radius)
                self.border_radius_spin.blockSignals(False)
                
                self.border_width_spin.blockSignals(True)
                self.border_width_spin.setValue(self.current_control.border_width)
                self.border_width_spin.blockSignals(False)
                
                self.update_button_color(self.border_color_btn, self.current_control.border_color)
                
                self.current_control.update_widget()

    def on_visual_style_changed(self, index):
        if self.current_control:
            style_name = self.visual_style_combo.currentText()
            self.current_control.visual_style = style_name
            self.current_control.custom_properties.add("visual_style")  # 标记为自定义属性
            
            # 切换视觉风格时，自动变更为"自定义"预设，避免逻辑混淆
            self.current_control.preset_style = "自定义"
            self.preset_style_combo.blockSignals(True)
            self.preset_style_combo.setCurrentText("自定义")
            self.preset_style_combo.blockSignals(False)
            
            # 根据风格设置默认边框属性
            if style_name == "圆角":
                self.current_control.border_radius = 15
                self.current_control.border_width = 1
            elif style_name == "描边":
                self.current_control.border_radius = 4
                self.current_control.border_width = 2
            elif style_name == "扁平":
                self.current_control.border_radius = 0
                if self.current_control.type == "QLineEdit":
                     self.current_control.border_width = 1 # 扁平输入框通常有底边框
                else:
                     self.current_control.border_width = 0
            elif style_name == "渐变":
                self.current_control.border_radius = 4
                self.current_control.border_width = 1
            else: # 默认
                self.current_control.border_radius = 4
                self.current_control.border_width = 1
            
            # 更新UI控件值
            self.border_radius_spin.blockSignals(True)
            self.border_radius_spin.setValue(self.current_control.border_radius)
            self.border_radius_spin.blockSignals(False)
            
            self.border_width_spin.blockSignals(True)
            self.border_width_spin.setValue(self.current_control.border_width)
            self.border_width_spin.blockSignals(False)
            
            self.current_control.update_widget()

    def on_border_radius_changed(self, value):
        if self.current_control:
            self.current_control.border_radius = value
            self.current_control.custom_properties.add("border_radius")  # 标记为自定义属性
            self.current_control.update_widget()

    def on_border_width_changed(self, value):
        if self.current_control:
            self.current_control.border_width = value
            self.current_control.custom_properties.add("border_width")  # 标记为自定义属性
            self.current_control.update_widget()

    def on_border_color_click(self):
        if not self.current_control:
            return
        color_dialog = QColorDialog(self.current_control.border_color, self)
        color_dialog.setWindowTitle("选择边框颜色")
        color_dialog.setStyleSheet("background-color: white; color: black;")
        color = color_dialog.getColor()
        if color.isValid():
            self.current_control.border_color = color
            self.current_control.custom_properties.add("border_color")  # 标记为自定义属性
            self.update_button_color(self.border_color_btn, color)
            self.current_control.update_widget()

    def on_bg_color_click(self):
        if not self.current_control:
            return
        color_dialog = QColorDialog(self.current_control.bg_color, self)
        color_dialog.setWindowTitle("选择背景色")
        color_dialog.setStyleSheet("background-color: white; color: black;")
        color = color_dialog.getColor()
        if color.isValid():
            self.current_control.bg_color = color
            self.current_control.custom_properties.add("bg_color")  # 标记为自定义属性
            self.bg_color_label.setText(color.name())
            self.update_button_color(self.bg_color_btn, color)
            self.current_control.update_widget()

    def on_fg_color_click(self):
        if not self.current_control:
            return
        color_dialog = QColorDialog(self.current_control.fg_color, self)
        color_dialog.setWindowTitle("选择文字色")
        color_dialog.setStyleSheet("background-color: white; color: black;")
        color = color_dialog.getColor()
        if color.isValid():
            self.current_control.fg_color = color
            self.current_control.custom_properties.add("fg_color")  # 标记为自定义属性
            self.fg_color_label.setText(color.name())
            self.update_button_color(self.fg_color_btn, color)
            self.current_control.update_widget()

    def on_event_edit_click(self):
        """打开事件编辑对话框"""
        if not self.current_control:
            return
        
        print(f"[调试] 打开事件编辑对话框 - 当前控件: {self.current_control.name}, 事件数量: {len(self.current_control.events)}")
        for idx, event_data in enumerate(self.current_control.events):
            print(f"[调试] 事件 {idx}: {event_data}")
        
        bg_color = self.current_main_window.bg_color if self.current_main_window else QColor(240, 240, 240)
        dialog = EventEditorDialog(self.current_control.events, self.current_control.type, self, bg_color)
        if dialog.exec_() == QDialog.Accepted:
            new_events = dialog.get_data()
            print(f"[调试] 对话框返回的事件数据: {new_events}")
            self.current_control.events = new_events
            print(f"[调试] 控件事件已更新: {self.current_control.events}")
            self.update_event_list()

    def update_event_list(self):
        """更新事件列表显示"""
        if not self.current_control:
            self.event_table.setRowCount(0)
            return
        
        self.event_table.blockSignals(True)
        self.event_table.setRowCount(0)
        
        for idx, event_data in enumerate(self.current_control.events):
            event_name = event_data[0] if len(event_data) > 0 else ""
            callback = event_data[1] if len(event_data) > 1 else ""
            # 只显示已绑定回调函数的事件
            if callback:
                row = self.event_table.rowCount()
                self.event_table.insertRow(row)
                self.event_table.setItem(row, 0, QTableWidgetItem(event_name))
                self.event_table.setItem(row, 1, QTableWidgetItem(callback))
                
                # 添加删除按钮
                delete_btn = QPushButton("×")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ff4444;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        font-size: 16px;
                        font-weight: bold;
                        min-width: 30px;
                        max-width: 30px;
                    }
                    QPushButton:hover {
                        background-color: #cc0000;
                    }
                    QPushButton:pressed {
                        background-color: #990000;
                    }
                """)
                
                # 删除按钮点击事件
                def on_delete_event(event_idx, btn=delete_btn):
                    from PyQt5.QtWidgets import QMessageBox
                    reply = QMessageBox.question(self, "确认删除", 
                        "确定要删除这个事件绑定吗？",
                        QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.current_control.events.pop(event_idx)
                        self.update_event_list()
                
                delete_btn.clicked.connect(lambda checked, i=idx, b=delete_btn: on_delete_event(i, b))
                self.event_table.setCellWidget(row, 2, delete_btn)
        
        self.event_table.blockSignals(False)

    # -------------------------- 控件特有属性变更回调 --------------------------
    def on_checked_changed(self, state):
        if self.current_control:
            self.current_control.checked = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_read_only_changed(self, state):
        if self.current_control:
            self.current_control.read_only = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_password_mode_changed(self, state):
        if self.current_control:
            self.current_control.password_mode = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_max_length_changed(self, value):
        if self.current_control:
            self.current_control.max_length = value
            self.current_control.update_widget()

    def on_placeholder_changed(self, text):
        if self.current_control:
            self.current_control.placeholder = text
            self.current_control.update_widget()

    def on_align_changed(self, index):
        if self.current_control:
            if index == 0:
                self.current_control.align = Qt.AlignLeft | Qt.AlignVCenter
            elif index == 1:
                self.current_control.align = Qt.AlignCenter
            else:
                self.current_control.align = Qt.AlignRight | Qt.AlignVCenter
            self.current_control.update_widget()

    def on_wrap_text_changed(self, state):
        if self.current_control:
            self.current_control.wrap_text = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_enabled_changed(self, state):
        if self.current_control:
            self.current_control.enabled = (state == Qt.Checked)
            self.current_control.update_widget()

    def on_visible_changed(self, state):
        if self.current_control:
            self.current_control.visible = (state == Qt.Checked)
            self.current_control.update_widget()

    # -------------------------- 主窗口属性变更回调 --------------------------
    def on_mw_name_changed(self, text):
        if self.current_main_window and text:
            self.current_main_window.name = text

    def on_mw_title_changed(self, text):
        if self.current_main_window:
            self.current_main_window.title = text

    def on_mw_x_changed(self, value):
        if self.current_main_window:
            self.current_main_window.x = value

    def on_mw_y_changed(self, value):
        if self.current_main_window:
            self.current_main_window.y = value

    def on_mw_w_changed(self, value):
        if self.current_main_window:
            self.current_main_window.width = value

    def on_mw_h_changed(self, value):
        if self.current_main_window:
            self.current_main_window.height = value

    def on_mw_bg_color_click(self):
        if not self.current_main_window:
            return
        color_dialog = QColorDialog(self.current_main_window.bg_color, self)
        color_dialog.setWindowTitle("选择背景色")
        color_dialog.setStyleSheet("background-color: white; color: black;")
        color = color_dialog.getColor()
        if color.isValid():
            self.current_main_window.bg_color = color
            self.mw_bg_color_label.setText(color.name())
            self.update_button_color(self.mw_bg_color_btn, color)

    def on_mw_title_color_click(self):
        if not self.current_main_window:
            return
        color_dialog = QColorDialog(self.current_main_window.title_color, self)
        color_dialog.setWindowTitle("选择标题栏颜色")
        color_dialog.setStyleSheet("background-color: white; color: black;")
        color = color_dialog.getColor()
        if color.isValid():
            self.current_main_window.title_color = color
            self.mw_title_color_label.setText(color.name())
            self.update_button_color(self.mw_title_color_btn, color)

    def on_mw_title_text_color_click(self):
        if not self.current_main_window:
            return
        color_dialog = QColorDialog(self.current_main_window.title_text_color, self)
        color_dialog.setWindowTitle("选择标题文字颜色")
        color_dialog.setStyleSheet("background-color: white; color: black;")
        color = color_dialog.getColor()
        if color.isValid():
            self.current_main_window.title_text_color = color
            self.mw_title_text_color_label.setText(color.name())
            self.update_button_color(self.mw_title_text_color_btn, color)

    def on_mw_title_height_changed(self, value):
        if self.current_main_window:
            self.current_main_window.title_height = value

    def on_mw_use_style_changed(self, use_style):
        if self.current_main_window:
            self.current_main_window.use_style = use_style
            self.update_mw_style_visibility()

    def on_mw_use_global_style_changed(self, use_global_style):
        """处理是否使用全局预设样式"""
        if self.current_main_window:
            # 获取 design_canvas 实例
            design_canvas = self.current_main_window.canvas
            if design_canvas:
                design_canvas.set_global_preset_style(use_global_style, design_canvas.global_preset_style)
                self.update_mw_global_style_visibility()

    def on_mw_global_preset_style_changed(self, index):
        """处理全局预设样式变化"""
        if self.current_main_window:
            # 获取 design_canvas 实例
            design_canvas = self.current_main_window.canvas
            if design_canvas:
                # 获取当前选中的文本
                preset_style = self.mw_global_preset_style_combo.currentText()
                design_canvas.set_global_preset_style(design_canvas.global_use_style, preset_style)

    def update_mw_global_style_visibility(self):
        """更新全局预设样式属性可见性"""
        use_global_style = self.mw_use_global_style_checkbox.isChecked()
        self.mw_global_preset_style_widget.setEnabled(use_global_style)

    def update_mw_style_visibility(self):
        """更新主窗口样式属性可见性"""
        visible = (self.mw_use_style_group.checkedId() == 1)
        
        # 背景色始终显示（原生也可以设置背景色）
        self.mw_bg_color_widget.setVisible(True)
        self.mw_bg_color_label.setVisible(True)
        
        # 其他样式属性仅在启用样式时显示
        self.mw_title_color_widget.setVisible(visible)
        self.mw_title_color_label.setVisible(visible)
        self.mw_title_text_color_widget.setVisible(visible)
        self.mw_title_text_color_label.setVisible(visible)
        self.mw_title_height_widget.setVisible(visible)

    def update_control_style_visibility(self):
        """更新控件样式属性可见性"""
        if not self.current_control:
            return
            
        use_style = (self.use_style_group.checkedId() == 1)
        
        # 仅在启用样式时显示的属性
        self.preset_style_widget.setVisible(use_style)
        self.visual_style_widget.setVisible(use_style)
        self.border_radius_widget.setVisible(use_style)
        self.border_width_widget.setVisible(use_style)
        self.border_color_widget.setVisible(use_style)
        
        # 始终显示的属性（原生支持）
        # 背景色、文字色、字体相关属性保持显示


    def update_parent_combo(self):
        """更新父容器下拉框"""
        if not self.current_control:
            return
            
        self.parent_combo.blockSignals(True)
        self.parent_combo.clear()
        
        # 添加主窗口作为根容器选项
        self.parent_combo.addItem("主窗口 (Root)", "MainWindow")
        
        # 获取所有可能的容器控件
        # 排除自己、自己的子孙控件
        def get_all_children(ctrl):
            children = []
            for child in ctrl.children:
                children.append(child)
                children.extend(get_all_children(child))
            return children
            
        descendants = get_all_children(self.current_control)
        
        # 容器类型列表
        container_types = ["QGroupBox", "QTabWidget", "QScrollArea", "QFrame"]
        
        canvas = self.current_control.parent_canvas
        current_parent_index = 0
        
        for i, control in enumerate(canvas.controls):
            # 必须是容器类型
            if control.type not in container_types:
                continue
                
            # 不能是自己
            if control == self.current_control:
                continue
                
            # 不能是自己的后代
            if control in descendants:
                continue
                
            self.parent_combo.addItem(f"{control.name} ({control.type})", control.id)
            
            # 检查是否是当前父容器
            if self.current_control.parent == control:
                current_parent_index = self.parent_combo.count() - 1
        
        # 如果当前父容器是主窗口（main_window_control）
        if self.current_control.parent and self.current_control.parent.type == "MainWindow":
             current_parent_index = 0
             
        self.parent_combo.setCurrentIndex(current_parent_index)
        self.parent_combo.blockSignals(False)

    def on_parent_changed(self, index):
        """父容器变更回调"""
        if not self.current_control:
            return
            
        data = self.parent_combo.itemData(index)
        canvas = self.current_control.parent_canvas
        
        new_parent = None
        if data == "MainWindow":
            new_parent = canvas.main_window_control
        else:
            new_parent = canvas.get_control_by_id(data)
            
        if not new_parent:
            return
            
        if self.current_control.parent == new_parent:
            return
            
        # 执行重置父容器逻辑
        # 1. 计算当前全局坐标
        if not self.current_control.widget:
            return
        global_pos = self.current_control.widget.mapToGlobal(QPoint(0, 0))
        
        # 2. 从旧父容器移除
        old_parent = self.current_control.parent
        if old_parent and self.current_control in old_parent.children:
            old_parent.children.remove(self.current_control)
            
        # 3. 设置新父容器
        self.current_control.parent = new_parent
        new_parent.children.append(self.current_control)
        
        # 4. 挂载到新父容器Widget
        self.current_control.attach_to_parent(new_parent)
        
        # 5. 计算新坐标
        # 获取新父容器的Widget（如果是主窗口，则是canvas）
        if new_parent.type == "MainWindow":
            parent_widget = canvas
            # mapFromGlobal 将转换到 canvas 的坐标系
            local_pos = parent_widget.mapFromGlobal(global_pos)
            
            # 减去主窗口的位置和标题栏
            rel_x = local_pos.x() - canvas.main_window_props.x
            rel_y = local_pos.y() - (canvas.main_window_props.y + canvas.main_window_props.title_height)
            
            self.current_control.rect.moveTo(rel_x, rel_y)
            
        else:
            # 容器控件
            parent_widget = new_parent.widget
            if not parent_widget:
                return
                
            local_pos = parent_widget.mapFromGlobal(global_pos)
            self.current_control.rect.moveTo(local_pos)
            
        # 6. 更新显示
        self.current_control.update_widget()
        if hasattr(canvas, 'update_control_list'):
            canvas.update_control_list() # 刷新层级面板
        if hasattr(canvas, 'update_selection_overlay'):
            canvas.update_selection_overlay()
    
    def on_text_edit_read_only_changed(self, state):
        if self.current_control:
            self.current_control.text_edit_read_only = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_text_edit_placeholder_changed(self, text):
        if self.current_control:
            self.current_control.text_edit_placeholder = text
            self.current_control.update_widget()
    
    def on_combo_editable_changed(self, state):
        if self.current_control:
            self.current_control.combo_editable = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_list_selection_mode_changed(self, index):
        if self.current_control:
            self.current_control.list_selection_mode = index
            self.current_control.update_widget()
    
    def on_list_item_add(self):
        """添加新列表项"""
        if self.current_control and self.current_control.type == "QListWidget":
            from PyQt5.QtWidgets import QListWidgetItem
            item = QListWidgetItem(f"新列表项{len(self.current_control.list_items) + 1}")
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.list_items_listwidget.addItem(item)
            self.list_items_listwidget.setCurrentRow(self.list_items_listwidget.count() - 1)
            self.list_items_listwidget.editItem(item)
            self.update_list_items_from_widget()
    
    def on_list_item_delete(self):
        """删除选中的列表项"""
        if self.current_control and self.current_control.type == "QListWidget":
            current_row = self.list_items_listwidget.currentRow()
            if current_row >= 0:
                self.list_items_listwidget.takeItem(current_row)
                self.update_list_items_from_widget()
    
    def on_list_item_move_up(self):
        """上移选中的列表项"""
        if self.current_control and self.current_control.type == "QListWidget":
            current_row = self.list_items_listwidget.currentRow()
            if current_row > 0:
                item = self.list_items_listwidget.takeItem(current_row)
                self.list_items_listwidget.insertItem(current_row - 1, item)
                self.list_items_listwidget.setCurrentRow(current_row - 1)
                self.update_list_items_from_widget()
    
    def on_list_item_move_down(self):
        """下移选中的列表项"""
        if self.current_control and self.current_control.type == "QListWidget":
            current_row = self.list_items_listwidget.currentRow()
            if current_row >= 0 and current_row < self.list_items_listwidget.count() - 1:
                item = self.list_items_listwidget.takeItem(current_row)
                self.list_items_listwidget.insertItem(current_row + 1, item)
                self.list_items_listwidget.setCurrentRow(current_row + 1)
                self.update_list_items_from_widget()
    
    def on_list_item_changed(self, item):
        """列表项内容变更"""
        if self.current_control and self.current_control.type == "QListWidget":
            self.update_list_items_from_widget()
    
    def on_list_item_selected(self, row):
        """列表项选中状态变更"""
        has_selection = row >= 0
        self.list_items_del_btn.setEnabled(has_selection)
        self.list_items_up_btn.setEnabled(has_selection and row > 0)
        self.list_items_down_btn.setEnabled(has_selection and row < self.list_items_listwidget.count() - 1)
    
    def update_list_items_from_widget(self):
        """从列表控件更新列表项数据"""
        if self.current_control and self.current_control.type == "QListWidget" and not self.updating_list_items:
            self.updating_list_items = True
            self.current_control.list_items = [self.list_items_listwidget.item(i).text() for i in range(self.list_items_listwidget.count())]
            self.current_control.update_widget()
            self.updating_list_items = False
    
    def on_list_edit_triggers_changed(self, index):
        if self.current_control and self.current_control.type == "QListWidget":
            self.current_control.list_edit_triggers = index
            self.current_control.update_widget()
    
    def on_list_alternating_row_colors_changed(self, state):
        if self.current_control and self.current_control.type == "QListWidget":
            self.current_control.list_alternating_row_colors = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_list_sorting_enabled_changed(self, state):
        if self.current_control and self.current_control.type == "QListWidget":
            self.current_control.list_sorting_enabled = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_list_view_mode_changed(self, index):
        if self.current_control and self.current_control.type == "QListWidget":
            self.current_control.list_view_mode = index
            self.current_control.update_widget()
    
    def on_list_drag_drop_mode_changed(self, index):
        if self.current_control and self.current_control.type == "QListWidget":
            self.current_control.list_drag_drop_mode = index
            self.current_control.update_widget()
    
    def on_list_resize_mode_changed(self, index):
        if self.current_control and self.current_control.type == "QListWidget":
            self.current_control.list_resize_mode = index
            self.current_control.update_widget()
    
    def on_list_movement_changed(self, index):
        if self.current_control and self.current_control.type == "QListWidget":
            self.current_control.list_movement = index
            self.current_control.update_widget()
    
    def on_text_edit_wrap_mode_changed(self, index):
        if self.current_control:
            self.current_control.text_edit_wrap_mode = index
            self.current_control.update_widget()
    
    def on_text_edit_alignment_changed(self, index):
        if self.current_control:
            self.current_control.text_edit_alignment = index
            self.current_control.update_widget()
    
    def on_table_data_edit_click(self):
        if self.current_control and self.current_control.type == "QTableWidget":
            bg_color = self.current_main_window.bg_color if self.current_main_window else QColor(240, 240, 240)
            dialog = TableEditorDialog(
                self.current_control.table_row_count,
                self.current_control.table_column_count,
                self.current_control.table_data,
                self.current_control.table_headers,
                self.current_control.table_row_headers,
                self.current_control.table_column_widths,
                self.current_control.table_row_heights,
                self,
                bg_color
            )
            if dialog.exec_() == QDialog.Accepted:
                self.current_control.table_row_count = dialog.row_count
                self.current_control.table_column_count = dialog.column_count
                self.current_control.table_data = dialog.get_data()
                self.current_control.table_headers = dialog.get_headers()
                self.current_control.table_row_headers = dialog.get_row_headers()
                self.current_control.table_column_widths = dialog.get_column_widths()
                self.current_control.table_row_heights = dialog.get_row_heights()
                self.current_control.update_widget()
    
    def on_table_show_grid_changed(self, state):
        if self.current_control and self.current_control.type == "QTableWidget":
            self.current_control.table_show_grid = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_table_selection_mode_changed(self, index):
        if self.current_control and self.current_control.type == "QTableWidget":
            self.current_control.table_selection_mode = index
            self.current_control.update_widget()
    
    def on_table_edit_triggers_changed(self, index):
        if self.current_control and self.current_control.type == "QTableWidget":
            self.current_control.table_edit_triggers = index
            self.current_control.update_widget()
    
    def on_table_alternating_row_colors_changed(self, state):
        if self.current_control and self.current_control.type == "QTableWidget":
            self.current_control.table_alternating_row_colors = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_table_sorting_enabled_changed(self, state):
        if self.current_control and self.current_control.type == "QTableWidget":
            self.current_control.table_sorting_enabled = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_table_corner_button_enabled_changed(self, state):
        if self.current_control and self.current_control.type == "QTableWidget":
            self.current_control.table_corner_button_enabled = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_tab_position_changed(self, index):
        if self.current_control and self.current_control.type == "QTabWidget":
            self.current_control.tab_position = index
            self.current_control.update_widget()
    
    def on_tab_shape_changed(self, index):
        if self.current_control and self.current_control.type == "QTabWidget":
            self.current_control.tab_shape = index
            self.current_control.update_widget()
    
    def on_tab_closable_changed(self, state):
        if self.current_control and self.current_control.type == "QTabWidget":
            self.current_control.tab_closable = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_tab_movable_changed(self, state):
        if self.current_control and self.current_control.type == "QTabWidget":
            self.current_control.tab_movable = (state == Qt.Checked)
            self.current_control.update_widget()
    
    def on_tab_count_changed(self, value):
        if self.current_control and self.current_control.type == "QTabWidget":
            self.current_control.tab_count = value
            self.current_control.update_widget()
    
    def on_tab_titles_changed(self):
        if self.current_control and self.current_control.type == "QTabWidget":
            titles = self.tab_titles_edit.toPlainText().strip().split("\n")
            self.current_control.tab_titles = [t.strip() for t in titles if t.strip()]
            if len(self.current_control.tab_titles) < self.current_control.tab_count:
                for i in range(len(self.current_control.tab_titles), self.current_control.tab_count):
                    self.current_control.tab_titles.append(f"选项卡{i+1}")
            self.current_control.update_widget()

    def on_font_changed(self, index):
        if self.current_control:
            font_name = ["微软雅黑", "宋体", "黑体", "楷体", "仿宋"][index]
            self.current_control.font.setFamily(font_name)
            self.current_control.update_widget()

    def on_font_size_changed(self, value):
        if self.current_control:
            self.current_control.font.setPointSize(value)
            self.current_control.custom_properties.add("font_size")  # 标记为自定义属性
            self.current_control.update_widget()

    def on_bold_changed(self, state):
        if self.current_control:
            self.current_control.font.setBold(state == Qt.Checked)
            self.current_control.custom_properties.add("bold")  # 标记为自定义属性
            self.current_control.update_widget()

    def on_italic_changed(self, state):
        if self.current_control:
            self.current_control.font.setItalic(state == Qt.Checked)
            self.current_control.update_widget()

    def on_underline_changed(self, state):
        if self.current_control:
            self.current_control.font.setUnderline(state == Qt.Checked)
            self.current_control.update_widget()

    def on_strikethrough_changed(self, state):
        if self.current_control:
            self.current_control.font.setStrikeOut(state == Qt.Checked)
            self.current_control.update_widget()

    def on_slider_min_changed(self, value):
        if self.current_control and self.current_control.type == "QSlider":
            self.current_control.slider_minimum = value
            self.current_control.update_widget()

    def on_slider_max_changed(self, value):
        if self.current_control and self.current_control.type == "QSlider":
            self.current_control.slider_maximum = value
            self.current_control.update_widget()

    def on_slider_val_changed(self, value):
        if self.current_control and self.current_control.type == "QSlider":
            self.current_control.slider_value = value
            self.current_control.update_widget()

    def on_slider_orient_changed(self, index):
        if self.current_control and self.current_control.type == "QSlider":
            self.current_control.slider_orientation = index + 1  # 1=水平, 2=垂直
            self.current_control.update_widget()
