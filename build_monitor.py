#!/usr/bin/env python3
"""
GitHub Actions 自动监控和修复工具
Automated monitoring and fixing tool for GitHub Actions
"""

import os
import sys
import time
import json
import subprocess
import requests
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import re

class BuildMonitor:
    def __init__(self, config_file: str = "build_monitor_config.json"):
        self.config = self.load_config(config_file)
        self.repo_owner = self.config.get("repo_owner", "moyu7925")
        self.repo_name = self.config.get("repo_name", "bag-unit-price-calculator")
        self.branch = self.config.get("branch", "main")
        self.workflow_file = self.config.get("workflow_file", ".github/workflows/android.yml")
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        self.max_iterations = self.config.get("max_iterations", 30)
        self.check_interval = self.config.get("check_interval", 30)
        self.last_run_id = None
        self.fix_history = []

    def load_config(self, config_file: str) -> Dict:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 无法加载配置文件: {e}")
        return {}

    def run_command(self, cmd: str, cwd: Optional[str] = None) -> Tuple[int, str, str]:
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=cwd,
                capture_output=True, text=True, timeout=120
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout"
        except Exception as e:
            return -1, "", str(e)

    def git_commit_and_push(self, message: str) -> bool:
        print(f"📝 提交更改: {message}")
        
        self.run_command("git add .")
        self.run_command(f'git commit -m "{message}"')
        code, out, err = self.run_command("git push origin main")
        
        if code == 0:
            print("✅ 推送成功")
            return True
        else:
            print(f"❌ 推送失败: {err}")
            return False

    def get_latest_workflow_run(self) -> Optional[Dict]:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs?per_page=3&branch={self.branch}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("workflow_runs"):
                    return data["workflow_runs"][0]
        except Exception as e:
            print(f"❌ 获取工作流状态失败: {e}")
        return None

    def get_workflow_run_logs(self, run_id: int) -> Optional[str]:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}/logs"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        try:
            response = requests.get(url, headers=headers, timeout=60)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"❌ 获取日志失败: {e}")
        return None

    def get_workflow_jobs(self, run_id: int) -> Optional[List[Dict]]:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}/jobs"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("jobs", [])
        except Exception as e:
            print(f"❌ 获取Jobs失败: {e}")
        return None

    def analyze_error(self, logs: str, jobs: Optional[List[Dict]] = None) -> Optional[str]:
        if not logs:
            return None
        
        log_lower = logs.lower()
        
        error_patterns = [
            ("aidl not found|aidl.*does not exist|cannot find aidl", "fix_aidl"),
            ("sdkmanager.*not found|sdkmanager.*does not exist", "fix_sdkmanager"),
            ("license.*not accepted|license.*rejected", "fix_license"),
            ("build-tools.*not found|cannot find build-tools", "fix_build_tools"),
            ("platform-tools.*not found|cannot find platform-tools", "fix_platform_tools"),
            ("ndk.*not found|cannot find ndk", "fix_ndk"),
            ("timeout|timed out", "fix_timeout"),
            ("memory.*exceeded|out of memory", "fix_memory"),
            ("disk.*space|no space left", "fix_disk"),
        ]
        
        for pattern, fix_type in error_patterns:
            if re.search(pattern, log_lower):
                return fix_type
        
        if jobs:
            for job in jobs:
                if job.get("conclusion") == "failure":
                    steps = job.get("steps", [])
                    for step in steps:
                        if step.get("conclusion") == "failure":
                            step_name = step.get("name", "").lower()
                            if "build" in step_name or "buildozer" in step_name:
                                return "fix_buildozer"
        
        return None

    def apply_fix(self, fix_type: str) -> bool:
        print(f"🔧 应用修复: {fix_type}")
        
        with open(self.workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        applied_fixes = []
        
        if fix_type == "fix_aidl":
            if "platform-tools-latest-linux.zip" not in content:
                fix_code = '''         
         if [ ! -f "$ANDROID_HOME/platform-tools/aidl" ]; then
           echo "aidl not found, downloading platform-tools..."
           cd /tmp
           rm -rf platform-tools platform-tools.zip
           wget -q --tries=3 --timeout=30 https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O platform-tools.zip
           unzip -q -o platform-tools.zip
           mkdir -p $ANDROID_HOME/platform-tools
           cp -rf platform-tools/* $ANDROID_HOME/platform-tools/
           chmod +x $ANDROID_HOME/platform-tools/aidl
         fi
         
         if [ -f "$ANDROID_HOME/platform-tools/aidl" ]; then
           echo "✓ aidl found"
           $ANDROID_HOME/platform-tools/aidl --version || true
         fi
'''
                if "Install Android SDK components" in content:
                    content = content.replace(
                        'sdkmanager --install "build-tools;34.0.0" || true',
                        'sdkmanager --install "build-tools;34.0.0" || true' + fix_code
                    )
                    applied_fixes.append("aidl_fix")
        
        elif fix_type == "fix_sdkmanager":
            if "commandlinetools-linux-11076708_latest.zip" not in content:
                fix_code = '''         
         mkdir -p $ANDROID_HOME/cmdline-tools
         cd /tmp
         if [ ! -f "cmdline-tools.zip" ]; then
           wget -q --tries=3 --timeout=30 https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdline-tools.zip
         fi
         unzip -q -o cmdline-tools.zip
         rm -rf $ANDROID_HOME/cmdline-tools/latest
         mv cmdline-tools $ANDROID_HOME/cmdline-tools/latest
         chmod +x $ANDROID_HOME/cmdline-tools/latest/bin/*
'''
                if "Setup Android SDK" in content:
                    content = content.replace(
                        'mkdir -p $ANDROID_HOME/cmdline-tools',
                        fix_code
                    )
                    applied_fixes.append("sdkmanager_fix")
        
        elif fix_type == "fix_license":
            if "d56f5187479451eabf01fb78af6dfcb131a6481e" not in content:
                license_fix = '''        echo "d56f5187479451eabf01fb78af6dfcb131a6481e" > ~/.android/google-android-ndk-license
'''
                if "android-sdk-preview-license" in content:
                    content = content.replace(
                        'echo "84831b9409646a918e30573bab4c9c91346d8abd" > ~/.android/android-sdk-preview-license',
                        'echo "84831b9409646a918e30573bab4c9c91346d8abd" > ~/.android/android-sdk-preview-license\n' + license_fix
                    )
                    applied_fixes.append("license_fix")
        
        elif fix_type == "fix_build_tools":
            if "build-tools;34.0.0" not in content:
                content = content.replace(
                    'sdkmanager --install "build-tools;33.0.2" || true',
                    'sdkmanager --install "build-tools;33.0.2" || true\n        sdkmanager --install "build-tools;34.0.0" || true'
                )
                applied_fixes.append("build_tools_fix")
        
        elif fix_type == "fix_platform_tools":
            if "platform-tools" not in content:
                content = content.replace(
                    'yes | sdkmanager --licenses || true',
                    'yes | sdkmanager --licenses || true\n        sdkmanager --install "platform-tools" || true'
                )
                applied_fixes.append("platform_tools_fix")
        
        elif fix_type == "fix_timeout":
            if "timeout-minutes: 60" in content:
                content = content.replace(
                    "timeout-minutes: 60",
                    "timeout-minutes: 90"
                )
                applied_fixes.append("timeout_fix")
        
        elif fix_type == "fix_buildozer":
            if "MAX_RETRIES: 2" in content:
                content = content.replace(
                    "MAX_RETRIES: 2",
                    "MAX_RETRIES: 3"
                )
                applied_fixes.append("retry_fix")
        
        if applied_fixes and content != original_content:
            with open(self.workflow_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 应用了修复: {', '.join(applied_fixes)}")
            self.fix_history.append({
                "type": fix_type,
                "fixes": applied_fixes,
                "time": datetime.now().isoformat()
            })
            return True
        
        print("⚠️ 无需修复或无法应用")
        return False

    def wait_for_new_run(self, current_run_id: int, timeout: int = 180) -> Optional[Dict]:
        print(f"⏳ 等待新的构建...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            time.sleep(15)
            new_run = self.get_latest_workflow_run()
            if new_run and new_run.get("id") != current_run_id:
                print(f"✅ 检测到新构建 #{new_run.get('id')}")
                return new_run
            print(".", end="", flush=True)
        
        print("\n⚠️ 等待超时")
        return None

    def display_run_info(self, run: Dict):
        run_id = run.get("id", 0)
        status = run.get("status", "unknown")
        conclusion = run.get("conclusion", "unknown")
        created_at = run.get("created_at", "")
        html_url = run.get("html_url", "")
        
        print(f"\n{'='*60}")
        print(f"📊 构建信息")
        print(f"{'='*60}")
        print(f"ID: {run_id}")
        print(f"状态: {status}")
        print(f"结果: {conclusion}")
        print(f"时间: {created_at}")
        print(f"链接: {html_url}")

    def monitor(self) -> bool:
        print("=" * 60)
        print("🚀 GitHub Actions 自动监控和修复工具")
        print("=" * 60)
        print(f"📦 仓库: {self.repo_owner}/{self.repo_name}")
        print(f"🌿 分支: {self.branch}")
        print(f"📄 工作流: {self.workflow_file}")
        print(f"🔄 最大迭代: {self.max_iterations}")
        print(f"⏱️ 检查间隔: {self.check_interval}秒")
        print("=" * 60)
        print("💡 按 Ctrl+C 停止监控")
        print("=" * 60)
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'='*60}")
            print(f"🔄 检查 #{iteration}/{self.max_iterations} | {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*60}")
            
            run = self.get_latest_workflow_run()
            
            if not run:
                print("⚠️ 无法获取状态，等待后重试...")
                time.sleep(self.check_interval)
                continue
            
            self.display_run_info(run)
            
            run_id = run.get("id", 0)
            status = run.get("status", "unknown")
            conclusion = run.get("conclusion", "unknown")
            
            if conclusion == "success":
                print("\n" + "🎉" * 20)
                print("🎉 构建成功！")
                print("🎉" * 20)
                print(f"\n📦 APK下载地址:")
                print(f"   {run.get('html_url', '')}#artifacts")
                print(f"\n✅ 修复历史:")
                for fix in self.fix_history:
                    print(f"   - {fix['type']}: {', '.join(fix['fixes'])} ({fix['time']})")
                print("\n✅ 监控完成！")
                return True
            
            if status == "in_progress" or status == "queued":
                print("🔨 构建进行中...")
                self.last_run_id = run_id
                time.sleep(self.check_interval)
                continue
            
            if conclusion == "failure" or status == "completed":
                if run_id == self.last_run_id:
                    print("⏭️ 同一个构建，跳过")
                    time.sleep(self.check_interval)
                    continue
                
                print("❌ 构建失败，分析错误...")
                
                jobs = self.get_workflow_jobs(run_id)
                logs = self.get_workflow_run_logs(run_id)
                fix_type = self.analyze_error(logs, jobs)
                
                if jobs:
                    print(f"\n📋 Jobs信息:")
                    for job in jobs:
                        job_name = job.get("name", "")
                        job_status = job.get("status", "")
                        job_conclusion = job.get("conclusion", "")
                        print(f"   {job_name}: {job_status} ({job_conclusion})")
                        
                        if job_conclusion == "failure":
                            steps = job.get("steps", [])
                            for step in steps:
                                if step.get("conclusion") == "failure":
                                    print(f"     ❌ 失败步骤: {step.get('name')}")
                
                if logs:
                    log_lines = logs.split('\n')
                    print(f"\n📄 日志长度: {len(log_lines)} 行")
                    
                    error_lines = []
                    for i, line in enumerate(log_lines[-100:]):
                        if any(kw in line.lower() for kw in ['error', 'failed', 'cannot', 'unable', 'exception']):
                            if line.strip() and len(line.strip()) > 10:
                                error_lines.append(line.strip())
                    
                    if error_lines:
                        print(f"\n🔍 关键错误信息:")
                        for line in error_lines[-5:]:
                            print(f"   {line[:100]}")
                
                if fix_type:
                    print(f"\n🔧 发现问题类型: {fix_type}")
                    
                    if self.apply_fix(fix_type):
                        msg = f"Auto-fix: {fix_type} at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        print(f"\n📤 推送修复...")
                        
                        if self.git_commit_and_push(msg):
                            print("⏳ 等待新构建启动...")
                            time.sleep(60)
                            self.last_run_id = run_id
                            continue
                        else:
                            print("❌ 推送失败，无法继续")
                            return False
                    else:
                        print("⚠️ 无法应用修复")
                else:
                    print("⚠️ 无法识别的错误，需要手动处理")
                    print("💡 提示: 查看完整日志以获取更多信息")
                    print(f"   {run.get('html_url', '')}")
                    return False
            
            print(f"\n⏳ {self.check_interval}秒后重新检查...")
            time.sleep(self.check_interval)
        
        print(f"\n❌ 已达到最大迭代次数 ({self.max_iterations})，构建仍未成功")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Actions 自动监控和修复工具")
    parser.add_argument("--config", default="build_monitor_config.json", help="配置文件路径")
    parser.add_argument("--max-iterations", type=int, help="最大迭代次数")
    parser.add_argument("--check-interval", type=int, help="检查间隔（秒）")
    
    args = parser.parse_args()
    
    monitor = BuildMonitor(args.config)
    
    if args.max_iterations:
        monitor.max_iterations = args.max_iterations
    if args.check_interval:
        monitor.check_interval = args.check_interval
    
    try:
        success = monitor.monitor()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断监控")
        print("监控已停止")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 监控出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
