---
domain: mp.weixin.qq.com
type: content-platform
visibility: public
access_stability: variable
best_strategy: scrapling
---

# mp.weixin.qq.com (微信公众号)

- 类型: 内容平台（公众号文章）
- 可见性: 公开文章阅读不需要额外授权，但链接有时效性
- 公开读取稳定性: 变化较多，Scrapling 配合 `#js_content` 选择器更稳定
- 正文选择器: `#js_content`
- 注意: 链接有过期时间，过期后标记为页面失效；图片资源可能无法归档
- 工作日采集成功率高于周末
