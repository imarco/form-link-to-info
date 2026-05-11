---
domain: zhihu.com
type: qa-platform
visibility: partial
access_stability: variable
best_strategy: scrapling
---

# zhihu.com (知乎)

- 类型: 问答 / 专栏平台
- 可见性: 首页和问题页多为公开可见，专栏深度内容可能需要用户确认
- 公开读取稳定性: 变化较多，Scrapling 对公开正文更稳定
- 正文选择器: `.Post-RichText`, `.RichText`
- 注册方式: 手机号 / 微信
- 注册页: https://www.zhihu.com/signup
- 注意: 长回答可能被折叠，需要展开
