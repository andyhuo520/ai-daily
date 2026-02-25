#!/usr/bin/env python3
"""
3D Interactive Lesson Generator
生成基于 Three.js 的交互式 3D 教学课件
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 内置 3D 模型定义
BUILTIN_MODELS = {
    # 天体
    "sun": {"type": "sphere", "radius": 5, "color": 0xFDB813, "emissive": 0xFDB813, "name": "太阳"},
    "mercury": {"type": "sphere", "radius": 0.8, "color": 0xA5A5A5, "name": "水星"},
    "venus": {"type": "sphere", "radius": 1.2, "color": 0xE6B800, "name": "金星"},
    "earth": {"type": "sphere", "radius": 1.3, "color": 0x2233FF, "texture": "earth", "name": "地球"},
    "mars": {"type": "sphere", "radius": 1.0, "color": 0xFF4500, "name": "火星"},
    "jupiter": {"type": "sphere", "radius": 3.5, "color": 0xD4A574, "stripes": True, "name": "木星"},
    "saturn": {"type": "sphere", "radius": 3.0, "color": 0xF4D03F, "rings": True, "name": "土星"},
    "uranus": {"type": "sphere", "radius": 2.0, "color": 0x4FD0E7, "name": "天王星"},
    "neptune": {"type": "sphere", "radius": 1.9, "color": 0x2E6FCC, "name": "海王星"},
    
    # 几何体
    "cube": {"type": "box", "size": [2, 2, 2], "color": 0x00ff00, "name": "立方体"},
    "sphere": {"type": "sphere", "radius": 1.5, "color": 0xff0000, "name": "球体"},
    "cylinder": {"type": "cylinder", "radius": 1, "height": 3, "color": 0x0000ff, "name": "圆柱体"},
    "cone": {"type": "cone", "radius": 1.5, "height": 3, "color": 0xff00ff, "name": "圆锥体"},
    "torus": {"type": "torus", "radius": 2, "tube": 0.5, "color": 0x00ffff, "name": "圆环"},
    
    # 分子
    "water": {"type": "molecule", "formula": "H2O", "name": "水分子"},
    "methane": {"type": "molecule", "formula": "CH4", "name": "甲烷"},
    "dna": {"type": "dna", "name": "DNA 双螺旋"},
    
    # 细胞
    "cell": {"type": "sphere", "radius": 3, "color": 0x90EE90, "transparent": True, "opacity": 0.7, "name": "细胞"},
}

# HTML 模板
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg-primary: {bg_primary};
            --bg-secondary: {bg_secondary};
            --bg-card: {bg_card};
            --text-primary: {text_primary};
            --text-secondary: {text_secondary};
            --accent: {accent};
            --accent-glow: {accent_glow};
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        /* 导航栏 */
        .navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: rgba({nav_rgba}, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba({accent_rgb}, 0.2);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2rem;
            z-index: 1000;
        }}
        
        .navbar h1 {{
            font-size: 1.2rem;
            background: linear-gradient(135deg, var(--accent), var(--accent-glow));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .nav-info {{
            display: flex;
            align-items: center;
            gap: 1rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }}
        
        .subject-badge {{
            padding: 4px 12px;
            background: rgba({accent_rgb}, 0.2);
            border: 1px solid rgba({accent_rgb}, 0.4);
            border-radius: 20px;
            color: var(--accent);
            font-size: 0.8rem;
        }}
        
        /* 主容器 */
        .main-container {{
            padding-top: 60px;
            min-height: 100vh;
        }}
        
        /* 3D 场景区域 */
        .scene-section {{
            position: relative;
            height: 70vh;
            background: var(--bg-secondary);
        }}
        
        #canvas-container {{
            width: 100%;
            height: 100%;
        }}
        
        .scene-overlay {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba({nav_rgba}, 0.9);
            backdrop-filter: blur(8px);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba({accent_rgb}, 0.2);
            max-width: 300px;
        }}
        
        .scene-controls {{
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .control-btn {{
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 8px;
            background: rgba({nav_rgba}, 0.9);
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }}
        
        .control-btn:hover {{
            background: rgba({accent_rgb}, 0.3);
            transform: scale(1.1);
        }}
        
        /* 内容区域 */
        .content-section {{
            padding: 3rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .section-title {{
            font-size: 2rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, var(--accent), var(--accent-glow));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .section-content {{
            font-size: 1.1rem;
            line-height: 1.8;
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }}
        
        /* 信息卡片 */
        .info-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        
        .info-card {{
            background: var(--bg-card);
            border: 1px solid rgba({accent_rgb}, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }}
        
        .info-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent), var(--accent-glow));
            transform: scaleX(0);
            transition: transform 0.3s;
        }}
        
        .info-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba({accent_rgb}, 0.2);
            border-color: rgba({accent_rgb}, 0.4);
        }}
        
        .info-card:hover::before {{
            transform: scaleX(1);
        }}
        
        .info-card h3 {{
            color: var(--accent);
            margin-bottom: 0.5rem;
            font-size: 1.2rem;
        }}
        
        .info-card p {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
        }}
        
        /* 详情弹窗 */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 2000;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}
        
        .modal.active {{
            display: flex;
        }}
        
        .modal-content {{
            background: var(--bg-card);
            border: 1px solid rgba({accent_rgb}, 0.3);
            border-radius: 20px;
            padding: 2rem;
            max-width: 600px;
            width: 100%;
            max-height: 80vh;
            overflow-y: auto;
            position: relative;
            animation: modalIn 0.3s ease;
        }}
        
        @keyframes modalIn {{
            from {{ opacity: 0; transform: scale(0.9); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        
        .modal-close {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
        }}
        
        /* 测验区域 */
        .quiz-section {{
            background: var(--bg-secondary);
            padding: 3rem 2rem;
            margin-top: 2rem;
        }}
        
        .quiz-container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .quiz-question {{
            font-size: 1.3rem;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
        }}
        
        .quiz-options {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        .quiz-option {{
            padding: 1rem 1.5rem;
            background: var(--bg-card);
            border: 2px solid rgba({accent_rgb}, 0.2);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .quiz-option:hover {{
            border-color: rgba({accent_rgb}, 0.5);
            background: rgba({accent_rgb}, 0.1);
        }}
        
        .quiz-option.correct {{
            border-color: #00ff88;
            background: rgba(0, 255, 136, 0.1);
        }}
        
        .quiz-option.wrong {{
            border-color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
        }}
        
        /* 页脚 */
        .footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
            border-top: 1px solid rgba({accent_rgb}, 0.1);
        }}
        
        /* 加载动画 */
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}
        
        .loading-spinner {{
            width: 50px;
            height: 50px;
            border: 3px solid rgba({accent_rgb}, 0.3);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        /* 标注 */
        .annotation {{
            position: absolute;
            background: rgba({accent_rgb}, 0.9);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            pointer-events: none;
            transform: translate(-50%, -100%);
            margin-top: -10px;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .annotation.visible {{
            opacity: 1;
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>📚 {title}</h1>
        <div class="nav-info">
            <span class="subject-badge">{subject}</span>
            <span>{topic}</span>
        </div>
    </nav>
    
    <main class="main-container">
        <!-- 3D 场景 -->
        <section class="scene-section">
            <div id="canvas-container"></div>
            <div class="loading" id="loading">
                <div class="loading-spinner"></div>
                <p style="margin-top: 1rem; color: var(--text-secondary);">加载 3D 场景中...</p>
            </div>
            
            <div class="scene-overlay">
                <h3 style="color: var(--accent); margin-bottom: 0.5rem;">🖱️ 交互指南</h3>
                <p style="font-size: 0.9rem; color: var(--text-secondary);">
                    • 拖拽旋转视角<br>
                    • 滚轮缩放<br>
                    • 点击对象查看详情
                </p>
            </div>
            
            <div class="scene-controls">
                <button class="control-btn" onclick="resetCamera()" title="重置视角">↺</button>
                <button class="control-btn" onclick="toggleAutoRotate()" title="自动旋转">⟲</button>
                <button class="control-btn" onclick="toggleTheme()" title="切换主题">☀</button>
            </div>
        </section>
        
        <!-- 内容区域 -->
        <section class="content-section">
            <h2 class="section-title">课程介绍</h2>
            <div class="section-content">
                {description}
            </div>
            
            <h2 class="section-title">知识点</h2>
            <div class="info-cards" id="info-cards">
                {info_cards}
            </div>
        </section>
        
        {quiz_section}
    </main>
    
    <!-- 详情弹窗 -->
    <div class="modal" id="detail-modal">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal()">×</button>
            <h2 id="modal-title" style="color: var(--accent); margin-bottom: 1rem;"></h2>
            <div id="modal-body"></div>
        </div>
    </div>
    
    <footer class="footer">
        <p>由 3D Interactive Lesson Generator 生成 · {current_date}</p>
    </footer>
    
    <script>
        // 3D 场景变量
        let scene, camera, renderer, controls;
        let objects = {{}};
        let autoRotate = false;
        let currentTheme = '{theme}';
        
        // 初始化场景
        function initScene() {{
            const container = document.getElementById('canvas-container');
            
            // 场景
            scene = new THREE.Scene();
            scene.background = new THREE.Color(currentTheme === 'dark' ? 0x0a0a0a : 0xf5f5f5);
            
            // 相机
            camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 5, 15);
            
            // 渲染器
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            container.appendChild(renderer.domElement);
            
            // 控制器
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.minDistance = 5;
            controls.maxDistance = 50;
            
            // 灯光
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(10, 10, 5);
            directionalLight.castShadow = true;
            scene.add(directionalLight);
            
            // 点光源（用于效果）
            const pointLight = new THREE.PointLight({accent_color}, 0.5, 100);
            pointLight.position.set(0, 0, 0);
            scene.add(pointLight);
            
            // 创建模型
            createModels();
            
            // 隐藏加载
            document.getElementById('loading').style.display = 'none';
            
            // 开始渲染
            animate();
            
            // 窗口调整
            window.addEventListener('resize', onWindowResize);
            
            // 点击事件
            renderer.domElement.addEventListener('click', onMouseClick);
        }}
        
        // 创建模型
        function createModels() {{
            const models = {models_json};
            
            models.forEach((modelData, index) => {{
                const def = {builtin_models_json}[modelData.id];
                if (!def) return;
                
                let geometry, material, mesh;
                
                switch(def.type) {{
                    case 'sphere':
                        geometry = new THREE.SphereGeometry(def.radius, 32, 32);
                        break;
                    case 'box':
                        geometry = new THREE.BoxGeometry(...def.size);
                        break;
                    case 'cylinder':
                        geometry = new THREE.CylinderGeometry(def.radius, def.radius, def.height, 32);
                        break;
                    case 'cone':
                        geometry = new THREE.ConeGeometry(def.radius, def.height, 32);
                        break;
                    case 'torus':
                        geometry = new THREE.TorusGeometry(def.radius, def.tube, 16, 100);
                        break;
                    default:
                        geometry = new THREE.SphereGeometry(1, 32, 32);
                }}
                
                material = new THREE.MeshPhongMaterial({{
                    color: def.color,
                    emissive: def.emissive || 0x000000,
                    transparent: def.transparent || false,
                    opacity: def.opacity || 1.0,
                    shininess: 100
                }});
                
                mesh = new THREE.Mesh(geometry, material);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                
                // 位置（如果是太阳系模型，按轨道排列）
                if ('{topic}'.includes('太阳系') || '{topic}'.includes('行星')) {{
                    const distance = (index + 1) * 3;
                    const angle = (index / models.length) * Math.PI * 2;
                    mesh.position.set(Math.cos(angle) * distance, 0, Math.sin(angle) * distance);
                }} else {{
                    mesh.position.set((index - models.length/2) * 4, 0, 0);
                }}
                
                mesh.userData = {{ name: def.name, info: modelData.info || '' }};
                objects[def.name] = mesh;
                scene.add(mesh);
                
                // 如果是土星，添加环
                if (def.rings) {{
                    const ringGeometry = new THREE.RingGeometry(def.radius * 1.4, def.radius * 2.2, 64);
                    const ringMaterial = new THREE.MeshBasicMaterial({{
                        color: 0xC4A35A,
                        side: THREE.DoubleSide,
                        transparent: true,
                        opacity: 0.6
                    }});
                    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
                    ring.rotation.x = Math.PI / 2;
                    mesh.add(ring);
                }}
            }});
        }}
        
        // 动画循环
        function animate() {{
            requestAnimationFrame(animate);
            
            controls.update();
            
            if (autoRotate) {{
                scene.rotation.y += 0.001;
            }}
            
            // 自转动画
            Object.values(objects).forEach((obj, i) => {{
                obj.rotation.y += 0.01 * (i + 1) * 0.1;
            }});
            
            renderer.render(scene, camera);
        }}
        
        // 窗口调整
        function onWindowResize() {{
            const container = document.getElementById('canvas-container');
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }}
        
        // 鼠标点击
        function onMouseClick(event) {{
            const mouse = new THREE.Vector2();
            const container = document.getElementById('canvas-container');
            const rect = container.getBoundingClientRect();
            
            mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / container.clientHeight) * 2 + 1;
            
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, camera);
            
            const intersects = raycaster.intersectObjects(Object.values(objects));
            
            if (intersects.length > 0) {{
                const obj = intersects[0].object;
                showModal(obj.userData.name, obj.userData.info);
            }}
        }}
        
        // 重置相机
        function resetCamera() {{
            camera.position.set(0, 5, 15);
            camera.lookAt(0, 0, 0);
            controls.reset();
        }}
        
        // 切换自动旋转
        function toggleAutoRotate() {{
            autoRotate = !autoRotate;
        }}
        
        // 切换主题
        function toggleTheme() {{
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            location.reload(); // 简化处理，实际应该动态切换CSS变量
        }}
        
        // 显示弹窗
        function showModal(title, content) {{
            document.getElementById('modal-title').textContent = title;
            document.getElementById('modal-body').innerHTML = content;
            document.getElementById('detail-modal').classList.add('active');
        }}
        
        // 关闭弹窗
        function closeModal() {{
            document.getElementById('detail-modal').classList.remove('active');
        }}
        
        // 点击弹窗外部关闭
        document.getElementById('detail-modal').addEventListener('click', function(e) {{
            if (e.target === this) closeModal();
        }});
        
        // 测验功能
        {quiz_js}
        
        // 初始化
        initScene();
    </script>
</body>
</html>'''

# 主题配色
THEMES = {
    "dark": {
        "bg_primary": "#0a0a0a",
        "bg_secondary": "#1a1a1a",
        "bg_card": "#242424",
        "text_primary": "#ffffff",
        "text_secondary": "#a0a0a0",
        "accent": "#00d4ff",
        "accent_glow": "#00ff88",
        "accent_color": "0x00d4ff",
        "accent_rgb": "0, 212, 255",
        "nav_rgba": "26, 26, 26",
    },
    "light": {
        "bg_primary": "#f5f5f5",
        "bg_secondary": "#ffffff",
        "bg_card": "#ffffff",
        "text_primary": "#1a1a1a",
        "text_secondary": "#666666",
        "accent": "#0066cc",
        "accent_glow": "#00aa66",
        "accent_color": "0x0066cc",
        "accent_rgb": "0, 102, 204",
        "nav_rgba": "255, 255, 255",
    },
}


def generate_lesson(args):
    """生成课程 HTML"""
    theme = THEMES.get(args.theme, THEMES["dark"])
    
    # 准备模型数据
    models = []
    if args.models:
        model_ids = [m.strip() for m in args.models.split(",")]
        for mid in model_ids:
            if mid in BUILTIN_MODELS:
                models.append({
                    "id": mid,
                    "info": f"<p>这是{BUILTIN_MODELS[mid]['name']}的详细信息。</p><p>您可以在这里添加更多描述、公式、图片等内容。</p>"
                })
    
    # 生成信息卡片
    info_cards = ""
    for model in models:
        def_info = BUILTIN_MODELS.get(model["id"], {})
        info_cards += f'''
        <div class="info-card" onclick="showModal('{def_info.get('name', '')}', '{model['info']}' )">
            <h3>{def_info.get('name', '')}</h3>
            <p>点击查看详细信息</p>
        </div>'''
    
    # 测验部分
    quiz_section = ""
    quiz_js = ""
    if args.quizzes:
        quiz_section = '''
        <section class="quiz-section">
            <div class="quiz-container">
                <h2 class="section-title">📝 知识测验</h2>
                <div id="quiz-content">
                    <div class="quiz-question">哪个行星是太阳系中最大的？</div>
                    <div class="quiz-options">
                        <div class="quiz-option" onclick="checkAnswer(this, false)">A. 地球</div>
                        <div class="quiz-option" onclick="checkAnswer(this, true)">B. 木星</div>
                        <div class="quiz-option" onclick="checkAnswer(this, false)">C. 土星</div>
                        <div class="quiz-option" onclick="checkAnswer(this, false)">D. 火星</div>
                    </div>
                </div>
            </div>
        </section>'''
        quiz_js = '''
        function checkAnswer(element, isCorrect) {
            element.classList.add(isCorrect ? 'correct' : 'wrong');
            if (isCorrect) {
                setTimeout(() => alert('回答正确！'), 100);
            }
        }
        '''
    
    # 填充模板
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')
    html = HTML_TEMPLATE.format(
        title=args.title,
        subject=args.subject,
        topic=args.topic,
        description=args.content or f"本课程将带您深入了解{args.topic}的奥秘。",
        info_cards=info_cards,
        quiz_section=quiz_section,
        quiz_js=quiz_js,
        models_json=json.dumps(models),
        builtin_models_json=json.dumps(BUILTIN_MODELS),
        theme=args.theme,
        current_date=current_date,
        **theme
    )
    
    return html


def main():
    parser = argparse.ArgumentParser(description="生成 3D 互动教学课件")
    parser.add_argument("--title", help="课程标题")
    parser.add_argument("--subject", default="科学", help="学科")
    parser.add_argument("--topic", help="主题")
    parser.add_argument("--content", help="课程内容描述")
    parser.add_argument("--models", help="3D 模型列表，逗号分隔")
    parser.add_argument("--theme", choices=["dark", "light"], default="dark", help="主题")
    parser.add_argument("--interactive", action="store_true", help="启用交互")
    parser.add_argument("--quizzes", action="store_true", help="添加测验")
    parser.add_argument("--output", "-o", required=True, help="输出文件")
    parser.add_argument("--config", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 如果提供了配置文件
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
            for key, value in config.items():
                if not getattr(args, key, None):
                    setattr(args, key, value)
    
    # 验证必需参数
    if not args.title or not args.topic:
        parser.error("需要提供 --title 和 --topic 参数，或通过 --config 提供配置文件")
    
    # 生成 HTML
    html = generate_lesson(args)
    
    # 写入文件
    output_path = Path(args.output)
    output_path.write_text(html, encoding='utf-8')
    
    print(f"✅ 课件已生成: {output_path.absolute()}")
    print(f"   标题: {args.title}")
    print(f"   主题: {args.topic}")
    print(f"   模型数: {len(args.models.split(',')) if args.models else 0}")


if __name__ == "__main__":
    main()
