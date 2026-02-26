---
name: video-analyzer
description: 下载 YouTube/Bilibili 视频，提取音频并转录，生成结构化摘要和关键时间点。
version: "1.0.0"
homepage: https://github.com/andyhuo520/video-analyzer
metadata:
  openclaw:
    requires:
      bins: ["python3", "ffmpeg"]
    optionalBins: ["yt-dlp", "whisper"]
---

# Video Analyzer - 视频解析专家

自动下载、转录和总结在线视频内容。

## 功能特性

### 📥 视频下载
- 支持 YouTube、Bilibili 等主流平台
- 自动选择最佳质量
- 支持代理配置

### 🎙️ 语音转录
- 使用 OpenAI Whisper 或本地模型
- 支持中文、英文、日文等多语言
- 生成带时间戳的字幕

### 📝 智能总结
- 提取关键观点和结论
- 生成章节时间戳
- 输出结构化 Markdown 报告

## 快速开始

```bash
# 解析单个视频
python3 scripts/analyze-video.py "https://youtu.be/SlB6M7__nDA" --output report.md

# 批量解析（配置文件）
python3 scripts/analyze-video.py --config batch-config.json

# 仅下载音频
python3 scripts/analyze-video.py "URL" --audio-only --output audio.mp3
```

## 依赖安装

```bash
# 安装 yt-dlp
pip3 install yt-dlp

# 安装 Whisper（可选，用于转录）
pip3 install openai-whisper

# 或安装 faster-whisper（更快）
pip3 install faster-whisper
```

## 输出格式

生成的报告包含：
- 📊 视频基本信息（标题、作者、时长）
- 🎯 核心观点总结
- ⏱️ 关键时间戳与章节
- 📝 完整转录文本
- 💡 个人洞察与关联

## 示例配置

```json
{
  "videos": [
    {
      "url": "https://youtu.be/xxx",
      "title": "自定义标题",
      "language": "zh",
      "chapters": true
    }
  ],
  "output_dir": "./output",
  "transcribe": true,
  "summarize": true
}
```

## 许可证

MIT