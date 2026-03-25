#!/usr/bin/env python3
"""
MP4 to MP3 Web Converter
基于 Flask + SQLite3 的在线 MP4 转 MP3 工具
"""

import os
import uuid
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename

# ==================== 配置 ====================

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于 session 和 flash 消息

# 上传配置
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
OUTPUT_FOLDER = Path(__file__).parent / 'outputs'
DATABASE = Path(__file__).parent / 'conversions.db'

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'mp4', 'm4a', 'mov', 'avi', 'mkv', 'wmv', 'flv'}

# 最大文件大小：500MB
MAX_CONTENT_LENGTH = 500 * 1024 * 1024

# 确保目录存在
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(OUTPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


# ==================== 数据库 ====================

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT NOT NULL,
            output_filename TEXT NOT NULL,
            file_size INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def save_conversion(original_filename, output_filename, file_size):
    """保存转换记录"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversions (original_filename, output_filename, file_size, status)
        VALUES (?, ?, ?, 'processing')
    ''', (original_filename, output_filename, file_size))
    
    conversion_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return conversion_id


def update_conversion_status(conversion_id, status, error_message=None):
    """更新转换状态"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if status == 'completed':
        cursor.execute('''
            UPDATE conversions 
            SET status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, conversion_id))
    else:
        cursor.execute('''
            UPDATE conversions 
            SET status = ?, error_message = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, error_message, conversion_id))
    
    conn.commit()
    conn.close()


def get_conversions(limit=50):
    """获取转换记录"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, original_filename, output_filename, file_size, status, 
               created_at, completed_at, error_message
        FROM conversions
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'original_filename': row[1],
            'output_filename': row[2],
            'file_size': row[3],
            'status': row[4],
            'created_at': row[5],
            'completed_at': row[6],
            'error_message': row[7]
        }
        for row in rows
    ]


# ==================== 工具函数 ====================

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes is None:
        return 'Unknown'
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def convert_to_mp3(input_path, output_path):
    """
    使用 ffmpeg 将视频文件转换为 MP3
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-vn",
        "-acodec", "libmp3lame",
        "-ab", "192k",
        "-y",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 分钟超时
        )
        
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "转换超时（超过 10 分钟）"
    except FileNotFoundError:
        return False, "未找到 ffmpeg，请安装 ffmpeg"
    except Exception as e:
        return False, str(e)


# ==================== 路由 ====================

@app.route('/')
def index():
    """首页 - 上传表单"""
    conversions = get_conversions(20)
    
    # 格式化数据
    for conv in conversions:
        conv['file_size_formatted'] = format_file_size(conv['file_size'])
    
    return render_template('index.html', conversions=conversions)


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传和转换"""
    # 检查文件是否存在
    if 'file' not in request.files:
        flash('❌ 没有选择文件', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('❌ 没有选择文件', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash(f'❌ 不支持的文件格式。允许的格式：{", ".join(ALLOWED_EXTENSIONS)}', 'error')
        return redirect(url_for('index'))
    
    try:
        # 生成唯一文件名
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        unique_id = uuid.uuid4().hex[:8]
        
        input_filename = f"{unique_id}.{file_ext}"
        output_filename = f"{unique_id}.mp3"
        
        input_path = UPLOAD_FOLDER / input_filename
        output_path = OUTPUT_FOLDER / output_filename
        
        # 保存上传的文件
        file.save(str(input_path))
        file_size = input_path.stat().st_size
        
        # 保存转换记录
        conversion_id = save_conversion(original_filename, output_filename, file_size)
        
        # 异步转换（在后台进行）
        def do_conversion():
            success, error = convert_to_mp3(input_path, output_path)
            
            if success:
                update_conversion_status(conversion_id, 'completed')
                # 可选：删除输入文件节省空间
                # input_path.unlink()
            else:
                update_conversion_status(conversion_id, 'failed', error)
                # 转换失败时删除输出文件（如果存在）
                if output_path.exists():
                    output_path.unlink()
        
        # 启动后台转换
        import threading
        thread = threading.Thread(target=do_conversion)
        thread.start()
        
        flash(f'✅ 文件已上传，正在转换中... (任务 ID: {conversion_id})', 'success')
        
    except Exception as e:
        flash(f'❌ 上传失败：{str(e)}', 'error')
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))


@app.route('/download/<int:conversion_id>')
def download(conversion_id):
    """下载转换后的 MP3 文件"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT output_filename, status FROM conversions WHERE id = ?
    ''', (conversion_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        flash('❌ 转换记录不存在', 'error')
        return redirect(url_for('index'))
    
    output_filename, status = row
    
    if status != 'completed':
        flash('❌ 转换尚未完成', 'error')
        return redirect(url_for('index'))
    
    file_path = OUTPUT_FOLDER / output_filename
    
    if not file_path.exists():
        flash('❌ 文件不存在', 'error')
        return redirect(url_for('index'))
    
    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=output_filename,
        mimetype='audio/mpeg'
    )


@app.route('/status/<int:conversion_id>')
def check_status(conversion_id):
    """检查转换状态（API）"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT status, error_message FROM conversions WHERE id = ?
    ''', (conversion_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': 'Conversion not found'}), 404
    
    status, error_message = row
    
    return jsonify({
        'id': conversion_id,
        'status': status,
        'error': error_message
    })


@app.route('/delete/<int:conversion_id>', methods=['POST'])
def delete_conversion(conversion_id):
    """删除转换记录"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT output_filename FROM conversions WHERE id = ?', (conversion_id,))
    row = cursor.fetchone()
    
    if row:
        output_filename = row[0]
        file_path = OUTPUT_FOLDER / output_filename
        
        # 删除文件
        if file_path.exists():
            file_path.unlink()
        
        # 删除记录
        cursor.execute('DELETE FROM conversions WHERE id = ?', (conversion_id,))
        conn.commit()
    
    conn.close()
    
    flash('✅ 记录已删除', 'success')
    return redirect(url_for('index'))


@app.route('/health')
def health():
    """健康检查"""
    # 检查 ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        ffmpeg_ok = True
    except:
        ffmpeg_ok = False
    
    return jsonify({
        'status': 'ok' if ffmpeg_ok else 'degraded',
        'ffmpeg': 'installed' if ffmpeg_ok else 'not installed',
        'database': 'ok' if DATABASE.exists() else 'not initialized'
    })


# ==================== 错误处理 ====================

@app.errorhandler(413)
def too_large(e):
    """文件大小超限"""
    flash(f'❌ 文件太大，最大允许 {MAX_CONTENT_LENGTH // 1024 // 1024}MB', 'error')
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(e):
    """服务器内部错误"""
    flash('❌ 服务器内部错误，请稍后重试', 'error')
    return redirect(url_for('index'))


# ==================== 主程序 ====================

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    print("=" * 60)
    print("🎵 MP4 to MP3 Web Converter")
    print("=" * 60)
    print(f"📁 上传目录：{UPLOAD_FOLDER}")
    print(f"📁 输出目录：{OUTPUT_FOLDER}")
    print(f"💾 数据库：{DATABASE}")
    print("=" * 60)
    print("🚀 启动服务器...")
    print("📍 访问地址：http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
