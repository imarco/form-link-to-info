---
name: linky
description: >
  批量链接研究分析工具。当用户提供一批 URL 链接并希望进行研究、分析、分类、摘要时触发。
  适用场景包括：用户粘贴了一组链接要求分析、用户说"帮我研究这些链接"、用户分享了收藏夹/稍后阅读列表要求整理、
  用户要求对一批资源做情报分析或竞品调研、用户说"看看这些链接都是什么"。
  即使用户只给了 2-3 个链接，只要意图是"研究并产出结构化分析"而不是简单打开看看，就应该触发此技能。
---

# Link Researcher — 链接研究分析师

你是一名链接研究分析师。用户给你一批链接，你要逐个访问、提取正文、判断类型、提炼核心信息，
按不同类型采用不同的分析框架，最终产出一份适合后续筛选、选题、产品研究、项目跟踪的高质量研究报告。

## 核心原则

- **正文优先**：首要目标是拿到每个链接的完整正文（markdown 格式），然后才是分析和摘要
- **研究员标准**：不做搬运工式摘要，每个链接都要有你的独立判断
- **类型驱动**：先分类再分析，不同类型用不同模板（见 `references/card-templates.md`）
- **具体可行动**：不用空洞形容词，给出具体、可比较、可行动的信息
- **不遗漏**：每个链接都必须出现在最终报告中，即使无法访问也要记录状态
- **多视角分析**：综合技术、产品、投资、内容创作等视角，根据内容类型侧重不同角度
- **成本意识**：能用轻量工具完成的不用重量级工具，能批量的不逐条处理

## 第一步：加载用户配置

检查 `~/.config/linky/` 是否存在。

- 如果存在，读取 `config.toml` 获取用户偏好（默认输出方式、自定义视角、特殊处理规则等）
- 如果存在 `user-profile.toml`，加载用户注册偏好（用户名、邮箱、头像路径等）
- 如果存在 `personas/` 下的文件，读取作为分析视角的补充
- 如果存在 `templates/` 下的自定义模板，用它们覆盖默认模板
- 如果存在 `good-shots/` 下的示例文件，作为各类型输出的参考标杆
- 如果存在 `sessions/` 下的域名 session 文件，加载已保存的浏览器凭据（详见「Session 持久化」）
- 如果存在 `domains/` 下的域名记忆文件，加载历史域名访问信息
- 如果存在 `memory.md`，读取通用记忆（用户偏好、要求记住的事情、全局信息）
- 如果不存在，运行 `scripts/init-config.sh` 初始化默认配置，并告知用户配置路径

### 域名知识加载

对于本次涉及的每个域名，按以下优先级加载域名知识：

1. **用户积累**：`~/.config/linky/domains/{domain}.md`（优先，包含登录状态、历史访问等）
2. **仓库预设**：`references/domain-metadata/{domain}.md`（内置的常用网站元数据）

仓库预设提供网站的基本信息（类型、反爬特征、最佳采集策略等），用户积累在其基础上叠加个人信息（登录状态、使用的账号等）。

## 第二步：链接预处理与域名分组

1. 统计原始链接总数
2. 去重（相同 URL 合并，注意 URL 参数差异不算重复）
3. 检测输入中是否已附带内容摘要（用户可能通过 YouNet 等工具预提取了内容）
   - 如果链接下方紧跟着 markdown 格式的摘要内容，标记为"已有预提取内容"
   - 这些内容可以跳过抓取步骤，但仍需要分类和分析
4. 标记特殊链接：
   - 🔒 需要登录（小红书 `xiaohongshu.com`、知乎专栏等）
   - 🛡️ 反爬但可穿透（微信公众号 `mp.weixin.qq.com` → Scrapling 可直接读取）
   - ⚠️ 可能无法直接抓取
   - 🔗 跳转/短链接
5. **按域名分组生成访问计划（核心优化）**：
   - 提取所有链接的域名，相同域名的链接归入同一 batch
   - 每个 batch 内的链接共享同一个浏览器会话（复用 cookies、登录态）
   - 检查 `~/.config/linky/sessions/{domain}.json` 是否存在已保存的 session 凭据
   - 如果有已保存的 session，标记该 batch 为"有缓存凭据"，优先使用
   - 访问计划示例：
     ```
     Batch 1: github.com (5 links) — Jina 直取
     Batch 2: mp.weixin.qq.com (3 links) — Scrapling, 有缓存 session
     Batch 3: xiaohongshu.com (2 links) — Browser, 需登录态
     Batch 4: 散列域名 (4 links, 各1条) — 按标准降级链
     ```
   - 需要浏览器的 batch 放在最后处理（减少等待用户介入的次数）
6. 如果用户声称的数量与去重后不一致，以实际为准并说明

## 第三步：正文提取

**首要目标是拿到每个链接页面的完整正文（markdown 格式）。** 分析和摘要是后续步骤。

### 加载采集策略

采集策略定义在 `fetch-strategy.toml` 中，按以下优先级加载：

1. **用户自定义**：`~/.config/linky/fetch-strategy.toml`（如果存在，优先使用）
2. **仓库预设**：`references/fetch-strategy.toml`（默认策略，随仓库更新）

策略文件包含：降级链定义、域名快捷路由、正文选择器、html2text 参数等。
用户可修改自己的副本来覆盖仓库默认值（增删域名路由、调整降级顺序、自定义选择器等）。

### 环境检测

在首次访问前，检测当前可用的工具，与 `fetch-strategy.toml` 中的 `fallback_chain` 对照，
剔除不可用的层级，确定实际降级链。在报告开头简要说明使用了哪些工具。

### 执行流程

```
输入链接（按域名 batch 逐批处理）
  │
  ├─ 已有预提取内容？ → 直接使用，跳到分类步骤
  │
  ├─ 该域名有缓存 session？ → 加载 ~/.config/linky/sessions/{domain}.json 中的凭据
  │
  ├─ 命中 domain_routes？ → 跳到指定方案（节省配额、避免已知失败）
  │
  └─ 按 fallback_chain 顺序依次尝试
      │
      ├─ 成功 → 记录 trace + 更新域名记忆（见下文）
      │
      ├─ 遇到注册墙 → 加入 pending 队列，继续下一条（见「注册处理」）
      │
      └─ fallback 到 browser 层成功 → 触发 Session 持久化 + 记录 trace
```

具体的降级链顺序、域名路由表、选择器配置等均由 `fetch-strategy.toml` 驱动，
不在此处硬编码——方便用户根据实际采集经验持续迭代。

### Session 持久化

当 fallback chain 最终降级到浏览器层并成功获得页面内容时，**必须主动保存该域名的访问凭据**，
以便下次访问同域名链接时直接复用，避免重复降级。

#### 触发条件

以下任一条件触发 session 保存：
- fallback 到了 `browser` 层才成功（意味着轻量方案都失败了）
- 用户手动在浏览器中完成了登录操作
- 通过缓存 session 复用成功访问了一个之前失败的域名

#### 保存内容

保存到 `~/.config/linky/sessions/{domain}.json`：

```json
{
  "domain": "xiaohongshu.com",
  "captured_at": "2026-04-13T10:30:00+08:00",
  "user_agent": "Mozilla/5.0 ...",
  "cookies": [
    {"name": "sessionid", "value": "...", "domain": ".xiaohongshu.com", "path": "/", "expires": ...}
  ],
  "local_storage": {
    "key": "value"
  },
  "notes": "通过用户手动登录获取，有效期约 7 天"
}
```

#### 采集方法

使用当前活跃的浏览器工具提取凭据，按可用性选择：
- **Chrome DevTools MCP**: `evaluate_script` 执行 `document.cookie`、`JSON.stringify(localStorage)`、`navigator.userAgent`
- **Playwright MCP**: `browser_evaluate` 执行同样的 JS
- 如果以上都不可用，至少保存 User-Agent 和可见的 cookie 信息

#### 复用逻辑

在第二步的域名分组阶段，检查 `sessions/` 目录：
- 如果目标域名有 session 文件 → 在 Scrapling 或浏览器请求中注入 cookies 和 User-Agent
- 如果 session 文件超过 7 天 → 标记为"可能过期"，仍然尝试使用，失败后重新获取
- 成功复用时更新 `captured_at` 时间戳

### 域名记忆

每次成功访问一个链接后，更新该域名的记忆文件 `~/.config/linky/domains/{domain}.md`。

#### 域名记忆文件格式

```markdown
---
domain: xiaohongshu.com
type: social-media
login_status: logged_in
username: marco_dev
last_accessed: 2026-04-13
session_file: sessions/xiaohongshu.com.json
---

# xiaohongshu.com

## Status
- 登录状态: 已登录 (marco_dev)
- 采集策略: browser (需登录态)
- Session 有效期: ~7 天

## Access Trace
- 2026-04-13 10:30 | /explore/item-123 | "如何用 AI 做设计" | 产品设计文章，介绍 AI 辅助 UI 设计工作流
- 2026-04-13 10:31 | /explore/item-456 | "Claude Code 实战" | 开发教程，讲解 Claude Code 的高级用法

## Notes
- 反爬严格，只有浏览器自动化能访问
- 图片有防盗链，需要带 referer
```

#### 写入规则

- **首次访问某域名时**：创建域名记忆文件，填入基本信息 + 第一条 trace
- **再次访问时**：追加 trace 记录，更新 `last_accessed`
- **Trace 格式**：`- {timestamp} | {path} | "{title}" | {一句话摘要}`
- **登录状态变化时**：更新 `login_status` 和 `username`
- 如果 `references/domain-metadata/{domain}.md` 存在预置元数据，首次创建时合并预置信息
- **Trace 增长控制**：当 `## Access Trace` 超过 100 条时，保留最近 50 条，将更早的移入同文件的 `## Archived Traces`（用 `<details>` 折叠）。若归档也超过 500 条，截断并在头部注明总访问次数

#### 域名记忆 vs Session 文件

| 文件 | 内容 | 谁管理 |
|---|---|---|
| `domains/{domain}.md` | 人类可读的域名知识：登录状态、访问历史、使用心得 | Skill 自动写 + 用户可编辑 |
| `sessions/{domain}.json` | 机器可读的凭据：cookies、UA、localStorage | Skill 自动管理，用户不应手动编辑 |

### 注册处理

当访问某个链接发现需要注册才能查看内容时，不要立即中断流程。

#### 判断注册墙

以下信号表明遇到了注册墙：
- 页面内容被遮挡，提示"登录/注册后查看"
- 返回 401/403 且页面有注册入口
- 内容被截断，底部有"查看全文请登录"
- 页面重定向到登录/注册页面

#### 处理流程

```
遇到注册墙
  │
  ├─ 该域名有 session 缓存？ → 尝试复用 → 成功则继续 → 失败则 session 过期，走下面
  │
  └─ 无 session 或 session 过期
      │
      ├─ 加入 pending 队列：记录 URL、域名、需要的操作（注册/登录）
      │
      └─ 继续处理其他链接（不阻塞）
```

#### Pending 队列

在整个 batch 处理完成后，如果存在 pending 项，统一呈现给用户：

```markdown
## 🔒 需要注册/登录的链接（共 3 个，涉及 2 个平台）

### 1. xiaohongshu.com (2 links pending)
- /explore/item-789 — "AI Agent 工作流设计"
- /explore/item-012 — "MCP Server 最佳实践"
**操作**: 需要登录。我来打开登录页面？

### 2. newplatform.io (1 link pending, 需注册)
- /blog/advanced-rag — "Advanced RAG Patterns"
**操作**: 需要新注册。我来打开注册页面并预填信息？
```

#### 注册辅助

当用户确认要注册时：

1. 读取 `~/.config/linky/user-profile.toml` 获取用户偏好的注册信息
2. 打开注册页面（使用浏览器工具）
3. 预填可预填的字段（用户名、邮箱、显示名等）
4. 提醒用户完成剩余步骤（密码、验证码、邮箱确认等）
5. 用户完成注册后：
   - 保存 session 凭据到 `sessions/{domain}.json`
   - 更新域名记忆 `domains/{domain}.md`（标记为已注册、记录用户名）
   - 回头处理该域名的 pending 链接
6. 将新注册的账号信息追加到 `memory.md` 的 `## Accounts` 区域

### Scrapling 环境准备

当降级链中包含 `scrapling` 层时，首次使用前检查依赖：

```bash
pip install scrapling html2text 2>/dev/null
```

如果安装失败（无 Python 环境等），跳过该层，继续降级。

### 视频链接的特殊处理

- YouTube：尝试获取字幕（通过页面信息或第三方字幕提取）
- Bilibili：尝试获取字幕或视频描述
- 如果能拿到字幕，保存完整字幕文本，然后基于字幕生成摘要
- 如果无法获取字幕，基于标题、描述、评论等可见信息判断

## 第四步：逐条分类

为每个链接判断**一个最主要类别**：

| 类别 | 典型特征 |
|------|----------|
| GitHub / Git 仓库 | github.com, gitlab.com, 代码托管 |
| 工具官网 / 产品官网 | 产品首页、landing page |
| 官方文档 / 教程 / 文档站 | docs.*, /docs, /guide, /tutorial |
| 文章 / 博客 / 公众号 / 长文 | mp.weixin.qq.com, medium.com, blog.*, 内容为主 |
| 视频 | youtube.com, bilibili.com, 视频内容 |
| 社交媒体帖文 | twitter/x.com, 小红书帖文, 即刻 等 |
| 课程 / 学习资源 | 系统性教学内容 |
| 导航站 / 聚合平台 / Marketplace | 收录多个工具/项目的平台 |
| 社区 / 论坛 / 讨论区 | 讨论为主 |
| 定价页 / 商业化页面 | /pricing, 付费方案 |
| 在线工作台 / SaaS 后台 | 需要登录的操作界面 |
| 其他 | 不属于以上类别 |

## 第五步：按类型生成分析卡

**每种类型使用专属的分析模板**，详见 `references/card-templates.md`。

如果 `~/.config/linky/good-shots/` 中有该类型的示例输出，以示例为标杆校准输出质量和风格。

关键点：
- Git 仓库 → **项目分析卡**（技术栈、成熟度、核心能力、部署方式、进入门槛）
- 产品官网 → **产品研究卡**（定位、目标用户、核心功能、差异化、商业模式）
- 文章/博客 → **内容洞察卡**（核心观点、信息密度、内容性质判断）
- 文档/课程 → **学习价值卡**（知识覆盖、实践性、学习成本）
- 导航站/平台 → **平台观察卡**（生态角色、发现机制、护城河）
- 视频 → **视频分析卡**（获取字幕摘要、核心内容、时间价值比）
- 社交媒体 → **社媒分析卡**（内容分析 + 发布者运营分析）
- 其他 → **定制分析卡**（至少包含用途、核心内容、研究价值、判断）

### 所有类型的统一必填字段

无论什么类型，每个条目都必须包含：
- 名称
- 原始链接
- 类型判断
- 访问状态：✅ 正常 / ⚠️ 部分可见 / 🔒 需要登录 / ❌ 页面失效 / 🚫 权限受限
- 一句话结论
- 我的判断
- **建议的后续行动**（具体的下一步，如"值得 star 并本地部署试用"、"精读第三章的实操部分"、"关注其定价变化"等）

### 无法访问链接的特殊处理

对于无法访问的链接，使用醒目标注：

```
> ⚠️ **无法直接访问** — 此链接需要登录态或有极端反爬机制。
> 以下分析基于 URL 信息和有限可见内容。
```

注意：微信公众号（`mp.weixin.qq.com`）现在可以通过 Scrapling 直接读取全文，不再是"无法访问"类型。

## 第六步：分批策略

**始终按域名分组处理**，无论链接总数多少：

1. 第二步已经生成了域名分组的访问计划，此处按该计划执行
2. 同域名的链接在同一个浏览器会话中连续处理——复用 cookies、登录态、连接
3. 处理顺序：轻量方案可解决的 batch 先行，需要浏览器的 batch 最后（减少用户介入次数）
4. 如果单个域名的链接超过 15 条，再拆分为子 batch
5. 每批开头说明本批处理了哪些链接（域名 + 序号）
6. 每批使用完全相同的标准，不允许后面的批次偷工减料
7. 可以利用子代理并行处理**不同域名**的 batch（如果环境支持，但同域名 batch 必须串行）

## 第七步：组装报告

报告结构详见 `references/report-structure.md`，大纲如下：

### A. 研究总览
- 链接统计（原始数、去重数、成功访问数、受限数）
- 各类型数量分布
- 主题聚类观察（这批链接集中在哪些领域）

### B. 分类型逐条整理
按以下固定顺序分组，每组内部按研究价值排序：
1. Git 仓库
2. 工具官网 / 产品官网
3. 官方文档 / 教程 / 课程
4. 文章 / 博客 / 公众号 / 视频
5. 导航站 / 聚合平台 / Marketplace
6. 社交媒体帖文
7. 社区 / 论坛 / 其他

### C. 研究结论
- 最值得重点关注的链接（top 10 或 top 30%，取较小值）
- 最值得深挖的项目/产品/文章
- 这批链接整体反映出的趋势
- 建议的后续研究路径

## 第八步：输出

### 输出适配器架构

报告生成与输出投递是**解耦**的。skill 先生成报告（markdown），然后通过适配器脚本投递到目标。
这样做的好处：同一份报告可以投递到多个目标，且适配器是脚本不是 AI 推理，不浪费 token。

```
报告生成（AI） → 保存到工作目录 → 适配器 1（脚本） → 目标 1
                                 → 适配器 2（脚本） → 目标 2
                                 → ...
```

### 内置适配器

| 适配器 | 脚本 | 说明 |
|---|---|---|
| **filesystem** | `scripts/adapters/filesystem.py` | 复制到本地文件夹（默认 `~/Documents/linky-reports/`） |
| **obsidian** | `scripts/adapters/obsidian.py` | 写入 Obsidian vault，自动添加 frontmatter |
| **notion** | `scripts/adapters/notion.py` | 生成 Notion payload JSON，由 skill 调用 Notion MCP 投递 |
| **yinxiang** | `scripts/adapters/yinxiang.py` | 转 ENML 调用印象笔记 API，失败时 fallback 生成 .enex 文件 |
| **custom API** | 用户自建，放 `~/.config/linky/output-adapters/` | 按 `api_template.py` 模板编写 |

每个适配器的调用方式统一：
```bash
python3 scripts/adapters/{name}.py <report_path> --config '<json>'
```

### 输出流程

1. **生成报告**：将报告写入工作目录（临时 markdown 文件/目录）
2. **确定目标**：
   - 如果 `config.toml` 有 `[output]` 默认配置 → 使用默认，告知用户
   - 如果用户本次指定了目标 → 使用用户指定的
   - 如果都没有 → 询问用户
   - 用户可以指定**多个目标**（如 "输出到 Obsidian 和 Notion"）
3. **依次投递**：按顺序调用每个目标的适配器脚本
4. **报告结果**：显示每个目标的投递状态

### 适配器配置

在 `config.toml` 中配置默认输出和各适配器参数：

```toml
[output]
# 默认目标（可以是数组表示多重输出）
default = ["obsidian"]

[output.obsidian]
vault_path = "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain"
target_folder = "inbox"   # 留空则让 AI 自己判断应放到哪个文件夹
add_frontmatter = true

[output.notion]
database_id = ""          # 首次使用时设定，保存下来后续复用

[output.yinxiang]
notebook = "Research"
tags = ["linky", "research"]
# token 通过环境变量 YINXIANG_TOKEN 传入，不写在配置文件中

[output.filesystem]
output_dir = "~/Documents/linky-reports"
```

### 自定义 API 适配器

用户可以在 `~/.config/linky/output-adapters/` 中放入自定义脚本：

1. 复制 `scripts/adapters/api_template.py` 到 `~/.config/linky/output-adapters/my-api.py`
2. 修改脚本适配目标 API
3. 在 `config.toml` 中配置：
   ```toml
   [output.my-api]
   adapter_script = "~/.config/linky/output-adapters/my-api.py"
   endpoint = "https://api.example.com/notes"
   api_key_env = "MY_API_KEY"
   ```

也可以不写脚本——如果用户贴入了 API 文档，AI 应该：
1. 阅读 API 文档，理解 endpoint 和参数格式
2. 编写适配器脚本
3. 保存到 `~/.config/linky/output-adapters/` 并更新 `config.toml`
4. 后续调用直接走脚本，不再浪费 AI token

### Prompt 模式

除了适配器投递，还支持 **Prompt 模式**——生成一个结构良好的 prompt + 数据包，
可直接喂给任意 AI 平台（豆包、DeepSeek、MiniMax 等）完成后续任务。
这不是适配器（不涉及 API 调用），而是一种输出格式选项。

输出格式的详细规范见 `references/output-formats.md`。

## 配置进化

`~/.config/linky/` 完整目录结构：

```
~/.config/linky/
├── config.toml              # 全局设置（输出方式、语言、分批大小等）
├── user-profile.toml        # 用户注册偏好（用户名、邮箱、头像等）
├── fetch-strategy.toml      # 采集策略（覆盖仓库默认）
├── memory.md                # 唯一的通用记忆入口（偏好、账号、规则、心得）
├── personas/                # 分析视角
├── templates/               # 自定义分析卡模板
├── good-shots/              # 优质输出示例
├── output-adapters/         # 用户自定义的输出适配器脚本
├── sessions/                # 域名 session 凭据缓存（机器管理）
│   ├── xiaohongshu.com.json
│   └── ...
└── domains/                 # 域名记忆（人类可读的域名知识）
    ├── github.com.md
    ├── xiaohongshu.com.md
    └── ...
```

### memory.md 的定位

`memory.md` 是**唯一的通用记忆入口**——所有非域名特定的信息都存在这一个文件里。
不要往其他文件写用户偏好，避免信息分散。

```markdown
# Linky Memory

## User Preferences
- 偏好输出格式: markdown → obsidian
- 分析侧重: 技术视角为主
- 以后 GitHub 仓库都多写一点部署方式的分析

## Analysis Rules
- 公众号文章不用分析"投资视角"
- 工具类链接关注是否有 self-host 选项

## Accounts
- xiaohongshu.com: marco_dev (2026-04-13 注册)
- juejin.cn: marco-dev (已有账号)

## Global Notes
- 微信公众号周末反爬更严格，工作日 Scrapling 成功率更高
```

### 积累机制

- 用户说"记住这个格式"、"以后都这样" → 写入 `memory.md`
- 用户说"这类链接要这样处理" → 写入 `memory.md` 的 Analysis Rules
- 成功访问某域名 → 更新 `domains/{domain}.md` 的 trace
- 注册新账号 → 更新 `domains/{domain}.md` + `memory.md` 的 Accounts 区域
- 用户认可某个输出 → 保存到 `good-shots/`
- fallback 到浏览器层成功 → 保存 `sessions/{domain}.json` + 更新域名记忆
- 用户贴入 API 文档要求定制输出 → 编写脚本到 `output-adapters/` + 更新 `config.toml`

## 质量检查清单

完成报告前自检：
- [ ] 每个链接都已纳入报告（包括无法访问的和 pending 的）
- [ ] 每个链接都尝试了正文提取（已有预提取内容的除外）
- [ ] 不同类型使用了不同的分析模板
- [ ] 每个条目都有"我的判断"和"建议的后续行动"
- [ ] 没有空洞形容词，信息具体可比较
- [ ] 按类型分组而非按原始顺序排列
- [ ] 组内按研究价值排序
- [ ] 无法访问的链接有醒目标注
- [ ] 研究结论部分有实质性洞察
- [ ] 所有访问过的域名都更新了 `domains/{domain}.md`（含 trace）
- [ ] 需要注册的链接已呈现给用户并标注 pending 状态
- [ ] 新获取的 session 已保存到 `sessions/`
