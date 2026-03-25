# MP4 to MP3 Web Converter

基于 Flask + SQLite3 的在线 MP4 转 MP3 工具，提供 Web 界面上传视频文件并自动提取音频。

## ✨ 功能特点

- 🌐 **Web 界面** - 美观易用的上传界面，支持拖拽上传
- 🔄 **自动转换** - 上传后自动后台转换为 MP3
- 📊 **转换历史** - 记录所有转换任务，随时下载
- 💾 **SQLite 数据库** - 轻量级数据存储，无需配置
- 🎧 **高质量输出** - 192kbps MP3 编码
- 📱 **响应式设计** - 支持手机和桌面端

## 📦 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 ffmpeg（必需）
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# Windows: 从 https://ffmpeg.org/download.html 下载
```

## 🚀 快速启动

```bash
# 进入项目目录
cd web_app

# 启动服务
python app.py
```

服务启动后访问：**http://localhost:5000**

## 📁 项目结构

```
web_app/
├── app.py              # Flask 主应用
├── requirements.txt    # Python 依赖
├── templates/
│   └── index.html      # 前端页面
├── uploads/            # 上传文件目录（自动创建）
├── outputs/            # 输出文件目录（自动创建）
└── conversions.db      # SQLite 数据库（自动创建）
```

## 🔧 配置选项

在 `app.py` 中可修改以下配置：

```python
# 上传目录
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'

# 输出目录
OUTPUT_FOLDER = Path(__file__).parent / 'outputs'

# 数据库路径
DATABASE = Path(__file__).parent / 'conversions.db'

# 允许的文件格式
ALLOWED_EXTENSIONS = {'mp4', 'm4a', 'mov', 'avi', 'mkv', 'wmv', 'flv'}

# 最大文件大小（字节）- 默认 500MB
MAX_CONTENT_LENGTH = 500 * 1024 * 1024

# 音频比特率
"-ab", "192k"  # 可改为 128k, 256k, 320k 等
```

## 🌐 生产环境部署

### 使用 Gunicorn

```bash
# 安装 gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
```

构建并运行：

```bash
docker build -t mp4-to-mp3-web .
docker run -p 5000:5000 -v $(pwd)/data:/app/data mp4-to-mp3-web
```

## 📊 API 接口

### 健康检查
```
GET /health
```

返回：
```json
{
  "status": "ok",
  "ffmpeg": "installed",
  "database": "ok"
}
```

### 检查转换状态
```
GET /status/<conversion_id>
```

### 下载转换后的文件
```
GET /download/<conversion_id>
```

## ⚠️ 注意事项

1. **文件大小限制**：默认最大 500MB，可在 `app.py` 中修改
2. **转换超时**：默认 10 分钟超时，防止大文件占用资源
3. **存储空间**：定期清理 `uploads/` 和 `outputs/` 目录
4. **安全性**：生产环境请添加用户认证和访问控制

## 🛠️ 故障排除

### ffmpeg 未找到
```bash
# 检查是否安装
ffmpeg -version

# 如果未安装，参考上方安装说明
```

### 端口被占用
```bash
# 修改端口
python app.py --port 8080

# 或在 app.py 中修改：
app.run(port=8080)
```

### 转换失败
检查错误日志，常见原因：
- 输入文件损坏
- 不支持的编码格式
- 磁盘空间不足

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**作者**: billwangcn  
**GitHub**: https://github.com/billwangcn/mp4-to-mp3-converter  
**创建日期**: 2026-03-25
