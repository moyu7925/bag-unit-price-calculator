# 应用图标说明

## 图标要求

为了生成APK，您需要准备以下图标文件：

### 1. 应用图标（必需）
- 文件名：`icon.png`
- 尺寸：192x192 像素
- 格式：PNG（支持透明背景）
- 位置：`mobile/assets/icon.png`

### 2. 启动屏幕图标（可选）
- 文件名：`presplash.png`
- 尺寸：1024x768 像素
- 格式：PNG
- 位置：`mobile/assets/presplash.png`

## 如何创建图标

### 方法1：使用在线工具
1. 访问 https://www.favicon-generator.org/ 或类似网站
2. 上传您的图片
3. 下载生成的图标
4. 重命名为 `icon.png`
5. 放置到 `mobile/assets/` 目录

### 方法2：使用图像编辑软件
1. 使用 Photoshop、GIMP 或 Paint.NET
2. 创建 192x192 像素的画布
3. 设计您的应用图标
4. 导出为 PNG 格式
5. 保存为 `mobile/assets/icon.png`

### 方法3：使用默认图标
如果您暂时没有图标，buildozer 会使用默认图标。

## 图标设计建议

- 使用简洁的图形
- 确保在小尺寸下清晰可见
- 使用与应用相关的颜色
- 避免过多文字

## 更新buildozer.spec

如果您的图标文件名不是 `icon.png`，请在 `buildozer.spec` 文件中修改：

```ini
[app]
icon.filename = assets/your_icon.png
presplash.filename = assets/your_presplash.png
```
