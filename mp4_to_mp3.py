#!/usr/bin/env python3
"""
MP4 转 MP3 转换脚本

使用方法:
    python mp4_to_mp3.py <input.mp4> [output.mp3]

依赖:
    - ffmpeg (必须安装)
    安装方法:
        - macOS: brew install ffmpeg
        - Ubuntu/Debian: sudo apt install ffmpeg
        - Windows: 从 https://ffmpeg.org/download.html 下载
"""

import subprocess
import sys
import os
from pathlib import Path


def check_ffmpeg():
    """检查 ffmpeg 是否已安装"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_mp4_to_mp3(input_file: str, output_file: str = None):
    """
    将 MP4 文件转换为 MP3 格式

    Args:
        input_file: 输入的 MP4 文件路径
        output_file: 输出的 MP3 文件路径（可选，默认为同名.mp3）

    Returns:
        bool: 转换是否成功
    """
    input_path = Path(input_file)

    # 检查输入文件是否存在
    if not input_path.exists():
        print(f"❌ 错误：文件不存在 - {input_file}")
        return False

    # 检查文件扩展名
    if input_path.suffix.lower() not in ['.mp4', '.m4a', '.mov', '.avi', '.mkv']:
        print(f"⚠️  警告：输入文件可能不是视频文件 - {input_path.suffix}")

    # 生成输出文件名
    if output_file is None:
        output_file = str(input_path.with_suffix('.mp3'))

    print(f"📥 输入文件：{input_path}")
    print(f"📤 输出文件：{output_file}")
    print("🔄 开始转换...")

    # ffmpeg 转换命令
    # -i: 输入文件
    # -vn: 禁用视频流
    # -acodec libmp3lame: 使用 MP3 编码器
    # -ab 192k: 音频比特率 192kbps
    # -y: 覆盖已存在的输出文件
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-vn",
        "-acodec", "libmp3lame",
        "-ab", "192k",
        "-y",
        output_file
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ 转换成功！")
            print(f"📁 输出文件：{os.path.abspath(output_file)}")
            return True
        else:
            print(f"❌ 转换失败：{result.stderr}")
            return False

    except FileNotFoundError:
        print("❌ 错误：未找到 ffmpeg 命令")
        print("   请先安装 ffmpeg:")
        print("   - macOS: brew install ffmpeg")
        print("   - Ubuntu/Debian: sudo apt install ffmpeg")
        print("   - Windows: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"❌ 发生错误：{e}")
        return False


def batch_convert(input_folder: str, output_folder: str = None):
    """
    批量转换文件夹中的所有 MP4 文件

    Args:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径（可选，默认为输入文件夹）
    """
    input_path = Path(input_folder)

    if not input_path.exists():
        print(f"❌ 错误：文件夹不存在 - {input_folder}")
        return

    if output_folder is None:
        output_folder = input_folder

    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # 查找所有视频文件
    video_extensions = ['.mp4', '.m4a', '.mov', '.avi', '.mkv', '.wmv', '.flv']
    video_files = [
        f for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in video_extensions
    ]

    if not video_files:
        print(f"⚠️  文件夹中没有视频文件：{input_folder}")
        return

    print(f"📁 找到 {len(video_files)} 个视频文件")
    print("-" * 50)

    success_count = 0
    for i, video_file in enumerate(video_files, 1):
        output_file = output_path / f"{video_file.stem}.mp3"
        print(f"\n[{i}/{len(video_files)}] 转换：{video_file.name}")

        if convert_mp4_to_mp3(str(video_file), str(output_file)):
            success_count += 1

    print("-" * 50)
    print(f"✅ 批量转换完成：{success_count}/{len(video_files)} 成功")


def main():
    """主函数"""
    # 检查 ffmpeg
    if not check_ffmpeg():
        print("❌ 未检测到 ffmpeg，请先安装 ffmpeg")
        print()
        print("安装方法:")
        print("  - macOS:     brew install ffmpeg")
        print("  - Ubuntu:    sudo apt install ffmpeg")
        print("  - Windows:   https://ffmpeg.org/download.html")
        print("  - Conda:     conda install -c conda-forge ffmpeg")
        sys.exit(1)

    print("🎵 MP4 转 MP3 转换工具")
    print("=" * 50)

    # 检查命令行参数
    if len(sys.argv) < 2:
        print()
        print("使用方法:")
        print("  单个文件：python mp4_to_mp3.py <input.mp4> [output.mp3]")
        print("  批量转换：python mp4_to_mp3.py --batch <input_folder> [output_folder]")
        print()
        print("示例:")
        print("  python mp4_to_mp3.py video.mp4")
        print("  python mp4_to_mp3.py video.mp4 audio.mp3")
        print("  python mp4_to_mp3.py --batch ./videos ./mp3s")
        sys.exit(1)

    # 批量转换模式
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("❌ 错误：请指定输入文件夹路径")
            sys.exit(1)

        input_folder = sys.argv[2]
        output_folder = sys.argv[3] if len(sys.argv) > 3 else None
        batch_convert(input_folder, output_folder)
    else:
        # 单个文件转换
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        convert_mp4_to_mp3(input_file, output_file)


if __name__ == "__main__":
    main()
