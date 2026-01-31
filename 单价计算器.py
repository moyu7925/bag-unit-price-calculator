import tkinter as tk
from tkinter import ttk, messagebox
import math
import os
import sys
import importlib.util

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

template_manager_path = os.path.join(base_dir, 'template_manager.py')

spec = importlib.util.spec_from_file_location("template_manager", template_manager_path)
template_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(template_manager)
TemplateManager = template_manager.TemplateManager

class UnitPriceCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("单价计算器 V4")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)
        
        self.template_manager = TemplateManager()
        
        self.setup_variables()
        self.create_widgets()
        self.setup_layout()
        self.bind_events()
    
    def setup_variables(self):
        last_used = self.template_manager.get_last_used_template()
        template_name = last_used or self.template_manager.get_default_template_name()
        
        if template_name:
            settings = self.template_manager.get_template_settings(template_name)
        else:
            settings = {}
        
        self.current_template_name = tk.StringVar(value=template_name or "")
        
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
        
        self.opening_var = tk.StringVar(value="")
        self.width_var = tk.StringVar(value="")
        self.thickness_var = tk.StringVar(value="")
        self.param_value_var = tk.StringVar(value=self.default_param_value)
        self.material_price_var = tk.StringVar(value=self.default_material_price)
        self.material_unit_price_var = tk.StringVar()
        self.material_weight_var = tk.StringVar()
        
        self.quantity_var = tk.StringVar(value="")
        self.process_param_var = tk.StringVar(value=self.default_process_param)
        self.process_unit_price_var = tk.StringVar(value="")
        self.process_fee_var = tk.StringVar()
        
        self.print_param_var = tk.StringVar(value=self.default_print_param)
        self.material_type_var = tk.StringVar(value=self.default_material_type)
        
        default_price = self.default_material_type_price_copper if self.default_material_type == '铜板' else self.default_material_type_price_rubber
        self.material_type_price_var = tk.StringVar(value=default_price)
        self.print_fee_var = tk.StringVar()
        self.print_unit_price_var = tk.StringVar()
        
        self.material_enabled_var = tk.BooleanVar(value=self.default_material_enabled)
        self.process_enabled_var = tk.BooleanVar(value=self.default_process_enabled)
        self.print_enabled_var = tk.BooleanVar(value=self.default_print_enabled)
        
        self.bag_unit_price_var = tk.StringVar()
        self.material_weight_var = tk.StringVar()
        self.spec_var = tk.StringVar()
    
    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        
        self.title_label = ttk.Label(self.main_frame, text="单价计算器 V4", font=("Arial", 16, "bold"))
        
        main_container = ttk.Frame(self.main_frame)
        
        template_frame = ttk.Frame(main_container)
        
        ttk.Label(template_frame, text="模板选择:").pack(side="left", padx=(0, 5))
        
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.current_template_name, 
                                            state="readonly", width=15)
        self.template_combo.pack(side="left", padx=5)
        self.template_combo['values'] = self.template_manager.get_template_names()
        
        self.apply_template_btn = ttk.Button(template_frame, text="应用", command=self.apply_selected_template, width=8)
        self.apply_template_btn.pack(side="left", padx=5)
        
        self.template_manager_btn = ttk.Button(template_frame, text="模板管理", command=self.open_template_manager_dialog, width=10)
        self.template_manager_btn.pack(side="left", padx=10)
        
        template_frame.pack(pady=5)
        
        control_frame = ttk.Frame(main_container)
        
        self.material_checkbox = ttk.Checkbutton(control_frame, text="原料", variable=self.material_enabled_var, command=self.on_calculation_toggled)
        self.process_checkbox = ttk.Checkbutton(control_frame, text="加工", variable=self.process_enabled_var, command=self.on_calculation_toggled)
        self.print_checkbox = ttk.Checkbutton(control_frame, text="印刷", variable=self.print_enabled_var, command=self.on_calculation_toggled)
        
        self.reset_btn = ttk.Button(control_frame, text="重置", command=self.reset_all_fields)
        
        self.material_checkbox.pack(side="left", padx=5)
        self.process_checkbox.pack(side="left", padx=5)
        self.print_checkbox.pack(side="left", padx=5)
        self.reset_btn.pack(side="left", padx=10)
        
        control_frame.pack(pady=5)
        
        columns_frame = ttk.Frame(main_container)
        
        self.material_frame = ttk.LabelFrame(columns_frame, text="原料计算")
        self.create_material_widgets()
        
        self.process_frame = ttk.LabelFrame(columns_frame, text="加工计算")
        self.create_process_widgets()
        
        self.print_frame = ttk.LabelFrame(columns_frame, text="印刷计算")
        self.create_print_widgets()
        
        self.material_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.process_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.print_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        columns_frame.pack(fill="x", pady=5)
        
        main_container.pack(fill="x", padx=5, pady=5)
        
        self.result_frame = ttk.LabelFrame(self.main_frame, text="目标计算结果")
        
        ttk.Label(self.result_frame, text="规格参数:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        ttk.Label(self.result_frame, textvariable=self.spec_var, font=("Arial", 14, "bold"), foreground="purple").grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        ttk.Label(self.result_frame, text="单袋单价（元/个）:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        ttk.Label(self.result_frame, textvariable=self.bag_unit_price_var, font=("Arial", 14, "bold"), foreground="blue").grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        ttk.Label(self.result_frame, text="原料重量（公斤）:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        ttk.Label(self.result_frame, textvariable=self.material_weight_var, font=("Arial", 14, "bold"), foreground="green").grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        self.detail_frame = ttk.LabelFrame(self.main_frame, text="详细计算过程")
        self.detail_text = tk.Text(self.detail_frame, height=6, width=80)
        self.detail_scrollbar = ttk.Scrollbar(self.detail_frame, orient="vertical", command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=self.detail_scrollbar.set)
    
    def create_material_widgets(self):
        material_inputs = [
            ("开口（长度-厘米）", self.opening_var),
            ("宽度（厘米）", self.width_var),
            ("厚度/C", self.thickness_var),
            ("参数值", self.param_value_var),
            ("原料价格（千元/吨）", self.material_price_var)
        ]
        
        for i, (label_text, var) in enumerate(material_inputs):
            ttk.Label(self.material_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(self.material_frame, textvariable=var, width=15).grid(row=i, column=1, padx=5, pady=5)
        
        ttk.Label(self.material_frame, text="原料单价（元/个）:").grid(row=len(material_inputs), column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.material_frame, textvariable=self.material_unit_price_var, font=("Arial", 10, "bold")).grid(row=len(material_inputs), column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.material_frame, text="原料重量（公斤）:").grid(row=len(material_inputs)+1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.material_frame, textvariable=self.material_weight_var, font=("Arial", 10, "bold")).grid(row=len(material_inputs)+1, column=1, sticky="w", padx=5, pady=5)
    
    def create_process_widgets(self):
        process_inputs = [
            ("个数", self.quantity_var),
            ("加工工费参数", self.process_param_var)
        ]
        
        for i, (label_text, var) in enumerate(process_inputs):
            ttk.Label(self.process_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(self.process_frame, textvariable=var, width=15).grid(row=i, column=1, padx=5, pady=5)
        
        ttk.Label(self.process_frame, text="加工单价（元/个）:").grid(row=len(process_inputs), column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.process_frame, textvariable=self.process_unit_price_var, font=("Arial", 10, "bold")).grid(row=len(process_inputs), column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.process_frame, text="加工费（元）:").grid(row=len(process_inputs)+1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.process_frame, textvariable=self.process_fee_var, font=("Arial", 10, "bold")).grid(row=len(process_inputs)+1, column=1, sticky="w", padx=5, pady=5)
    
    def create_print_widgets(self):
        ttk.Label(self.print_frame, text="印刷工费参数（元/个）").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.print_frame, textvariable=self.print_param_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.print_frame, text="版材类型").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.material_combo = ttk.Combobox(self.print_frame, textvariable=self.material_type_var, 
                                            values=["铜板", "胶版"], state="readonly", width=12)
        self.material_combo.grid(row=1, column=1, padx=5, pady=5)
        self.material_combo.bind("<<ComboboxSelected>>", self.on_material_type_changed)
        
        ttk.Label(self.print_frame, text="版材价格（元）").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.print_frame, textvariable=self.material_type_price_var, font=("Arial", 10, "bold")).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.print_frame, text="印刷单价（元/个）:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.print_frame, textvariable=self.print_unit_price_var, font=("Arial", 10, "bold")).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.print_frame, text="印刷费（元）:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.print_frame, textvariable=self.print_fee_var, font=("Arial", 10, "bold")).grid(row=4, column=1, sticky="w", padx=5, pady=5)
    
    def on_material_type_changed(self, event):
        material_type = self.material_type_var.get()
        if material_type == '铜板':
            self.material_type_price_var.set(self.default_material_type_price_copper)
        else:
            self.material_type_price_var.set(self.default_material_type_price_rubber)
        
        self.calculate_all()
    
    def on_calculation_toggled(self):
        self.calculate_all()
    
    def get_current_settings(self):
        return {
            'param_value': self.param_value_var.get(),
            'material_price': self.material_price_var.get(),
            'process_param': self.process_param_var.get(),
            'print_param': self.print_param_var.get(),
            'material_type': self.material_type_var.get(),
            'material_type_price_copper': self.default_material_type_price_copper,
            'material_type_price_rubber': self.default_material_type_price_rubber,
            'material_enabled': self.material_enabled_var.get(),
            'process_enabled': self.process_enabled_var.get(),
            'print_enabled': self.print_enabled_var.get()
        }
    
    def apply_template(self, template_name):
        settings = self.template_manager.get_template_settings(template_name)
        if settings is None:
            messagebox.showerror("错误", f"模板 '{template_name}' 不存在")
            return False
        
        self.current_template_name.set(template_name)
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
        
        self.param_value_var.set(self.default_param_value)
        self.material_price_var.set(self.default_material_price)
        self.process_param_var.set(self.default_process_param)
        self.process_unit_price_var.set("")
        self.print_param_var.set(self.default_print_param)
        self.material_type_var.set(self.default_material_type)
        
        if self.default_material_type == '铜板':
            self.material_type_price_var.set(self.default_material_type_price_copper)
        else:
            self.material_type_price_var.set(self.default_material_type_price_rubber)
        
        self.material_enabled_var.set(self.default_material_enabled)
        self.process_enabled_var.set(self.default_process_enabled)
        self.print_enabled_var.set(self.default_print_enabled)
        
        self.root.update_idletasks()
        self.calculate_all()
        
        return True
    
    def apply_selected_template(self):
        template_name = self.current_template_name.get()
        if template_name:
            self.apply_template(template_name)
    
    def reset_all_fields(self):
        template_name = self.current_template_name.get()
        if template_name:
            self.apply_template(template_name)
        
        self.opening_var.set("")
        self.width_var.set("")
        self.thickness_var.set("")
        
        self.quantity_var.set("")
        
        self.material_unit_price_var.set("")
        self.material_weight_var.set("")
        self.process_fee_var.set("")
        self.print_fee_var.set("")
        self.print_unit_price_var.set("")
        
        self.bag_unit_price_var.set("")
        
        self.detail_text.delete(1.0, tk.END)
    
    def open_template_manager_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("模板管理")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        left_frame = ttk.LabelFrame(main_frame, text="模板列表", width=220)
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        right_frame = ttk.LabelFrame(main_frame, text="参数设置")
        right_frame.pack(side="left", fill="both", expand=True)
        
        selected_template_var = tk.StringVar(value=self.current_template_name.get())
        
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="新建模板", command=lambda: create_new_template(dialog, refresh_template_list, update_template_combo)).pack(fill="x", pady=2)
        ttk.Button(button_frame, text="复制模板", command=lambda: duplicate_selected_template(refresh_template_list, update_template_combo)).pack(fill="x", pady=2)
        ttk.Button(button_frame, text="删除模板", command=lambda: delete_selected_template(refresh_template_list, update_template_combo)).pack(fill="x", pady=2)
        ttk.Button(button_frame, text="重命名", command=lambda: rename_selected_template(refresh_template_list, update_template_combo)).pack(fill="x", pady=2)
        ttk.Button(button_frame, text="设为默认", command=lambda: set_as_default_template(refresh_template_list)).pack(fill="x", pady=2)
        
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        template_list_canvas = tk.Canvas(list_frame)
        template_list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=template_list_canvas.yview)
        template_list_scrollable_frame = ttk.Frame(template_list_canvas)
        
        def template_list_frame_configure(event):
            bbox = template_list_canvas.bbox("all")
            if bbox:
                template_list_canvas.configure(scrollregion=bbox)
        
        template_list_scrollable_frame.bind("<Configure>", template_list_frame_configure)
        
        template_list_canvas.create_window((0, 0), window=template_list_scrollable_frame, anchor="nw")
        template_list_canvas.configure(yscrollcommand=template_list_scrollbar.set)
        
        template_list_canvas.pack(side="left", fill="both", expand=True)
        template_list_scrollbar.pack(side="right", fill="y")
        
        template_list_frame = ttk.Frame(template_list_scrollable_frame)
        template_list_frame.pack(fill="x", padx=2, pady=2)
        
        def on_mousewheel(event):
            if template_list_canvas.yview() != (0.0, 1.0):
                template_list_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        template_list_canvas.bind("<MouseWheel>", on_mousewheel)
        
        settings_entries = {}
        
        def refresh_template_list():
            for widget in template_list_frame.winfo_children():
                widget.destroy()
            
            current_selection = selected_template_var.get()
            template_names = self.template_manager.get_template_names()
            for name in template_names:
                template = self.template_manager.get_template(name)
                is_default = template.get("is_default", False) if template else False
                is_selected = (name == current_selection)
                
                frame = tk.Frame(template_list_frame, bd=1, relief="solid")
                frame.pack(fill="x", pady=1)
                
                font = ("Arial", 9, "bold") if is_selected else ("Arial", 9)
                radio_btn = tk.Radiobutton(frame, text=name, variable=selected_template_var, 
                                            value=name, width=14, font=font,
                                            command=lambda n=name: load_template_settings(n))
                radio_btn.pack(side="left", padx=3)
                
                if is_default:
                    label = tk.Label(frame, text="⭐", font=("Arial", 8))
                    label.pack(side="left")
                else:
                    tk.Label(frame, font=("Arial", 8), width=1).pack(side="left")
        
        def load_template_settings(template_name):
            template = self.template_manager.get_template(template_name)
            if template:
                settings = template.get("settings", {})
                
                for key, entry in settings_entries.items():
                    if key == 'template_name':
                        name_entry_var.set(template_name)
                    else:
                        value = settings.get(key, "")
                        if isinstance(entry, ttk.Entry):
                            entry.delete(0, tk.END)
                            entry.insert(0, value)
                        elif isinstance(entry, ttk.Combobox):
                            entry.set(value)
                        elif isinstance(entry, tk.BooleanVar):
                            entry.set(bool(value))
            
            selected_template_var.set(template_name)
            name_entry_var.set(template_name)
            refresh_template_list()
        
        def create_new_template(parent_dialog, refresh_cb, update_cb):
            dialog2 = tk.Toplevel(parent_dialog)
            dialog2.title("新建模板")
            dialog2.geometry("350x180")
            dialog2.transient(parent_dialog)
            dialog2.grab_set()
            
            ttk.Label(dialog2, text="模板名称:").pack(anchor="w", padx=20, pady=(20, 5))
            name_entry = ttk.Entry(dialog2, width=30)
            name_entry.pack(fill="x", padx=20, pady=5)
            
            ttk.Label(dialog2, text="将参照默认模板数值创建新模板", font=("Arial", 9), foreground="gray").pack(pady=5)
            
            def save():
                name = name_entry.get().strip()
                if not name:
                    messagebox.showerror("错误", "请输入模板名称")
                    return
                
                if name in self.template_manager.get_template_names():
                    messagebox.showerror("错误", f"模板 '{name}' 已存在")
                    return
                
                default_template_name = self.template_manager.get_default_template_name()
                settings = self.template_manager.get_template_settings(default_template_name)
                if settings is None:
                    settings = self.get_current_settings()
                success, msg = self.template_manager.create_template(name, settings)
                if success:
                    refresh_cb()
                    update_cb()
                    selected_template_var.set(name)
                    load_template_settings(name)
                    messagebox.showinfo("成功", msg)
                    dialog2.destroy()
                else:
                    messagebox.showerror("错误", msg)
            
            btn_frame = ttk.Frame(dialog2)
            btn_frame.pack(pady=15)
            ttk.Button(btn_frame, text="创建", command=save).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="取消", command=dialog2.destroy).pack(side="left", padx=5)
            
            dialog2.update_idletasks()
            x = parent_dialog.winfo_x() + (parent_dialog.winfo_width() // 2) - (dialog2.winfo_width() // 2)
            y = parent_dialog.winfo_y() + (parent_dialog.winfo_height() // 2) - (dialog2.winfo_height() // 2)
            dialog2.geometry(f"+{x}+{y}")
        
        def duplicate_selected_template(refresh_cb, update_cb):
            source_name = selected_template_var.get()
            if not source_name:
                messagebox.showwarning("警告", "请先选择一个模板")
                return
            
            dialog2 = tk.Toplevel(dialog)
            dialog2.title("复制模板")
            dialog2.geometry("350x150")
            dialog2.transient(dialog)
            dialog2.grab_set()
            
            ttk.Label(dialog2, text=f"源模板: {source_name}", font=("Arial", 10)).pack(pady=(15, 5))
            ttk.Label(dialog2, text="新模板名称:").pack(anchor="w", padx=60)
            name_entry = ttk.Entry(dialog2, width=30)
            name_entry.pack(fill="x", padx=60, pady=5)
            
            def save():
                new_name = name_entry.get().strip()
                if not new_name:
                    messagebox.showerror("错误", "请输入新名称")
                    return
                
                if new_name in self.template_manager.get_template_names():
                    messagebox.showerror("错误", f"模板 '{new_name}' 已存在")
                    return
                
                success, msg = self.template_manager.duplicate_template(source_name, new_name)
                if success:
                    refresh_cb()
                    update_cb()
                    selected_template_var.set(new_name)
                    load_template_settings(new_name)
                    messagebox.showinfo("成功", msg)
                    dialog2.destroy()
                else:
                    messagebox.showerror("错误", msg)
            
            btn_frame = ttk.Frame(dialog2)
            btn_frame.pack(pady=15)
            ttk.Button(btn_frame, text="复制", command=save).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="取消", command=dialog2.destroy).pack(side="left", padx=5)
            
            dialog2.update_idletasks()
            x = dialog.winfo_x() + (dialog.winfo_width() // 2) - (dialog2.winfo_width() // 2)
            y = dialog.winfo_y() + (dialog.winfo_height() // 2) - (dialog2.winfo_height() // 2)
            dialog2.geometry(f"+{x}+{y}")
        
        def delete_selected_template(refresh_cb, update_cb):
            template_name = selected_template_var.get()
            if not template_name:
                messagebox.showwarning("警告", "请先选择一个模板")
                return
            
            template = self.template_manager.get_template(template_name)
            if template and template.get("is_default", False):
                messagebox.showerror("错误", "无法删除默认模板")
                return
            
            if messagebox.askyesno("确认", f"确定要删除模板 '{template_name}' 吗？"):
                success, msg = self.template_manager.delete_template(template_name)
                if success:
                    refresh_cb()
                    update_cb()
                    names = self.template_manager.get_template_names()
                    if names:
                        selected_template_var.set(names[0])
                        load_template_settings(names[0])
                    messagebox.showinfo("成功", msg)
                else:
                    messagebox.showerror("错误", msg)
        
        def rename_selected_template(refresh_cb, update_cb):
            old_name = selected_template_var.get()
            if not old_name:
                messagebox.showwarning("警告", "请先选择一个模板")
                return
            
            template = self.template_manager.get_template(old_name)
            if template and template.get("is_default", False):
                messagebox.showerror("错误", "默认模板无法重命名")
                return
            
            dialog2 = tk.Toplevel(dialog)
            dialog2.title("重命名模板")
            dialog2.geometry("350x150")
            dialog2.transient(dialog)
            dialog2.grab_set()
            
            ttk.Label(dialog2, text=f"当前名称: {old_name}", font=("Arial", 10)).pack(pady=(15, 5))
            ttk.Label(dialog2, text="新名称:").pack(anchor="w", padx=60)
            name_entry = ttk.Entry(dialog2, width=30)
            name_entry.pack(fill="x", padx=60, pady=5)
            name_entry.insert(0, old_name)
            
            def save():
                new_name = name_entry.get().strip()
                if not new_name:
                    messagebox.showerror("错误", "请输入新名称")
                    return
                
                if new_name == old_name:
                    dialog2.destroy()
                    return
                
                success, msg = self.template_manager.rename_template(old_name, new_name)
                if success:
                    refresh_cb()
                    update_cb()
                    selected_template_var.set(new_name)
                    load_template_settings(new_name)
                    messagebox.showinfo("成功", msg)
                    dialog2.destroy()
                else:
                    messagebox.showerror("错误", msg)
            
            btn_frame = ttk.Frame(dialog2)
            btn_frame.pack(pady=15)
            ttk.Button(btn_frame, text="确认", command=save).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="取消", command=dialog2.destroy).pack(side="left", padx=5)
            
            dialog2.update_idletasks()
            x = dialog.winfo_x() + (dialog.winfo_width() // 2) - (dialog2.winfo_width() // 2)
            y = dialog.winfo_y() + (dialog.winfo_height() // 2) - (dialog2.winfo_height() // 2)
            dialog2.geometry(f"+{x}+{y}")
        
        def set_as_default_template(refresh_cb):
            template_name = selected_template_var.get()
            if not template_name:
                messagebox.showwarning("警告", "请先选择一个模板")
                return
            
            success, msg = self.template_manager.set_default_template(template_name)
            if success:
                refresh_cb()
                messagebox.showinfo("成功", msg)
            else:
                messagebox.showerror("错误", msg)
        
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        
        ttk.Label(scrollable_frame, text="模板名称:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(10, 5))
        row += 1
        
        name_entry_var = tk.StringVar(value=selected_template_var.get())
        name_entry = ttk.Entry(scrollable_frame, textvariable=name_entry_var, width=20)
        name_entry.grid(row=row, column=0, sticky="w", padx=20, pady=5)
        settings_entries['template_name'] = name_entry_var
        row += 1
        
        def is_default_template(name):
            template = self.template_manager.get_template(name)
            return template and template.get("is_default", False) if template else False
        
        def update_template_name_in_list(event=None):
            current_name = selected_template_var.get()
            new_name = name_entry_var.get().strip()
            
            if not current_name or not new_name:
                return
            
            if current_name == new_name:
                return
            
            if is_default_template(current_name):
                messagebox.showerror("错误", "默认模板无法重命名")
                name_entry_var.set(current_name)
                return
            
            success, msg = self.template_manager.rename_template(current_name, new_name)
            if success:
                refresh_template_list()
                update_template_combo()
                selected_template_var.set(new_name)
            else:
                messagebox.showerror("错误", msg)
                name_entry_var.set(current_name)
        
        name_entry.bind("<FocusOut>", update_template_name_in_list)
        name_entry.bind("<Return>", update_template_name_in_list)
        
        def on_name_entry_focus_in(event):
            name_entry.select_range(0, tk.END)
        
        name_entry.bind("<FocusIn>", on_name_entry_focus_in)
        
        ttk.Label(scrollable_frame, text="原料计算:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(10, 5))
        row += 1
        
        ttk.Label(scrollable_frame, text="参数值 (0.01~10):").grid(row=row, column=0, sticky="w", padx=20)
        entry = ttk.Entry(scrollable_frame, width=15)
        entry.grid(row=row, column=1, sticky="w", padx=5)
        entry.insert(0, self.default_param_value)
        settings_entries['param_value'] = entry
        row += 1
        
        ttk.Label(scrollable_frame, text="原料价格 (1~1000):").grid(row=row, column=0, sticky="w", padx=20)
        entry = ttk.Entry(scrollable_frame, width=15)
        entry.grid(row=row, column=1, sticky="w", padx=5)
        entry.insert(0, self.default_material_price)
        settings_entries['material_price'] = entry
        row += 1
        
        ttk.Label(scrollable_frame, text="加工计算:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(10, 5))
        row += 1
        
        ttk.Label(scrollable_frame, text="加工工费参数 (0.01~5):").grid(row=row, column=0, sticky="w", padx=20)
        entry = ttk.Entry(scrollable_frame, width=15)
        entry.grid(row=row, column=1, sticky="w", padx=5)
        entry.insert(0, self.default_process_param)
        settings_entries['process_param'] = entry
        row += 1
        
        ttk.Label(scrollable_frame, text="印刷计算:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(10, 5))
        row += 1
        
        ttk.Label(scrollable_frame, text="印刷工费参数 (0.001~1):").grid(row=row, column=0, sticky="w", padx=20)
        entry = ttk.Entry(scrollable_frame, width=15)
        entry.grid(row=row, column=1, sticky="w", padx=5)
        entry.insert(0, self.default_print_param)
        settings_entries['print_param'] = entry
        row += 1
        
        ttk.Label(scrollable_frame, text="默认版材类型:").grid(row=row, column=0, sticky="w", padx=20)
        combo = ttk.Combobox(scrollable_frame, values=["铜板", "胶版"], state="readonly", width=12)
        combo.grid(row=row, column=1, sticky="w", padx=5)
        combo.set(self.default_material_type)
        settings_entries['material_type'] = combo
        row += 1
        
        ttk.Label(scrollable_frame, text="铜板价格 (10~1000):").grid(row=row, column=0, sticky="w", padx=20)
        entry = ttk.Entry(scrollable_frame, width=15)
        entry.grid(row=row, column=1, sticky="w", padx=5)
        entry.insert(0, self.default_material_type_price_copper)
        settings_entries['material_type_price_copper'] = entry
        row += 1
        
        ttk.Label(scrollable_frame, text="胶版价格 (10~500):").grid(row=row, column=0, sticky="w", padx=20)
        entry = ttk.Entry(scrollable_frame, width=15)
        entry.grid(row=row, column=1, sticky="w", padx=5)
        entry.insert(0, self.default_material_type_price_rubber)
        settings_entries['material_type_price_rubber'] = entry
        row += 1
        
        ttk.Label(scrollable_frame, text="计算模块启用:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(10, 5))
        row += 1
        
        var1 = tk.BooleanVar(value=self.default_material_enabled)
        ttk.Checkbutton(scrollable_frame, text="原料计算", variable=var1).grid(row=row, column=0, sticky="w", padx=20)
        settings_entries['material_enabled'] = var1
        row += 1
        
        var2 = tk.BooleanVar(value=self.default_process_enabled)
        ttk.Checkbutton(scrollable_frame, text="加工计算", variable=var2).grid(row=row, column=0, sticky="w", padx=20)
        settings_entries['process_enabled'] = var2
        row += 1
        
        var3 = tk.BooleanVar(value=self.default_print_enabled)
        ttk.Checkbutton(scrollable_frame, text="印刷计算", variable=var3).grid(row=row, column=0, sticky="w", padx=20)
        settings_entries['print_enabled'] = var3
        row += 1
        
        def on_mousewheel2(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<MouseWheel>", on_mousewheel2)
        
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        def save_settings():
            errors = []
            numeric_fields = ['param_value', 'material_price', 'process_param', 'print_param', 
                             'material_type_price_copper', 'material_type_price_rubber']
            
            for key, entry in settings_entries.items():
                if key == 'template_name':
                    continue
                if not isinstance(entry, ttk.Entry) or isinstance(entry, ttk.Combobox):
                    continue
                    
                value = entry.get().strip()
                if value:
                    try:
                        float_value = float(value)
                        if key in numeric_fields:
                            field_ranges = {
                                'param_value': ('参数值', 0.01, 10.0),
                                'material_price': ('原料价格', 1, 1000),
                                'process_param': ('加工工费参数', 0.01, 5.0),
                                'print_param': ('印刷工费参数', 0.001, 1.0),
                                'material_type_price_copper': ('铜板价格', 10, 1000),
                                'material_type_price_rubber': ('胶版价格', 10, 500)
                            }
                            if key in field_ranges:
                                name, min_val, max_val = field_ranges[key]
                                if float_value < min_val or float_value > max_val:
                                    errors.append(f"{name} 超出有效范围（{min_val} ~ {max_val}）")
                    except ValueError:
                        field_names = {
                            'param_value': '参数值',
                            'material_price': '原料价格',
                            'process_param': '加工工费参数',
                            'print_param': '印刷工费参数',
                            'material_type_price_copper': '铜板价格',
                            'material_type_price_rubber': '胶版价格'
                        }
                        errors.append(f"{field_names.get(key, key)} 请输入有效数字")
            
            if errors:
                messagebox.showerror("输入错误", "\n".join(errors))
                return
            
            template_name = selected_template_var.get()
            if not template_name:
                messagebox.showerror("错误", "请先选择一个模板")
                return
            
            settings = {}
            for key, entry in settings_entries.items():
                if key == 'template_name':
                    continue
                if isinstance(entry, ttk.Entry):
                    settings[key] = entry.get()
                elif isinstance(entry, ttk.Combobox):
                    settings[key] = entry.get()
                elif isinstance(entry, tk.BooleanVar):
                    settings[key] = entry.get()
            
            success, msg = self.template_manager.update_template(template_name, settings)
            if success:
                self.apply_template(template_name)
                messagebox.showinfo("成功", "设置已保存并应用到当前模板")
                dialog.destroy()
            else:
                messagebox.showerror("错误", msg)
        
        ttk.Button(button_frame, text="保存", command=save_settings, width=10).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy, width=10).pack(side="left", padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def update_template_combo():
            self.template_combo['values'] = self.template_manager.get_template_names()
        
        refresh_template_list()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def setup_layout(self):
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.result_frame.pack(fill="x", padx=10, pady=5)
        
        self.detail_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.detail_text.pack(side="left", fill="both", expand=True)
        self.detail_scrollbar.pack(side="right", fill="y")
    
    def bind_events(self):
        for var in [self.opening_var, self.width_var, self.thickness_var, self.param_value_var, 
                   self.material_price_var, self.quantity_var, self.process_param_var, 
                   self.print_param_var]:
            var.trace_add("write", self.on_values_changed)
    
    def on_values_changed(self, *args):
        self.calculate_all()
    
    def get_float_value(self, var_str):
        try:
            return float(var_str.get() or 0)
        except ValueError:
            return 0.0
    
    def calculate_material(self):
        import decimal
        from decimal import Decimal
        
        opening = Decimal(str(self.get_float_value(self.opening_var)))
        width = Decimal(str(self.get_float_value(self.width_var)))
        thickness = Decimal(str(self.get_float_value(self.thickness_var)))
        param_value = Decimal(str(self.get_float_value(self.param_value_var)))
        material_price = Decimal(str(self.get_float_value(self.material_price_var)))
        quantity = Decimal(str(self.get_float_value(self.quantity_var)))
        
        unit_price = (opening / 100) * (width / 100) * (thickness * 2 / 100) * param_value * material_price
        total_weight = (opening / 100) * (width / 100) * (thickness * 2 / 100) * param_value * quantity
        
        rounded_unit_price = float(unit_price.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        rounded_total_weight = float(total_weight.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        
        self.material_unit_price_var.set(f"{rounded_unit_price:.3f}")
        self.material_weight_var.set(f"{rounded_total_weight:.3f}")
        
        return rounded_unit_price, rounded_total_weight
    
    def calculate_process(self):
        import decimal
        from decimal import Decimal
        
        opening = Decimal(str(self.get_float_value(self.opening_var)))
        quantity = Decimal(str(self.get_float_value(self.quantity_var)))
        process_param = Decimal(str(self.get_float_value(self.process_param_var)))
        
        basic_process_unit_price = (opening / Decimal('100')) * process_param
        basic_process_fee = basic_process_unit_price * quantity
        
        if basic_process_fee < 100:
            final_process_fee = Decimal('100')
            final_process_unit_price = final_process_fee / quantity if quantity > 0 else Decimal('0')
        else:
            final_process_fee = basic_process_fee
            final_process_unit_price = basic_process_unit_price
        
        rounded_final_process_unit_price = float(final_process_unit_price.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        rounded_final_process_fee = float(final_process_fee.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        
        self.process_unit_price_var.set(f"{rounded_final_process_unit_price:.3f}")
        self.process_fee_var.set(f"{rounded_final_process_fee:.3f}")
        
        return rounded_final_process_fee
    
    def calculate_print(self):
        import decimal
        from decimal import Decimal
        
        quantity = Decimal(str(self.get_float_value(self.quantity_var)))
        print_param = Decimal(str(self.get_float_value(self.print_param_var)))
        material_type = self.material_type_var.get()
        
        basic_print_unit_price = print_param
        basic_print_fee = basic_print_unit_price * quantity
        
        if material_type == "铜板":
            material_price = Decimal(str(self.default_material_type_price_copper))
        else:
            material_price = Decimal(str(self.default_material_type_price_rubber))
        
        rounded_material_price = float(material_price.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        self.material_type_price_var.set(f"{rounded_material_price:.3f}")
        
        if basic_print_fee < material_price:
            final_print_unit_price = material_price / quantity if quantity > 0 else Decimal('0')
            final_print_fee = material_price
        else:
            final_print_unit_price = basic_print_unit_price
            final_print_fee = basic_print_fee
        
        rounded_final_print_unit_price = float(final_print_unit_price.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        rounded_final_print_fee = float(final_print_fee.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        
        self.print_unit_price_var.set(f"{rounded_final_print_unit_price:.3f}")
        self.print_fee_var.set(f"{rounded_final_print_fee:.3f}")
        return rounded_final_print_fee
    
    def calculate_all(self):
        try:
            if self.material_enabled_var.get():
                unit_price, weight = self.calculate_material()
            else:
                unit_price = 0.0
                weight = 0.0
            
            if self.process_enabled_var.get():
                process_fee = self.calculate_process()
                process_unit_price = self.get_float_value(self.process_unit_price_var)
            else:
                process_fee = 0.0
                process_unit_price = 0.0
                self.process_unit_price_var.set("0.000")
                self.process_fee_var.set("0.000")
            
            if self.print_enabled_var.get():
                print_fee = self.calculate_print()
                print_unit_price = self.get_float_value(self.print_unit_price_var)
            else:
                print_fee = 0.0
                print_unit_price = 0.0
                self.print_unit_price_var.set("0.000")
                self.print_fee_var.set("0.000")
            
            import decimal
            from decimal import Decimal
            
            unit_price_decimal = Decimal(str(unit_price))
            process_unit_price_decimal = Decimal(str(process_unit_price))
            print_unit_price_decimal = Decimal(str(print_unit_price))
            
            bag_unit_price_decimal = unit_price_decimal + process_unit_price_decimal + print_unit_price_decimal
            bag_unit_price = float(bag_unit_price_decimal.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
            
            weight_decimal = Decimal(str(weight))
            rounded_weight = float(weight_decimal.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
            
            self.bag_unit_price_var.set(f"{bag_unit_price:.3f}")
            self.material_weight_var.set(f"{rounded_weight:.3f}")
            
            opening = self.opening_var.get() or "0"
            width = self.width_var.get() or "0"
            thickness = self.thickness_var.get() or "0"
            param_value = self.param_value_var.get() or "0"
            material_price = self.material_price_var.get() or "0"
            quantity = self.quantity_var.get() or "0"
            process_param = self.process_param_var.get() or "0"
            print_param = self.print_param_var.get() or "0"
            material_type_price = self.material_type_price_var.get() or "0"
            
            self.spec_var.set(f"{opening} * {width}    {thickness}C")
            
            detail_text = f"""
=== 计算算式 ===

原料计算：
- 原料单价 = ({opening}/100) × ({width}/100) × ({thickness}×2/100) × {param_value} × {material_price} = {unit_price:.3f} 元/个
- 原料重量 = ({opening}/100) × ({width}/100) × ({thickness}×2/100) × {param_value} × {quantity} = {weight:.3f} 公斤

加工计算：
- 加工单价 = ({opening}/100) × {process_param} = {process_unit_price:.3f} 元/个
- 加工费 = {process_unit_price:.3f} × {quantity} = {process_fee:.3f} 元（最低100元）

印刷计算：
- 印刷单价 = {print_param} = {print_unit_price:.3f} 元/个
- 印刷费 = {print_unit_price:.3f} × {quantity} = {print_fee:.3f} 元（最低{material_type_price}元）

单袋单价 = {unit_price:.3f} + {process_unit_price:.3f} + {print_unit_price:.3f} = {bag_unit_price:.3f} 元/个
"""
            
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, detail_text)
            
        except Exception as e:
            messagebox.showerror("计算错误", f"计算过程中发生错误：{str(e)}")
    
    def run(self):
        self.calculate_all()
        self.root.mainloop()

def main():
    import sys
    
    root = tk.Tk()
    app = UnitPriceCalculator(root)
    
    def on_closing():
        template_name = app.current_template_name.get()
        if template_name:
            app.template_manager.set_last_used_template(template_name)
        
        root.quit()
        root.destroy()
        sys.exit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    app.run()

if __name__ == "__main__":
    main()
