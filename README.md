# ziwei-paipan — 紫微斗数排盘 Skill（Claude / Codex / 任意 Agent）

把 **FateStar 排盘引擎 + 郑大钱 AI 命理师**封装成 Agent Skill。装上后,对 AI 说「帮我排 1990 年 7 月 23 日早上 8 点出生男性的紫微盘」即自动出盘 + 专业解读。

支持纯排盘(免费、不要 key）与郑大钱深度断盘(知识引擎 + 古籍锚定）。

---

## 下载 & 安装

### 给 AI Agent

`git clone` 或下载 zip,把 `ziwei-paipan` 拷进 Agent 的 skills 目录:

```bash
git clone https://github.com/LouisLin0723/fatestar-ziwei-skill.git

# Claude Code / Claude Desktop
cp -r fatestar-ziwei-skill/ziwei-paipan ~/.claude/skills/

# OpenAI Codex
cp -r fatestar-ziwei-skill/ziwei-paipan ~/.codex/skills/

# 通用 / 多工具共享(Codex、Cursor、OpenClaw 等读同一目录）
cp -r fatestar-ziwei-skill/ziwei-paipan ~/.agents/skills/
```

重启客户端(或重载 skills）即生效。`SKILL.md` 用通用格式(frontmatter `name` + `description`），Claude 与 Codex 都识别。

### 给人类

1. 下载 zip 或 `git clone`
2. 解压,把 `ziwei-paipan` 放进 Agent 的 skills 目录
3.（可选）配一个 API key 解锁郑大钱解读（见下）
4. 重启 Agent,问「帮我排…的紫微盘」验证

---

## API Key 配置（一个 key 搞定）

**你只需要一个 `fs_live_` key。** 排盘免费、匿名可用;只有要「郑大钱」专业解读才需 key。

### 默认行为（重要）

装上 skill 后,问命理问题(事业 / 财运 / 感情 / 健康 / 该不该…）时,skill 会:

1. **默认先用郑大钱回答** —— 免费会员每天 **3 次**(北京时间 **21:00** 重置）。知识引擎 + 郑大钱人格 + 古籍锚定,比 AI 自己瞎解读准得多。
2. **3 次用完 → 自动切回你自己的 LLM** —— skill 检测到积分耗尽(HTTP `402`），无缝改用 **Agent 本身的模型**排盘 + 解读兜底,并提示你:去充值 或 等 21:00 免费重置。

不会卡住,降级无感。

### 怎么配 key

```bash
export FATESTAR_API_KEY="fs_live_xxxxxxxx"    # Linux / macOS
set FATESTAR_API_KEY=fs_live_xxxxxxxx         # Windows CMD
$env:FATESTAR_API_KEY="fs_live_xxxxxxxx"      # Windows PowerShell
```

### 拿一个 key

访问 **https://www.fatestar.top** → 注册免费会员 → 开发者中心创建 `fs_live_` key（免费会员每天 3 积分,做新手任务 / 邀请好友 / 连续登录可领更多）。

### 能力优先级

> 带 key 且有积分 → **郑大钱解读**(扣积分,最准） → 积分用完 → **你自己的 LLM**(兜底） → 纯排盘数据(**永远免费,不要 key**）

---

## 用法

装好后自然语言触发:

> 帮我排 1995 年 3 月 12 日下午 2 点出生女性的紫微命盘,看看事业。

AI 自动调引擎拿十二宫 + 四化 + 格局 → 默认郑大钱断盘(有 key 有积分）→ 否则自己解读。

---

## 验证安装

重启 Agent,用大白话直接问:

| 测试 | 说什么 | 成功标志 |
|---|---|---|
| 排盘(免费） | 「帮我排 1990 年 7 月 23 日早上 8 点、男 的紫微盘」 | 出完整命盘 |
| 解读(扣积分） | 「我今年事业运如何?该不该跳槽?」 | 郑大钱断盘（需 key + 积分） |

---

## 文件结构

```
fatestar-ziwei-skill/
├── README.md              # 本文件
└── ziwei-paipan/
    └── SKILL.md           # Skill 定义（给 AI 读的 SOP + curl 示例）
```

---

## 更多接入

MCP Server / REST API / 各 Agent 客户端速查 → **https://www.fatestar.top/docs**

---

MIT · Powered by [FateStar](https://www.fatestar.top)
