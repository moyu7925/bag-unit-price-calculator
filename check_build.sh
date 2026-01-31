#!/bin/bash
# 快速检查构建状态

echo "============================================================"
echo "快速构建状态检查"
echo "============================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python"
    exit 1
fi

# 检查命令行参数
if [ $# -eq 0 ]; then
    echo "用法: ./check_build.sh [选项]"
    echo ""
    echo "选项:"
    echo "  latest         检查最新构建"
    echo "  success        检查最新成功构建"
    echo "  failed         检查最新失败构建"
    echo "  run-id [ID]    检查指定构建ID"
    echo ""
    echo "示例:"
    echo "  ./check_build.sh latest"
    echo "  ./check_build.sh failed"
    echo "  ./check_build.sh run-id 123456"
    echo ""
    exit 0
fi

# 执行检查
case "$1" in
    latest)
        python3 build_status_checker.py --latest
        ;;
    success)
        python3 build_status_checker.py --latest-success
        ;;
    failed)
        python3 build_status_checker.py --latest-failed --show-logs
        ;;
    run-id)
        if [ -z "$2" ]; then
            echo "[错误] 请指定构建ID"
            exit 1
        fi
        python3 build_status_checker.py --run-id "$2"
        ;;
    *)
        echo "[错误] 未知选项: $1"
        exit 1
        ;;
esac

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 检查失败"
    exit 1
fi

echo ""
