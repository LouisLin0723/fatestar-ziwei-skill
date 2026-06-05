# FateStar Ziwei Skill

> 紫微斗数 (Zi Wei Dou Shu / Purple Star Astrology) 排盘 Skill for AI agents — 把 **FateStar 排盘引擎 + 郑大钱 AI 命理师**封装成跨平台 Agent Skill。装上后对 AI 说「帮我排 1990 年 7 月 23 日早上 8 点出生男性的紫微盘」,即自动出盘 + 专业断盘。

**排盘免费、匿名可用**(不要 key);**郑大钱深度解读**付费(知识引擎 + 古籍锚定,需 `fs_live_` key)。引擎自建 102 颗星 + 三合派四化 + 真太阳时,**仓库不含引擎源码** —— 4 套 CLI 都是 `https://www.fatestar.top` 的瘦客户端。

[English summary ↓](#english)

---

## 下载 & 安装

### 给 AI Agent

平台有 skill 市场就搜 **ziwei** / **fatestar** 装;否则手动:

```bash
# 下载 (git clone 出的目录就叫 fatestar-ziwei-skill)
git clone https://github.com/LouisLin0723/fatestar-ziwei-skill.git
# 或下载 zip: curl -L -o z.zip https://github.com/LouisLin0723/fatestar-ziwei-skill/archive/refs/heads/main.zip && unzip z.zip
#   ⚠️ zip 解压出的目录名带后缀 fatestar-ziwei-skill-main, 下方 mv 源名相应改

# 整个目录放进 Agent 的 skills 目录, 命名为 ziwei-paipan
# Claude Code:     mv fatestar-ziwei-skill ~/.claude/skills/ziwei-paipan
# OpenAI Codex:    mv fatestar-ziwei-skill ~/.codex/skills/ziwei-paipan
# OpenClaw:        mv fatestar-ziwei-skill ~/.openclaw/skills/ziwei-paipan
# Cursor/Windsurf: mv fatestar-ziwei-skill <项目>/.skills/ziwei-paipan
# 多工具共享:       mv fatestar-ziwei-skill ~/.agents/skills/ziwei-paipan
```

`~/.agents/skills/` 适合多个 AI 工具读同一目录 (Codex、Cursor、OpenClaw 等)。重启客户端即生效。`SKILL.md` 用通用 frontmatter 格式,Claude / Codex 都识别。

### 给人类

1. 下载 zip 或 `git clone`
2. 解压,整个目录改名 `ziwei-paipan` 放进 Agent 的 skills 目录
3.(可选)配一个 `fs_live_` key 解锁郑大钱解读(见下)
4. 跑装后验证,再问「帮我排…的紫微盘」

### 零安装替代:远程 MCP

不想装 skill?同一个引擎也是 MCP server,配置里填一个地址即可:

```jsonc
// 远程 (推荐, 零安装)
{ "mcpServers": { "ziwei": { "url": "https://www.fatestar.top/api/mcp" } } }

// 本地 stdio (开源 npm 包, 自带引擎, 断网也能排盘)
{ "mcpServers": { "ziwei": { "command": "npx", "args": ["-y", "@fatestar/ziwei-mcp"] } } }
```

---

## API Key 配置(一个 key 搞定)

**你只需要一个 `fs_live_` key。** 排盘(`chart` / `transits`)免费、匿名可用;只有「郑大钱」专业解读(`reading`)才需 key、才扣积分。

### 默认行为(重要)

问命理问题(事业 / 财运 / 感情 / 健康 / 该不该…)时,skill 会:

1. **默认先用郑大钱回答** —— 免费会员每天 **3 积分**(北京时间 **21:00** 重置)。知识引擎 + 郑大钱人格 + 古籍锚定,比 AI 自己瞎解读准得多。
2. **积分用完 → 自动切回你自己的 LLM** —— skill 检测到 `402`(积分耗尽),无缝改用 **Agent 本身的模型** + `chart` 免费排盘兜底,并提示你充值或等 21:00 重置。

不会卡住,降级无感。

### 怎么配 key

```bash
cp .env.example .env
# 编辑 .env, 填: FATESTAR_API_KEY=fs_live_xxxxxxxx
```

或直接设环境变量:

```bash
export FATESTAR_API_KEY="fs_live_xxxxxxxx"    # Linux / macOS
set FATESTAR_API_KEY=fs_live_xxxxxxxx         # Windows CMD
$env:FATESTAR_API_KEY="fs_live_xxxxxxxx"      # Windows PowerShell
```

### 拿一个 key

访问 **https://www.fatestar.top** → 注册免费会员 → 做新手任务领积分 → 开发者中心创建固定的 `fs_live_` key(可重复使用)。

### 能力优先级

> 带 key 且有积分 → **郑大钱解读**(扣积分,最准)→ 积分用完 → **你自己的 LLM**(兜底)→ 纯排盘数据(**永远免费,不要 key**)

Key 优先级: `--api_key` 参数 > `.env` 文件 > 环境变量 > 匿名。

---

## 装后验证

### 第 1 步:探测可用 runtime

按顺序跑,第一个成功的决定用哪个 CLI:

```bash
python --version    # 需 >= 3.6 (纯标准库, 无需 pip install)
python3 --version   # macOS 常只有 python3
node --version      # 需 >= 12, 零外部依赖
# Shell 兜底: Windows PowerShell 5.1+ / Linux·macOS bash 4+ 带 curl
```

优先级:**Python > Node.js > PowerShell / Bash**

### 第 2 步:跑 entry test(每个可用 runtime 各跑一次)

`doc` 离线(不联网),打印完整接口规范:

```bash
python  scripts/ziwei_cli.py  doc
node    scripts/ziwei_cli.js  doc
powershell -ExecutionPolicy Bypass -File scripts/ziwei_cli.ps1 doc
bash    scripts/ziwei_cli.sh  doc
```

### 第 3 步:把推荐 runtime 写进 runtime.conf

```bash
echo "Runtime: Python" > runtime.conf
echo "Command: python scripts/ziwei_cli.py" >> runtime.conf
```

其他例子:`python3 scripts/ziwei_cli.py` / `node scripts/ziwei_cli.js` / `powershell -ExecutionPolicy Bypass -File scripts/ziwei_cli.ps1` / `bash scripts/ziwei_cli.sh`。

**重要:** runtime 偏好存在 `runtime.conf`,不在 SKILL.md。Agent 加载时读 `runtime.conf` 选 CLI;文件缺失/损坏则回退 SKILL.md 的平台探测流程。已存在就替换,别追加。

### 日常用法

`runtime.conf` 就位后,直接用存好的 `Command`。以 `python scripts/ziwei_cli.py` 为例:

```bash
# 免费排本命盘
python scripts/ziwei_cli.py chart --year 1990 --month 7 --day 23 --hour 8 --gender male

# 免费排 2026 流年(6 层运限)
python scripts/ziwei_cli.py transits --year 1990 --month 7 --day 23 --hour 8 --gender male --target-year 2026

# 郑大钱解读(付费, 需 fs_live_ key)
python scripts/ziwei_cli.py reading --year 1990 --month 7 --day 23 --hour 8 --gender male --question "看我今年事业运,该不该跳槽?"
```

`chart` / `transits` 直接打印命盘 JSON(免费);`reading` 打印郑大钱解读全文。

### 第 4 步(可选):测一次真排盘

```bash
python scripts/ziwei_cli.py chart --year 1990 --month 7 --day 23 --hour 8 --gender male
```

返回 JSON 命盘 = API 连通成功。

---

## 自然语言触发示例

装好后,直接对 AI 说:

> 帮我排 1995 年 3 月 12 日下午 2 点出生女性的紫微命盘,看看事业。

AI 自动调引擎拿十二宫 + 四化 + 格局 → 默认郑大钱断盘(有 key 有积分)→ 否则自己解读。

| 测试 | 说什么 | 成功标志 |
|---|---|---|
| 排盘(免费) | 「帮我排 1990 年 7 月 23 日早上 8 点、男 的紫微盘」 | 出完整命盘 |
| 解读(扣积分) | 「我今年事业运如何?该不该跳槽?」 | 郑大钱断盘(需 key + 积分) |

---

## 文件结构

```
ziwei-paipan/                 (本仓库, 改名后放进 skills 目录)
├── .env.example              # API key 模板
├── .env                      # 你的 key (gitignore, 从 .env.example 复制)
├── runtime.conf              # 探测到的 runtime (gitignore)
├── runtime.conf.example      # runtime 模板
├── SKILL.md                  # 给 AI 读的 Skill 定义 (SOP + 命令速查)
├── README.md                 # 本文件
├── SECURITY.md               # 漏洞上报政策
├── TEST_PLAN.md              # 端到端测试场景
├── LICENSE                   # MIT
└── scripts/
    ├── ziwei_cli.py          # Python CLI (纯标准库)
    ├── ziwei_cli.js          # Node.js CLI (内置 https)
    ├── ziwei_cli.ps1         # PowerShell CLI (UTF-8 BOM)
    ├── ziwei_cli.sh          # Bash CLI (curl; reading 配 jq 更佳)
    ├── generate.py           # 从 shared 同步 4 个 CLI 的公共块
    └── shared/
        ├── constants.json    # API 地址 + 端点 + 枚举
        └── doc_spec.md        # 接口规范模板 (doc 命令渲染它)
```

更多接入(MCP / REST API / 各 Agent 客户端速查)→ **https://www.fatestar.top/docs**

---

<a name="english"></a>
## English

**Zi Wei Dou Shu (Purple Star Astrology) skill for AI agents.** Wraps FateStar's
self-built charting engine + the 郑大钱 (Zheng Da Qian) AI master into a cross-platform
Agent Skill. Charting (`chart` / `transits`) is **free and anonymous**; the 郑大钱 reading
(`reading`) is paid (needs an `fs_live_` key). No engine source here — the four CLIs
(Python / Node.js / PowerShell / Bash) are thin clients over `https://www.fatestar.top`.

Install: download the zip, move it into your agent's skills dir as `ziwei-paipan`, then
detect a runtime and write `runtime.conf`. Routine calls:

```bash
python scripts/ziwei_cli.py chart    --year 1990 --month 7 --day 23 --hour 8 --gender male
python scripts/ziwei_cli.py transits --year 1990 --month 7 --day 23 --hour 8 --gender male --target-year 2026
python scripts/ziwei_cli.py reading  --year 1990 --month 7 --day 23 --hour 8 --gender male --question "..."
```

Zero-install alternative — remote MCP: `{ "mcpServers": { "ziwei": { "url": "https://www.fatestar.top/api/mcp" } } }`

---

MIT licensed · Powered by [FateStar](https://www.fatestar.top) · 排盘引擎自建,只讲真话。
