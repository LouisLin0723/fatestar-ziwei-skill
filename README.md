# FateStar Ziwei Skill

中文在前，English below.

---

## 中文

> 紫微斗数（Zi Wei Dou Shu / Purple Star Astrology）排盘 Skill for AI agents。把 **FateStar 排盘数据 + 郑大钱 AI 解读入口**封装成跨平台 Agent Skill。装上后，对 AI 说「帮我排 1990 年 7 月 23 日早上 8 点出生男性的紫微盘」，即可自动调用排盘数据；配置 Key 且积分足够时，可调用郑大钱解读。

**排盘免费、匿名可用**；**郑大钱解读**需 `FSFSKey`，按积分规则计费。
本仓库是 Agent Skill 与 CLI thin client，不包含 FateStar 服务端、郑大钱人格训练、知识引擎、私有提示词、评测集或检索语料。

### 能力边界

| 能力 | 是否免费 | 是否在本仓库内 |
| --- | --- | --- |
| `chart` 本命盘 | 免费 | CLI 调用入口在本仓库；真实计算由 FateStar API 返回 |
| `transits` 6 层运限 | 免费 | CLI 调用入口在本仓库；真实计算由 FateStar API 返回 |
| `reading` 郑大钱解读 | 付费，扣积分 | 仅提供调用入口；人格训练与知识引擎在 FateStar 服务端 |

### 开源边界与 know-how 保护

本仓库开源的目标是让用户和 Agent 更容易接入 FateStar，而不是公开郑大钱的核心 know-how。

- 仓库只包含 Skill 定义、4 套 CLI thin client、安装说明与测试计划。
- 不包含郑大钱人格训练、私有 prompt、知识库、RAG / rerank 策略、评测集、模型路由、反幻觉规则、计费风控或服务端实现。
- `reading` 只调用 FateStar 托管接口；客户端不会拿到原始 prompt、检索上下文或知识库内容。
- MIT License 只覆盖本仓库代码；FateStar 品牌、托管服务、郑大钱人格、知识引擎、训练数据与后台策略仍为 FateStar 私有资产。
- 若你要做二次开发，建议把本仓库当成接入层，而不是命理知识库或郑大钱的实现源码。

### 下载与安装

如果平台有 Skill 市场，搜索 **ziwei** / **fatestar** 安装；否则手动安装：

```bash
# 下载
git clone https://github.com/LouisLin0723/fatestar-ziwei-skill.git

# 或下载 zip
curl -L -o z.zip https://github.com/LouisLin0723/fatestar-ziwei-skill/archive/refs/heads/master.zip
unzip z.zip

# zip 解压出的目录名是 fatestar-ziwei-skill-master
# 把整个目录放进 Agent 的 skills 目录，命名为 ziwei-paipan
mv fatestar-ziwei-skill ~/.codex/skills/ziwei-paipan
```

常见目录：

```bash
# Claude Code
mv fatestar-ziwei-skill ~/.claude/skills/ziwei-paipan

# OpenAI Codex
mv fatestar-ziwei-skill ~/.codex/skills/ziwei-paipan

# OpenClaw
mv fatestar-ziwei-skill ~/.openclaw/skills/ziwei-paipan

# Cursor / Windsurf 项目内
mv fatestar-ziwei-skill <项目>/.skills/ziwei-paipan

# 多工具共享
mv fatestar-ziwei-skill ~/.agents/skills/ziwei-paipan
```

重启客户端后生效。`SKILL.md` 使用通用 frontmatter 格式，Claude / Codex 等 Agent 都能读取。

### 零安装替代：远程 MCP

不想安装 Skill 时，可直接使用同一个 FateStar 远程 MCP：

```jsonc
{
  "mcpServers": {
    "ziwei": { "url": "https://www.fatestar.top/api/mcp" }
  }
}
```

完整 MCP 文档见：<https://github.com/LouisLin0723/fatestar-ziwei-mcp>

### API Key 配置

排盘（`chart` / `transits`）免费、匿名可用；只有「郑大钱」解读（`reading`）需要 `FSFSKey`，并按积分规则计费。

```bash
cp .env.example .env
# 编辑 .env，填入：
FATESTAR_API_KEY=FSFSKey20260606XXXXXXXXXXXXXXXXXXXX
```

也可以设置环境变量：

```bash
export FATESTAR_API_KEY="FSFSKey20260606XXXXXXXXXXXXXXXXXXXX"    # Linux / macOS
set FATESTAR_API_KEY=FSFSKey20260606XXXXXXXXXXXXXXXXXXXX         # Windows CMD
$env:FATESTAR_API_KEY="FSFSKey20260606XXXXXXXXXXXXXXXXXXXX"      # Windows PowerShell
```

拿 Key：访问 <https://www.fatestar.top> → 注册免费会员 → 做新手任务领积分 → 开发者中心创建 `FSFSKey`。

### 默认行为

问事业、财运、感情、健康、该不该等命理问题时，Skill 会：

1. 优先调用郑大钱解读。该路径使用 FateStar 知识引擎与郑大钱人格，需要 Key 和积分。
2. 如果未配置 Key 或积分不足，回退到 `chart` 免费排盘 + Agent 自身模型解释，并明确提示当前不是郑大钱解读。

能力优先级：

```text
带 Key 且有积分 → 郑大钱解读（扣积分）
积分不足 / 未配置 Key → 免费排盘数据 + Agent 自身模型解释
只要命盘数据 → chart / transits 免费匿名调用
```

### 装后验证

先探测可用 runtime：

```bash
python --version    # 需 >= 3.6，纯标准库，无需 pip install
python3 --version   # macOS 常只有 python3
node --version      # 需 >= 12，零外部依赖
```

跑离线接口规范：

```bash
python  scripts/ziwei_cli.py  doc
node    scripts/ziwei_cli.js  doc
powershell -ExecutionPolicy Bypass -File scripts/ziwei_cli.ps1 doc
bash    scripts/ziwei_cli.sh  doc
```

把推荐 runtime 写进 `runtime.conf`：

```bash
echo "Runtime: Python" > runtime.conf
echo "Command: python scripts/ziwei_cli.py" >> runtime.conf
```

### CLI 用法

```bash
# 免费排本命盘
python scripts/ziwei_cli.py chart --year 1990 --month 7 --day 23 --hour 8 --gender male

# 免费排 2026 流年（6 层运限）
python scripts/ziwei_cli.py transits --year 1990 --month 7 --day 23 --hour 8 --gender male --target-year 2026

# 郑大钱解读（付费，需 FSFSKey）
python scripts/ziwei_cli.py reading --year 1990 --month 7 --day 23 --hour 8 --gender male --question "看我今年事业运，该不该跳槽？"
```

### 自然语言触发示例

装好后，直接对 AI 说：

> 帮我排 1995 年 3 月 12 日下午 2 点出生女性的紫微命盘，看看事业。

Agent 会先拿排盘数据；如果有 Key 且积分足够，再调用郑大钱解读。否则会用 Agent 自身模型基于免费排盘数据解释。

### 文件结构

```text
ziwei-paipan/
├── .env.example
├── runtime.conf.example
├── SKILL.md
├── README.md
├── SECURITY.md
├── TEST_PLAN.md
└── scripts/
    ├── ziwei_cli.py
    ├── ziwei_cli.js
    ├── ziwei_cli.ps1
    ├── ziwei_cli.sh
    ├── generate.py
    └── shared/
        ├── constants.json
        └── doc_spec.md
```

更多接入（MCP / REST API / 各 Agent 客户端速查）：<https://www.fatestar.top/docs>

---

## English

> FateStar Ziwei Skill is a cross-platform Agent Skill for Zi Wei Dou Shu (Purple Star Astrology). It lets AI agents call FateStar charting data and, when an `FSFSKey` with credits is configured, the paid Zheng Da Qian AI reading endpoint.

Charting is free and anonymous. Zheng Da Qian readings require an `FSFSKey` and are charged by credits.
This repository is an Agent Skill plus CLI thin clients. It does **not** include FateStar's server-side implementation, Zheng Da Qian persona training, knowledge engine, private prompts, evaluation sets, retrieval corpus, or anti-hallucination rules.

### Capability Boundary

| Capability | Billing | Included in this repo |
| --- | --- | --- |
| `chart` natal chart | Free | CLI entrypoint only; data is returned by the FateStar API |
| `transits` six transit levels | Free | CLI entrypoint only; data is returned by the FateStar API |
| `reading` Zheng Da Qian reading | Paid credits | API entrypoint only; persona training and knowledge engine stay server-side |

### Open-Source Boundary and Know-How Protection

This repository is open so users and agents can integrate with FateStar easily. It is not a release of Zheng Da Qian's core know-how.

- The repo contains Skill metadata, four CLI thin clients, installation docs, and a test plan.
- It does not contain private prompts, persona training data, knowledge base content, RAG / reranking logic, evaluation data, model routing, anti-hallucination rules, billing controls, or server implementation.
- `reading` calls the hosted FateStar endpoint. The client never receives raw prompts, retrieval context, or private corpus content.
- The MIT License applies to this repository's code. FateStar's brand, hosted service, Zheng Da Qian persona, knowledge engine, training data, and backend strategy remain proprietary FateStar assets.
- For forks or integrations, treat this repository as the integration layer, not as the implementation of FateStar's interpretation engine.

### Installation

If your platform has a Skill marketplace, search **ziwei** or **fatestar**. Otherwise install manually:

```bash
git clone https://github.com/LouisLin0723/fatestar-ziwei-skill.git

# Or download the zip
curl -L -o z.zip https://github.com/LouisLin0723/fatestar-ziwei-skill/archive/refs/heads/master.zip
unzip z.zip

# Put the whole directory into your agent's skills directory as ziwei-paipan
mv fatestar-ziwei-skill ~/.codex/skills/ziwei-paipan
```

Common locations:

```bash
# Claude Code
mv fatestar-ziwei-skill ~/.claude/skills/ziwei-paipan

# OpenAI Codex
mv fatestar-ziwei-skill ~/.codex/skills/ziwei-paipan

# OpenClaw
mv fatestar-ziwei-skill ~/.openclaw/skills/ziwei-paipan

# Cursor / Windsurf project
mv fatestar-ziwei-skill <project>/.skills/ziwei-paipan

# Shared by multiple tools
mv fatestar-ziwei-skill ~/.agents/skills/ziwei-paipan
```

Restart the client after installation.

### Zero-Install Alternative: Remote MCP

Use the same FateStar engine through the hosted remote MCP endpoint:

```jsonc
{
  "mcpServers": {
    "ziwei": { "url": "https://www.fatestar.top/api/mcp" }
  }
}
```

Remote MCP docs: <https://github.com/LouisLin0723/fatestar-ziwei-mcp>

### API Key

`chart` and `transits` are free and anonymous. Only `reading` requires an `FSFSKey`.

```bash
cp .env.example .env
# Edit .env:
FATESTAR_API_KEY=FSFSKey20260606XXXXXXXXXXXXXXXXXXXX
```

Or set an environment variable:

```bash
export FATESTAR_API_KEY="FSFSKey20260606XXXXXXXXXXXXXXXXXXXX"    # Linux / macOS
set FATESTAR_API_KEY=FSFSKey20260606XXXXXXXXXXXXXXXXXXXX         # Windows CMD
$env:FATESTAR_API_KEY="FSFSKey20260606XXXXXXXXXXXXXXXXXXXX"      # Windows PowerShell
```

Get a key at <https://www.fatestar.top>: sign up, claim starter credits, then create an `FSFSKey` in the developer center.

### Default Behavior

For astrology questions about career, money, relationships, health, timing, or decisions, the Skill:

1. Tries Zheng Da Qian first when a valid Key and credits are available.
2. Falls back to free `chart` data plus the agent's own model explanation when no Key is configured or credits are insufficient.

Priority:

```text
Valid Key + credits → Zheng Da Qian reading
No Key / insufficient credits → free chart data + agent model explanation
Chart data only → chart / transits free anonymous calls
```

### Verification

Probe runtimes:

```bash
python --version
python3 --version
node --version
```

Run the offline spec:

```bash
python  scripts/ziwei_cli.py  doc
node    scripts/ziwei_cli.js  doc
powershell -ExecutionPolicy Bypass -File scripts/ziwei_cli.ps1 doc
bash    scripts/ziwei_cli.sh  doc
```

Write `runtime.conf`:

```bash
echo "Runtime: Python" > runtime.conf
echo "Command: python scripts/ziwei_cli.py" >> runtime.conf
```

### CLI Examples

```bash
# Free natal chart
python scripts/ziwei_cli.py chart --year 1990 --month 7 --day 23 --hour 8 --gender male

# Free 2026 transits
python scripts/ziwei_cli.py transits --year 1990 --month 7 --day 23 --hour 8 --gender male --target-year 2026

# Paid Zheng Da Qian reading
python scripts/ziwei_cli.py reading --year 1990 --month 7 --day 23 --hour 8 --gender male --question "How is my career this year?"
```

Full developer docs: <https://www.fatestar.top/docs>

---

MIT licensed. Powered by [FateStar](https://www.fatestar.top).
