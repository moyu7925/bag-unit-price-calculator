#!/usr/bin/env python3
"""
构建状态检查器 - 不需要GitHub Token
"""

import requests
import re
from datetime import datetime

def check_build_status():
    url = "https://github.com/moyu7925/bag-unit-price-calculator/actions"

    try:
        print("正在获取构建状态...")
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            html = response.text

            print("=" * 60)
            print("🔍 GitHub Actions 构建状态")
            print("=" * 60)
            print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🔗 链接: {url}")
            print("=" * 60)

            # 查找所有构建ID
            run_ids = re.findall(r'/actions/runs/(\d+)', html)
            if run_ids:
                latest_run_id = run_ids[0]
                print(f"\n📦 最新构建ID: {latest_run_id}")
                print(f"🔗 构建链接: https://github.com/moyu7925/bag-unit-price-calculator/actions/runs/{latest_run_id}")

                # 尝试多种方式检测状态
                status = "未知"

                # 方法1: 查找状态图标
                if "status-icon--success" in html or "color-fg-success" in html:
                    status = "✅ 成功"
                elif "status-icon--failure" in html or "color-fg-danger" in html:
                    status = "❌ 失败"
                elif "status-icon--in_progress" in html or "anim-rotate" in html:
                    status = "🔨 进行中"
                elif "status-icon--queued" in html:
                    status = "⏳ 排队中"

                # 方法2: 查找状态文本
                if status == "未知":
                    if "Succeeded" in html or "成功" in html:
                        status = "✅ 成功"
                    elif "Failed" in html or "失败" in html:
                        status = "❌ 失败"
                    elif "In progress" in html or "进行中" in html:
                        status = "🔨 进行中"
                    elif "Queued" in html or "排队" in html:
                        status = "⏳ 排队中"

                print(f"\n📊 构建状态: {status}")

                # 查找工作流名称
                workflow_match = re.search(r'Build Android APK', html)
                if workflow_match:
                    print(f"📋 工作流: Build Android APK")

                print("\n" + "=" * 60)
                print("💡 提示:")
                print("   - 点击链接查看详细日志")
                print("   - 构建成功后可在Artifacts中下载APK")
                print("=" * 60)

                return latest_run_id, status
            else:
                print("\n⚠️ 未找到构建记录")
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    return None, "未知"

if __name__ == "__main__":
    run_id, status = check_build_status()
    print(f"\n构建ID: {run_id}")
    print(f"状态: {status}")
