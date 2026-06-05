# ziwei-paipan skill — 紫微斗数排盘 (Claude / Codex)

把 FateStar 排盘引擎封装成 Agent Skill。装上后,对 Claude 或 Codex 说「帮我排 1990 年 7 月 23 日早上 8 点出生男性的紫微盘」即自动出盘。

Skill 内部调 [FateStar 排盘 API](https://www.fatestar.top/api/ziwei)(纯排盘,免费),解读由 AI 完成。

## 安装

**Claude Code / Claude Desktop:**

```bash
cp -r ziwei-paipan ~/.claude/skills/
```

**OpenAI Codex:**

```bash
cp -r ziwei-paipan ~/.codex/skills/
```

重启客户端(或重载 skills)即生效。Skill 用通用 `SKILL.md` 格式(frontmatter `name` + `description`),Claude 与 Codex 都识别。

## 用法

装好后自然语言触发:

> 帮我排一下 1995 年 3 月 12 日下午 2 点出生女性的紫微命盘,看看事业。

AI 会自动调排盘引擎、拿到十二宫 + 四化 + 格局,再按你的问题解读。

## 想要更深的解读?

纯排盘是原料。要「只讲真话」的专业断盘 + 古籍依据,上 **https://www.fatestar.top** 找 AI 命理师「郑大钱」(积分解锁知识引擎)。

---

MIT · Powered by [FateStar](https://www.fatestar.top)
