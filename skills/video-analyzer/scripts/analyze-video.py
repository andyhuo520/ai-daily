#!/usr/bin/env python3
"""
Video Analyzer - 视频下载与解析工具
支持 YouTube、Bilibili 等平台
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

class VideoAnalyzer:
    def __init__(self, output_dir="./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.yt_dlp_path = self._find_yt_dlp()
        
    def _find_yt_dlp(self):
        """查找 yt-dlp 可执行文件"""
        possible_paths = [
            "yt-dlp",
            "/Users/user/Library/Python/3.9/bin/yt-dlp",
            "/usr/local/bin/yt-dlp",
            "/opt/homebrew/bin/yt-dlp",
        ]
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue
        return None
    
    def _install_yt_dlp(self):
        """自动安装 yt-dlp"""
        print("🔧 正在安装 yt-dlp...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"], 
                          check=True, timeout=120)
            self.yt_dlp_path = self._find_yt_dlp()
            if self.yt_dlp_path:
                print(f"✅ yt-dlp 安装成功: {self.yt_dlp_path}")
                return True
        except Exception as e:
            print(f"❌ 安装失败: {e}")
        return False
    
    def get_video_info(self, url):
        """获取视频信息"""
        if not self.yt_dlp_path:
            if not self._install_yt_dlp():
                return None
        
        try:
            cmd = [
                self.yt_dlp_path,
                "--dump-json",
                "--no-download",
                "--no-playlist",
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return json.loads(result.stdout.strip().split('\n')[0])
        except Exception as e:
            print(f"⚠️ 获取信息失败: {e}")
        return None
    
    def download_audio(self, url, output_name=None):
        """下载音频"""
        if not self.yt_dlp_path:
            if not self._install_yt_dlp():
                return None
        
        if not output_name:
            output_name = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        output_path = self.output_dir / f"{output_name}.mp3"
        
        try:
            print(f"⬇️ 正在下载音频...")
            cmd = [
                self.yt_dlp_path,
                "-f", "bestaudio/best",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "192K",
                "--no-playlist",
                "-o", str(output_path),
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"✅ 音频已保存: {output_path}")
                return output_path
            else:
                print(f"❌ 下载失败: {result.stderr}")
        except Exception as e:
            print(f"❌ 错误: {e}")
        return None
    
    def download_video(self, url, output_name=None, quality="720"):
        """下载视频"""
        if not self.yt_dlp_path:
            if not self._install_yt_dlp():
                return None
        
        if not output_name:
            output_name = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        output_path = self.output_dir / f"{output_name}.mp4"
        
        try:
            print(f"⬇️ 正在下载视频 (最高 {quality}p)...")
            cmd = [
                self.yt_dlp_path,
                "-f", f"best[height<={quality}]/best",
                "--no-playlist",
                "-o", str(output_path),
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"✅ 视频已保存: {output_path}")
                return output_path
            else:
                print(f"❌ 下载失败: {result.stderr}")
        except Exception as e:
            print(f"❌ 错误: {e}")
        return None
    
    def extract_frames(self, video_path, num_frames=5):
        """提取关键帧"""
        frames_dir = self.output_dir / f"frames_{Path(video_path).stem}"
        frames_dir.mkdir(exist_ok=True)
        
        try:
            # 获取视频时长
            probe_cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)
            ]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip())
            
            # 提取均匀分布的帧
            for i in range(num_frames):
                timestamp = (duration / (num_frames + 1)) * (i + 1)
                output_frame = frames_dir / f"frame_{i+1:02d}_{timestamp:.0f}s.jpg"
                
                cmd = [
                    "ffmpeg", "-y", "-ss", str(timestamp), "-i", str(video_path),
                    "-vframes", "1", "-q:v", "2", str(output_frame)
                ]
                subprocess.run(cmd, capture_output=True, timeout=30)
            
            print(f"✅ 已提取 {num_frames} 帧到: {frames_dir}")
            return frames_dir
        except Exception as e:
            print(f"⚠️ 提取帧失败: {e}")
        return None
    
    def generate_report(self, video_info, output_file=None):
        """生成视频分析报告"""
        if not video_info:
            return None
        
        if not output_file:
            output_file = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        else:
            output_file = Path(output_file)
        
        title = video_info.get('title', '未知标题')
        uploader = video_info.get('uploader', '未知作者')
        duration = video_info.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}"
        view_count = video_info.get('view_count', 0)
        upload_date = video_info.get('upload_date', '')
        description = video_info.get('description', '')
        webpage_url = video_info.get('webpage_url', '')
        
        # 格式化日期
        if upload_date and len(upload_date) == 8:
            upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
        
        report = f"""# 📺 视频分析报告

## 基本信息

| 项目 | 内容 |
|------|------|
| **标题** | {title} |
| **作者** | {uploader} |
| **时长** | {duration_str} |
| **发布日期** | {upload_date} |
| **观看次数** | {view_count:,} |
| **原链接** | {webpage_url} |

---

## 📝 视频简介

{description[:1000] if description else "*暂无简介*"}

---

## 🎯 内容分析

*此部分需要人工观看或配合转录文本填写*

### 核心观点

1. **[待填写]** 主要论点/核心概念
2. **[待填写]** 重要发现/结论
3. **[待填写]** 实际应用/启示

### 关键时间戳

| 时间 | 内容 |
|------|------|
| 00:00 | 开场/引言 |
| **{duration_str}** | 结束/总结 |

---

## 💡 个人洞察

*[观看后记录个人思考和关联]*

---

## 🔗 相关资源

- 原视频: {webpage_url}
- 分析报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*由 Video Analyzer Skill 自动生成*
"""
        
        output_file.write_text(report, encoding='utf-8')
        print(f"✅ 报告已保存: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(description="视频下载与分析工具")
    parser.add_argument("url", nargs="?", help="视频 URL")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--audio-only", action="store_true", help="仅下载音频")
    parser.add_argument("--video", action="store_true", help="下载视频")
    parser.add_argument("--quality", default="720", help="视频质量 (默认 720p)")
    parser.add_argument("--frames", type=int, default=5, help="提取帧数")
    parser.add_argument("--output-dir", default="./output", help="输出目录")
    parser.add_argument("--info-only", action="store_true", help="仅获取信息")
    
    args = parser.parse_args()
    
    if not args.url and not args.info_only:
        parser.print_help()
        return
    
    analyzer = VideoAnalyzer(output_dir=args.output_dir)
    
    # 获取视频信息
    if args.url:
        print(f"🔍 正在分析: {args.url}")
        video_info = analyzer.get_video_info(args.url)
        
        if video_info:
            print(f"\n📺 {video_info.get('title', 'Unknown')}")
            print(f"👤 {video_info.get('uploader', 'Unknown')}")
            print(f"⏱️ {video_info.get('duration', 0) // 60}:{video_info.get('duration', 0) % 60:02d}")
            
            # 生成报告
            if not args.audio_only and not args.video:
                report_path = analyzer.generate_report(video_info, args.output)
                if report_path:
                    print(f"\n📄 报告已生成，请查看: {report_path}")
        else:
            print("❌ 无法获取视频信息，可能需要代理或视频受限制")
            return
    
    # 下载音频
    if args.audio_only and args.url:
        audio_path = analyzer.download_audio(args.url, args.output)
        if audio_path:
            print(f"\n🎵 音频已下载: {audio_path}")
    
    # 下载视频
    if args.video and args.url:
        video_path = analyzer.download_video(args.url, args.output, args.quality)
        if video_path:
            print(f"\n🎬 视频已下载: {video_path}")
            # 提取关键帧
            if args.frames > 0:
                analyzer.extract_frames(video_path, args.frames)


if __name__ == "__main__":
    main()
