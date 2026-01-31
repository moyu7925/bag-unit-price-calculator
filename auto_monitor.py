#!/usr/bin/env python3
"""
Auto Monitor and Fix GitHub Actions Build Script
自动监控和修复GitHub Actions构建脚本
"""

import os
import time
import subprocess
import requests
import sys
from datetime import datetime

# 配置
REPO_OWNER = "moyu7925"
REPO_NAME = "bag-unit-price-calculator"
WORKFLOW_FILE = ".github/workflows/android.yml"
BRANCH = "main"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 错误模式和处理方案
ERROR_PATTERNS = {
    "Aidl not found": "fix_aidl",
    "sdkmanager does not exist": "fix_sdkmanager",
    "license.*not accepted": "fix_license",
    "build-tools.*not found": "fix_build_tools",
    "platform-tools.*not found": "fix_platform_tools",
}

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def git_commit_and_push(message):
    """Git提交并推送"""
    print(f"📝 提交更改: {message}")
    run_command(f'git add .')
    run_command(f'git commit -m "{message}"')
    return run_command("git push origin main")

def get_latest_workflow_run():
    """获取最新的工作流运行"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs?per_page=1"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("workflow_runs"):
                return data["workflow_runs"][0]
    except Exception as e:
        print(f"❌ 获取工作流状态失败: {e}")
    return None

def get_workflow_run_logs(run_id):
    """获取工作流日志"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/logs"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"❌ 获取日志失败: {e}")
    return None

def parse_error(logs):
    """解析错误信息"""
    if not logs:
        return None
    
    errors = []
    lines = logs.split('\n')
    
    for line in lines:
        for pattern in ERROR_PATTERNS.keys():
            if pattern.lower() in line.lower():
                errors.append((line.strip(), pattern))
                break
    
    return errors if errors else None

def fix_aidl():
    """修复aidl问题"""
    print("🔧 修复aidl问题...")
    
    with open(WORKFLOW_FILE, 'r') as f:
        content = f.read()
    
    # 检查是否已经有修复aidl的步骤
    if "platform-tools-latest-linux.zip" in content:
        print("  ✓ aidl修复步骤已存在")
        return False
    
    # 添加修复步骤
    fix_code = '''         
         # Verify and fix aidl
         if [ ! -f "$ANDROID_HOME/platform-tools/aidl" ]; then
           echo "aidl not found, downloading platform-tools separately..."
           cd /tmp
           wget -q https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O platform-tools.zip
           unzip -qo platform-tools.zip
           cp -r platform-tools/* $ANDROID_HOME/platform-tools/
         fi
         
         # Verify aidl exists
         if [ -f "$ANDROID_HOME/platform-tools/aidl" ]; then
           echo "✓ aidl found at $ANDROID_HOME/platform-tools/aidl"
           $ANDROID_HOME/platform-tools/aidl --version
         else
           echo "✗ aidl still not found, listing available files:"
           find $ANDROID_HOME -name "aidl" -type f 2>/dev/null
           ls -la $ANDROID_HOME/platform-tools/
         fi
'''
    
    # 在sdkmanager命令后添加修复代码
    if 'sdkmanager "platform-tools"' in content:
        content = content.replace(
            'sdkmanager "platform-tools" "platforms;android-31" "build-tools;33.0.2"',
            'sdkmanager "platform-tools" "platforms;android-31" "build-tools;33.0.2"' + fix_code
        )
        with open(WORKFLOW_FILE, 'w') as f:
            f.write(content)
        return True
    
    return False

def monitor_and_fix(max_iterations=20, wait_seconds=30):
    """监控并自动修复"""
    print("🚀 开始自动监控和修复GitHub Actions构建...")
    print(f"📊 仓库: {REPO_OWNER}/{REPO_NAME}")
    print(f"🌿 分支: {BRANCH}")
    print("-" * 50)
    
    for iteration in range(max_iterations):
        print(f"\n{'='*50}")
        print(f"🔄 第 {iteration + 1}/{max_iterations} 次检查")
        print(f"{'='*50}")
        
        # 获取最新工作流状态
        run = get_latest_workflow_run()
        
        if not run:
            print("❌ 无法获取工作流状态")
            time.sleep(wait_seconds)
            continue
        
        status = run.get("status", "unknown")
        conclusion = run.get("conclusion", "unknown")
        run_id = run.get("id", 0)
        
        print(f"📌 状态: {status}")
        print(f"📋 结果: {conclusion}")
        print(f"🔗 链接: {run.get('html_url', '')}")
        
        # 如果构建成功
        if conclusion == "success":
            print("\n🎉 构建成功！")
            artifacts_url = run.get("artifacts_url", "")
            if artifacts_url:
                print(f"📦 下载地址: {artifacts_url}")
            return True
        
        # 如果构建失败，分析错误
        if conclusion == "failure":
            print("\n❌ 构建失败，分析错误...")
            logs = get_workflow_run_logs(run_id)
            errors = parse_error(logs)
            
            if errors:
                print(f"发现 {len(errors)} 个错误:")
                for i, (error_line, pattern) in enumerate(errors, 1):
                    print(f"  {i}. {error_line}")
                
                # 根据错误类型修复
                fixed = False
                for error_line, pattern in errors:
                    fix_func = ERROR_PATTERNS.get(pattern)
                    if fix_func and globals().get(fix_func):
                        if globals()[fix_func]():
                            print(f"  ✓ 已应用修复: {fix_func}")
                            fixed = True
                
                if fixed:
                    print("\n📤 推送修复...")
                    if git_commit_and_push(f"Auto-fix: {pattern} at {datetime.now().strftime('%Y-%m-%d %H:%M')}"):
                        print("  ✓ 修复已推送，等待新构建...")
                        time.sleep(wait_seconds * 2)  # 等待构建启动
                        continue
            else:
                print("  ⚠️ 无法解析错误，请手动检查")
        
        # 等待后重新检查
        print(f"\n⏳ 等待 {wait_seconds} 秒后重新检查...")
        time.sleep(wait_seconds)
    
    print(f"\n❌ 已达到最大迭代次数 ({max_iterations})，构建仍未成功")
    return False

if __name__ == "__main__":
    print("📦 自动监控和修复GitHub Actions构建工具")
    print("=" * 50)
    
    # 运行监控
    success = monitor_and_fix(
        max_iterations=int(sys.argv[1]) if len(sys.argv) > 1 else 20,
        wait_seconds=int(sys.argv[2]) if len(sys.argv) > 2 else 30
    )
    
    sys.exit(0 if success else 1)
