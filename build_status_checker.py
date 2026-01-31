#!/usr/bin/env python3
"""
构建状态检查和错误分析工具
Build status checker and error analyzer
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import re

class BuildStatusChecker:
    def __init__(self, repo_owner: str = "moyu7925", repo_name: str = "bag-unit-price-calculator"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = os.environ.get("GITHUB_TOKEN", "")

    def make_request(self, url: str) -> Optional[Dict]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None

    def get_workflow_runs(self, limit: int = 10) -> Optional[List[Dict]]:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs?per_page={limit}"
        data = self.make_request(url)
        if data:
            return data.get("workflow_runs", [])
        return None

    def get_workflow_run(self, run_id: int) -> Optional[Dict]:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}"
        return self.make_request(url)

    def get_workflow_jobs(self, run_id: int) -> Optional[List[Dict]]:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}/jobs"
        data = self.make_request(url)
        if data:
            return data.get("jobs", [])
        return None

    def get_job_logs(self, job_id: int) -> Optional[str]:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/jobs/{job_id}/logs"
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

    def analyze_job_failure(self, job: Dict) -> Dict:
        result = {
            "job_name": job.get("name", ""),
            "status": job.get("status", ""),
            "conclusion": job.get("conclusion", ""),
            "failed_steps": [],
            "error_patterns": [],
            "suggestions": []
        }
        
        steps = job.get("steps", [])
        for step in steps:
            if step.get("conclusion") == "failure":
                step_info = {
                    "name": step.get("name", ""),
                    "number": step.get("number", 0),
                    "started_at": step.get("started_at", ""),
                    "completed_at": step.get("completed_at", "")
                }
                result["failed_steps"].append(step_info)
        
        return result

    def detect_error_patterns(self, logs: str) -> List[str]:
        if not logs:
            return []
        
        patterns = [
            ("aidl.*not found|aidl.*does not exist", "AIDL工具缺失"),
            ("sdkmanager.*not found|sdkmanager.*does not exist", "SDK Manager缺失"),
            ("license.*not accepted|license.*rejected", "许可证未接受"),
            ("build-tools.*not found", "Build Tools缺失"),
            ("platform-tools.*not found", "Platform Tools缺失"),
            ("ndk.*not found", "NDK缺失"),
            ("timeout|timed out", "构建超时"),
            ("memory.*exceeded|out of memory", "内存不足"),
            ("disk.*space|no space left", "磁盘空间不足"),
            ("connection.*refused|network.*error", "网络连接错误"),
            ("permission.*denied|access.*denied", "权限错误"),
            ("buildozer.*error", "Buildozer错误"),
            ("gradle.*error", "Gradle错误"),
            ("compilation.*error|compile.*error", "编译错误"),
            ("dependency.*error|dependencies.*error", "依赖错误"),
        ]
        
        detected = []
        log_lower = logs.lower()
        
        for pattern, description in patterns:
            if re.search(pattern, log_lower):
                detected.append(description)
        
        return detected

    def get_fix_suggestions(self, error_patterns: List[str]) -> List[str]:
        suggestions = []
        
        pattern_map = {
            "AIDL工具缺失": [
                "检查工作流中的Android SDK安装步骤",
                "确保platform-tools正确安装",
                "添加aidl修复步骤"
            ],
            "SDK Manager缺失": [
                "验证cmdline-tools下载和安装",
                "检查ANDROID_HOME环境变量",
                "确保sdkmanager路径正确"
            ],
            "许可证未接受": [
                "添加所有必要的许可证接受步骤",
                "包括android-sdk-license, android-sdk-preview-license, google-android-ndk-license"
            ],
            "Build Tools缺失": [
                "安装多个版本的build-tools",
                "确保build-tools版本与Android API匹配"
            ],
            "Platform Tools缺失": [
                "单独下载platform-tools",
                "验证platform-tools目录结构"
            ],
            "NDK缺失": [
                "安装指定版本的NDK",
                "检查NDK版本兼容性"
            ],
            "构建超时": [
                "增加timeout-minutes",
                "优化构建步骤",
                "使用缓存减少下载时间"
            ],
            "内存不足": [
                "增加GitHub Actions runner内存",
                "优化构建配置",
                "分阶段构建"
            ],
            "磁盘空间不足": [
                "清理临时文件",
                "减少构建产物",
                "使用缓存策略"
            ],
            "网络连接错误": [
                "增加下载重试次数",
                "使用镜像源",
                "添加超时处理"
            ],
            "权限错误": [
                "检查文件权限",
                "确保sudo使用正确",
                "验证目录权限"
            ],
            "Buildozer错误": [
                "检查buildozer.spec配置",
                "验证Python依赖",
                "清理buildozer缓存"
            ],
            "Gradle错误": [
                "检查gradle配置",
                "验证依赖版本",
                "清理gradle缓存"
            ],
            "编译错误": [
                "检查源代码语法",
                "验证依赖兼容性",
                "查看详细编译日志"
            ],
            "依赖错误": [
                "更新依赖版本",
                "检查requirements.txt",
                "验证依赖冲突"
            ]
        }
        
        for pattern in error_patterns:
            if pattern in pattern_map:
                suggestions.extend(pattern_map[pattern])
        
        return list(set(suggestions))

    def display_run_summary(self, run: Dict):
        print("\n" + "=" * 60)
        print("📊 构建运行摘要")
        print("=" * 60)
        print(f"ID: {run.get('id', 0)}")
        print(f"名称: {run.get('name', '')}")
        print(f"状态: {run.get('status', 'unknown')}")
        print(f"结果: {run.get('conclusion', 'unknown')}")
        print(f"分支: {run.get('head_branch', '')}")
        print(f"提交: {run.get('head_sha', '')[:7]}")
        print(f"触发者: {run.get('triggering_actor', '')}")
        print(f"开始时间: {run.get('created_at', '')}")
        print(f"结束时间: {run.get('updated_at', '')}")
        print(f"持续时间: {run.get('run_duration', 0)}秒")
        print(f"链接: {run.get('html_url', '')}")
        print("=" * 60)

    def display_job_details(self, job: Dict, show_logs: bool = False):
        print(f"\n📋 Job: {job.get('name', '')}")
        print(f"   状态: {job.get('status', '')}")
        print(f"   结果: {job.get('conclusion', '')}")
        print(f"   开始: {job.get('started_at', '')}")
        print(f"   结束: {job.get('completed_at', '')}")
        
        steps = job.get("steps", [])
        print(f"   步骤数: {len(steps)}")
        
        for step in steps:
            status = step.get("conclusion", step.get("status", ""))
            icon = "✅" if status == "success" else "❌" if status == "failure" else "⏳"
            print(f"     {icon} {step.get('name', '')}: {status}")
        
        if show_logs and job.get("conclusion") == "failure":
            logs = self.get_job_logs(job.get("id", 0))
            if logs:
                print(f"\n   📄 日志摘要 (最后50行):")
                log_lines = logs.split('\n')
                for line in log_lines[-50:]:
                    if line.strip():
                        print(f"     {line[:100]}")

    def check_build_status(self, run_id: Optional[int] = None) -> bool:
        if run_id:
            run = self.get_workflow_run(run_id)
            if not run:
                print(f"❌ 无法找到构建 #{run_id}")
                return False
            runs = [run]
        else:
            runs = self.get_workflow_runs(5)
            if not runs:
                print("❌ 无法获取构建列表")
                return False
        
        print("\n" + "🔍" * 30)
        print("🔍 构建状态检查")
        print("🔍" * 30)
        
        all_success = True
        
        for i, run in enumerate(runs, 1):
            print(f"\n--- 构建 #{i} ---")
            self.display_run_summary(run)
            
            run_id = run.get("id", 0)
            conclusion = run.get("conclusion", "unknown")
            
            if conclusion == "success":
                print("✅ 构建成功")
            elif conclusion == "failure":
                print("❌ 构建失败")
                all_success = False
                
                jobs = self.get_workflow_jobs(run_id)
                if jobs:
                    print(f"\n📋 Jobs详情:")
                    for job in jobs:
                        if job.get("conclusion") == "failure":
                            print(f"\n❌ 失败的Job:")
                            self.display_job_details(job)
                            
                            failure_info = self.analyze_job_failure(job)
                            print(f"\n🔍 失败分析:")
                            print(f"   失败步骤数: {len(failure_info['failed_steps'])}")
                            
                            for step in failure_info['failed_steps']:
                                print(f"     - {step['name']} (步骤 {step['number']})")
                            
                            logs = self.get_job_logs(job.get("id", 0))
                            if logs:
                                error_patterns = self.detect_error_patterns(logs)
                                if error_patterns:
                                    print(f"\n⚠️ 检测到错误模式:")
                                    for pattern in error_patterns:
                                        print(f"     - {pattern}")
                                    
                                    suggestions = self.get_fix_suggestions(error_patterns)
                                    if suggestions:
                                        print(f"\n💡 修复建议:")
                                        for suggestion in suggestions:
                                            print(f"     • {suggestion}")
            else:
                print(f"⏳ 构建状态: {conclusion}")
        
        return all_success

    def get_latest_successful_run(self) -> Optional[Dict]:
        runs = self.get_workflow_runs(20)
        if not runs:
            return None
        
        for run in runs:
            if run.get("conclusion") == "success":
                return run
        return None

    def get_latest_failed_run(self) -> Optional[Dict]:
        runs = self.get_workflow_runs(20)
        if not runs:
            return None
        
        for run in runs:
            if run.get("conclusion") == "failure":
                return run
        return None

    def compare_runs(self, run_id1: int, run_id2: int):
        run1 = self.get_workflow_run(run_id1)
        run2 = self.get_workflow_run(run_id2)
        
        if not run1 or not run2:
            print("❌ 无法获取构建信息")
            return
        
        print("\n" + "=" * 60)
        print("📊 构建对比")
        print("=" * 60)
        
        print(f"\n构建 #{run_id1}:")
        print(f"  状态: {run1.get('status', '')}")
        print(f"  结果: {run1.get('conclusion', '')}")
        print(f"  时间: {run1.get('created_at', '')}")
        
        print(f"\n构建 #{run_id2}:")
        print(f"  状态: {run2.get('status', '')}")
        print(f"  结果: {run2.get('conclusion', '')}")
        print(f"  时间: {run2.get('created_at', '')}")
        
        duration1 = run1.get('run_duration', 0)
        duration2 = run2.get('run_duration', 0)
        
        print(f"\n持续时间对比:")
        print(f"  #{run_id1}: {duration1}秒")
        print(f"  #{run_id2}: {duration2}秒")
        print(f"  差异: {abs(duration1 - duration2)}秒")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="构建状态检查和错误分析工具")
    parser.add_argument("--repo-owner", default="moyu7925", help="仓库所有者")
    parser.add_argument("--repo-name", default="bag-unit-price-calculator", help="仓库名称")
    parser.add_argument("--run-id", type=int, help="检查特定的构建ID")
    parser.add_argument("--latest", action="store_true", help="检查最新构建")
    parser.add_argument("--latest-success", action="store_true", help="获取最新成功构建")
    parser.add_argument("--latest-failed", action="store_true", help="获取最新失败构建")
    parser.add_argument("--compare", nargs=2, type=int, metavar=("ID1", "ID2"), help="对比两个构建")
    parser.add_argument("--show-logs", action="store_true", help="显示失败步骤的日志")
    
    args = parser.parse_args()
    
    checker = BuildStatusChecker(args.repo_owner, args.repo_name)
    
    if args.compare:
        checker.compare_runs(args.compare[0], args.compare[1])
    elif args.run_id:
        checker.check_build_status(args.run_id)
    elif args.latest_success:
        run = checker.get_latest_successful_run()
        if run:
            print(f"\n✅ 最新成功构建: #{run.get('id')}")
            checker.display_run_summary(run)
        else:
            print("❌ 没有找到成功的构建")
    elif args.latest_failed:
        run = checker.get_latest_failed_run()
        if run:
            print(f"\n❌ 最新失败构建: #{run.get('id')}")
            checker.display_run_summary(run)
            jobs = checker.get_workflow_jobs(run.get("id", 0))
            if jobs:
                for job in jobs:
                    if job.get("conclusion") == "failure":
                        checker.display_job_details(job, args.show_logs)
                        logs = checker.get_job_logs(job.get("id", 0))
                        if logs:
                            error_patterns = checker.detect_error_patterns(logs)
                            if error_patterns:
                                print(f"\n⚠️ 检测到错误模式:")
                                for pattern in error_patterns:
                                    print(f"   - {pattern}")
                                suggestions = checker.get_fix_suggestions(error_patterns)
                                if suggestions:
                                    print(f"\n💡 修复建议:")
                                    for suggestion in suggestions:
                                        print(f"   • {suggestion}")
        else:
            print("❌ 没有找到失败的构建")
    else:
        checker.check_build_status()

if __name__ == "__main__":
    main()
