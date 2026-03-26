# form-link-to-info

批量链接研究分析工具 —— Claude Code Skill。

给一批 URL，自动逐个访问、提取正文、判断类型、按不同模板生成结构化分析报告。

## 功能

- **正文提取**：Jina Reader → WebFetch → 浏览器自动化（Playwright / Chrome），多级降级策略
- **类型识别**：自动分类为 Git 仓库 / 产品官网 / 文章 / 视频 / 社媒帖文 / 文档 / 平台等
- **差异化分析**：不同类型使用不同分析卡模板（项目分析卡、产品研究卡、内容洞察卡等）
- **多视角判断**：综合技术、产品、投资、内容创作视角给出独立判断和后续行动建议
- **多种输出**：Notion / 单文件 Markdown / 多文件 Markdown / Prompt 模式（喂给其他 AI 平台）
- **配置进化**：偏好和模板累积在 `~/.config/link-researcher/`，越用越贴合个人需求

## 安装

### Claude Code

```bash
claude install-skill https://github.com/imarco/form-link-to-info
```

## 使用

在 Claude Code 中直接说：

```
帮我研究这些链接：
https://github.com/anthropics/claude-code
https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview
https://simonwillison.net/2025/Jan/24/claude-code/
```

或者：

```
看看这些链接，输出成 prompt 模式，我要喂给 deepseek 做进一步整理：
https://github.com/langgenius/dify
https://dify.ai/
```

## 配置

首次使用时自动初始化 `~/.config/link-researcher/`：

```
~/.config/link-researcher/
├── config.toml        # 全局设置（默认输出方式、批量大小等）
├── personas/          # 分析视角定义
├── templates/         # 自定义分析卡模板（覆盖默认）
├── good-shots/        # 优质输出示例（质量标杆）
└── preferences.md     # 累积偏好
```

## License

MIT
