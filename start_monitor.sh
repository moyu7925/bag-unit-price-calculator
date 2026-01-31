#!/bin/bash
# Linux/Mac启动脚本 - 自动监控和修复GitHub Actions构建

echo "============================================================"
echo "GitHub Actions 自动监控和修复工具"
echo "============================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

# 检查是否设置了GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    echo "[警告] 未设置GITHUB_TOKEN环境变量"
    echo ""
    echo "请设置GitHub Token以访问API："
    echo "  export GITHUB_TOKEN=your_token_here"
    echo ""
    echo "或者创建 .env 文件并添加："
    echo "  GITHUB_TOKEN=your_token_here"
    echo ""
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 加载.env文件（如果存在）
if [ -f .env ]; then
    echo "[信息] 加载.env文件..."
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "[信息] 启动监控..."
echo ""

# 启动监控脚本
python3 build_monitor.py "$@"

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 监控脚本执行失败"
    exit 1
fi

echo ""
echo "[完成] 监控已停止"
