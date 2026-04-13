---
domain: github.com
type: code-hosting
login_required: optional
anti_scrape: low
best_strategy: jina
---

# github.com

- 类型: 代码托管平台
- 登录要求: 大部分内容无需登录，私有仓库需要
- 反爬: 宽松，Jina/WebFetch 直取即可
- API: 有完善的 REST/GraphQL API，可用 `gh` CLI
- 注意: README 和代码文件通过 Jina 质量最好；Issues/Discussions 用 API 更可靠
- 注册页: https://github.com/signup
