# 移动端自动打包工作流

## 概述

本项目提供了完全自动化的Android APK打包工作流，包括自动监控和错误修复功能。

## 文件说明

### 工作流文件

- [`.github/workflows/android.yml`](.github/workflows/android.yml) - GitHub Actions工作流配置

### 监控和修复工具

- [`build_monitor.py`](build_monitor.py) - 自动监控和修复工具
- [`build_status_checker.py`](build_status_checker.py) - 构建状态检查和错误分析工具
- [`build_monitor_config.json`](build_monitor_config.json) - 监控配置文件

## 功能特性

### 工作流特性

1. **完全自动化** - 无需人工干预，自动完成所有步骤
2. **智能缓存** - 缓存依赖和构建产物，加速构建
3. **自动重试** - 构建失败时自动重试
4. **错误修复** - 自动检测并修复常见错误
5. **详细日志** - 上传构建日志，便于问题排查

### 监控工具特性

1. **实时监控** - 持续监控构建状态
2. **错误分析** - 自动分析构建错误
3. **自动修复** - 根据错误类型自动应用修复
4. **状态检查** - 检查构建状态和历史
5. **详细报告** - 生成详细的构建报告

## 使用方法

### 1. 配置GitHub Token

设置环境变量 `GITHUB_TOKEN`：

```bash
export GITHUB_TOKEN=your_github_token
```

或者在Windows PowerShell中：

```powershell
$env:GITHUB_TOKEN="your_github_token"
```

### 2. 启动自动监控

运行监控脚本：

```bash
python build_monitor.py
```

可选参数：

```bash
python build_monitor.py --config build_monitor_config.json
python build_monitor.py --max-iterations 50 --check-interval 20
```

### 3. 检查构建状态

检查最新构建：

```bash
python build_status_checker.py --latest
```

检查特定构建：

```bash
python build_status_checker.py --run-id 123456
```

获取最新成功构建：

```bash
python build_status_checker.py --latest-success
```

获取最新失败构建：

```bash
python build_status_checker.py --latest-failed --show-logs
```

对比两个构建：

```bash
python build_status_checker.py --compare 123456 123457
```

### 4. 手动触发构建

在GitHub仓库页面：
1. 进入 Actions 标签
2. 选择 "Build Android APK" 工作流
3. 点击 "Run workflow"
4. 选择分支并运行

## 配置说明

### build_monitor_config.json

配置文件包含以下部分：

```json
{
  "repo_owner": "moyu7925",
  "repo_name": "bag-unit-price-calculator",
  "branch": "main",
  "workflow_file": ".github/workflows/android.yml",
  "max_iterations": 30,
  "check_interval": 30,
  "monitoring": {
    "enabled": true,
    "auto_fix": true,
    "auto_push": true
  }
}
```

## 自动修复的错误类型

| 错误类型 | 描述 | 修复方法 |
|---------|------|---------|
| AIDL工具缺失 | aidl not found | 下载platform-tools |
| SDK Manager缺失 | sdkmanager not found | 重新安装cmdline-tools |
| 许可证未接受 | license not accepted | 添加许可证接受步骤 |
| Build Tools缺失 | build-tools not found | 安装指定版本 |
| Platform Tools缺失 | platform-tools not found | 安装platform-tools |
| NDK缺失 | ndk not found | 安装指定版本NDK |
| 构建超时 | timeout | 增加超时时间 |
| 内存不足 | out of memory | 优化内存使用 |
| 磁盘空间不足 | no space left | 清理磁盘 |
| Buildozer错误 | buildozer error | 修复配置 |

## 工作流程

1. **代码推送** - 推送代码到main分支
2. **自动触发** - GitHub Actions自动触发构建
3. **环境准备** - 安装依赖和工具
4. **构建APK** - 使用Buildozer构建APK
5. **上传产物** - 上传APK和日志
6. **状态监控** - 监控脚本检查构建状态
7. **错误修复** - 如果失败，自动修复并重新构建
8. **完成通知** - 构建成功后通知

## 故障排查

### 构建失败

1. 检查构建日志：
   ```bash
   python build_status_checker.py --latest-failed --show-logs
   ```

2. 查看错误分析：
   ```bash
   python build_status_checker.py --latest-failed
   ```

3. 手动应用修复：
   ```bash
   python build_monitor.py
   ```

### API限制

如果遇到GitHub API限制（HTTP 403），请：
1. 检查GITHUB_TOKEN是否正确
2. 确认token有足够的权限
3. 等待API限制重置

### 网络问题

如果遇到网络问题：
1. 检查网络连接
2. 增加重试次数
3. 使用镜像源

## 最佳实践

1. **定期更新** - 定期更新依赖和工具版本
2. **监控日志** - 定期检查构建日志
3. **优化配置** - 根据实际情况优化配置
4. **备份配置** - 备份重要的配置文件
5. **测试修复** - 在本地测试修复后再推送

## 许可证

MIT License
