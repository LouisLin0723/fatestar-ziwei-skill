# Security Policy / 安全政策

## 上报漏洞 (Reporting a Vulnerability)

发现安全漏洞请负责任地私下上报，**不要开公开 GitHub issue**。
If you find a security vulnerability, please report it privately — **do NOT open a public GitHub issue**.

### 上报方式 (How to Report)

发邮件到 **support@fatestar.top**，标题前缀 `[Security]`，附：
Email **support@fatestar.top** with the subject prefixed `[Security]`, including:

- 漏洞描述 / Description of the vulnerability
- 复现步骤 / Steps to reproduce
- 潜在影响 / Potential impact
- 修复建议（如有）/ Suggested fix (if any)

### 响应时间 (Response Timeline)

| 动作 / Action | 时限 / Timeframe |
|------|----------|
| 确认收到 / Acknowledgment | 48 小时内 / within 48h |
| 初步评估 / Initial assessment | 5 个工作日内 / within 5 business days |
| 发布修复 / Fix release | 视严重程度 / depends on severity |

### 范围 (Scope)

本政策覆盖 / This policy covers:
- 本仓库的 skill 定义与配置示例 / This repo's skill definition and config examples
- `scripts/` 下的 CLI 脚本 / CLI scripts under `scripts/`
- 官方文档（`SKILL.md` / `README.md` / `doc_spec.md`）/ Official docs

### 不在范围 (Out of Scope)

- FateStar API 后端（`www.fatestar.top`）/ The FateStar API backend
- 消费本 skill 的第三方 AI agent 平台 / Third-party AI agent platforms consuming this skill
- 用户自身的 API key 配置错误 / User misconfiguration of API keys

## 支持版本 (Supported Versions)

| 版本 / Version | 支持 / Supported |
|---------|-----------|
| 最新 / Latest | 是 / Yes |

## 用户安全最佳实践 (Best Practices for Users)

- API key 存环境变量或 `.env`，绝不写进代码 / Store keys in env vars or `.env`, never in code
- `.env` 已在 `.gitignore` 中 / `.env` is gitignored
- 定期轮换 key / Rotate keys periodically
- 排盘 (`chart` / `transits`) 匿名即可，无需 key / Charting needs no key — stay anonymous
