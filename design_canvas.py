from PyQt5.QtWidgets import QWidget, QMessageBox, QMenu, QAction
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal, QMimeData
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QDrag
from ui_control import UIControl
from main_window_props import MainWindowProperties


def get_control_absolute_rect(control, main_window_props):
    """
    递归计算控件的绝对坐标（相对于画布）
    
    Args:
        control: 要计算的控件
        main_window_props: 主窗口属性
    
    Returns:
        QRect: 控件的绝对坐标矩形
    """
    if not control:
        return QRect()
    
    # 如果是主窗口控件，返回主窗口的整体坐标（不含标题栏）
    if control.type == "MainWindow":
        return QRect(
            main_window_props.x,
            main_window_props.y,
            main_window_props.width,
            main_window_props.height
        )
    
    # 从控件自身的rect开始
    abs_rect = QRect(control.rect)
    
    # 递归加上所有父容器的偏移
    parent = control.parent
    if parent:
        current_control = control
        while parent:
            # 如果父容器是主窗口，停止递归并加上主窗口的偏移和标题栏高度
            if parent.type == "MainWindow":
                abs_rect.translate(
                    main_window_props.x,
                    main_window_props.y + main_window_props.title_height
                )
                break
            
            # 1. 先加上父容器的偏移
            abs_rect.translate(parent.rect.x(), parent.rect.y())
            
            # 2. 对于QTabWidget的子控件，不需要额外添加tab bar高度
            # 因为self.rect已经是相对于QTabWidget整个控件的坐标（包括tab bar）
            
            # 继续向上遍历
            current_control = parent
            parent = parent.parent
    else:
        # 如果控件没有父容器，直接加上主窗口的偏移和标题栏高度
        abs_rect.translate(
            main_window_props.x,
            main_window_props.y + main_window_props.title_height
        )
    
    return abs_rect


def get_control_parent_bounds(control, main_window_props):
    """
    递归计算控件的父容器边界（绝对坐标）
    
    Args:
        control: 要计算的控件
        main_window_props: 主窗口属性
    
    Returns:
        QRect: 父容器的边界矩形（绝对坐标）
    """
    if not control or not control.parent:
        # 没有父容器，返回主窗口内容区域
        return QRect(
            main_window_props.x,
            main_window_props.y + main_window_props.title_height,
            main_window_props.width,
            main_window_props.height
        )
    
    # 如果父容器是主窗口，返回主窗口内容区域
    if control.parent.type == "MainWindow":
        return QRect(
            main_window_props.x,
            main_window_props.y + main_window_props.title_height,
            main_window_props.width,
            main_window_props.height
        )
    
    # 计算父容器的绝对坐标
    parent_abs_rect = get_control_absolute_rect(control.parent, main_window_props)
    
    # 使用 get_content_rect 获取内容区域
    if hasattr(control.parent, 'get_content_rect'):
        content_rect = control.parent.get_content_rect()
        return QRect(
            parent_abs_rect.x() + content_rect.x(),
            parent_abs_rect.y() + content_rect.y(),
            content_rect.width(),
            content_rect.height()
        )
    
    return parent_abs_rect


class SelectionOverlay(QWidget):
    """选中框和控制点覆盖层：确保始终显示在控件上方"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 调试信息
        print(f"SelectionOverlay: 初始化完成, geometry={self.geometry()}, pos={self.pos()}")
    
    def showEvent(self, event):
        """显示事件"""
        print(f"SelectionOverlay: showEvent, geometry={self.geometry()}, pos={self.pos()}, parent={self.parent()}")
        super().showEvent(event)
    
    def paintEvent(self, event):
        """绘制选中框、控制点和预览框"""
        super().paintEvent(event)
        painter = QPainter(self)
        
        parent = self.parent()
        
        # 绘制主窗口选中框
        if parent.main_window_selected_flag and parent.main_window_props:
            # 主窗口不绘制选中框
            pass
        
        # 绘制控件选中框和控制点
        if parent.selected_control and parent.main_window_props:
            # 统一使用 get_control_absolute_rect 计算绝对坐标，避免 mapTo 可能导致的坐标系问题
            abs_rect = get_control_absolute_rect(parent.selected_control, parent.main_window_props)
            
            # 绘制控制点
            self.draw_resize_handles(painter, abs_rect)
        
        # 绘制调整大小预览框
        if parent.resizing and parent.resize_current_rect:
            pen = QPen(QColor(0, 204, 102), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(QColor(0, 204, 102, 30))
            painter.drawRect(parent.resize_current_rect)
            
            # 绘制宽高信息
            width = parent.resize_current_rect.width()
            height = parent.resize_current_rect.height()
            size_text = f"{width} x {height}"
            
            # 设置文本样式
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 10))
            
            # 计算文本位置（在矩形左上方）
            text_rect = painter.fontMetrics().boundingRect(size_text)
            text_x = parent.resize_current_rect.x() - text_rect.width() - 5
            text_y = parent.resize_current_rect.y() - 5
            
            # 绘制文本背景
            bg_rect = QRect(text_x - 2, text_y - text_rect.height() + 2, 
                           text_rect.width() + 4, text_rect.height() + 4)
            painter.setBrush(QColor(255, 255, 255, 200))
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawRect(bg_rect)
            
            # 绘制文本
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(text_x, text_y, size_text)
        
        # 绘制绘制预览框
        if parent.drawing_mode:
            drawing_rect = QRect(parent.drawing_start_pos, parent.drawing_current_pos).normalized()
            pen = QPen(QColor(0, 204, 102), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(QColor(0, 204, 102, 30))
            painter.drawRect(drawing_rect)
    
    def draw_resize_handles(self, painter, rect):
        """绘制控件的控制点（8个角和边的中点）"""
        draw_size = 10
        handle_color = QColor(100, 149, 237)
        
        # 定义8个控制点的位置
        handles = self.parent().get_resize_handles(rect)
        
        # 绘制每个控制点
        for handle_pos in handles.values():
            handle_rect = QRect(handle_pos.x() - draw_size // 2, 
                              handle_pos.y() - draw_size // 2, 
                              draw_size, draw_size)
            painter.setPen(QPen(handle_color, 1))
            painter.setBrush(QColor(255, 255, 255))
            painter.drawRect(handle_rect)
    
    def mousePressEvent(self, event):
        """鼠标按下：根据优先级判断操作（控制点 > 选项卡 > 移动 > 选择）"""
        print(f"SelectionOverlay: mousePressEvent 被调用, button={event.button()}, pos={event.pos()}")
        
        parent = self.parent()
        
        # 如果是绘制模式，直接忽略事件，让父控件处理
        if parent.drawing_mode:
            print(f"SelectionOverlay: 检测到绘制模式，忽略事件")
            event.ignore()
            return
        
        if event.button() == Qt.LeftButton:
            
            # 优先级1: 检查是否点击了选中控件的控制点
            if parent.selected_control and parent.main_window_props:
                abs_rect = get_control_absolute_rect(parent.selected_control, parent.main_window_props)
                handle = parent.get_resize_handle_at(event.pos(), abs_rect)
                if handle:
                    print(f"SelectionOverlay: 检测到控制点={handle}，执行调整大小操作")
                    parent.resizing = True
                    parent.resize_handle = handle
                    parent.resize_start_rect = parent.selected_control.rect
                    parent.resize_start_pos = event.pos()
                    parent.resize_current_rect = None
                    parent.update_selection_overlay()
                    event.accept()  # 接受事件，防止继续传播
                    return
            
            # 优先级2: 检查是否点击在选项卡上（如果选中控件在QTabWidget中）
            if parent.selected_control and parent.selected_control.parent and parent.selected_control.parent.type == "QTabWidget":
                tab_widget = parent.selected_control.parent.widget
                if tab_widget:
                    tab_bar = tab_widget.tabBar()
                    # 转换坐标到选项卡栏
                    # 使用全局坐标转换更加安全，避免 mapTo 在复杂层级中可能出现的问题
                    tab_bar_pos = tab_bar.mapFromGlobal(event.globalPos())
                    clicked_tab = tab_bar.tabAt(tab_bar_pos)
                    if clicked_tab >= 0:
                        print(f"SelectionOverlay: 检测到选项卡={clicked_tab}，执行选项卡切换")
                        # 调用QTabWidget的原始鼠标事件处理
                        original_mouse_press = tab_widget.mousePressEvent
                        # 创建相对于QTabWidget的鼠标事件
                        # 同样使用全局坐标转换
                        tab_widget_pos = tab_widget.mapFromGlobal(event.globalPos())
                        from PyQt5.QtGui import QMouseEvent
                        mouse_event = QMouseEvent(
                            event.type(),
                            tab_widget_pos,
                            event.globalPos(),
                            event.button(),
                            event.buttons(),
                            event.modifiers()
                        )
                        original_mouse_press(mouse_event)
                        event.accept()  # 接受事件，防止继续传播
                        return
            
            # 优先级3: 查找点击位置对应的控件并选中（合并了原有的移动逻辑）
            print(f"SelectionOverlay: 查找点击位置的控件，pos={event.pos()}")
            clicked_control = None
            # 从后往前遍历，确保选中最上层的控件
            for control in reversed(parent.controls):
                # 检查控件是否可见（包括父容器隐藏的情况）
                if control.widget and not control.widget.isVisible():
                    continue
                    
                control_abs_rect = get_control_absolute_rect(control, parent.main_window_props)
                if control_abs_rect.contains(event.pos()):
                    clicked_control = control
                    break
            
            if clicked_control:
                print(f"SelectionOverlay: 找到控件 {clicked_control.type}，执行选择和移动操作")
                # 调用父控件的统一处理方法
                parent.handle_control_click(clicked_control, event.pos(), event.button())
                # 接受事件，防止父控件DesignCanvas再处理一次
                event.accept()
                return
            
            # 检查是否点击了主窗口区域
            window_rect = QRect(parent.main_window_props.x, parent.main_window_props.y, 
                               parent.main_window_props.width, parent.main_window_props.height + parent.main_window_props.title_height)
            if window_rect.contains(event.pos()):
                # 点击主窗口内部空白区域，选择主窗口
                parent.main_window_selected_flag = True
                parent.selected_control = None
                parent.update_control_list()
                parent.main_window_selected.emit(parent.main_window_props)
                parent.control_selected.emit(None)
                parent.update_selection_overlay()
                event.accept()
                return
            else:
                # 点击空白区域，取消所有选中
                parent.main_window_selected_flag = False
                parent.selected_control = None
                parent.update_control_list()
                parent.main_window_selected.emit(None)
                parent.control_selected.emit(None)
                parent.update_selection_overlay()
                event.accept()
                return
        else:
            event.ignore()
    
    def mouseMoveEvent(self, event):
        """鼠标移动：传递给父控件或选中控件"""
        parent = self.parent()
        
        # 如果正在调整大小，传递给父控件处理
        if parent.resizing:
            parent.mouseMoveEvent(event)
            return
        
        # 如果正在绘制模式，传递给父控件处理
        if parent.drawing_mode:
            parent.mouseMoveEvent(event)
            return
            
        # 如果正在移动控件，传递给父控件处理
        if parent.moving_control:
            parent.mouseMoveEvent(event)
            return
        
        # 如果有选中控件，传递给选中控件 (仅当不移动时)
        if parent.selected_control and parent.selected_control.widget:
            local_pos = parent.selected_control.widget.mapFromGlobal(event.globalPos())
            from PyQt5.QtGui import QMouseEvent
            mouse_event = QMouseEvent(
                event.type(),
                local_pos,
                event.globalPos(),
                event.button(),
                event.buttons(),
                event.modifiers()
            )
            parent.selected_control.on_mouse_move(mouse_event)
        else:
            # 没有选中控件，传递给父控件
            parent.mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放：传递给父控件或选中控件"""
        parent = self.parent()
        
        # 如果正在调整大小，传递给父控件处理
        if parent.resizing:
            parent.mouseReleaseEvent(event)
            return
        
        # 如果正在绘制模式，传递给父控件处理
        if parent.drawing_mode:
            parent.mouseReleaseEvent(event)
            return
            
        # 如果正在移动控件，传递给父控件处理
        if parent.moving_control:
            parent.mouseReleaseEvent(event)
            return
        
        # 如果有选中控件，传递给选中控件 (仅当不移动时)
        if parent.selected_control and parent.selected_control.widget:
            local_pos = parent.selected_control.widget.mapFromGlobal(event.globalPos())
            from PyQt5.QtGui import QMouseEvent
            mouse_event = QMouseEvent(
                event.type(),
                local_pos,
                event.globalPos(),
                event.button(),
                event.buttons(),
                event.modifiers()
            )
            parent.selected_control.widget.mouseReleaseEvent(mouse_event)
        else:
            # 没有选中控件，传递给父控件
            parent.mouseReleaseEvent(event)


class DesignCanvas(QWidget):
    """设计画布：承载所有控件，支持拖拽创建、移动控件"""
    control_created = pyqtSignal(UIControl)  # 控件创建信号
    control_selected = pyqtSignal(object)  # 控件选中信号
    control_deleted = pyqtSignal(object)  # 控件删除信号
    main_window_selected = pyqtSignal(object)  # 主窗口选中信号
    drawing_mode_changed = pyqtSignal(bool, str)  # 绘制模式改变信号 (是否绘制模式, 控件类型)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(9999, 9999)
        self.setStyleSheet("background-color: #ffffff; border: 1px solid #cccccc;")
        self.setAcceptDrops(True)
        
        # 全局预设样式
        self.global_use_style = False  # 是否使用全局预设样式
        self.global_preset_style = "现代简约"  # 全局预设主题名称
        
        # 状态管理
        self.controls = []
        self.selected_control = None
        self.drag_start_pos = QPoint(0, 0)
        self.dragging_control_type = None
        
        # 控件拖动状态
        self.moving_control = False
        self.move_start_pos = QPoint(0, 0)
        self.move_start_rect = None
        self.move_start_abs_rect = None  # 拖动开始时的控件绝对坐标
        
        # 绘制模式状态
        self.drawing_mode = False
        self.drawing_control_type = None
        self.drawing_start_pos = QPoint(0, 0)
        self.drawing_current_pos = QPoint(0, 0)
        
        # 控制点拖动状态
        self.resizing = False
        self.resize_handle = None  # 当前拖动的控制点
        self.resize_start_rect = None  # 拖动开始时的控件矩形
        self.resize_start_pos = QPoint(0, 0)  # 拖动开始时的鼠标位置
        self.resize_current_rect = None  # 当前预览的矩形
        
        # 主窗口模拟
        self.main_window_props = MainWindowProperties()
        self.main_window_props.canvas = self
        self.main_window_selected_flag = False
        
        # 创建主窗口控件对象（作为所有顶层控件的父容器）
        self.main_window_control = UIControl("MainWindow", self)
        self.main_window_control.type = "MainWindow"
        
        # 初始化选中框和控制点覆盖层
        self.selection_overlay = SelectionOverlay(self)
        self.selection_overlay.setGeometry(0, 0, 9999, 9999)
        self.selection_overlay.raise_()  # 确保覆盖层始终在最上层
        
        # 启用右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def clear_canvas(self):
        """清空画布"""
        # 移除所有控件的Widget
        for control in self.controls:
            if control.widget:
                control.widget.setParent(None)
                control.widget.deleteLater()
        
        self.controls.clear()
        self.selected_control = None
        self.update()
        self.control_deleted.emit(None) # None 表示全部删除
        self.main_window_control.name = "主窗口"
        self.main_window_control.rect = QRect(
            self.main_window_props.x,
            self.main_window_props.y,
            self.main_window_props.width,
            self.main_window_props.height + self.main_window_props.title_height
        )
        self.main_window_control.parent = None  # 主窗口没有父容器
        self.main_window_control.children = []

    def set_global_preset_style(self, use_style, preset_style):
        """设置全局预设样式
        
        Args:
            use_style: 是否使用全局预设样式
            preset_style: 预设样式名称
        """
        self.global_use_style = use_style
        self.global_preset_style = preset_style
        
        print(f"[全局样式] 启用: {use_style}, 样式: {preset_style}")
        
        # 应用全局预设样式到所有控件
        self.apply_global_preset_style_to_all()

    def apply_global_preset_style_to_all(self):
        """将全局预设主题应用到所有控件（只覆盖未被手动设置的属性）"""
        if not self.global_use_style:
            print(f"[全局样式] 未启用，跳过应用")
            return
        
        theme_data = UIControl.PRESET_THEMES.get(self.global_preset_style, {})
        if not theme_data:
            print(f"[全局样式] 未找到预设主题: {self.global_preset_style}")
            return
        
        print(f"[全局样式] 应用主题 '{self.global_preset_style}' 到 {len(self.controls)} 个控件")
        
        for control in self.controls:
            # 根据控件类型获取对应的样式数据
            control_type = control.type
            preset_data = theme_data.get(control_type, {})
            
            if not preset_data:
                print(f"[全局样式] 控件类型 {control_type} 在主题中未定义样式，跳过")
                continue
            
            # 应用预设样式值（只覆盖未被手动设置的属性）
            if "bg_color" in preset_data and "bg_color" not in control.custom_properties:
                control.bg_color = QColor(preset_data["bg_color"])
            if "fg_color" in preset_data and "fg_color" not in control.custom_properties:
                control.fg_color = QColor(preset_data["fg_color"])
            if "font_size" in preset_data and "font_size" not in control.custom_properties:
                control.font.setPointSize(preset_data["font_size"])
            if "bold" in preset_data and "bold" not in control.custom_properties:
                control.font.setBold(preset_data["bold"])
            if "visual_style" in preset_data and "visual_style" not in control.custom_properties:
                control.visual_style = preset_data["visual_style"]
            if "border_radius" in preset_data and "border_radius" not in control.custom_properties:
                control.border_radius = preset_data["border_radius"]
            if "border_width" in preset_data and "border_width" not in control.custom_properties:
                control.border_width = preset_data["border_width"]
            if "border_color" in preset_data and "border_color" not in control.custom_properties:
                control.border_color = QColor(preset_data["border_color"])
            
            # 更新控件
            control.update_widget()
            print(f"[全局样式] 已应用到控件 {control.name} ({control_type})")

    def get_global_preset_style(self):
        """获取全局预设样式设置
        
        Returns:
            tuple: (use_style, preset_style)
        """
        return (self.global_use_style, self.global_preset_style)
        
        # 确保覆盖层始终在最上层
        if hasattr(self, 'selection_overlay'):
            self.selection_overlay.raise_()

    def paintEvent(self, event):
        """绘制画布：显示网格背景、主窗口"""
        super().paintEvent(event)
        painter = QPainter(self)
        
        # 绘制主窗口模拟区域（包含标题栏和内容区）
        # height 属性现在代表内容区高度，所以总高度需要加上标题栏高度
        window_rect = QRect(self.main_window_props.x, self.main_window_props.y, 
                          self.main_window_props.width, self.main_window_props.height + self.main_window_props.title_height)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        
        # 根据是否启用样式绘制背景
        # 无论是否启用样式，都支持设置背景色
        painter.setBrush(self.main_window_props.bg_color)
        painter.drawRect(window_rect)
        
        # 绘制主窗口内部的圆点网格
        if self.main_window_props.grid_enabled:
            self.draw_window_grid(painter, window_rect)
        
        # 绘制窗口标题栏
        title_rect = QRect(self.main_window_props.x, self.main_window_props.y, 
                          self.main_window_props.width, self.main_window_props.title_height)
        
        if self.main_window_props.use_style:
            # 启用样式：使用自定义标题栏颜色
            painter.setPen(QPen(self.main_window_props.title_color, 1))
            painter.setBrush(self.main_window_props.title_color)
            painter.drawRect(title_rect)
            
            # 绘制窗口标题
            painter.setPen(self.main_window_props.title_text_color)
            painter.setFont(QFont("Microsoft YaHei", 10))
            painter.drawText(title_rect, Qt.AlignCenter, self.main_window_props.title)
        else:
            # 原生样式：使用默认系统风格标题栏（模拟）
            # Windows 10 默认标题栏颜色通常是白色或浅灰
            default_title_bg = QColor(255, 255, 255)
            default_title_text = QColor(0, 0, 0)
            
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.setBrush(default_title_bg)
            painter.drawRect(title_rect)
            
            # 绘制窗口标题
            painter.setPen(default_title_text)
            painter.setFont(QFont("Microsoft YaHei", 9))
            # 靠左显示，模拟原生
            title_text_rect = title_rect.adjusted(10, 0, -10, 0)
            painter.drawText(title_text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.main_window_props.title)

    def draw_window_grid(self, painter, window_rect):
        """绘制主窗口内部的灰色网格"""
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        
        # 计算主窗口内容区域（排除标题栏）
        content_x = window_rect.x() + self.main_window_props.grid_start_x
        content_y = window_rect.y() + self.main_window_props.title_height + self.main_window_props.grid_start_y
        content_width = window_rect.width()
        # 内容区域高度即为 props.height
        content_height = self.main_window_props.height
        
        # 绘制垂直线
        for x in range(content_x, content_x + content_width, 20):
            painter.drawLine(x, content_y, x, content_y + content_height)
        
        # 绘制水平线
        for y in range(content_y, content_y + content_height, 20):
            painter.drawLine(content_x, y, content_x + content_width, y)

    def get_resize_handles(self, rect):
        """获取控件8个控制点的位置"""
        return {
            'top_left': rect.topLeft(),
            'top': QPoint(rect.center().x(), rect.top()),
            'top_right': rect.topRight(),
            'right': QPoint(rect.right(), rect.center().y()),
            'bottom_right': rect.bottomRight(),
            'bottom': QPoint(rect.center().x(), rect.bottom()),
            'bottom_left': rect.bottomLeft(),
            'left': QPoint(rect.left(), rect.center().y())
        }
    
    def get_resize_handle_at(self, pos, rect):
        """检测鼠标位置是否在某个控制点上"""
        handle_size = 16
        handles = self.get_resize_handles(rect)
        
        for handle_name, handle_pos in handles.items():
            handle_rect = QRect(handle_pos.x() - handle_size // 2, 
                              handle_pos.y() - handle_size // 2, 
                              handle_size, handle_size)
            if handle_rect.contains(pos):
                return handle_name
        
        return None
    
    def update_cursor_for_handle(self, handle):
        """根据控制点位置更新鼠标光标"""
        if not handle:
            self.setCursor(Qt.ArrowCursor)
            return
        
        cursor_map = {
            'top_left': Qt.SizeFDiagCursor,
            'top': Qt.SizeVerCursor,
            'top_right': Qt.SizeBDiagCursor,
            'right': Qt.SizeHorCursor,
            'bottom_right': Qt.SizeFDiagCursor,
            'bottom': Qt.SizeVerCursor,
            'bottom_left': Qt.SizeBDiagCursor,
            'left': Qt.SizeHorCursor
        }
        
        self.setCursor(cursor_map.get(handle, Qt.ArrowCursor))

    # -------------------------- 鼠标事件处理 --------------------------
    def update_selection_overlay(self):
        """更新选中框和控制点覆盖层的状态"""
        # 始终提升到最上层，并始终接收鼠标事件
        if hasattr(self, 'selection_overlay'):
            self.selection_overlay.raise_()
            self.selection_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.selection_overlay.update()

    def handle_control_click(self, control, event_pos, button):
        """处理控件点击事件：选中控件并准备拖动"""
        if not control:
            return

        # 选中控件
        self.selected_control = control
        self.main_window_selected_flag = False
        self.update_control_list()
        self.control_selected.emit(control)
        self.main_window_selected.emit(None)
        self.update_selection_overlay()
        
        # 开始拖动控件
        if button == Qt.LeftButton:
            self.moving_control = True
            self.move_start_pos = event_pos
            self.move_start_rect = QRect(control.rect)
            self.move_start_abs_rect = get_control_absolute_rect(control, self.main_window_props)

    def mousePressEvent(self, event):
        """鼠标按下：检测是否点击控制点、主窗口或开始绘制"""
        # 如果事件已经被SelectionOverlay处理过，直接返回
        if event.isAccepted():
            return
            
        if self.drawing_mode and event.button() == Qt.LeftButton:
            # 绘制模式：开始绘制
            print(f"DesignCanvas: mousePressEvent (绘制模式) - 捕获绘制起始位置 {event.pos()}")
            self.drawing_start_pos = event.pos()
            self.drawing_current_pos = event.pos()
            self.update_selection_overlay()
            return
        
        # 检查是否点击了选中控件的控制点
        if self.selected_control and event.button() == Qt.LeftButton:
            # 使用辅助函数计算绝对坐标（支持多层嵌套）
            abs_rect = get_control_absolute_rect(self.selected_control, self.main_window_props)
            
            handle = self.get_resize_handle_at(event.pos(), abs_rect)
            if handle:
                # 开始调整大小
                self.resizing = True
                self.resize_handle = handle
                self.resize_start_rect = self.selected_control.rect
                self.resize_start_pos = event.pos()
                self.resize_current_rect = None
                self.update_selection_overlay()
                return
    
    def mouseMoveEvent(self, event):
        """鼠标移动：更新绘制预览框、调整大小预览、移动控件或更新鼠标光标"""
        if self.drawing_mode and event.buttons() == Qt.LeftButton:
            self.drawing_current_pos = event.pos()
            self.update_selection_overlay()
            return
        
        if self.resizing and event.buttons() == Qt.LeftButton and self.selected_control:
            # 更新调整大小预览
            self.update_resize_preview(event.pos())
            self.update_selection_overlay()
            return
        
        if self.moving_control and event.buttons() == Qt.LeftButton and self.selected_control:
            delta = event.pos() - self.move_start_pos
            
            new_rect = QRect(self.move_start_rect)
            new_rect.translate(delta)
            
            parent = self.selected_control.parent
            
            if parent and parent.type == "MainWindow":
                parent_bounds = get_control_parent_bounds(self.selected_control, self.main_window_props)
                
                min_x = 0
                min_y = 0
                max_x = self.main_window_props.width - new_rect.width()
                max_y = self.main_window_props.height - new_rect.height()
                
                new_rect.moveLeft(max(min_x, min(new_rect.left(), max_x)))
                new_rect.moveTop(max(min_y, min(new_rect.top(), max_y)))
            elif parent:
                parent_bounds = get_control_parent_bounds(self.selected_control, self.main_window_props)
                parent_abs_rect = get_control_absolute_rect(parent, self.main_window_props)
                
                min_x = parent_bounds.x() - parent_abs_rect.x()
                min_y = parent_bounds.y() - parent_abs_rect.y()
                max_x = parent_bounds.right() - parent_abs_rect.x() - new_rect.width()
                max_y = parent_bounds.bottom() - parent_abs_rect.y() - new_rect.height()
                
                new_rect.moveLeft(max(min_x, min(new_rect.left(), max_x)))
                new_rect.moveTop(max(min_y, min(new_rect.top(), max_y)))
            else:
                max_x = self.main_window_props.width - new_rect.width()
                max_y = self.main_window_props.height - new_rect.height()
                
                new_rect.moveLeft(max(0, min(new_rect.left(), max_x)))
                new_rect.moveTop(max(0, min(new_rect.top(), max_y)))
            
            self.selected_control.rect = new_rect
            self.selected_control.update_geometry()
            
            # 触发信号更新属性面板
            self.control_selected.emit(self.selected_control)
            
            self.update_selection_overlay()
            return
        
        # 更新鼠标光标（当鼠标悬停在控制点上时）
        if self.selected_control and not self.resizing:
            # 使用辅助函数计算绝对坐标（支持多层嵌套）
            abs_rect = get_control_absolute_rect(self.selected_control, self.main_window_props)
            
            handle = self.get_resize_handle_at(event.pos(), abs_rect)
            self.update_cursor_for_handle(handle)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放：完成绘制、结束调整大小或结束拖拽"""
        if self.drawing_mode and event.button() == Qt.LeftButton:
            # 绘制模式：完成绘制
            self.finish_drawing()
            return
        
        if self.resizing and event.button() == Qt.LeftButton:
            # 完成调整大小
            if self.selected_control:
                # 检查是否是MainWindow控件或父布局属于MainWindow
                if (self.selected_control.type == "MainWindow" or 
                    (self.selected_control.parent and self.selected_control.parent.type == "MainWindow")):
                    self.finish_resizing_main_window()
                else:
                    self.finish_resizing()
            return
        
        if self.moving_control and event.button() == Qt.LeftButton:
            # 完成移动控件
            self.moving_control = False
            self.move_start_pos = QPoint(0, 0)
            self.move_start_rect = None
            self.control_selected.emit(self.selected_control)
            return
    
    def keyPressEvent(self, event):
        """键盘按键事件：处理删除快捷键"""
        if event.key() == Qt.Key_Delete and not self.drawing_mode:
            self.delete_selected_control()
        super().keyPressEvent(event)
    
    def update_resize_preview(self, pos):
        """更新调整大小预览框"""
        if not self.selected_control or not self.resize_start_rect:
            return
        
        # 计算鼠标偏移量
        delta = pos - self.resize_start_pos
        
        # 获取原始矩形
        original = self.resize_start_rect
        
        # 计算控件在画布上的绝对位置（直接使用 get_control_absolute_rect）
        abs_original = get_control_absolute_rect(self.selected_control, self.main_window_props)
        
        # 根据拖动的控制点计算新的绝对矩形
        abs_new_rect = QRect(abs_original)
        
        # 使用辅助函数获取父容器边界
        parent_bounds = get_control_parent_bounds(self.selected_control, self.main_window_props)
        
        # 边界限制
        min_x = parent_bounds.x()
        min_y = parent_bounds.y()
        max_x = parent_bounds.right()
        max_y = parent_bounds.bottom()
        
        # 根据拖动的控制点计算新的绝对矩形，同时考虑边界限制
        if self.resize_handle == 'top_left':
            new_top = max(min_y, abs_original.top() + delta.y())
            new_left = max(min_x, abs_original.left() + delta.x())
            abs_new_rect.setTopLeft(QPoint(new_left, new_top))
        elif self.resize_handle == 'top':
            new_top = max(min_y, abs_original.top() + delta.y())
            abs_new_rect.setTop(new_top)
        elif self.resize_handle == 'top_right':
            new_top = max(min_y, abs_original.top() + delta.y())
            new_right = min(max_x, abs_original.right() + delta.x())
            abs_new_rect.setTopRight(QPoint(new_right, new_top))
        elif self.resize_handle == 'right':
            new_right = min(max_x, abs_original.right() + delta.x())
            abs_new_rect.setRight(new_right)
        elif self.resize_handle == 'bottom_right':
            new_right = min(max_x, abs_original.right() + delta.x())
            new_bottom = min(max_y, abs_original.bottom() + delta.y())
            abs_new_rect.setBottomRight(QPoint(new_right, new_bottom))
        elif self.resize_handle == 'bottom':
            new_bottom = min(max_y, abs_original.bottom() + delta.y())
            abs_new_rect.setBottom(new_bottom)
        elif self.resize_handle == 'bottom_left':
            new_bottom = min(max_y, abs_original.bottom() + delta.y())
            new_left = max(min_x, abs_original.left() + delta.x())
            abs_new_rect.setBottomLeft(QPoint(new_left, new_bottom))
        elif self.resize_handle == 'left':
            new_left = max(min_x, abs_original.left() + delta.x())
            abs_new_rect.setLeft(new_left)
        
        # 确保最小尺寸
        min_size = 20
        if abs_new_rect.width() < min_size:
            if self.resize_handle in ['top_left', 'left', 'bottom_left']:
                abs_new_rect.setLeft(abs_new_rect.right() - min_size)
            else:
                abs_new_rect.setRight(abs_new_rect.left() + min_size)
        
        if abs_new_rect.height() < min_size:
            if self.resize_handle in ['top_left', 'top', 'top_right']:
                abs_new_rect.setTop(abs_new_rect.bottom() - min_size)
            else:
                abs_new_rect.setBottom(abs_new_rect.top() + min_size)
        
        # 最终边界限制（确保不会超出）
        abs_new_rect.setLeft(max(min_x, abs_new_rect.left()))
        abs_new_rect.setTop(max(min_y, abs_new_rect.top()))
        abs_new_rect.setRight(min(max_x, abs_new_rect.right()))
        abs_new_rect.setBottom(min(max_y, abs_new_rect.bottom()))
        
        # 将绝对坐标转换回相对于父容器的坐标
        if self.selected_control.parent:
            # 控件在父容器内，使用递归函数计算父容器的绝对位置
            parent_abs_rect = get_control_absolute_rect(self.selected_control.parent, self.main_window_props)
            
            # 获取父容器的内容区域偏移
            content_rect = self.selected_control.parent.get_content_rect()
            
            # 计算相对于父容器内容区域的坐标
            new_rect = QRect(
                abs_new_rect.x() - parent_abs_rect.x() - content_rect.x(),
                abs_new_rect.y() - parent_abs_rect.y() - content_rect.y(),
                abs_new_rect.width(),
                abs_new_rect.height()
            )
        else:
            # 控件在主窗口内
            new_rect = QRect(
                abs_new_rect.x() - self.main_window_props.x,
                abs_new_rect.y() - (self.main_window_props.y + self.main_window_props.title_height),
                abs_new_rect.width(),
                abs_new_rect.height()
            )
        
        # 更新预览矩形
        self.resize_current_rect = abs_new_rect
    
    def finish_resizing_main_window(self):
        """处理MainWindow的调整大小，或父布局属于MainWindow的控件的调整大小"""
        if not self.selected_control or not self.resize_current_rect:
            self.resizing = False
            self.resize_handle = None
            self.resize_start_rect = None
            self.resize_start_pos = QPoint(0, 0)
            self.resize_current_rect = None
            self.setCursor(Qt.ArrowCursor)
            self.update_selection_overlay()
            return
        
        if self.selected_control.type == "MainWindow":
            # 处理MainWindow控件的调整大小
            # 更新main_window_props的宽度和高度
            # 总高度减去标题栏高度，得到内容区域高度
            new_width = self.resize_current_rect.width()
            total_height = self.resize_current_rect.height()
            # 确保内容区域高度至少为0
            new_height = max(0, total_height - self.main_window_props.title_height)
            self.main_window_props.width = new_width
            self.main_window_props.height = new_height
            # 保持标题栏高度的默认值30，确保位置约束和绝对坐标计算正确
            self.main_window_props.title_height = 30
            
            # 更新MainWindow控件的矩形
            self.selected_control.rect = QRect(0, 0, new_width, new_height)
            
            # 更新MainWindow的widget尺寸
            if self.selected_control.widget:
                self.selected_control.widget.setGeometry(
                    self.main_window_props.x,
                    self.main_window_props.y,
                    new_width,
                    new_height
                )
        else:
            # 处理父布局属于MainWindow的控件的调整大小
            # 将预览矩形转换回相对于父容器的坐标
            rel_rect = QRect(
                self.resize_current_rect.x() - self.main_window_props.x,
                self.resize_current_rect.y() - (self.main_window_props.y + self.main_window_props.title_height),
                self.resize_current_rect.width(),
                self.resize_current_rect.height()
            )
            
            # 更新控件的矩形
            self.selected_control.rect = rel_rect
            
            # 更新控件的widget尺寸和位置
            if self.selected_control.widget:
                self.selected_control.update_geometry()
        
        # 发送信号通知属性面板更新
        self.control_selected.emit(self.selected_control)
        
        # 重置调整大小状态
        self.resizing = False
        self.resize_handle = None
        self.resize_start_rect = None
        self.resize_start_pos = QPoint(0, 0)
        self.resize_current_rect = None
        
        # 恢复默认光标
        self.setCursor(Qt.ArrowCursor)
        
        # 更新画布
        self.update_selection_overlay()
        self.update()
    
    def finish_resizing(self):
        """完成调整大小，更新控件属性"""
        if not self.selected_control or not self.resize_current_rect:
            self.resizing = False
            self.resize_handle = None
            self.resize_start_rect = None
            self.resize_start_pos = QPoint(0, 0)
            self.resize_current_rect = None
            self.setCursor(Qt.ArrowCursor)
            self.update_selection_overlay()
            return
        
        # 将预览矩形转换回相对坐标
        if self.selected_control.parent:
            # 控件在父容器内，需要转换为相对于父容器的坐标
            parent_abs_rect = get_control_absolute_rect(self.selected_control.parent, self.main_window_props)
            
            # 计算相对于父容器的坐标，不再减去内容区域偏移，保持与update_geometry方法的一致性
            rel_rect = QRect(
                self.resize_current_rect.x() - parent_abs_rect.x(),
                self.resize_current_rect.y() - parent_abs_rect.y(),
                self.resize_current_rect.width(),
                self.resize_current_rect.height()
            )
        else:
            # 控件在主窗口内，直接转换，需要减去标题栏高度
            rel_rect = QRect(
                self.resize_current_rect.x() - self.main_window_props.x,
                self.resize_current_rect.y() - (self.main_window_props.y + self.main_window_props.title_height),
                self.resize_current_rect.width(),
                self.resize_current_rect.height()
            )
        
        # 更新控件的矩形
        self.selected_control.rect = rel_rect
        
        # 更新控件的widget尺寸和位置
        if self.selected_control.widget:
            self.selected_control.update_geometry()
        
        # 发送信号通知属性面板更新
        self.control_selected.emit(self.selected_control)
        
        # 重置调整大小状态
        self.resizing = False
        self.resize_handle = None
        self.resize_start_rect = None
        self.resize_start_pos = QPoint(0, 0)
        self.resize_current_rect = None
        
        # 恢复默认光标
        self.setCursor(Qt.ArrowCursor)
        
        # 更新画布
        self.update_selection_overlay()

    # -------------------------- 拖拽创建控件 --------------------------
    def dragEnterEvent(self, event):
        """拖拽进入画布：接受控件类型数据"""
        if event.mimeData().hasText():
            self.dragging_control_type = event.mimeData().text()
            event.acceptProposedAction()

    def dropEvent(self, event):
        """拖拽释放：创建控件"""
        if not self.dragging_control_type:
            return
        
        # 创建控件
        new_control = UIControl(self.dragging_control_type, self)
        
        # 应用全局预设主题（如果启用）
        if self.global_use_style:
            theme_data = UIControl.PRESET_THEMES.get(self.global_preset_style, {})
            if theme_data:
                # 根据控件类型获取对应的样式数据
                control_type = self.dragging_control_type
                preset_data = theme_data.get(control_type, {})
                if preset_data:
                    if "bg_color" in preset_data:
                        new_control.bg_color = QColor(preset_data["bg_color"])
                    if "fg_color" in preset_data:
                        new_control.fg_color = QColor(preset_data["fg_color"])
                    if "font_size" in preset_data:
                        new_control.font.setPointSize(preset_data["font_size"])
                    if "bold" in preset_data:
                        new_control.font.setBold(preset_data["bold"])
                    if "visual_style" in preset_data:
                        new_control.visual_style = preset_data["visual_style"]
                    if "border_radius" in preset_data:
                        new_control.border_radius = preset_data["border_radius"]
                    if "border_width" in preset_data:
                        new_control.border_width = preset_data["border_width"]
                    if "border_color" in preset_data:
                        new_control.border_color = QColor(preset_data["border_color"])
        
        # 设置控件位置为相对于主窗口的坐标
        drop_pos = event.pos()
        x = drop_pos.x() - new_control.rect.width()//2
        y = drop_pos.y() - new_control.rect.height()//2
        
        # 检测是否在容器控件上
        parent_control = self.find_container_at_position(drop_pos)
        
        if parent_control:
            # 在容器控件上，建立父子关系
            parent_abs_rect = get_control_absolute_rect(parent_control, self.main_window_props)
            
            # 使用 get_content_rect 获取内容区域
            content_rect = parent_control.get_content_rect()
            
            # 转换为相对于父容器的坐标
            rel_x = drop_pos.x() - parent_abs_rect.x() - new_control.rect.width()//2
            rel_y = drop_pos.y() - parent_abs_rect.y() - new_control.rect.height()//2
            
            # 限制在内容区域范围内
            # content_rect.x() 通常为0，y() 对于TabWidget可能为30
            min_x = content_rect.x()
            min_y = content_rect.y()
            max_x = content_rect.width() + content_rect.x() - new_control.rect.width()
            max_y = content_rect.height() + content_rect.y() - new_control.rect.height()
            
            rel_x = max(min_x, min(rel_x, max_x))
            rel_y = max(min_y, min(rel_y, max_y))
            
            new_control.rect.moveTo(rel_x, rel_y)
            new_control.parent = parent_control
            
            # 如果是QTabWidget，记录所在的标签页索引
            if parent_control.type == "QTabWidget" and parent_control.widget:
                tab_widget = parent_control.widget
                if tab_widget.currentWidget():
                    new_control.parent_tab_index = tab_widget.currentIndex()
            
            parent_control.children.append(new_control)
        else:
            # 在主窗口上，设置父容器为主窗口控件
            content_width = self.main_window_props.width
            content_height = self.main_window_props.height
            x = max(0, min(x, content_width - new_control.rect.width()))
            y = max(0, min(y, content_height - new_control.rect.height()))
            new_control.rect.moveTo(x, y)
            new_control.parent = self.main_window_control
            self.main_window_control.children.append(new_control)
        
        # 创建控件预览
        new_control.create_widget()
        
        # 添加到控件列表
        self.controls.append(new_control)
        
        # 选中新控件
        self.selected_control = new_control
        self.main_window_selected_flag = False
        
        # 发送信号
        self.control_created.emit(new_control)
        
        # 更新UI
        self.update_control_list()
        self.control_selected.emit(new_control)
        self.main_window_selected.emit(None)
        
        # 更新选中框和控制点
        if hasattr(self, 'selection_overlay'):
            self.update_selection_overlay()
        
        # 重置拖拽状态
        self.dragging_control_type = None

    def find_container_at_position(self, pos):
        """查找指定位置上的容器控件"""
        # 定义容器控件类型
        container_types = ["QTabWidget", "QTextEdit", "QListWidget", "QTableWidget", "QGroupBox", "QScrollArea", "QFrame"]
        
        # 从后往前遍历（后创建的控件在上层）
        for control in reversed(self.controls):
            if control.type in container_types:
                # 使用辅助函数计算容器控件的绝对坐标（支持多层嵌套）
                abs_rect = get_control_absolute_rect(control, self.main_window_props)
                if abs_rect.contains(pos):
                    # 如果是QTabWidget，需要检查是否在标签页内容区域
                    if control.type == "QTabWidget" and control.widget:
                        tab_widget = control.widget
                        current_tab = tab_widget.currentWidget()
                        if current_tab:
                            # 获取标签页内容区域（排除标签栏）
                            tab_bar_height = tab_widget.tabBar().height()
                            content_rect = QRect(
                                abs_rect.x(),
                                abs_rect.y() + tab_bar_height,
                                abs_rect.width(),
                                abs_rect.height() - tab_bar_height
                            )
                            if content_rect.contains(pos):
                                return control
                    else:
                        return control
        
        return None

    # -------------------------- 控件列表管理 --------------------------
    def update_control_list(self):
        """更新控件列表选中状态"""
        for control in self.controls:
            if control.list_item:
                control.list_item.setSelected(control == self.selected_control)

    def get_control_by_id(self, control_id):
        """根据ID获取控件"""
        for control in self.controls:
            if control.id == control_id:
                return control
        return None

    def delete_selected_control(self):
        """删除选中的控件"""
        if not self.selected_control:
            QMessageBox.warning(self, "警告", "请先选中要删除的控件！")
            return
        # 保存要删除的控件引用
        control_to_delete = self.selected_control
        
        # 递归删除所有子控件
        self.delete_control_recursive(control_to_delete)
        
        # 清空选中状态
        self.selected_control = None
        # 更新UI
        self.control_selected.emit(None)
        self.update_selection_overlay()

    def delete_control_recursive(self, control):
        """递归删除控件及其所有子控件"""
        # 先删除所有子控件
        for child in control.children[:]:  # 使用切片复制，避免在遍历时修改列表
            self.delete_control_recursive(child)
        
        # 从父控件的子列表中移除
        if control.parent and control in control.parent.children:
            control.parent.children.remove(control)
        
        # 从画布移除控件
        control.widget.deleteLater()
        # 从列表移除
        if control in self.controls:
            self.controls.remove(control)
        # 发送删除信号（通知控件列表移除对应的项）
        self.control_deleted.emit(control)

    def delete_control_by_id(self, control_id):
        """根据控件ID删除控件"""
        control_to_delete = None
        for control in self.controls:
            if control.id == control_id:
                control_to_delete = control
                break
        
        if control_to_delete:
            # 递归删除控件及其所有子控件
            self.delete_control_recursive(control_to_delete)
            
            if self.selected_control == control_to_delete:
                self.selected_control = None
            self.control_selected.emit(None)
            self.update_selection_overlay()

    def copy_control_by_id(self, control_id):
        """根据控件ID复制控件，位置在原控件下方"""
        source_control = None
        for control in self.controls:
            if control.id == control_id:
                source_control = control
                break
        
        if source_control:
            new_control = UIControl(source_control.type, self)
            new_control.rect = QRect(
                source_control.rect.x(),
                source_control.rect.y() + source_control.rect.height() + 10,
                source_control.rect.width(),
                source_control.rect.height()
            )
            
            # 继承父容器
            new_control.parent = source_control.parent
            if new_control.parent:
                new_control.parent.children.append(new_control)
            
            # 应用全局预设主题（如果启用）
            if self.global_use_style:
                theme_data = UIControl.PRESET_THEMES.get(self.global_preset_style, {})
                if theme_data:
                    # 根据控件类型获取对应的样式数据
                    control_type = source_control.type
                    preset_data = theme_data.get(control_type, {})
                    if preset_data:
                        if "bg_color" in preset_data:
                            new_control.bg_color = QColor(preset_data["bg_color"])
                        if "fg_color" in preset_data:
                            new_control.fg_color = QColor(preset_data["fg_color"])
                        if "font_size" in preset_data:
                            new_control.font.setPointSize(preset_data["font_size"])
                        if "bold" in preset_data:
                            new_control.font.setBold(preset_data["bold"])
                        if "visual_style" in preset_data:
                            new_control.visual_style = preset_data["visual_style"]
                        if "border_radius" in preset_data:
                            new_control.border_radius = preset_data["border_radius"]
                        if "border_width" in preset_data:
                            new_control.border_width = preset_data["border_width"]
                        if "border_color" in preset_data:
                            new_control.border_color = QColor(preset_data["border_color"])
            
            new_control.create_widget()
            self.controls.append(new_control)
            self.control_created.emit(new_control)
            self.selected_control = new_control
            self.main_window_selected_flag = False
            self.control_selected.emit(new_control)
            self.main_window_selected.emit(None)
            self.update_selection_overlay()

    def show_context_menu(self, position):
        """显示右键菜单"""
        if not self.selected_control:
            return

        menu = QMenu(self)

        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_selected_control)
        menu.addAction(delete_action)

        copy_action = QAction("复制", self)
        copy_action.triggered.connect(lambda: self.copy_control_by_id(self.selected_control.id))
        menu.addAction(copy_action)

        # 添加宽高修改菜单
        if self.selected_control.parent:
            size_menu = menu.addMenu("宽高修改")

            inherit_both_action = QAction("继承宽高", self)
            inherit_both_action.triggered.connect(self.inherit_parent_size)
            size_menu.addAction(inherit_both_action)

            inherit_height_action = QAction("继承高度", self)
            inherit_height_action.triggered.connect(self.inherit_parent_height)
            size_menu.addAction(inherit_height_action)

            inherit_width_action = QAction("继承宽度", self)
            inherit_width_action.triggered.connect(self.inherit_parent_width)
            size_menu.addAction(inherit_width_action)

        menu.exec_(self.mapToGlobal(position))
    
    def inherit_parent_size(self):
        """继承父控件的宽高"""
        if not self.selected_control or not self.selected_control.parent:
            return
        
        parent_control = self.selected_control.parent
        
        # 使用 get_content_rect 获取父控件的内容区域
        if hasattr(parent_control, 'get_content_rect'):
            content_rect = parent_control.get_content_rect()
            parent_width = content_rect.width()
            parent_height = content_rect.height()
        else:
            parent_width = parent_control.rect.width()
            parent_height = parent_control.rect.height()
        
        # 更新子控件的宽高
        self.selected_control.rect.setWidth(parent_width)
        self.selected_control.rect.setHeight(parent_height)
        
        # 更新widget
        if self.selected_control.widget:
            self.selected_control.widget.setGeometry(self.selected_control.rect)
        
        # 发送信号通知属性面板更新
        self.control_selected.emit(self.selected_control)
        
        # 更新选中框
        self.update_selection_overlay()
    
    def inherit_parent_height(self):
        """继承父控件的高度"""
        if not self.selected_control or not self.selected_control.parent:
            return
        
        parent_control = self.selected_control.parent
        
        # 使用 get_content_rect 获取父控件的内容区域
        if hasattr(parent_control, 'get_content_rect'):
            content_rect = parent_control.get_content_rect()
            parent_height = content_rect.height()
        else:
            parent_height = parent_control.rect.height()
        
        # 更新子控件的高度
        self.selected_control.rect.setHeight(parent_height)
        
        # 更新widget
        if self.selected_control.widget:
            self.selected_control.widget.setGeometry(self.selected_control.rect)
        
        # 发送信号通知属性面板更新
        self.control_selected.emit(self.selected_control)
        
        # 更新选中框
        self.update_selection_overlay()
    
    def inherit_parent_width(self):
        """继承父控件的宽度"""
        if not self.selected_control or not self.selected_control.parent:
            return
        
        parent_control = self.selected_control.parent
        
        # 使用 get_content_rect 获取父控件的内容区域
        if hasattr(parent_control, 'get_content_rect'):
            content_rect = parent_control.get_content_rect()
            parent_width = content_rect.width()
        else:
            parent_width = parent_control.rect.width()
        
        # 更新子控件的宽度
        self.selected_control.rect.setWidth(parent_width)
        
        # 更新widget
        if self.selected_control.widget:
            self.selected_control.widget.setGeometry(self.selected_control.rect)
        
        # 发送信号通知属性面板更新
        self.control_selected.emit(self.selected_control)
        
        # 更新选中框
        self.update_selection_overlay()
    
    # -------------------------- 绘制模式管理 --------------------------
    def start_drawing(self, control_type):
        """开始绘制模式"""
        self.drawing_mode = True
        self.drawing_control_type = control_type
        self.drawing_start_pos = QPoint(0, 0)
        self.drawing_current_pos = QPoint(0, 0)
        self.setCursor(Qt.CrossCursor)
        self.update_selection_overlay()
        self.drawing_mode_changed.emit(True, control_type)
    
    def cancel_drawing(self):
        """取消绘制模式"""
        self.drawing_mode = False
        self.drawing_control_type = None
        self.drawing_start_pos = QPoint(0, 0)
        self.drawing_current_pos = QPoint(0, 0)
        self.setCursor(Qt.ArrowCursor)
        self.update_selection_overlay()
        self.drawing_mode_changed.emit(False, "")
    
    def finish_drawing(self):
        """完成绘制并创建控件"""
        print(f"DesignCanvas: finish_drawing - 绘制模式={self.drawing_mode}, 控件类型={self.drawing_control_type}, 起始位置={self.drawing_start_pos}, 当前位置={self.drawing_current_pos}")
        if not self.drawing_control_type:
            self.cancel_drawing()
            return
        
        # 计算绘制区域
        drawing_rect = QRect(self.drawing_start_pos, self.drawing_current_pos).normalized()
        print(f"DesignCanvas: finish_drawing - 计算绘制区域={drawing_rect}")
        
        # 检查绘制区域是否有效（最小尺寸）
        if drawing_rect.width() < 10 or drawing_rect.height() < 10:
            print(f"DesignCanvas: finish_drawing - 绘制区域太小，取消绘制")
            self.cancel_drawing()
            return
        
        # 检测是否在容器控件上
        parent_control = self.find_container_at_position(drawing_rect.center())
        
        if parent_control:
            # 在容器控件上，建立父子关系
            parent_abs_rect = get_control_absolute_rect(parent_control, self.main_window_props)
            
            # 使用 get_content_rect 获取内容区域
            content_rect = parent_control.get_content_rect()
            
            # 转换为相对于父容器的坐标
            rel_x = drawing_rect.x() - parent_abs_rect.x()
            rel_y = drawing_rect.y() - parent_abs_rect.y()
            rel_width = drawing_rect.width()
            rel_height = drawing_rect.height()
            
            # 限制在内容区域范围内
            min_x = content_rect.x()
            min_y = content_rect.y()
            max_x = content_rect.width() + content_rect.x() - rel_width
            max_y = content_rect.height() + content_rect.y() - rel_height
            
            rel_x = max(min_x, min(rel_x, max_x))
            rel_y = max(min_y, min(rel_y, max_y))
            
            # 对于所有容器控件，rel_y已经是相对于内容区域的坐标
            # 不需要额外调整TabBar高度，因为get_control_absolute_rect会处理这个转换
            
            # 创建控件
            new_control = UIControl(self.drawing_control_type, self)
            new_control.rect = QRect(rel_x, rel_y, rel_width, rel_height)
            new_control.parent = parent_control
            
            # 应用全局预设主题（如果启用）
            if self.global_use_style:
                theme_data = UIControl.PRESET_THEMES.get(self.global_preset_style, {})
                if theme_data:
                    # 根据控件类型获取对应的样式数据
                    control_type = self.drawing_control_type
                    preset_data = theme_data.get(control_type, {})
                    if preset_data:
                        if "bg_color" in preset_data:
                            new_control.bg_color = QColor(preset_data["bg_color"])
                        if "fg_color" in preset_data:
                            new_control.fg_color = QColor(preset_data["fg_color"])
                        if "font_size" in preset_data:
                            new_control.font.setPointSize(preset_data["font_size"])
                        if "bold" in preset_data:
                            new_control.font.setBold(preset_data["bold"])
                        if "visual_style" in preset_data:
                            new_control.visual_style = preset_data["visual_style"]
                        if "border_radius" in preset_data:
                            new_control.border_radius = preset_data["border_radius"]
                        if "border_width" in preset_data:
                            new_control.border_width = preset_data["border_width"]
                        if "border_color" in preset_data:
                            new_control.border_color = QColor(preset_data["border_color"])
            
            # 如果是QTabWidget，记录所在的标签页索引
            if parent_control.type == "QTabWidget" and parent_control.widget:
                tab_widget = parent_control.widget
                if tab_widget.currentWidget():
                    new_control.parent_tab_index = tab_widget.currentIndex()
                    
            parent_control.children.append(new_control)
        else:
            # 在主窗口上
            # 转换为相对于主窗口的坐标
            # 主窗口内容区域的左上角坐标（相对于画布）
            content_x = self.main_window_props.x
            content_y = self.main_window_props.y + self.main_window_props.title_height
            content_width = self.main_window_props.width
            content_height = self.main_window_props.height
            
            # 检查绘制区域是否在主窗口内容区域内
            if (drawing_rect.x() < content_x or 
                drawing_rect.y() < content_y or
                drawing_rect.right() > content_x + content_width or
                drawing_rect.bottom() > content_y + content_height):
                QMessageBox.warning(self, "警告", "控件必须在主窗口内容区域内！")
                self.cancel_drawing()
                return
            
            # 计算相对坐标（相对于主窗口内容区域的左上角）
            rel_x = drawing_rect.x() - content_x
            rel_y = drawing_rect.y() - content_y
            rel_width = drawing_rect.width()
            rel_height = drawing_rect.height()
            
            # 创建控件
            new_control = UIControl(self.drawing_control_type, self)
            new_control.rect = QRect(rel_x, rel_y, rel_width, rel_height)
            new_control.parent = self.main_window_control
            
            # 应用全局预设主题（如果启用）
            if self.global_use_style:
                theme_data = UIControl.PRESET_THEMES.get(self.global_preset_style, {})
                if theme_data:
                    # 根据控件类型获取对应的样式数据
                    control_type = self.drawing_control_type
                    preset_data = theme_data.get(control_type, {})
                    if preset_data:
                        if "bg_color" in preset_data:
                            new_control.bg_color = QColor(preset_data["bg_color"])
                        if "fg_color" in preset_data:
                            new_control.fg_color = QColor(preset_data["fg_color"])
                        if "font_size" in preset_data:
                            new_control.font.setPointSize(preset_data["font_size"])
                        if "bold" in preset_data:
                            new_control.font.setBold(preset_data["bold"])
                        if "visual_style" in preset_data:
                            new_control.visual_style = preset_data["visual_style"]
                        if "border_radius" in preset_data:
                            new_control.border_radius = preset_data["border_radius"]
                        if "border_width" in preset_data:
                            new_control.border_width = preset_data["border_width"]
                        if "border_color" in preset_data:
                            new_control.border_color = QColor(preset_data["border_color"])
            
            self.main_window_control.children.append(new_control)
        
        new_control.create_widget()
        
        # 添加到控件列表
        self.controls.append(new_control)
        
        # 选中新控件
        self.selected_control = new_control
        self.main_window_selected_flag = False
        
        # 发送信号
        self.control_created.emit(new_control)
        self.update_control_list()
        self.control_selected.emit(new_control)
        self.main_window_selected.emit(None)
        
        # 重置绘制状态，但保持绘制模式，允许用户连续创建多个相同类型的控件
        self.drawing_start_pos = QPoint(0, 0)
        self.drawing_current_pos = QPoint(0, 0)
        self.update_selection_overlay()
