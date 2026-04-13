---
domain: zhihu.com
type: qa-platform
login_required: partial
anti_scrape: high
best_strategy: scrapling
---

# zhihu.com (知乎)

- 类型: 问答 / 专栏平台
- 登录要求: 首页和问题页无需登录，专栏深度内容可能需要
- 反爬: 频繁变化，Scrapling 比 Jina 稳定
- 正文选择器: `.Post-RichText`, `.RichText`
- 注册方式: 手机号 / 微信
- 注册页: https://www.zhihu.com/signup
- 注意: 长回答可能被折叠，需要展开
