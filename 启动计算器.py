#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单价计算器启动脚本
用于快速启动桌面窗口型单价计算器工具
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        messagebox.showerror("版本错误", "此工具需要Python 3.6或更高版本")
        return False
    return True

def check_dependencies():
    """检查依赖项"""
    try:
        import tkinter
        return True
    except ImportError:
        messagebox.showerror("依赖错误", "缺少tkinter库，请安装Python的tkinter支持")
        return False

def launch_calculator():
    """启动计算器"""
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        calculator_file = os.path.join(current_dir, "单价计算器.py")
        
        if not os.path.exists(calculator_file):
            messagebox.showerror("文件错误", f"找不到计算器主文件：{calculator_file}")
            return
        
        # 导入并运行计算器
        sys.path.insert(0, current_dir)
        from 单价计算器 import UnitPriceCalculator
        
        # 创建主窗口
        root = tk.Tk()
        app = UnitPriceCalculator(root)
        app.run()
        
    except Exception as e:
        messagebox.showerror("启动错误", f"启动计算器时发生错误：\n{str(e)}")

def main():
    """主函数"""
    print("=" * 50)
    print("           单价计算器 v1.0")
    print("=" * 50)
    print("正在启动桌面窗口型单价计算器...")
    
    # 检查环境和依赖
    if not check_python_version():
        return
    
    if not check_dependencies():
        return
    
    print("环境检查通过，正在启动计算器...")
    
    # 启动计算器
    launch_calculator()

if __name__ == "__main__":
    main()