---
name: 3d-interactive-lesson
description: 创建基于 Three.js 和 SVG 的 3D 互动教学课件。用户输入教学内容，自动生成精美的交互式 HTML 页面。
version: "1.0.0"
homepage: https://github.com/andyhuo520/3d-interactive-lesson
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    optionalBins: ["node"]
---

# 3D 互动教学课件生成器

将教学内容转化为精美的 3D 交互式 HTML 课件。

## 快速开始

```bash
# 生成单个课件
python3 scripts/generate-lesson.py --topic "太阳系行星" --output lesson.html

# 使用配置文件批量生成
python3 scripts/generate-lesson.py --config lesson-config.json
```

## 功能特性

### 🎨 视觉设计
- 现代化暗色/亮色主题
- 毛玻璃效果 UI
- 流畅的页面过渡动画
- 响应式布局

### 🎮 3D 交互
- Three.js 驱动的 3D 场景
- 模型旋转、缩放、平移
- 点击交互显示详细信息
- 动画演示（轨道运动、分解图等）

### 📚 教学内容
- 支持数学公式（KaTeX）
- 交互式标注系统
- 步骤化演示
- 测验问答模块

## 使用示例

### 示例 1：太阳系教学
```bash
python3 scripts/generate-lesson.py \
  --title "太阳系探索" \
  --subject "科学" \
  --topic "太阳系行星" \
  --content "介绍八大行星的特点、轨道和相对大小" \
  --models "sun,mercury,venus,earth,mars,jupiter,saturn,uranus,neptune" \
  --output solar-system.html
```

### 示例 2：人体解剖
```bash
python3 scripts/generate-lesson.py \
  --title "人体骨骼系统" \
  --subject "生物" \
  --topic "骨骼结构" \
  --interactive \
  --quizzes \
  --output human-skeleton.html
```

## 配置文件格式

```json
{
  "title": "课程标题",
  "subject": "学科",
  "topic": "主题",
  "description": "课程描述",
  "theme": "dark|light",
  "sections": [
    {
      "type": "3d-scene",
      "title": "3D 场景标题",
      "models": ["model1", "model2"],
      "interactions": ["rotate", "zoom", "click"]
    },
    {
      "type": "content",
      "title": "文字内容",
      "text": "详细说明..."
    },
    {
      "type": "quiz",
      "question": "问题",
      "options": ["A", "B", "C"],
      "answer": 0
    }
  ]
}
```

## 支持的 3D 模型

内置模型：
- 几何体：立方体、球体、圆柱体、圆锥体、圆环
- 天体：太阳、行星、卫星
- 生物：细胞、DNA 双螺旋、人体器官
- 分子：水分子、甲烷、苯环

自定义模型：
```bash
# 使用 GLB/GLTF 格式
python3 scripts/generate-lesson.py --custom-model path/to/model.glb
```

## 输出文件

生成的 HTML 文件包含：
- 完整的 Three.js 场景
- 嵌入式 CSS 样式
- JavaScript 交互代码
- 响应式布局
- 离线可用（无需服务器）

## 依赖

- Python 3.8+
- Three.js (CDN)
- KaTeX (数学公式)

## 许可证

MIT