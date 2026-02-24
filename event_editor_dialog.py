from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class EventEditorDialog(QDialog):
    """事件绑定编辑对话框"""
    def __init__(self, events_data, control_type=None, parent=None, bg_color=None):
        super().__init__(parent)
        self.events_data = [event[:] for event in events_data] if events_data else []
        self.control_type = control_type
        self.bg_color = bg_color if bg_color else QColor("#f5f7fa")
        
        # 定义所有事件及其描述
        self.all_events = {
            "clicked": "鼠标点击事件",
            "doubleClicked": "鼠标双击事件",
            "pressed": "鼠标按下事件",
            "released": "鼠标释放事件",
            "entered": "鼠标进入事件",
            "left": "鼠标离开事件",
            "focusIn": "控件获得焦点",
            "focusOut": "控件失去焦点",
            "valueChanged": "控件值改变事件",
            "textChanged": "文本内容改变事件",
            "currentTextChanged": "下拉框文本改变",
            "currentIndexChanged": "下拉框索引改变",
            "itemClicked": "列表项鼠标点击",
            "itemDoubleClicked": "列表项鼠标双击",
            "itemChanged": "列表项内容改变",
            "itemSelectionChanged": "列表项选择改变",
            "cellClicked": "表格单元格鼠标点击",
            "cellDoubleClicked": "表格单元格鼠标双击",
            "cellChanged": "表格单元格内容改变",
            "currentCellChanged": "表格当前单元格改变",
            "returnPressed": "回车键按下事件",
            "selectionChanged": "文本选择改变",
            "cursorPositionChanged": "光标位置改变",
            "copyAvailable": "复制可用状态改变",
            "redoAvailable": "重做可用状态改变",
            "undoAvailable": "撤销可用状态改变",
            "currentRowChanged": "当前行改变",
            "cellEntered": "鼠标进入单元格",
            "cellPressed": "单元格鼠标按下"
        }
        
        # 定义不同控件支持的事件
        self.control_events = {
            "QLabel": ["clicked", "doubleClicked", "pressed", "released", "entered", "left", "focusIn", "focusOut"],
            "QPushButton": ["clicked", "doubleClicked", "pressed", "released", "entered", "left", "focusIn", "focusOut"],
            "QLineEdit": ["textChanged", "returnPressed", "focusIn", "focusOut", "selectionChanged", "cursorPositionChanged"],
            "QTextEdit": ["textChanged", "copyAvailable", "redoAvailable", "undoAvailable", "focusIn", "focusOut", "selectionChanged"],
            "QListWidget": ["itemClicked", "itemDoubleClicked", "itemChanged", "itemSelectionChanged", "currentRowChanged", "focusIn", "focusOut"],
            "QTableWidget": ["cellClicked", "cellDoubleClicked", "cellChanged", "currentCellChanged", "cellEntered", "cellPressed", "focusIn", "focusOut"],
            "QComboBox": ["currentTextChanged", "currentIndexChanged", "focusIn", "focusOut"]
        }
        
        # 根据控件类型获取支持的事件
        if control_type and control_type in self.control_events:
            self.event_names = self.control_events[control_type]
        else:
            # 如果没有指定控件类型或控件类型不在列表中，显示所有事件
            self.event_names = list(self.all_events.keys())
        
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("事件绑定")
        self.setMinimumSize(400, 200)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.bg_color.name()};
                color: #333333;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # 说明标签
        info_label = QLabel("添加新的事件绑定")
        info_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(info_label)
        
        # 事件名称下拉框
        event_name_layout = QHBoxLayout()
        event_name_label = QLabel("事件名称：")
        event_name_label.setFixedWidth(80)
        event_name_label.setStyleSheet("color: #495057; font-weight: 500;")
        
        self.event_combo = QComboBox()
        for event_name in self.event_names:
            description = self.all_events.get(event_name, "")
            display_text = f"{event_name}    {description}"
            self.event_combo.addItem(display_text, event_name)
        self.event_combo.setMinimumHeight(36)
        self.event_combo.setStyleSheet("""
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
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #495057;
            }
        """)
        
        event_name_layout.addWidget(event_name_label)
        event_name_layout.addWidget(self.event_combo)
        layout.addLayout(event_name_layout)
        
        # 回调函数输入框
        callback_layout = QHBoxLayout()
        callback_label = QLabel("回调函数：")
        callback_label.setFixedWidth(80)
        callback_label.setStyleSheet("color: #495057; font-weight: 500;")
        
        self.callback_edit = QLineEdit()
        self.callback_edit.setMinimumHeight(36)
        self.callback_edit.setPlaceholderText("输入回调函数名称")
        self.callback_edit.setStyleSheet("""
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
        
        callback_layout.addWidget(callback_label)
        callback_layout.addWidget(self.callback_edit)
        layout.addLayout(callback_layout)
        
        layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 添加按钮
        add_btn = QPushButton("添加")
        add_btn.setMinimumHeight(40)
        add_btn.setMinimumWidth(100)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c9aff;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7ab0ff;
            }
            QPushButton:pressed {
                background-color: #4a88e0;
            }
        """)
        add_btn.clicked.connect(self.on_add_event)
        button_layout.addWidget(add_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #555555;
                border: 1px solid #d9d9d9;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f5f7fa;
                border-color: #5c9aff;
                color: #5c9aff;
            }
            QPushButton:pressed {
                background-color: #e6f7ff;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)

    def on_add_event(self):
        """添加事件"""
        event_name = self.event_combo.currentData()
        callback = self.callback_edit.text().strip()
        
        print(f"[调试] 添加事件 - 事件名: {event_name}, 回调类型: {type(callback)}, 回调值: '{callback}'")
        
        # 如果没有输入回调函数，生成默认的打印语句
        if not callback:
            event_description = self.all_events.get(event_name, event_name)
            callback = f'print("{event_description}触发")'
            print(f"[调试] 生成默认回调: '{callback}'")
        else:
            # 判断用户输入的是什么类型
            # 如果包含括号，说明是完整的代码或函数调用，直接使用
            if '(' in callback and ')' in callback:
                # 验证回调代码是否为有效的Python代码
                try:
                    compile(callback, '<string>', 'exec')
                except SyntaxError as e:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "代码错误", f"回调函数代码语法错误：\n{str(e)}\n\n请输入有效的Python代码，例如：\nprint('事件触发')\nself.do_something()")
                    return
            else:
                # 如果不包含括号，判断是否是有效的Python标识符（函数名）
                # Python 3 支持中文标识符
                import re
                if re.match(r'^[\u4e00-\u9fa5a-zA-Z_][\u4e00-\u9fa5a-zA-Z0-9_]*$', callback):
                    # 是有效的函数名，转换为函数调用
                    callback = f'{callback}()'
                    print(f"[调试] 自动转换为函数调用: '{callback}'")
                else:
                    # 不是有效的函数名，作为普通文本，生成print语句
                    callback = f'print("{callback}")'
                    print(f"[调试] 转换为print语句: '{callback}'")
        
        # 检查是否已存在相同的事件
        for event_data in self.events_data:
            if event_data[0] == event_name:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "警告", f"事件 '{event_name}' 已经绑定过了！")
                return
        
        # 添加新事件
        self.events_data.append([event_name, callback])
        print(f"[调试] 事件已添加到数据: {[event_name, callback]}")
        self.accept()

    def get_data(self):
        """获取事件数据"""
        return self.events_data
