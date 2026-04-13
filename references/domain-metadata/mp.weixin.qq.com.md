---
domain: mp.weixin.qq.com
type: content-platform
login_required: false
anti_scrape: high
best_strategy: scrapling
---

# mp.weixin.qq.com (微信公众号)

- 类型: 内容平台（公众号文章）
- 登录要求: 阅读不需要，但链接有时效性
- 反爬: 严格，Jina 被 403；Scrapling StealthyFetcher 可穿透
- 正文选择器: `#js_content`
- 注意: 链接有过期时间，过期后无法访问；图片有防盗链
- 工作日采集成功率高于周末
