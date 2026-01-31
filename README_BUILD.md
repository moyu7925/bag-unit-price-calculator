# 移动端自动打包系统

这是一个完全自动化的Android APK打包系统，包含GitHub Actions工作流、自动监控和错误修复功能。

## 快速开始

### 1. 设置GitHub Token

创建GitHub Personal Access Token：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：`repo:status`, `repo_deployment`, `public_repo`, `workflow`
4. 复制生成的token

设置环境变量：

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN=your_token_here
```

或者创建 `.env` 文件：
```
GITHUB_TOKEN=your_token_here
```

### 2. 启动自动监控

**Windows:**
```cmd
start_monitor.bat
```

**Linux/Mac:**
```bash
chmod +x start_monitor.sh
./start_monitor.sh
```

### 3. 检查构建状态

**Windows:**
```cmd
check_build.bat latest
check_build.bat failed
```

**Linux/Mac:**
```bash
./check_build.sh latest
./check_build.sh failed
```

## 文件说明

### 工作流文件
- [`.github/workflows/android.yml`](.github/workflows/android.yml) - GitHub Actions工作流配置

### 监控工具
- [`build_monitor.py`](build_monitor.py) - 自动监控和修复工具
- [`build_status_checker.py`](build_status_checker.py) - 构建状态检查工具
- [`build_monitor_config.json`](build_monitor_config.json) - 监控配置文件

### 启动脚本
- [`start_monitor.bat`](start_monitor.bat) - Windows启动脚本
- [`start_monitor.sh`](start_monitor.sh) - Linux/Mac启动脚本
- [`check_build.bat`](check_build.bat) - Windows检查脚本
- [`check_build.sh`](check_build.sh) - Linux/Mac检查脚本

### 文档
- [`BUILD_WORKFLOW.md`](BUILD_WORKFLOW.md) - 详细工作流文档

## 功能特性

### 自动化工作流

✅ **完全自动化** - 无需人工干预
✅ **智能缓存** - 加速构建过程
✅ **自动重试** - 失败时自动重试
✅ **错误修复** - 自动检测并修复常见错误
✅ **详细日志** - 保存完整的构建日志

### 监控系统

✅ **实时监控** - 持续监控构建状态
✅ **错误分析** - 智能分析构建错误
✅ **自动修复** - 根据错误类型自动修复
✅ **状态报告** - 生成详细的构建报告
✅ **历史追踪** - 记录修复历史

## 支持的自动修复

| 错误类型 | 修复方法 |
|---------|---------|
| AIDL工具缺失 | 下载platform-tools |
| SDK Manager缺失 | 重新安装cmdline-tools |
| 许可证未接受 | 添加许可证接受步骤 |
| Build Tools缺失 | 安装指定版本 |
| Platform Tools缺失 | 安装platform-tools |
| NDK缺失 | 安装指定版本NDK |
| 构建超时 | 增加超时时间 |
| 内存不足 | 优化内存使用 |
| 磁盘空间不足 | 清理磁盘 |
| Buildozer错误 | 修复配置 |

## 使用示例

### 监控构建

```bash
# 使用默认配置
python build_monitor.py

# 指定配置文件
python build_monitor.py --config build_monitor_config.json

# 自定义参数
python build_monitor.py --max-iterations 50 --check-interval 20
```

### 检查状态

```bash
# 检查最新构建
python build_status_checker.py --latest

# 检查最新成功构建
python build_status_checker.py --latest-success

# 检查最新失败构建（显示日志）
python build_status_checker.py --latest-failed --show-logs

# 检查指定构建
python build_status_checker.py --run-id 123456

# 对比两个构建
python build_status_checker.py --compare 123456 123457
```

### 手动触发构建

1. 访问仓库的 Actions 页面
2. 选择 "Build Android APK" 工作流
3. 点击 "Run workflow"
4. 选择分支并运行

## 配置说明

编辑 [`build_monitor_config.json`](build_monitor_config.json) 来自定义配置：

```json
{
  "repo_owner": "your_username",
  "repo_name": "your_repo",
  "branch": "main",
  "max_iterations": 30,
  "check_interval": 30,
  "monitoring": {
    "enabled": true,
    "auto_fix": true,
    "auto_push": true
  }
}
```

## 工作流程

```
代码推送 → 触发构建 → 环境准备 → 构建APK → 上传产物
    ↓
监控脚本检查状态
    ↓
构建失败？
    ↓ 是
分析错误 → 应用修复 → 推送代码 → 重新构建
    ↓
构建成功 → 下载APK
```

## 故障排查

### API限制 (HTTP 403)

- 检查GITHUB_TOKEN是否正确
- 确认token有足够权限
- 等待API限制重置

### 构建失败

```bash
# 查看失败详情
python build_status_checker.py --latest-failed --show-logs

# 手动启动监控修复
python build_monitor.py
```

### 网络问题

- 检查网络连接
- 增加重试次数
- 使用镜像源

## 最佳实践

1. **定期更新** - 保持依赖和工具最新
2. **监控日志** - 定期检查构建日志
3. **优化配置** - 根据实际情况调整
4. **备份配置** - 备份重要配置文件
5. **测试修复** - 本地测试后再推送

## 系统要求

- Python 3.7+
- Git
- GitHub账号和Personal Access Token
- 稳定的网络连接

## 许可证

MIT License
