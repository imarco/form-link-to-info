#!/bin/bash
# Initialize default configuration for link-researcher skill

CONFIG_DIR="$HOME/.config/link-researcher"

# Create directory structure
mkdir -p "$CONFIG_DIR/personas"
mkdir -p "$CONFIG_DIR/templates"
mkdir -p "$CONFIG_DIR/good-shots"

# Write default config if not exists
if [ ! -f "$CONFIG_DIR/config.toml" ]; then
cat > "$CONFIG_DIR/config.toml" << 'TOML'
# Link Researcher 配置文件
# 修改此文件来自定义分析行为

# 默认输出方式: "notion" | "markdown" | "multi-file" | "prompt"
default_output = "markdown"

# 输出目录（markdown/multi-file 模式），留空则使用当前工作目录
output_dir = ""

# 默认语言
language = "zh-CN"

# 每批处理的链接数量上限
batch_size = 15

# 分析时包含的视角，逗号分隔
# 可选: tech, product, investment, content-creator
# 设为 "all" 则全部启用
perspectives = "all"

[notion]
# 目标页面 ID 或数据库 ID（使用 Notion 输出时需配置）
target_page_id = ""
# 是否同时创建数据库条目
create_database_entries = false

[extraction]
# 正文提取的首选工具，按优先级排列
# 可选: "jina", "webfetch", "browser"
# Jina Reader (r.jina.ai) 免费且质量好，推荐作为首选
preferred_order = ["jina", "webfetch", "browser"]

[prompt_mode]
# 是否在 prompt 中包含完整正文（false 则只包含摘要，更精简）
include_full_text = false
TOML
echo "Created default config at $CONFIG_DIR/config.toml"
fi

# Migrate from yaml if exists
if [ -f "$CONFIG_DIR/config.yaml" ] && [ ! -f "$CONFIG_DIR/.migrated" ]; then
  echo "Note: Found old config.yaml. Please migrate settings to config.toml manually."
  echo "  Old: $CONFIG_DIR/config.yaml"
  echo "  New: $CONFIG_DIR/config.toml"
  touch "$CONFIG_DIR/.migrated"
fi

# Write default persona if not exists
if [ ! -f "$CONFIG_DIR/personas/default.md" ]; then
cat > "$CONFIG_DIR/personas/default.md" << 'MD'
# 默认分析视角

分析每个链接时，综合以下视角给出判断：

## 技术视角
- 技术可行性、架构质量、技术栈选择
- 代码质量、维护性、社区活跃度

## 产品视角
- 市场定位、用户价值、产品成熟度
- 与竞品的差异化

## 投资/趋势视角
- 是否代表某个趋势
- 商业模式是否可持续
- 团队/社区的增长势头

## 内容创作视角
- 是否适合作为选题素材
- 信息密度和原创性
- 是否值得二次创作或引用

根据链接的具体类型，侧重最相关的 1-2 个视角。
MD
echo "Created default persona at $CONFIG_DIR/personas/default.md"
fi

# Write default preferences if not exists
if [ ! -f "$CONFIG_DIR/preferences.md" ]; then
cat > "$CONFIG_DIR/preferences.md" << 'MD'
# 累积偏好

这个文件记录用户在使用过程中积累的偏好和特殊规则。
当用户说"记住这个"、"以后都这样处理"时，在这里添加条目。

## 特殊处理规则

## 格式偏好

## 关注重点

MD
echo "Created preferences file at $CONFIG_DIR/preferences.md"
fi

# Write good-shots README if directory is empty
if [ ! -f "$CONFIG_DIR/good-shots/README.md" ]; then
cat > "$CONFIG_DIR/good-shots/README.md" << 'MD'
# Good Shots — 优质输出示例

将你认可的输出示例放在这里，按链接类型命名：

- `github-repo.md` — Git 仓库的理想输出
- `product.md` — 产品官网的理想输出
- `article.md` — 文章/博客的理想输出
- `video.md` — 视频的理想输出
- `social-media.md` — 社媒帖文的理想输出
- `docs-tutorial.md` — 文档/教程的理想输出
- `platform.md` — 导航站/平台的理想输出

这些示例会被 skill 读取，作为生成分析卡时的质量标杆。
MD
echo "Created good-shots README at $CONFIG_DIR/good-shots/README.md"
fi

echo ""
echo "Link Researcher config initialized at $CONFIG_DIR"
echo ""
echo "Directory structure:"
echo "  $CONFIG_DIR/"
echo "  ├── config.toml        # 全局设置"
echo "  ├── personas/          # 分析视角"
echo "  │   └── default.md"
echo "  ├── templates/         # 自定义分析卡模板"
echo "  ├── good-shots/        # 优质输出示例"
echo "  │   └── README.md"
echo "  └── preferences.md     # 累积偏好"
