# 快速开始指南

## 当前状态

✅ 自动化工作流已部署到GitHub
✅ 监控和修复工具已就绪
✅ 新构建已触发（ID: 21543712096）

## 立即查看构建状态

直接在浏览器中打开：
```
https://github.com/moyu7925/bag-unit-price-calculator/actions
```

## 设置GitHub Token（用于自动监控）

### 步骤1：生成GitHub Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写描述（如：Build Monitor）
4. 选择以下权限：
   - ✅ repo:status
   - ✅ repo_deployment
   - ✅ public_repo
   - ✅ workflow
5. 点击 "Generate token"
6. 复制生成的token（只显示一次！）

### 步骤2：设置Token

**Windows PowerShell:**
```powershell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Windows CMD:**
```cmd
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 步骤3：启动监控

```powershell
cd C:\Users\L\Desktop\单价计算器\github_project
python build_monitor.py
```

## 监控命令

```powershell
# 启动监控（默认参数）
python build_monitor.py

# 自定义参数
python build_monitor.py --max-iterations 20 --check-interval 30

# 检查最新构建
python build_status_checker.py --latest

# 检查失败构建
python build_status_checker.py --latest-failed --show-logs

# 检查成功构建
python build_status_checker.py --latest-success
```

## 工作流程

```
推送代码 → GitHub Actions自动构建 → 监控脚本检测状态
                                              ↓
                                        构建失败？
                                              ↓ 是
                                    分析错误 → 应用修复 → 推送代码 → 重新构建
                                              ↓
                                        构建成功 → 下载APK
```

## 自动修复功能

监控系统会自动修复以下错误：

| 错误 | 修复方法 |
|------|---------|
| AIDL工具缺失 | 下载platform-tools |
| SDK Manager缺失 | 重新安装cmdline-tools |
| 许可证未接受 | 添加许可证接受步骤 |
| Build Tools缺失 | 安装多个版本 |
| Platform Tools缺失 | 安装platform-tools |
| NDK缺失 | 安装指定版本NDK |
| 构建超时 | 增加超时时间 |
| Buildozer错误 | 修复配置和增加重试 |

## 手动触发构建

1. 访问：https://github.com/moyu7925/bag-unit-price-calculator/actions
2. 选择 "Build Android APK" 工作流
3. 点击 "Run workflow"
4. 选择分支：main
5. 点击 "Run workflow" 按钮

## 下载APK

构建成功后：

1. 访问构建页面
2. 点击页面底部的 "Artifacts"
3. 下载 `android-apk-[commit-hash].zip`
4. 解压得到APK文件

## 常见问题

### Q: 为什么监控脚本提示API限制？

A: 需要设置GITHUB_TOKEN环境变量。参考上面的"设置GitHub Token"步骤。

### Q: 构建失败怎么办？

A: 监控脚本会自动分析和修复。如果无法自动修复，请查看构建日志：
```powershell
python build_status_checker.py --latest-failed --show-logs
```

### Q: 如何停止监控？

A: 按 `Ctrl+C` 停止监控脚本。

### Q: 监控脚本会修改代码吗？

A: 是的，如果构建失败，脚本会自动修改工作流文件并推送修复。

## 文件说明

| 文件 | 说明 |
|------|------|
| [`.github/workflows/android.yml`](.github/workflows/android.yml) | GitHub Actions工作流 |
| [`build_monitor.py`](build_monitor.py) | 自动监控和修复工具 |
| [`build_status_checker.py`](build_status_checker.py) | 构建状态检查工具 |
| [`build_monitor_config.json`](build_monitor_config.json) | 监控配置文件 |
| [`BUILD_WORKFLOW.md`](BUILD_WORKFLOW.md) | 详细文档 |
| [`README_BUILD.md`](README_BUILD.md) | 快速开始指南 |

## 当前构建

- **构建ID**: 21543712096
- **状态**: 进行中
- **链接**: https://github.com/moyu7925/bag-unit-price-calculator/actions/runs/21543712096

## 下一步

1. 设置GitHub Token（如果需要自动监控）
2. 访问构建页面查看进度
3. 等待构建完成
4. 下载APK文件

---

**提示**: 如果不设置Token，仍然可以手动在GitHub网页上查看构建状态和下载APK。
