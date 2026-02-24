from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTableWidget, QTableWidgetItem, QSpinBox, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class TableEditorDialog(QDialog):
    """表格数据编辑对话框"""
    def __init__(self, row_count, column_count, table_data, table_headers, table_row_headers, table_column_widths, table_row_heights, parent=None, bg_color=None):
        super().__init__(parent)
        self.row_count = row_count
        self.column_count = column_count
        self.table_data = [row[:] for row in table_data]
        self.table_headers = table_headers[:]
        self.table_row_headers = table_row_headers[:]
        self.table_column_widths = table_column_widths[:]
        self.table_row_heights = table_row_heights[:]
        self.bg_color = bg_color if bg_color else QColor("#f5f7fa")
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("编辑表格数据")
        self.setMinimumSize(900, 700)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.bg_color.name()};
                color: #2c3e50;
            }}
            QLabel {{
                color: #2c3e50;
            }}
            QLineEdit, QSpinBox {{
                background-color: #ffffff;
                border: 1px solid #d9d9d9;
                padding: 4px;
                border-radius: 4px;
                color: #2c3e50;
            }}
            QTableWidget {{
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                gridline-color: #f0f0f0;
                color: #2c3e50;
            }}
            QHeaderView::section {{
                background-color: #f5f7fa;
                border: 1px solid #e0e0e0;
                padding: 4px;
            }}
            QPushButton {{
                background-color: #5c9aff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #7ab0ff;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # 行列数设置
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("行数："))
        self.row_spin = QSpinBox()
        self.row_spin.setRange(1, 1000)
        self.row_spin.setValue(self.row_count)
        self.row_spin.valueChanged.connect(self.on_row_count_changed)
        size_layout.addWidget(self.row_spin)
        
        size_layout.addWidget(QLabel("列数："))
        self.column_spin = QSpinBox()
        self.column_spin.setRange(1, 1000)
        self.column_spin.setValue(self.column_count)
        self.column_spin.valueChanged.connect(self.on_column_count_changed)
        size_layout.addWidget(self.column_spin)
        
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # 表格
        self.table = QTableWidget()
        self.table.setRowCount(self.row_count)
        self.table.setColumnCount(self.column_count)
        self.table.setHorizontalHeaderLabels(self.table_headers)
        self.table.setVerticalHeaderLabels(self.table_row_headers)
        self.table.cellChanged.connect(self.on_cell_changed)
        layout.addWidget(self.table)
        
        # 列标题和行标题编辑
        headers_layout = QHBoxLayout()
        
        col_headers_layout = QVBoxLayout()
        col_headers_layout.addWidget(QLabel("列标题（逗号分隔）："))
        self.headers_edit = QLineEdit()
        self.headers_edit.setText(",".join(self.table_headers))
        self.headers_edit.editingFinished.connect(self.on_headers_edit_finished)
        col_headers_layout.addWidget(self.headers_edit)
        headers_layout.addLayout(col_headers_layout)
        
        row_headers_layout = QVBoxLayout()
        row_headers_layout.addWidget(QLabel("行标题（逗号分隔）："))
        self.row_headers_edit = QLineEdit()
        self.row_headers_edit.setText(",".join(self.table_row_headers))
        self.row_headers_edit.editingFinished.connect(self.on_row_headers_edit_finished)
        row_headers_layout.addWidget(self.row_headers_edit)
        headers_layout.addLayout(row_headers_layout)
        
        layout.addLayout(headers_layout)
        
        # 列宽和行高编辑
        sizes_edit_layout = QHBoxLayout()
        
        col_widths_layout = QVBoxLayout()
        col_widths_layout.addWidget(QLabel("列宽（逗号分隔）："))
        self.column_widths_edit = QLineEdit()
        self.column_widths_edit.setText(",".join(str(w) for w in self.table_column_widths))
        self.column_widths_edit.editingFinished.connect(self.on_column_widths_edit_finished)
        col_widths_layout.addWidget(self.column_widths_edit)
        sizes_edit_layout.addLayout(col_widths_layout)
        
        row_heights_layout = QVBoxLayout()
        row_heights_layout.addWidget(QLabel("行高（逗号分隔）："))
        self.row_heights_edit = QLineEdit()
        self.row_heights_edit.setText(",".join(str(h) for h in self.table_row_heights))
        self.row_heights_edit.editingFinished.connect(self.on_row_heights_edit_finished)
        row_heights_layout.addWidget(self.row_heights_edit)
        sizes_edit_layout.addLayout(row_heights_layout)
        
        layout.addLayout(sizes_edit_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 行管理按钮
        row_buttons_layout = QVBoxLayout()
        add_row_btn = QPushButton("添加行")
        add_row_btn.clicked.connect(self.on_add_row)
        row_buttons_layout.addWidget(add_row_btn)
        
        delete_row_btn = QPushButton("删除行")
        delete_row_btn.clicked.connect(self.on_delete_row)
        row_buttons_layout.addWidget(delete_row_btn)
        
        insert_row_btn = QPushButton("插入行")
        insert_row_btn.clicked.connect(self.on_insert_row)
        row_buttons_layout.addWidget(insert_row_btn)
        
        move_row_up_btn = QPushButton("上移行")
        move_row_up_btn.clicked.connect(self.on_move_row_up)
        row_buttons_layout.addWidget(move_row_up_btn)
        
        move_row_down_btn = QPushButton("下移行")
        move_row_down_btn.clicked.connect(self.on_move_row_down)
        row_buttons_layout.addWidget(move_row_down_btn)
        
        button_layout.addLayout(row_buttons_layout)
        
        # 列管理按钮
        column_buttons_layout = QVBoxLayout()
        add_column_btn = QPushButton("添加列")
        add_column_btn.clicked.connect(self.on_add_column)
        column_buttons_layout.addWidget(add_column_btn)
        
        delete_column_btn = QPushButton("删除列")
        delete_column_btn.clicked.connect(self.on_delete_column)
        column_buttons_layout.addWidget(delete_column_btn)
        
        insert_column_btn = QPushButton("插入列")
        insert_column_btn.clicked.connect(self.on_insert_column)
        column_buttons_layout.addWidget(insert_column_btn)
        
        move_column_left_btn = QPushButton("左移列")
        move_column_left_btn.clicked.connect(self.on_move_column_left)
        column_buttons_layout.addWidget(move_column_left_btn)
        
        move_column_right_btn = QPushButton("右移列")
        move_column_right_btn.clicked.connect(self.on_move_column_right)
        column_buttons_layout.addWidget(move_column_right_btn)
        
        button_layout.addLayout(column_buttons_layout)
        
        # 确定取消按钮
        ok_cancel_layout = QVBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.setMinimumHeight(40)
        ok_btn.clicked.connect(self.accept)
        ok_cancel_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        ok_cancel_layout.addWidget(cancel_btn)
        
        button_layout.addLayout(ok_cancel_layout)
        
        layout.addLayout(button_layout)

    def load_data(self):
        """加载表格数据"""
        self.table.blockSignals(True)
        for row_idx, row_data in enumerate(self.table_data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.table.setItem(row_idx, col_idx, item)
        self.table.blockSignals(False)

    def get_data(self):
        """获取表格数据"""
        data = []
        for row_idx in range(self.table.rowCount()):
            row_data = []
            for col_idx in range(self.table.columnCount()):
                item = self.table.item(row_idx, col_idx)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            data.append(row_data)
        return data

    def get_headers(self):
        """获取列标题"""
        headers = []
        for col_idx in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col_idx)
            if header_item:
                headers.append(header_item.text())
            else:
                headers.append(f"列{col_idx + 1}")
        return headers

    def on_row_count_changed(self, value):
        """行数改变"""
        self.row_count = value
        self.table.setRowCount(value)
        while len(self.table_data) < value:
            self.table_data.append([""] * self.column_count)
        while len(self.table_data) > value:
            self.table_data.pop()

    def on_column_count_changed(self, value):
        """列数改变"""
        self.column_count = value
        self.table.setColumnCount(value)
        while len(self.table_headers) < value:
            self.table_headers.append(f"列{len(self.table_headers) + 1}")
        while len(self.table_headers) > value:
            self.table_headers.pop()
        self.table.setHorizontalHeaderLabels(self.table_headers)
        for row in self.table_data:
            while len(row) < value:
                row.append("")
            while len(row) > value:
                row.pop()

    def on_cell_changed(self, row, column):
        """单元格改变"""
        if row < len(self.table_data):
            if column < len(self.table_data[row]):
                item = self.table.item(row, column)
                if item:
                    self.table_data[row][column] = item.text()

    def on_headers_edit_finished(self):
        """列标题编辑完成"""
        headers_text = self.headers_edit.text()
        self.table_headers = [h.strip() for h in headers_text.split(",") if h.strip()]
        while len(self.table_headers) < self.column_count:
            self.table_headers.append(f"列{len(self.table_headers) + 1}")
        self.table.setHorizontalHeaderLabels(self.table_headers)

    def on_row_headers_edit_finished(self):
        """行标题编辑完成"""
        headers_text = self.row_headers_edit.text()
        self.table_row_headers = [h.strip() for h in headers_text.split(",") if h.strip()]
        while len(self.table_row_headers) < self.row_count:
            self.table_row_headers.append(f"行{len(self.table_row_headers) + 1}")
        self.table.setVerticalHeaderLabels(self.table_row_headers)

    def on_column_widths_edit_finished(self):
        """列宽编辑完成"""
        widths_text = self.column_widths_edit.text()
        try:
            widths = [int(w.strip()) for w in widths_text.split(",") if w.strip()]
            while len(widths) < self.column_count:
                widths.append(100)
            while len(widths) > self.column_count:
                widths.pop()
            self.table_column_widths = widths
            for col_idx, width in enumerate(widths):
                self.table.setColumnWidth(col_idx, width)
        except ValueError:
            pass

    def on_row_heights_edit_finished(self):
        """行高编辑完成"""
        heights_text = self.row_heights_edit.text()
        try:
            heights = [int(h.strip()) for h in heights_text.split(",") if h.strip()]
            while len(heights) < self.row_count:
                heights.append(30)
            while len(heights) > self.row_count:
                heights.pop()
            self.table_row_heights = heights
            for row_idx, height in enumerate(heights):
                self.table.setRowHeight(row_idx, height)
        except ValueError:
            pass

    def on_add_row(self):
        """添加行"""
        self.row_count += 1
        self.table.setRowCount(self.row_count)
        self.row_spin.setValue(self.row_count)
        self.table_data.append([""] * self.column_count)
        self.table_row_headers.append(f"行{self.row_count}")
        self.table.setVerticalHeaderLabels(self.table_row_headers)
        self.row_headers_edit.setText(",".join(self.table_row_headers))
        self.table_row_heights.append(30)
        self.row_heights_edit.setText(",".join(str(h) for h in self.table_row_heights))

    def on_delete_row(self):
        """删除行"""
        if self.row_count > 1:
            self.row_count -= 1
            self.table.setRowCount(self.row_count)
            self.row_spin.setValue(self.row_count)
            self.table_data.pop()
            self.table_row_headers.pop()
            self.table.setVerticalHeaderLabels(self.table_row_headers)
            self.row_headers_edit.setText(",".join(self.table_row_headers))
            self.table_row_heights.pop()
            self.row_heights_edit.setText(",".join(str(h) for h in self.table_row_heights))

    def on_insert_row(self):
        """插入行"""
        self.row_count += 1
        self.table.setRowCount(self.row_count)
        self.row_spin.setValue(self.row_count)
        self.table.insertRow(0)
        self.table_data.insert(0, [""] * self.column_count)
        self.table_row_headers.insert(0, "新行")
        self.table.setVerticalHeaderLabels(self.table_row_headers)
        self.row_headers_edit.setText(",".join(self.table_row_headers))
        self.table_row_heights.insert(0, 30)
        self.row_heights_edit.setText(",".join(str(h) for h in self.table_row_heights))

    def on_move_row_up(self):
        """上移行"""
        if self.row_count > 1:
            current_row = self.table.currentRow()
            if current_row > 0:
                self.table_data.insert(current_row - 1, self.table_data.pop(current_row))
                self.table_row_headers.insert(current_row - 1, self.table_row_headers.pop(current_row))
                self.table_row_heights.insert(current_row - 1, self.table_row_heights.pop(current_row))
                self.load_data()
                self.table.setVerticalHeaderLabels(self.table_row_headers)
                self.row_headers_edit.setText(",".join(self.table_row_headers))
                self.row_heights_edit.setText(",".join(str(h) for h in self.table_row_heights))
                self.table.selectRow(current_row - 1)

    def on_move_row_down(self):
        """下移行"""
        if self.row_count > 1:
            current_row = self.table.currentRow()
            if current_row < self.row_count - 1:
                self.table_data.insert(current_row + 1, self.table_data.pop(current_row))
                self.table_row_headers.insert(current_row + 1, self.table_row_headers.pop(current_row))
                self.table_row_heights.insert(current_row + 1, self.table_row_heights.pop(current_row))
                self.load_data()
                self.table.setVerticalHeaderLabels(self.table_row_headers)
                self.row_headers_edit.setText(",".join(self.table_row_headers))
                self.row_heights_edit.setText(",".join(str(h) for h in self.table_row_heights))
                self.table.selectRow(current_row + 1)

    def on_add_column(self):
        """添加列"""
        self.column_count += 1
        self.table.setColumnCount(self.column_count)
        self.column_spin.setValue(self.column_count)
        self.table_headers.append(f"列{self.column_count}")
        self.table.setHorizontalHeaderLabels(self.table_headers)
        self.headers_edit.setText(",".join(self.table_headers))
        self.table_column_widths.append(100)
        self.column_widths_edit.setText(",".join(str(w) for w in self.table_column_widths))
        for row in self.table_data:
            row.append("")

    def on_delete_column(self):
        """删除列"""
        if self.column_count > 1:
            self.column_count -= 1
            self.table.setColumnCount(self.column_count)
            self.column_spin.setValue(self.column_count)
            self.table_headers.pop()
            self.table.setHorizontalHeaderLabels(self.table_headers)
            self.headers_edit.setText(",".join(self.table_headers))
            self.table_column_widths.pop()
            self.column_widths_edit.setText(",".join(str(w) for w in self.table_column_widths))
            for row in self.table_data:
                if row:
                    row.pop()

    def on_insert_column(self):
        """插入列"""
        self.column_count += 1
        self.table.setColumnCount(self.column_count)
        self.column_spin.setValue(self.column_count)
        self.table.insertColumn(0)
        self.table_headers.insert(0, "新列")
        self.table.setHorizontalHeaderLabels(self.table_headers)
        self.headers_edit.setText(",".join(self.table_headers))
        self.table_column_widths.insert(0, 100)
        self.column_widths_edit.setText(",".join(str(w) for w in self.table_column_widths))
        for row in self.table_data:
            row.insert(0, "")

    def on_move_column_left(self):
        """左移列"""
        if self.column_count > 1:
            current_column = self.table.currentColumn()
            if current_column > 0:
                self.table_headers.insert(current_column - 1, self.table_headers.pop(current_column))
                self.table.setHorizontalHeaderLabels(self.table_headers)
                for row in self.table_data:
                    if row and len(row) > 1:
                        row.insert(current_column - 1, row.pop(current_column))
                self.load_data()
                self.table.selectColumn(current_column - 1)

    def on_move_column_right(self):
        """右移列"""
        if self.column_count > 1:
            current_column = self.table.currentColumn()
            if current_column < self.column_count - 1:
                self.table_headers.insert(current_column + 1, self.table_headers.pop(current_column))
                self.table.setHorizontalHeaderLabels(self.table_headers)
                for row in self.table_data:
                    if row and len(row) > 1:
                        row.insert(current_column + 1, row.pop(current_column))
                self.load_data()
                self.table.selectColumn(current_column + 1)
