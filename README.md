# MP4 to MP3 Converter

一个简单易用的 MP4 转 MP3 音频提取工具，基于 Python 和 ffmpeg。

## ✨ 功能特点

- 🎵 单个文件转换
- 📁 批量文件夹转换
- ✅ 自动检测 ffmpeg 是否安装
- 🎯 支持多种视频格式（MP4、MOV、AVI、MKV、M4A 等）
- 🎧 192kbps 高质量 MP3 输出
- 📝 详细的进度提示和错误信息

## 📦 依赖安装

脚本需要 **ffmpeg**，安装方法：

| 系统 | 命令 |
|------|------|
| **macOS** | `brew install ffmpeg` |
| **Ubuntu/Debian** | `sudo apt install ffmpeg` |
| **Windows** | [官网下载](https://ffmpeg.org/download.html) |
| **Conda** | `conda install -c conda-forge ffmpeg` |

## 🚀 使用方法

### 单个文件转换

```bash
# 基本用法（输出同名 MP3 文件）
python mp4_to_mp3.py video.mp4

# 指定输出文件名
python mp4_to_mp3.py video.mp4 audio.mp3
```

### 批量转换

```bash
# 转换文件夹中所有视频文件
python mp4_to_mp3.py --batch ./videos

# 指定输出文件夹
python mp4_to_mp3.py --batch ./videos ./mp3s
```

## 📖 示例

```bash
# 转换单个视频
python mp4_to_mp3.py my_video.mp4

# 批量转换整个文件夹
python mp4_to_mp3.py --batch /path/to/videos /path/to/output
```

## 🛠️ 技术细节

- 使用 `ffmpeg` 进行音视频处理
- 音频编码：`libmp3lame`
- 比特率：`192kbps`
- 支持格式：MP4, M4A, MOV, AVI, MKV, WMV, FLV

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**作者**: 516545865@qq.com  
**创建日期**: 2026-03-25
