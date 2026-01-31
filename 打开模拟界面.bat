@echo off
chcp 65001 > nul
echo ========================================
echo 单价计算器 - 移动端模拟界面
echo ========================================
echo.
echo 正在打开模拟界面...
echo.

start "" "%~dp0mobile\模拟界面.html"

echo 模拟界面已在浏览器中打开
echo.
echo 提示：
echo - 这是HTML模拟界面，用于预览移动端效果
echo - 可以在浏览器中测试所有功能
echo - 界面已针对移动端优化
echo.
pause
