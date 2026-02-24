import json
from ui_control import UIControl
from main_window_props import MainWindowProperties

class ProjectManager:
    """项目管理器：负责项目的保存和加载"""
    
    # 加密配置
    ENCRYPTION_KEY = b"EasyUI_Secure_Key_2024" # 密钥
    MAGIC_HEADER = b"EASYPACK_V1" # 文件头标识

    @staticmethod
    def _xor_cipher(data, key):
        """简单的XOR加解密"""
        key_len = len(key)
        result = bytearray(len(data))
        for i in range(len(data)):
            result[i] = data[i] ^ key[i % key_len]
        return bytes(result)

    @staticmethod
    def save_project(file_path, design_canvas):
        """保存项目到文件（支持加密）"""
        project_data = {
            "version": "1.0",
            "main_window": design_canvas.main_window_props.to_dict(),
            "controls": [control.to_dict() for control in design_canvas.controls]
        }
        
        try:
            # 1. 转为JSON字符串
            json_str = json.dumps(project_data, indent=4, ensure_ascii=False)
            
            # 2. 决定是否加密：如果是 .pack 后缀则加密
            if file_path.endswith(".pack"):
                # 转为bytes
                data_bytes = json_str.encode("utf-8")
                # 加密
                encrypted_data = ProjectManager._xor_cipher(data_bytes, ProjectManager.ENCRYPTION_KEY)
                # 写入：头标识 + 加密数据
                with open(file_path, "wb") as f:
                    f.write(ProjectManager.MAGIC_HEADER + encrypted_data)
            else:
                # 普通JSON保存
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                    
            return True
        except Exception as e:
            print(f"保存项目失败: {e}")
            return False

    @staticmethod
    def load_project(file_path, design_canvas):
        """从文件加载项目（支持解密）"""
        try:
            content = ""
            project_data = {}
            
            # 0. 检查文件大小
            import os
            if os.path.getsize(file_path) == 0:
                print(f"文件为空，初始化空白项目: {file_path}")
                project_data = {} 
            else:
                # 1. 尝试以二进制读取并检查头标识
                try:
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    
                    if file_bytes.startswith(ProjectManager.MAGIC_HEADER):
                        # 是加密文件，进行解密
                        encrypted_data = file_bytes[len(ProjectManager.MAGIC_HEADER):]
                        decrypted_bytes = ProjectManager._xor_cipher(encrypted_data, ProjectManager.ENCRYPTION_KEY)
                        content = decrypted_bytes.decode("utf-8")
                    else:
                        # 不是加密文件，尝试按文本解码
                        # 尝试多种编码格式读取
                        encodings = ["utf-8", "gbk", "gb2312", "utf-16", "latin1"]
                        for encoding in encodings:
                            try:
                                content = file_bytes.decode(encoding)
                                break
                            except UnicodeDecodeError:
                                continue
                except Exception as e:
                    print(f"读取文件失败: {e}")
                
                if content:
                    try:
                        project_data = json.loads(content)
                    except json.JSONDecodeError:
                        print(f"JSON解析失败，初始化空白项目: {file_path}")
                        project_data = {}
                else:
                    print(f"无法读取文件内容，初始化空白项目: {file_path}")
                    project_data = {}

            # 1. 清除现有画布
            design_canvas.clear_canvas()
            
            # 2. 恢复主窗口属性
            mw_data = project_data.get("main_window", {})
            design_canvas.main_window_props = MainWindowProperties.from_dict(mw_data)
            design_canvas.main_window_props.canvas = design_canvas
            
            # 3. 恢复控件
            controls_data = project_data.get("controls", [])
            controls_map = {} # id -> control
            
            # 第一遍：创建所有控件
            for control_data in controls_data:
                control = UIControl.from_dict(control_data, design_canvas)
                controls_map[control.id] = control
                design_canvas.controls.append(control)
                control.create_widget() # 创建UI组件
            
            # 第二遍：建立父子关系
            for control_data in controls_data:
                control_id = control_data.get("id")
                parent_id = control_data.get("parent_id")
                
                if control_id in controls_map:
                    child = controls_map[control_id]
                    
                    if parent_id in controls_map:
                        # 父控件是普通控件
                        parent = controls_map[parent_id]
                        child.parent = parent
                        parent.children.append(child)
                    else:
                        # 父控件不在列表中（通常是主窗口），或者没有父控件
                        # 将其挂载到主窗口下
                        parent = design_canvas.main_window_control
                        child.parent = parent
                        parent.children.append(child)
                        
                    # 重新设置父组件
                    child.attach_to_parent(parent)

            # 更新画布
            design_canvas.update()
            design_canvas.update_control_list()
            
            return True
        except Exception as e:
            print(f"加载项目失败: {e}")
            import traceback
            traceback.print_exc()
            return False
