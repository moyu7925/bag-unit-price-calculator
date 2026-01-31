#!/usr/bin/env python3
"""
持续监控GitHub Actions，自动修复错误直到成功
"""

import os
import time
import subprocess
import requests
import sys

REPO = "moyu7925/bag-unit-price-calculator"
BRANCH = "main"
WORKFLOW_FILE = ".github/workflows/android.yml"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def git_push(message):
    run_cmd('git add .')
    run_cmd(f'git commit -m "{message}"')
    return run_cmd("git push origin main")

def get_run_status():
    url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=1&branch={BRANCH}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if data.get("workflow_runs"):
                return data["workflow_runs"][0]
    except Exception as e:
        print(f"Error: {e}")
    return None

def get_run_logs(run_id):
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/logs"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return None

def analyze_error(logs):
    """分析错误并返回修复方案"""
    if not logs:
        return None, None
    
    log_lower = logs.lower()
    
    if "aidl not found" in log_lower:
        return "aidl", "Auto-fix: download platform-tools for aidl"
    
    return None, None

def apply_fix(fix_type):
    """应用修复"""
    with open(WORKFLOW_FILE, 'r') as f:
        content = f.read()
    
    if fix_type == "aidl":
        if "platform-tools-latest-linux.zip" in content:
            return False  # 已修复
        
        fix = '''         
         # Verify and fix aidl
         if [ ! -f "$ANDROID_HOME/platform-tools/aidl" ]; then
           echo "aidl not found, downloading platform-tools separately..."
           cd /tmp
           wget -q https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O platform-tools.zip
           unzip -qo platform-tools.zip
           cp -r platform-tools/* $ANDROID_HOME/platform-tools/
         fi'''
        
        if 'sdkmanager "platform-tools"' in content:
            content = content.replace(
                'sdkmanager "platform-tools" "platforms;android-31" "build-tools;33.0.2"',
                'sdkmanager "platform-tools" "platforms;android-31" "build-tools;33.0.2"' + fix
            )
            with open(WORKFLOW_FILE, 'w') as f:
                f.write(content)
            return True
    
    return False

def monitor():
    print("=" * 60)
    print("🚀 开始自动监控构建状态")
    print(f"📦 仓库: {REPO}")
    print(f"🌿 分支: {BRANCH}")
    print("=" * 60)
    
    iteration = 0
    max_iterations = 30
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 检查 #{iteration}/{max_iterations}")
        
        run = get_run_status()
        if not run:
            print("  ⚠️ 无法获取状态，等待...")
            time.sleep(30)
            continue
        
        status = run.get("status", "unknown")
        conclusion = run.get("conclusion", "unknown")
        run_id = run.get("id", 0)
        
        print(f"  📊 状态: {status} | 结果: {conclusion}")
        
        if conclusion == "success":
            print("\n" + "=" * 60)
            print("🎉 构建成功！")
            print(f"📦 APK下载: {run.get('html_url', '')}/artifacts")
            print("=" * 60)
            return True
        
        if conclusion == "failure":
            print("  ❌ 构建失败，分析错误...")
            logs = get_run_logs(run_id)
            fix_type, msg = analyze_error(logs)
            
            if fix_type:
                print(f"  🔧 发现问题: {fix_type}")
                
                if apply_fix(fix_type):
                    print("  📤 推送修复...")
                    if git_push(msg)[0] == 0:
                        print("  ✅ 修复已推送，等待新构建...")
                        time.sleep(45)  # 等待构建启动
                        continue
                else:
                    print("  ⚠️ 修复已存在或无法应用")
            else:
                print("  ⚠️ 无法自动修复，请查看日志")
        
        # 等待
        print("  ⏳ 等待 30 秒后重新检查...")
        time.sleep(30)
    
    print(f"\n❌ 达到最大迭代次数，构建仍未成功")
    return False

if __name__ == "__main__":
    monitor()
