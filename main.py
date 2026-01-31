import os
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

from calculator_logic import CalculatorLogic
from template_manager import TemplateManager

class CalculatorScreen(Screen):
    pass

class TemplateManagerScreen(Screen):
    pass

class UnitPriceCalculatorApp(App):
    def build(self):
        Window.size = (dp(400), dp(700))
        self.title = "单价计算器 V4"
        
        self.template_manager = TemplateManager()
        self.calculator = CalculatorLogic()
        
        self.setup_default_values()
        
        self.sm = ScreenManager()
        self.calculator_screen = CalculatorScreen(name='calculator')
        self.template_screen = TemplateManagerScreen(name='template_manager')
        self.sm.add_widget(self.calculator_screen)
        self.sm.add_widget(self.template_screen)
        
        Clock.schedule_once(self.init_ui, 0)
        
        return self.sm
    
    def setup_default_values(self):
        last_used = self.template_manager.get_last_used_template()
        template_name = last_used or self.template_manager.get_default_template_name()
        
        if template_name:
            settings = self.template_manager.get_template_settings(template_name)
        else:
            settings = {}
        
        self.current_template_name = template_name or ""
        self.default_param_value = settings.get('param_value', '0.95')
        self.default_material_price = settings.get('material_price', '9')
        self.default_process_param = settings.get('process_param', '0.2')
        self.default_print_param = settings.get('print_param', '0.015')
        self.default_material_type = settings.get('material_type', '铜板')
        self.default_material_type_price_copper = settings.get('material_type_price_copper', '100')
        self.default_material_type_price_rubber = settings.get('material_type_price_rubber', '50')
        self.default_material_enabled = settings.get('material_enabled', True)
        self.default_process_enabled = settings.get('process_enabled', True)
        self.default_print_enabled = settings.get('print_enabled', True)
        
        self.calculator.material_enabled = self.default_material_enabled
        self.calculator.process_enabled = self.default_process_enabled
        self.calculator.print_enabled = self.default_print_enabled
        self.calculator.default_material_type_price_copper = float(self.default_material_type_price_copper)
        self.calculator.default_material_type_price_rubber = float(self.default_material_type_price_rubber)
    
    def init_ui(self, dt):
        self.update_template_spinner()
        self.apply_template(self.current_template_name)
    
    def update_template_spinner(self):
        template_names = self.template_manager.get_template_names()
        spinner = self.calculator_screen.ids.template_spinner
        spinner.values = template_names
        if self.current_template_name in template_names:
            spinner.text = self.current_template_name
    
    def apply_template(self, template_name):
        if not template_name:
            return
        
        settings = self.template_manager.get_template_settings(template_name)
        if settings is None:
            return
        
        self.current_template_name = template_name
        self.template_manager.set_last_used_template(template_name)
        
        self.default_param_value = settings.get('param_value', '0.95')
        self.default_material_price = settings.get('material_price', '9')
        self.default_process_param = settings.get('process_param', '0.2')
        self.default_print_param = settings.get('print_param', '0.015')
        self.default_material_type = settings.get('material_type', '铜板')
        self.default_material_type_price_copper = settings.get('material_type_price_copper', '100')
        self.default_material_type_price_rubber = settings.get('material_type_price_rubber', '50')
        self.default_material_enabled = settings.get('material_enabled', True)
        self.default_process_enabled = settings.get('process_enabled', True)
        self.default_print_enabled = settings.get('print_enabled', True)
        
        screen = self.calculator_screen
        screen.ids.param_value.text = self.default_param_value
        screen.ids.material_price.text = self.default_material_price
        screen.ids.process_param.text = self.default_process_param
        screen.ids.print_param.text = self.default_print_param
        screen.ids.material_type.text = self.default_material_type
        
        screen.ids.material_checkbox.active = self.default_material_enabled
        screen.ids.process_checkbox.active = self.default_process_enabled
        screen.ids.print_checkbox.active = self.default_print_enabled
        
        self.calculator.material_enabled = self.default_material_enabled
        self.calculator.process_enabled = self.default_process_enabled
        self.calculator.print_enabled = self.default_print_enabled
        
        self.calculate_all()
    
    def on_template_selected(self, spinner, text):
        if text:
            self.apply_template(text)
    
    def on_material_type_changed(self, spinner, text):
        if text == '铜板':
            material_price = self.default_material_type_price_copper
        else:
            material_price = self.default_material_type_price_rubber
        
        self.calculator.material_type = text
        self.calculate_all()
    
    def on_calculation_toggled(self, checkbox, value):
        self.calculator.material_enabled = self.calculator_screen.ids.material_checkbox.active
        self.calculator.process_enabled = self.calculator_screen.ids.process_checkbox.active
        self.calculator.print_enabled = self.calculator_screen.ids.print_checkbox.active
        self.calculate_all()
    
    def on_value_changed(self, instance, value):
        self.calculate_all()
    
    def calculate_all(self):
        screen = self.calculator_screen
        
        opening = screen.ids.opening.text
        width = screen.ids.width.text
        thickness = screen.ids.thickness.text
        param_value = screen.ids.param_value.text or self.default_param_value
        material_price = screen.ids.material_price.text or self.default_material_price
        quantity = screen.ids.quantity.text
        process_param = screen.ids.process_param.text or self.default_process_param
        print_param = screen.ids.print_param.text or self.default_print_param
        material_type = screen.ids.material_type.text
        
        self.calculator.set_values(
            opening, width, thickness, param_value, material_price,
            quantity, process_param, print_param, material_type
        )
        
        try:
            result = self.calculator.calculate_all()
            
            screen.ids.bag_unit_price.text = f"{result['bag_unit_price']:.3f} 元"
            screen.ids.material_weight.text = f"{result['material_weight']:.3f} kg"
            screen.ids.material_unit_price.text = f"{result['material_unit_price']:.3f} 元"
            screen.ids.process_unit_price.text = f"{result['process_unit_price']:.3f} 元"
            screen.ids.print_unit_price.text = f"{result['print_unit_price']:.3f} 元"
            
            total_fee = result['material_unit_price'] * self.calculator.quantity + result['process_fee'] + result['print_fee']
            screen.ids.total_fee.text = f"{total_fee:.3f} 元"
            
        except Exception as e:
            pass
    
    def reset_all_fields(self):
        template_name = self.current_template_name
        if template_name:
            self.apply_template(template_name)
        
        screen = self.calculator_screen
        screen.ids.opening.text = ""
        screen.ids.width.text = ""
        screen.ids.thickness.text = ""
        screen.ids.quantity.text = ""
        
        screen.ids.material_unit_price.text = "0.000 元"
        screen.ids.material_weight.text = "0.000 kg"
        screen.ids.process_unit_price.text = "0.000 元"
        screen.ids.print_unit_price.text = "0.000 元"
        screen.ids.bag_unit_price.text = "0.000 元"
        screen.ids.total_fee.text = "0.000 元"
    
    def open_template_manager(self):
        self.sm.current = 'template_manager'
        self.refresh_template_list()
    
    def back_to_calculator(self):
        self.sm.current = 'calculator'
        self.update_template_spinner()
    
    def refresh_template_list(self):
        screen = self.template_screen
        template_names = self.template_manager.get_template_names()
        
        layout = screen.ids.template_list_layout
        layout.clear_widgets()
        
        current_template = screen.ids.template_name.text if screen.ids.template_name.text else ""
        
        for name in template_names:
            template = self.template_manager.get_template(name)
            is_default = template.get("is_default", False) if template else False
            is_selected = (name == current_template)
            
            btn = Button(
                text=f"{'⭐ ' if is_default else ''}{name}",
                size_hint_y=None,
                height=dp(40),
                font_size=dp(13),
                background_color=[0.9, 0.95, 1, 1] if is_selected else [1, 1, 1, 1],
                color=[0, 0, 0, 1],
                on_release=lambda btn, n=name: self.select_template(n)
            )
            layout.add_widget(btn)
    
    def select_template(self, template_name):
        screen = self.template_screen
        screen.ids.template_name.text = template_name
        
        template = self.template_manager.get_template(template_name)
        if template:
            settings = template.get("settings", {})
            
            screen.ids.param_value.text = settings.get('param_value', '')
            screen.ids.material_price.text = settings.get('material_price', '')
            screen.ids.process_param.text = settings.get('process_param', '')
            screen.ids.print_param.text = settings.get('print_param', '')
            screen.ids.material_type.text = settings.get('material_type', '铜板')
            screen.ids.material_type_price_copper.text = settings.get('material_type_price_copper', '')
            screen.ids.material_type_price_rubber.text = settings.get('material_type_price_rubber', '')
            screen.ids.material_enabled.active = settings.get('material_enabled', True)
            screen.ids.process_enabled.active = settings.get('process_enabled', True)
            screen.ids.print_enabled.active = settings.get('print_enabled', True)
        
        self.refresh_template_list()
    
    def create_new_template(self):
        screen = self.template_screen
        name = screen.ids.new_template_name.text
        
        if not name:
            self.show_error("请输入模板名称")
            return
        
        if name in self.template_manager.get_template_names():
            self.show_error(f"模板 '{name}' 已存在")
            return
        
        default_template_name = self.template_manager.get_default_template_name()
        settings = self.template_manager.get_template_settings(default_template_name)
        if settings is None:
            settings = self.get_current_template_settings()
        
        success, msg = self.template_manager.create_template(name, settings)
        if success:
            screen.ids.new_template_name.text = ""
            self.refresh_template_list()
            self.select_template(name)
            self.show_info("创建成功")
        else:
            self.show_error(msg)
    
    def duplicate_template(self):
        screen = self.template_screen
        current_name = screen.ids.template_name.text
        
        if not current_name:
            self.show_error("请先选择一个模板")
            return
        
        new_name = screen.ids.new_template_name.text
        if not new_name:
            self.show_error("请输入新模板名称")
            return
        
        if new_name in self.template_manager.get_template_names():
            self.show_error(f"模板 '{new_name}' 已存在")
            return
        
        success, msg = self.template_manager.duplicate_template(current_name, new_name)
        if success:
            screen.ids.new_template_name.text = ""
            self.refresh_template_list()
            self.select_template(new_name)
            self.show_info("复制成功")
        else:
            self.show_error(msg)
    
    def delete_template(self):
        screen = self.template_screen
        template_name = screen.ids.template_name.text
        
        if not template_name:
            self.show_error("请先选择一个模板")
            return
        
        template = self.template_manager.get_template(template_name)
        if template and template.get("is_default", False):
            self.show_error("无法删除默认模板")
            return
        
        success, msg = self.template_manager.delete_template(template_name)
        if success:
            self.refresh_template_list()
            names = self.template_manager.get_template_names()
            if names:
                self.select_template(names[0])
            self.show_info("删除成功")
        else:
            self.show_error(msg)
    
    def rename_template(self):
        screen = self.template_screen
        old_name = screen.ids.template_name.text
        
        if not old_name:
            self.show_error("请先选择一个模板")
            return
        
        template = self.template_manager.get_template(old_name)
        if template and template.get("is_default", False):
            self.show_error("默认模板无法重命名")
            return
        
        new_name = screen.ids.new_template_name.text
        if not new_name:
            self.show_error("请输入新名称")
            return
        
        if new_name == old_name:
            return
        
        success, msg = self.template_manager.rename_template(old_name, new_name)
        if success:
            screen.ids.new_template_name.text = ""
            self.refresh_template_list()
            self.select_template(new_name)
            self.show_info("重命名成功")
        else:
            self.show_error(msg)
    
    def set_as_default(self):
        screen = self.template_screen
        template_name = screen.ids.template_name.text
        
        if not template_name:
            self.show_error("请先选择一个模板")
            return
        
        success, msg = self.template_manager.set_default_template(template_name)
        if success:
            self.refresh_template_list()
            self.show_info("已设为默认模板")
        else:
            self.show_error(msg)
    
    def save_template_settings(self):
        screen = self.template_screen
        template_name = screen.ids.template_name.text
        
        if not template_name:
            self.show_error("请先选择一个模板")
            return
        
        settings = {
            'param_value': screen.ids.param_value.text,
            'material_price': screen.ids.material_price.text,
            'process_param': screen.ids.process_param.text,
            'print_param': screen.ids.print_param.text,
            'material_type': screen.ids.material_type.text,
            'material_type_price_copper': screen.ids.material_type_price_copper.text,
            'material_type_price_rubber': screen.ids.material_type_price_rubber.text,
            'material_enabled': screen.ids.material_enabled.active,
            'process_enabled': screen.ids.process_enabled.active,
            'print_enabled': screen.ids.print_enabled.active
        }
        
        success, msg = self.template_manager.update_template(template_name, settings)
        if success:
            self.apply_template(template_name)
            self.show_info("保存成功")
        else:
            self.show_error(msg)
    
    def get_current_template_settings(self):
        screen = self.calculator_screen
        return {
            'param_value': screen.ids.param_value.text,
            'material_price': screen.ids.material_price.text,
            'process_param': screen.ids.process_param.text,
            'print_param': screen.ids.print_param.text,
            'material_type': screen.ids.material_type.text,
            'material_type_price_copper': str(self.default_material_type_price_copper),
            'material_type_price_rubber': str(self.default_material_type_price_rubber),
            'material_enabled': screen.ids.material_checkbox.active,
            'process_enabled': screen.ids.process_checkbox.active,
            'print_enabled': screen.ids.print_checkbox.active
        }
    
    def show_error(self, message):
        popup = Popup(
            title='错误',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_info(self, message):
        popup = Popup(
            title='提示',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def on_stop(self):
        template_name = self.current_template_name
        if template_name:
            self.template_manager.set_last_used_template(template_name)

if __name__ == '__main__':
    UnitPriceCalculatorApp().run()
