#!/bin/bash
# 🏯 数字宫廷 - 初始化脚本
# 一键配置三宫六院制OpenClaw

echo "🏯 数字宫廷初始化"
echo "=================="
echo ""

# 检查OpenClaw配置目录
CONFIG_DIR="$HOME/.openclaw"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "❌ 未找到OpenClaw配置目录"
    exit 1
fi

# 备份原配置
echo "📦 备份原配置..."
if [ -f "$CONFIG_DIR/openclaw.json" ]; then
    cp "$CONFIG_DIR/openclaw.json" "$CONFIG_DIR/openclaw.json.backup.$(date +%Y%m%d)"
    echo "✅ 原配置已备份"
fi

# 复制宫廷配置
echo "🏛️ 安装宫廷配置..."
cp "$(dirname "$0")/.openclaw/court-agents.json" "$CONFIG_DIR/court-agents.json"
echo "✅ 宫廷配置已安装"

# 创建快捷命令
echo "⚡ 创建快捷命令..."

# 添加到.bashrc或.zshrc
SHELL_RC="$HOME/.zshrc"
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

# 检查是否已添加
if ! grep -q "# 数字宫廷快捷命令" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" << 'EOF'

# 数字宫廷快捷命令
alias 李德全='echo "🏯 大内总管李德全，听候皇上差遣！"'
alias 皇后='echo "👑 皇后娘娘驾到"'
alias 代码贵妃='echo "🧑‍💻 Python贵妃在景阳宫待命"'
alias 文案贵妃='echo "✍️ 墨香贵妃在承乾宫待命"'
alias 后宫='echo "🏛️ 数字宫廷成员：李德全(总管)、皇后(首席)、Python贵妃(代码)、墨香贵妃(文案)、算珠妃(数据)、探花妃(搜索)、绮罗嫔(设计)、护卫嫔(安全)、夫子贵人(教学)、剪辑贵人(视频)、闹钟常在(提醒)、笔墨答应(记录)"'

EOF
    echo "✅ 快捷命令已添加到 $SHELL_RC"
    echo "   请运行: source $SHELL_RC"
else
    echo "✅ 快捷命令已存在"
fi

echo ""
echo "🎉 数字宫廷初始化完成！"
echo ""
echo "📖 使用方法："
echo "   1. 重启OpenClaw: openclaw gateway restart"
echo "   2. 在Telegram中使用 /李德全 召唤总管"
echo "   3. 或直接召唤各宫娘娘: /代码、/文案、/数据 等"
echo ""
echo "🏛️ 宫廷成员："
echo "   👑 皇上（用户）"
echo "   🏯 大内总管 李德全（总调度）"
echo "   👸 皇后 富察氏（首席智囊）"
echo "   🧑‍💻 代码贵妃 Python娘娘（景阳宫）"
echo "   ✍️ 文案贵妃 墨香娘娘（承乾宫）"
echo "   📊 数据妃 算珠娘娘（钟粹宫）"
echo "   🔍 搜索妃 探花娘娘（延禧宫）"
echo "   🎨 设计嫔 绮罗娘娘（永和宫）"
echo "   🛡️ 安全嫔 护卫娘娘（景仁宫）"
echo "   📚 教学贵人 夫子娘娘（储秀宫）"
echo "   🎬 视频贵人 剪辑娘娘（翊坤宫）"
echo "   ⏰ 提醒常在 闹钟娘娘（启祥宫）"
echo "   📝 记录答应 笔墨娘娘（长春宫）"
echo ""
echo "🎯 试试这些命令："
echo "   /李德全 生成日报"
echo "   /代码 写个爬虫"
echo "   /文案 写篇文章"
echo "   /数据 分析文件"
echo "   /搜索 查资料"
echo ""
