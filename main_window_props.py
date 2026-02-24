from PyQt5.QtGui import QColor


class MainWindowProperties:
    """主窗口属性：管理主窗口的所有可编辑属性"""
    def __init__(self):
        # 基础属性
        self.name = "MainWindow"
        self.title = "主窗口"
        self.x = 0
        self.y = 0
        self.width = 800
        self.height = 600
        self.bg_color = QColor(240, 240, 240)
        self.title_color = QColor(0, 102, 204)
        self.title_text_color = QColor(255, 255, 255)
        self.title_height = 30
        self.use_style = True
        
        # 网格设置
        self.grid_enabled = True
        self.grid_spacing = 8
        self.grid_start_x = 3
        self.grid_start_y = 1
        self.grid_color = QColor(0, 0, 0)
        
        # 画布引用（用于访问全局样式设置）
        self.canvas = None

    def to_dict(self):
        """序列化为字典"""
        return {
            "name": self.name,
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "bg_color": self.bg_color.name(),
            "title_color": self.title_color.name(),
            "title_text_color": self.title_text_color.name(),
            "title_height": self.title_height,
            "use_style": self.use_style,
            "grid_enabled": self.grid_enabled,
            "grid_spacing": self.grid_spacing,
            "grid_start_x": self.grid_start_x,
            "grid_start_y": self.grid_start_y,
            "grid_color": self.grid_color.name()
        }

    @classmethod
    def from_dict(cls, data):
        """从字典反序列化"""
        props = cls()
        props.name = data.get("name", "MainWindow")
        props.title = data.get("title", "主窗口")
        props.x = data.get("x", 0)
        props.y = data.get("y", 0)
        props.width = data.get("width", 800)
        props.height = data.get("height", 600)
        props.bg_color = QColor(data.get("bg_color", "#F0F0F0"))
        props.title_color = QColor(data.get("title_color", "#0066CC"))
        props.title_text_color = QColor(data.get("title_text_color", "#FFFFFF"))
        props.title_height = data.get("title_height", 30)
        props.use_style = data.get("use_style", True)
        props.grid_enabled = data.get("grid_enabled", True)
        props.grid_spacing = data.get("grid_spacing", 8)
        props.grid_start_x = data.get("grid_start_x", 3)
        props.grid_start_y = data.get("grid_start_y", 1)
        props.grid_color = QColor(data.get("grid_color", "#000000"))
        props.canvas = None
        return props
