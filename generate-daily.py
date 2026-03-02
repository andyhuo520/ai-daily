#!/usr/bin/env python3
"""
AI Daily 新闻日报生成器
数据来源：Hacker News, Reddit, Product Hunt 等
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import os
import re

# ============ 配置 ============
DATA_SOURCES = {
    "hacker_news": {
        "name": "Hacker News",
        "icon": "phosphor:fire-duotone",
        "color": "#FF6600",
        "enabled": True
    },
    "reddit_ml": {
        "name": "Reddit r/MachineLearning",
        "icon": "phosphor:reddit-logo-duotone",
        "color": "#FF4500",
        "enabled": True
    },
    "reddit_artificial": {
        "name": "Reddit r/artificial",
        "icon": "phosphor:reddit-logo-duotone",
        "color": "#FF4500",
        "enabled": True
    },
    "reddit_openai": {
        "name": "Reddit r/OpenAI",
        "icon": "phosphor:reddit-logo-duotone",
        "color": "#FF4500",
        "enabled": True
    },
    "product_hunt": {
        "name": "Product Hunt AI",
        "icon": "phosphor:package-duotone",
        "color": "#DA552F",
        "enabled": False  # 需要API key
    }
}

AI_KEYWORDS = [
    'AI', 'artificial intelligence', 'machine learning', 'deep learning',
    'LLM', 'GPT', 'neural', 'OpenAI', 'Claude', 'Gemini', 'agent', 
    'robot', 'automation', 'transformer', 'diffusion', 'RAG', 'embedding',
    'training', 'inference', 'model', 'GPT-5', 'AGI', 'ChatGPT', 'Copilot',
    '人工智能', '机器学习', '深度学习', '大模型', 'AI', 'LLM'
]

def fetch_hacker_news_ai(limit=15):
    """从Hacker News获取AI相关新闻"""
    print("📡 正在获取 Hacker News 数据...")
    
    try:
        # 获取top stories
        with urllib.request.urlopen("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10) as r:
            story_ids = json.load(r)[:100]
        
        stories = []
        for sid in story_ids:
            if len(stories) >= limit:
                break
            try:
                with urllib.request.urlopen(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5) as r:
                    story = json.load(r)
                
                title = story.get('title', '')
                # 过滤AI相关
                if any(kw.lower() in title.lower() for kw in AI_KEYWORDS):
                    stories.append({
                        'title': title,
                        'url': story.get('url', f"https://news.ycombinator.com/item?id={sid}"),
                        'score': story.get('score', 0),
                        'comments': story.get('descendants', 0),
                        'source': 'Hacker News'
                    })
            except:
                continue
        
        print(f"   ✅ 获取到 {len(stories)} 条AI相关新闻")
        return sorted(stories, key=lambda x: x['score'], reverse=True)
    
    except Exception as e:
        print(f"   ❌ 获取失败: {e}")
        return []

def fetch_reddit(subreddit, limit=10):
    """从Reddit获取帖子"""
    print(f"📡 正在获取 Reddit r/{subreddit} 数据...")
    
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AI Daily Bot',
            'Accept': 'application/json'
        })
        
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.load(r)
        
        posts = []
        for child in data['data']['children']:
            post = child['data']
            # 跳过置顶帖和招聘帖
            if post.get('stickied', False):
                continue
            if 'hiring' in post.get('title', '').lower():
                continue
                
            posts.append({
                'title': post['title'],
                'url': f"https://reddit.com{post['permalink']}",
                'score': post['score'],
                'comments': post['num_comments'],
                'source': f'Reddit r/{subreddit}'
            })
            
            if len(posts) >= limit:
                break
        
        print(f"   ✅ 获取到 {len(posts)} 条帖子")
        return posts
    
    except Exception as e:
        print(f"   ❌ 获取失败: {e}")
        return []

def categorize_news(news_list):
    """将新闻分类"""
    categories = {
        'cover': [],      # 头条（高热度）
        'research': [],   # 研究/技术
        'product': [],    # 产品/发布
        'industry': [],   # 行业/商业
        'tools': [],      # 工具/开源
        'discussion': []  # 讨论/观点
    }
    
    # 关键词分类
    research_kw = ['paper', 'research', 'model', 'training', 'benchmark', 'arxiv', 'study', '新研究', '论文']
    product_kw = ['launch', 'release', 'announce', 'new', 'update', '发布', '推出', '更新']
    industry_kw = ['funding', 'acquire', 'invest', 'market', 'business', '融资', '收购', '投资']
    tools_kw = ['open source', 'github', 'tool', 'library', 'framework', '开源', '工具']
    discussion_kw = ['opinion', 'discussion', 'why', 'how', 'what', '思考', '讨论', '观点']
    
    # 先按热度排序
    sorted_news = sorted(news_list, key=lambda x: x.get('score', 0), reverse=True)
    
    for news in sorted_news:
        title_lower = news['title'].lower()
        
        # 头条：热度最高的几条
        if len(categories['cover']) < 3 and news.get('score', 0) > 100:
            categories['cover'].append(news)
            continue
        
        # 分类
        if any(kw in title_lower for kw in research_kw):
            categories['research'].append(news)
        elif any(kw in title_lower for kw in product_kw):
            categories['product'].append(news)
        elif any(kw in title_lower for kw in industry_kw):
            categories['industry'].append(news)
        elif any(kw in title_lower for kw in tools_kw):
            categories['tools'].append(news)
        elif any(kw in title_lower for kw in discussion_kw):
            categories['discussion'].append(news)
        else:
            # 默认放到研究或产品
            if len(categories['research']) < len(categories['product']):
                categories['research'].append(news)
            else:
                categories['product'].append(news)
    
    return categories

def generate_html(categories, date_str, prev_date=None, next_date=None):
    """生成HTML页面"""
    
    weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekday = weekday_names[date_obj.weekday()]
    
    # 日期导航
    prev_link = f"archive/{prev_date}.html" if prev_date else "#"
    next_link = f"archive/{next_date}.html" if next_date else "#"
    today_link = "index.html"
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智讯 · {date_str}</title>
    <script src="https://code.iconify.design/3/3.1.0/iconify.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --cream: #FAF7F2;
            --cream-dark: #F5F0E8;
            --beige: #E8E0D5;
            --gold: #C9A962;
            --gold-light: #D4B978;
            --charcoal: #2C2824;
            --warm-gray: #8B8680;
            --border: rgba(201,169,98,0.3);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans SC', -apple-system, sans-serif;
            background: var(--cream);
            color: var(--charcoal);
            line-height: 1.8;
        }}
        
        /* 导航栏 */
        .navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(44, 40, 36, 0.95);
            backdrop-filter: blur(10px);
            z-index: 1000;
            border-bottom: 1px solid var(--gold);
        }}
        .navbar-inner {{
            max-width: 900px;
            margin: 0 auto;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .navbar-brand {{
            font-family: 'Noto Serif SC', serif;
            font-size: 20px;
            color: var(--gold);
            text-decoration: none;
            font-weight: 600;
        }}
        .navbar-links {{
            display: flex;
            gap: 20px;
            align-items: center;
        }}
        .navbar-links a {{
            color: var(--beige);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.2s;
        }}
        .navbar-links a:hover {{
            color: var(--gold);
        }}
        
        /* 日期导航 */
        .date-nav {{
            background: var(--charcoal);
            padding: 60px 20px 40px;
            text-align: center;
        }}
        .date-picker {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .date-btn {{
            background: transparent;
            border: 1px solid var(--gold);
            color: var(--gold);
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .date-btn:hover:not(:disabled) {{
            background: var(--gold);
            color: var(--charcoal);
        }}
        .date-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}
        .current-date {{
            font-family: 'Noto Serif SC', serif;
            font-size: 36px;
            color: var(--cream);
            font-weight: 600;
        }}
        .current-weekday {{
            color: var(--gold);
            font-size: 16px;
            margin-top: 8px;
        }}
        
        /* 分类区块 */
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .section {{
            margin-bottom: 50px;
        }}
        .section-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 25px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--border);
        }}
        .section-header h2 {{
            font-family: 'Noto Serif SC', serif;
            font-size: 22px;
            color: var(--charcoal);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-header .iconify {{
            color: var(--gold);
            font-size: 24px;
        }}
        
        /* 新闻卡片 */
        .news-card {{
            background: var(--cream-dark);
            border: 1px solid var(--beige);
            padding: 25px;
            margin-bottom: 15px;
            transition: all 0.3s;
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        .news-card:hover {{
            border-color: var(--gold);
            transform: translateX(5px);
        }}
        .news-title {{
            font-size: 17px;
            font-weight: 500;
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        .news-meta {{
            display: flex;
            gap: 20px;
            font-size: 13px;
            color: var(--warm-gray);
        }}
        .news-meta span {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .source-tag {{
            background: var(--gold);
            color: var(--cream);
            padding: 2px 8px;
            font-size: 11px;
            border-radius: 2px;
        }}
        
        /* 头条特殊样式 */
        .hero-card {{
            background: linear-gradient(135deg, var(--charcoal) 0%, #1A1815 100%);
            color: var(--cream);
            border: 2px solid var(--gold);
            padding: 35px;
        }}
        .hero-card .news-title {{
            font-family: 'Noto Serif SC', serif;
            font-size: 24px;
            font-weight: 600;
        }}
        .hero-card .news-meta {{
            color: var(--beige);
        }}
        
        /* 数据来源 */
        .sources {{
            background: var(--cream-dark);
            padding: 30px;
            margin-top: 50px;
            border: 1px solid var(--beige);
        }}
        .sources h3 {{
            font-family: 'Noto Serif SC', serif;
            font-size: 18px;
            margin-bottom: 15px;
            color: var(--charcoal);
        }}
        .source-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
            font-size: 14px;
            color: var(--warm-gray);
        }}
        .source-item .iconify {{
            font-size: 18px;
            color: var(--gold);
        }}
        
        /* 页脚 */
        footer {{
            text-align: center;
            padding: 40px 20px;
            background: var(--charcoal);
            color: var(--beige);
            font-size: 14px;
        }}
        footer a {{
            color: var(--gold);
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar">
        <div class="navbar-inner">
            <a href="index.html" class="navbar-brand">智讯 AI Daily</a>
            <div class="navbar-links">
                <a href="archive.html">📖 往期回顾</a>
                <a href="https://github.com/andyhuo520/ai-daily" target="_blank">GitHub</a>
            </div>
        </div>
    </nav>
    
    <!-- 日期导航 -->
    <div class="date-nav">
        <div class="date-picker">
            <button class="date-btn" onclick="location.href='{prev_link}'" {'disabled' if not prev_date else ''}>
                <span class="iconify" data-icon="phosphor:caret-left"></span>
                前一天
            </button>
            <button class="date-btn" onclick="location.href='{today_link}'">
                <span class="iconify" data-icon="phosphor:calendar-duotone"></span>
                今天
            </button>
            <button class="date-btn" onclick="location.href='{next_link}'" {'disabled' if not next_date else ''}>
                后一天
                <span class="iconify" data-icon="phosphor:caret-right"></span>
            </button>
        </div>
        <div class="current-date">{date_obj.strftime("%Y年%m月%d日")}</div>
        <div class="current-weekday">{weekday}</div>
    </div>
    
    <!-- 内容区 -->
    <div class="container">
'''
    
    # 头条
    if categories['cover']:
        html += '''
        <section class="section">
            <div class="section-header">
                <h2><span class="iconify" data-icon="phosphor:star-duotone"></span>今日头条</h2>
            </div>
'''
        for news in categories['cover'][:3]:
            html += f'''
            <a href="{news['url']}" target="_blank" class="news-card hero-card">
                <div class="news-title">{news['title']}</div>
                <div class="news-meta">
                    <span><span class="iconify" data-icon="phosphor:arrow-up"></span>{news['score']}</span>
                    <span><span class="iconify" data-icon="phosphor:chat-circle"></span>{news['comments']}</span>
                    <span class="source-tag">{news['source']}</span>
                </div>
            </a>
'''
        html += '        </section>\n'
    
    # 研究/技术
    if categories['research']:
        html += '''
        <section class="section">
            <div class="section-header">
                <h2><span class="iconify" data-icon="phosphor:brain-duotone"></span>研究与技术</h2>
            </div>
'''
        for news in categories['research'][:5]:
            html += f'''
            <a href="{news['url']}" target="_blank" class="news-card">
                <div class="news-title">{news['title']}</div>
                <div class="news-meta">
                    <span><span class="iconify" data-icon="phosphor:arrow-up"></span>{news['score']}</span>
                    <span><span class="iconify" data-icon="phosphor:chat-circle"></span>{news['comments']}</span>
                    <span class="source-tag">{news['source']}</span>
                </div>
            </a>
'''
        html += '        </section>\n'
    
    # 产品/发布
    if categories['product']:
        html += '''
        <section class="section">
            <div class="section-header">
                <h2><span class="iconify" data-icon="phosphor:rocket-duotone"></span>产品与发布</h2>
            </div>
'''
        for news in categories['product'][:5]:
            html += f'''
            <a href="{news['url']}" target="_blank" class="news-card">
                <div class="news-title">{news['title']}</div>
                <div class="news-meta">
                    <span><span class="iconify" data-icon="phosphor:arrow-up"></span>{news['score']}</span>
                    <span><span class="iconify" data-icon="phosphor:chat-circle"></span>{news['comments']}</span>
                    <span class="source-tag">{news['source']}</span>
                </div>
            </a>
'''
        html += '        </section>\n'
    
    # 行业/商业
    if categories['industry']:
        html += '''
        <section class="section">
            <div class="section-header">
                <h2><span class="iconify" data-icon="phosphor:trend-up-duotone"></span>行业动态</h2>
            </div>
'''
        for news in categories['industry'][:5]:
            html += f'''
            <a href="{news['url']}" target="_blank" class="news-card">
                <div class="news-title">{news['title']}</div>
                <div class="news-meta">
                    <span><span class="iconify" data-icon="phosphor:arrow-up"></span>{news['score']}</span>
                    <span><span class="iconify" data-icon="phosphor:chat-circle"></span>{news['comments']}</span>
                    <span class="source-tag">{news['source']}</span>
                </div>
            </a>
'''
        html += '        </section>\n'
    
    # 工具/开源
    if categories['tools']:
        html += '''
        <section class="section">
            <div class="section-header">
                <h2><span class="iconify" data-icon="phosphor:code-duotone"></span>工具与开源</h2>
            </div>
'''
        for news in categories['tools'][:5]:
            html += f'''
            <a href="{news['url']}" target="_blank" class="news-card">
                <div class="news-title">{news['title']}</div>
                <div class="news-meta">
                    <span><span class="iconify" data-icon="phosphor:arrow-up"></span>{news['score']}</span>
                    <span><span class="iconify" data-icon="phosphor:chat-circle"></span>{news['comments']}</span>
                    <span class="source-tag">{news['source']}</span>
                </div>
            </a>
'''
        html += '        </section>\n'
    
    # 数据来源
    html += f'''
        <!-- 数据来源 -->
        <div class="sources">
            <h3>📡 数据来源</h3>
            <div class="source-item">
                <span class="iconify" data-icon="phosphor:fire-duotone"></span>
                Hacker News - Y Combinator技术社区热门
            </div>
            <div class="source-item">
                <span class="iconify" data-icon="phosphor:reddit-logo-duotone"></span>
                Reddit r/MachineLearning - 机器学习讨论
            </div>
            <div class="source-item">
                <span class="iconify" data-icon="phosphor:reddit-logo-duotone"></span>
                Reddit r/artificial - 人工智能资讯
            </div>
            <div class="source-item">
                <span class="iconify" data-icon="phosphor:reddit-logo-duotone"></span>
                Reddit r/OpenAI - OpenAI相关讨论
            </div>
        </div>
    </div>
    
    <!-- 页脚 -->
    <footer>
        <p>智讯 AI Daily · 每日AI资讯精选</p>
        <p style="margin-top: 8px; font-size: 12px;">
            Generated by <a href="https://github.com/andyhuo520/ai-daily" target="_blank">OpenClaw</a> · 
            {datetime.now().strftime("%Y-%m-%d %H:%M")}
        </p>
    </footer>
</body>
</html>
'''
    
    return html

def main():
    """主函数"""
    print("=" * 50)
    print("📰 AI Daily 新闻日报生成器")
    print("=" * 50)
    
    # 获取今天日期
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 生成日期: {today}\n")
    
    # 收集所有新闻
    all_news = []
    
    # Hacker News
    try:
        hn_news = fetch_hacker_news_ai(limit=8)
        all_news.extend(hn_news)
    except Exception as e:
        print(f"   ⚠️ HN获取失败: {e}")
    
    # Reddit各板块（只取两个最活跃的）
    for subreddit in ['MachineLearning', 'artificial']:
        try:
            reddit_news = fetch_reddit(subreddit, limit=5)
            all_news.extend(reddit_news)
        except Exception as e:
            print(f"   ⚠️ Reddit r/{subreddit}获取失败: {e}")
    
    print(f"\n📊 共收集到 {len(all_news)} 条新闻")
    
    # 分类
    categories = categorize_news(all_news)
    
    # 计算前后日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 生成HTML
    print("\n📝 正在生成HTML...")
    html = generate_html(categories, today, prev_date=yesterday, next_date=None)
    
    # 保存文件
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 保存为index.html（今天的）
    index_path = os.path.join(output_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"   ✅ 已保存: {index_path}")
    
    # 同时保存到archive目录
    archive_dir = os.path.join(output_dir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    archive_path = os.path.join(archive_dir, f'{today}.html')
    with open(archive_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"   ✅ 已存档: {archive_path}")
    
    print("\n" + "=" * 50)
    print("✨ 生成完成！")
    print(f"🌐 访问地址: https://andyhuo520.github.io/ai-daily/")
    print("=" * 50)

if __name__ == '__main__':
    main()
