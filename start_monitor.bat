@echo off
REM Windows启动脚本 - 自动监控和修复GitHub Actions构建

echo ============================================================
echo GitHub Actions 自动监控和修复工具
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查是否设置了GITHUB_TOKEN
if "%GITHUB_TOKEN%"=="" (
    echo [警告] 未设置GITHUB_TOKEN环境变量
    echo.
    echo 请设置GitHub Token以访问API：
    echo   set GITHUB_TOKEN=your_token_here
    echo.
    echo 或者创建 .env 文件并添加：
    echo   GITHUB_TOKEN=your_token_here
    echo.
    set /p CONTINUE="是否继续？(y/n): "
    if /i not "%CONTINUE%"=="y" (
        exit /b 0
    )
)

echo [信息] 启动监控...
echo.

REM 启动监控脚本
python build_monitor.py

if errorlevel 1 (
    echo.
    echo [错误] 监控脚本执行失败
    pause
    exit /b 1
)

echo.
echo [完成] 监控已停止
pause
