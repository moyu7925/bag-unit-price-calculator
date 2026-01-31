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
    url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=5&branch={BRANCH}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("workflow_runs"):
                return data["workflow_runs"][0]
    except Exception as e:
        print(f"  ⚠️ API请求失败: {e}")
    return None

def get_run_logs(run_id):
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/logs"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
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
    
    # 检测各种错误模式
    error_patterns = [
        ("aidl not found", "aidl"),
        ("build-tools.*not found", "build_tools"),
        ("platform-tools.*not found", "platform_tools"),
        ("license.*not accepted", "license"),
        ("sdkmanager.*does not exist", "sdkmanager"),
    ]
    
    for pattern, fix_type in error_patterns:
        if pattern in log_lower:
            return fix_type, f"Auto-fix: {fix_type} at {time.strftime('%Y-%m-%d %H:%M')}"
    
    return None, None

def apply_fix(fix_type):
    """应用修复"""
    print(f"  🔧 应用修复: {fix_type}")
    
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_applied = []
    
    if fix_type in ["aidl", "platform_tools"]:
        # 添加或增强 aidl 修复
        if "platform-tools-latest-linux.zip" not in content:
            fix_code = '''         
         # Verify and fix aidl
         if [ ! -f "$ANDROID_HOME/platform-tools/aidl" ]; then
           echo "aidl not found, downloading platform-tools separately..."
           cd /tmp
           rm -rf platform-tools platform-tools.zip
           wget -q https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O platform-tools.zip
           unzip -qo platform-tools.zip
           mkdir -p $ANDROID_HOME/platform-tools
           cp -rf platform-tools/* $ANDROID_HOME/platform-tools/
         fi
         
         # Verify aidl exists
         if [ -f "$ANDROID_HOME/platform-tools/aidl" ]; then
           echo "✓ aidl found at $ANDROID_HOME/platform-tools/aidl"
           $ANDROID_HOME/platform-tools/aidl --version
         else
           echo "✗ aidl still not found, trying alternative..."
           ls -la $ANDROID_HOME/build-tools/33.0.2/ | grep aidl || true
         fi'''
            
            if 'sdkmanager "platform-tools"' in content:
                content = content.replace(
                    'sdkmanager "platform-tools" "platforms;android-31" "build-tools;33.0.2"',
                    'sdkmanager "platform-tools" "platforms;android-31" "build-tools;33.0.2"' + fix_code
                )
                fixes_applied.append("added_aidl_fix")
    
    if fix_type == "build_tools":
        # 增强 build-tools 安装
        if "build-tools;33.0.2" in content:
            content = content.replace(
                'sdkmanager "platform-tools" "platforms;android-31" "build-tools;33.0.2"',
                'sdkmanager "platform-tools" "platforms;android-31" "build-tools;33.0.2" "build-tools;34.0.0"'
            )
            fixes_applied.append("added_build_tools_34")
    
    if fixes_applied:
        with open(WORKFLOW_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 应用了修复: {', '.join(fixes_applied)}")
        return True
    
    print("  ⚠️ 无需修复或无法应用")
    return False

def wait_for_new_run(current_run_id, timeout=120):
    """等待新的构建开始"""
    print(f"  ⏳ 等待新的构建...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        time.sleep(15)
        new_run = get_run_status()
        if new_run and new_run.get("id") != current_run_id:
            print(f"  ✅ 检测到新构建 #{new_run.get('id')}")
            return new_run
        print("  .", end="", flush=True)
    
    print("  ⚠️ 等待超时")
    return None

def monitor():
    print("=" * 60)
    print("🚀 开始自动监控构建状态")
    print(f"📦 仓库: {REPO}")
    print(f"🌿 分支: {BRANCH}")
    print("=" * 60)
    print("💡 按 Ctrl+C 停止监控")
    print("=" * 60)
    
    iteration = 0
    last_run_id = None
    
    try:
        while True:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"🔄 检查 #{iteration} | {time.strftime('%H:%M:%S')}")
            print(f"{'='*60}")
            
            run = get_run_status()
            if not run:
                print("  ⚠️ 无法获取状态，10秒后重试...")
                time.sleep(10)
                continue
            
            run_id = run.get("id", 0)
            status = run.get("status", "unknown")
            conclusion = run.get("conclusion", "unknown")
            
            print(f"  📊 状态: {status} | 结果: {conclusion}")
            print(f"  🔗 链接: {run.get('html_url', '')}")
            
            # 如果构建成功
            if conclusion == "success":
                print("\n" + "🎉" * 20)
                print("🎉 构建成功！")
                print("🎉" * 20)
                print(f"\n📦 APK下载地址:")
                print(f"   {run.get('html_url', '')}#artifacts")
                print("\n✅ 监控完成！")
                return True
            
            # 如果正在运行
            if status == "in_progress":
                print("  🔨 构建进行中...")
                last_run_id = run_id
                time.sleep(30)
                continue
            
            # 如果构建失败
            if conclusion == "failure" or status == "completed":
                # 如果是同一个构建，跳过
                if run_id == last_run_id:
                    print("  ⏭️ 同一个构建，跳过")
                    time.sleep(10)
                    continue
                
                print("  ❌ 构建失败，分析错误...")
                logs = get_run_logs(run_id)
                fix_type, msg = analyze_error(logs)
                
                if logs:
                    print(f"  📄 日志长度: {len(logs)} 字符")
                    # 显示最后几行
                    lines = logs.split('\n')
                    if len(lines) > 10:
                        print("\n  📋 最后日志:")
                        for line in lines[-10:]:
                            if line.strip():
                                print(f"     {line[:80]}")
                
                if fix_type:
                    print(f"\n  🔧 发现问题: {fix_type}")
                    
                    if apply_fix(fix_type):
                        print(f"\n  📤 推送修复...")
                        result = git_push(msg)
                        
                        if result[0] == 0:
                            print("  ✅ 修复已推送")
                            print("  ⏳ 等待构建启动...")
                            time.sleep(60)
                            last_run_id = run_id
                            continue
                        else:
                            print(f"  ❌ 推送失败: {result[2]}")
                    else:
                        print("  ⚠️ 无法应用修复")
                else:
                    print("  ⚠️ 无法识别的错误，需要手动处理")
                    # 显示关键错误行
                    if logs:
                        print("\n  🔍 关键错误:")
                        for line in logs.split('\n'):
                            if any(kw in line.lower() for kw in ['error', 'failed', 'cannot', 'unable']):
                                if line.strip() and len(line.strip()) > 10:
                                    print(f"     {line[:100]}")
                                    break
            
            # 等待后重新检查
            print(f"\n  ⏳ 20秒后重新检查...")
            time.sleep(20)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断监控")
        print("监控已停止")
        return False
    
    return False

if __name__ == "__main__":
    try:
        monitor()
    except Exception as e:
        print(f"\n❌ 监控出错: {e}")
        import traceback
        traceback.print_exc()
