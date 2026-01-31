import json
import os
from datetime import datetime

class TemplateManager:
    def __init__(self, data_file="不能删除的数据文件.json"):
        self.data_file = data_file
        self.data = {
            "templates": {},
            "last_used_template": None
        }
        self.load()
    
    def load(self):
        """从文件加载模板数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self._init_default_templates()
        except Exception as e:
            print(f"加载模板数据失败: {e}")
            self._init_default_templates()
    
    def save(self):
        """保存模板数据到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模板数据失败: {e}")
    
    def _init_default_templates(self):
        """初始化默认模板"""
        default_settings = {
            "param_value": "0.95",
            "material_price": "9",
            "process_param": "0.2",
            "print_param": "0.015",
            "material_type": "铜板",
            "material_type_price_copper": "100",
            "material_type_price_rubber": "50",
            "material_enabled": True,
            "process_enabled": True,
            "print_enabled": True
        }
        
        self.data = {
            "templates": {
                "默认模板": {
                    "name": "默认模板",
                    "is_default": True,
                    "settings": default_settings.copy()
                }
            },
            "last_used_template": "默认模板"
        }
        self.save()
    
    def get_template_names(self):
        """获取所有模板名称列表"""
        return list(self.data["templates"].keys())
    
    def get_template(self, name):
        """获取指定模板的完整信息"""
        if name in self.data["templates"]:
            return self.data["templates"][name]
        return None
    
    def get_template_settings(self, name):
        """获取指定模板的设置"""
        template = self.get_template(name)
        if template:
            return template.get("settings", {})
        return None
    
    def get_last_used_template(self):
        """获取最近使用的模板名称"""
        last_used = self.data.get("last_used_template")
        if last_used and last_used in self.data["templates"]:
            return last_used
        return None
    
    def set_last_used_template(self, name):
        """设置最近使用的模板"""
        if name in self.data["templates"]:
            self.data["last_used_template"] = name
            self.save()
    
    def create_template(self, name, settings, is_default=False):
        """创建新模板"""
        if name in self.data["templates"]:
            return False, f"模板 '{name}' 已存在"
        
        self.data["templates"][name] = {
            "name": name,
            "is_default": is_default,
            "settings": settings.copy()
        }
        self.data["last_used_template"] = name
        self.save()
        return True, f"模板 '{name}' 创建成功"
    
    def update_template(self, name, settings):
        """更新现有模板"""
        if name not in self.data["templates"]:
            return False, f"模板 '{name}' 不存在"
        
        self.data["templates"][name]["settings"] = settings.copy()
        self.save()
        return True, f"模板 '{name}' 更新成功"
    
    def delete_template(self, name):
        """删除模板"""
        if name not in self.data["templates"]:
            return False, f"模板 '{name}' 不存在"
        
        if self.data["templates"][name].get("is_default", False):
            return False, "无法删除默认模板"
        
        del self.data["templates"][name]
        
        if self.data["last_used_template"] == name:
            remaining = self.get_template_names()
            if remaining:
                self.data["last_used_template"] = remaining[0]
            else:
                self.data["last_used_template"] = None
        
        self.save()
        return True, f"模板 '{name}' 删除成功"
    
    def rename_template(self, old_name, new_name):
        """重命名模板"""
        if old_name not in self.data["templates"]:
            return False, f"模板 '{old_name}' 不存在"
        
        if new_name in self.data["templates"]:
            return False, f"模板 '{new_name}' 已存在"
        
        template = self.data["templates"].pop(old_name)
        template["name"] = new_name
        self.data["templates"][new_name] = template
        
        if self.data["last_used_template"] == old_name:
            self.data["last_used_template"] = new_name
        
        self.save()
        return True, f"模板已重命名为 '{new_name}'"
    
    def set_default_template(self, name):
        """设置默认模板"""
        if name not in self.data["templates"]:
            return False, f"模板 '{name}' 不存在"
        
        for template_name in self.data["templates"]:
            self.data["templates"][template_name]["is_default"] = (template_name == name)
        
        self.save()
        return True, f"默认模板已设置为 '{name}'"
    
    def duplicate_template(self, source_name, new_name):
        """复制模板"""
        source_settings = self.get_template_settings(source_name)
        if source_settings is None:
            return False, f"模板 '{source_name}' 不存在"
        
        return self.create_template(new_name, source_settings)
    
    def get_default_template_name(self):
        """获取默认模板名称"""
        for name, template in self.data["templates"].items():
            if template.get("is_default", False):
                return name
        return None
