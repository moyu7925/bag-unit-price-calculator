@echo off
echo 正在打包单价计算器 V3...
echo.

REM 检查是否安装了 PyInstaller
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller 未安装，正在安装...
    python -m pip install pyinstaller
    echo.
)

REM 创建初始模板数据文件
echo 创建初始模板数据文件...
if not exist "不能删除的数据文件.json" (
    echo { > "不能删除的数据文件.json"
    echo   "templates": { >> "不能删除的数据文件.json"
    echo     "默认模板": { >> "不能删除的数据文件.json"
    echo       "name": "默认模板", >> "不能删除的数据文件.json"
    echo       "is_default": true, >> "不能删除的数据文件.json"
    echo       "settings": { >> "不能删除的数据文件.json"
    echo         "param_value": "0.95", >> "不能删除的数据文件.json"
    echo         "material_price": "9", >> "不能删除的数据文件.json"
    echo         "process_param": "0.2", >> "不能删除的数据文件.json"
    echo         "print_param": "0.015", >> "不能删除的数据文件.json"
    echo         "material_type": "铜板", >> "不能删除的数据文件.json"
    echo         "material_type_price_copper": "100", >> "不能删除的数据文件.json"
    echo         "material_type_price_rubber": "50", >> "不能删除的数据文件.json"
    echo         "material_enabled": true, >> "不能删除的数据文件.json"
    echo         "process_enabled": true, >> "不能删除的数据文件.json"
    echo         "print_enabled": true >> "不能删除的数据文件.json"
    echo       } >> "不能删除的数据文件.json"
    echo     } >> "不能删除的数据文件.json"
    echo   }, >> "不能删除的数据文件.json"
    echo   "last_used_template": "默认模板" >> "不能删除的数据文件.json"
    echo } >> "不能删除的数据文件.json"
    echo 模板数据文件创建成功
) else (
    echo 模板数据文件已存在，跳过创建
)
echo.

REM 打包程序
echo 开始打包...
pyinstaller --onefile --windowed --name "单价计算器" --add-data "template_manager.py;." --add-data "不能删除的数据文件.json;." "单价计算器.py"

if %errorlevel% equ 0 (
    echo.
    echo 打包成功！
    echo 可执行文件位于: dist\单价计算器.exe
    echo.
    echo 注意：程序在同一目录下使用 "不能删除的数据文件.json" 保存模板数据
    echo 请勿删除或重命名该文件，否则将使用默认设置
) else (
    echo.
    echo 打包失败，请检查错误信息
)

echo.
pause
