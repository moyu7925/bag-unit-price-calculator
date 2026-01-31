@echo off
REM 快速检查构建状态

echo ============================================================
echo 快速构建状态检查
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python
    pause
    exit /b 1
)

REM 检查命令行参数
if "%1"=="" (
    echo 用法: check_build.bat [选项]
    echo.
    echo 选项:
    echo   latest         检查最新构建
    echo   success        检查最新成功构建
    echo   failed         检查最新失败构建
    echo   run-id [ID]    检查指定构建ID
    echo.
    echo 示例:
    echo   check_build.bat latest
    echo   check_build.bat failed
    echo   check_build.bat run-id 123456
    echo.
    pause
    exit /b 0
)

REM 执行检查
if "%1"=="latest" (
    python build_status_checker.py --latest
) else if "%1"=="success" (
    python build_status_checker.py --latest-success
) else if "%1"=="failed" (
    python build_status_checker.py --latest-failed --show-logs
) else if "%1"=="run-id" (
    if "%2"=="" (
        echo [错误] 请指定构建ID
        pause
        exit /b 1
    )
    python build_status_checker.py --run-id %2
) else (
    echo [错误] 未知选项: %1
    pause
    exit /b 1
)

if errorlevel 1 (
    echo.
    echo [错误] 检查失败
    pause
    exit /b 1
)

echo.
pause
