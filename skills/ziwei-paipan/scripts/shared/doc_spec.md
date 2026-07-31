# FateStar Ziwei 接口规范（给 AI Agent 读）

紫微斗数（Zi Wei Dou Shu / Purple Star Astrology）排盘 + AI 解读，引擎由 FateStar 自研
（102 颗星 · 三合派四化 · 真太阳时）。**排盘免费、可匿名**；**郑大钱（Zheng Da Qian）解读**
付费（扣积分，需 `FSFSKey`）。

## 协议

- 排盘（免费）：GET / POST  https://www.fatestar.top/api/ziwei
- 解读（付费）：POST        https://www.fatestar.top/api/ziwei/reading
- 渠道标记：所有 CLI 请求发送 `X-FateStar-Client: skill/2.2.0`。
- 认证：排盘可匿名；配置 Key 时免费请求也携带 Key做用户归属，但不扣积分。解读必须带 Key。

## CLI 调用方式 ({{LANG_NAME}})

```{{LANG_CODEBLOCK}}
{{LANG_INVOKE}} <command> [options]
```

## 命令一览

### 1. chart — 本命盘（免费）
输入出生信息出完整本命盘。匿名、无需 Key、不扣积分。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --year | int | 是 | 出生年（公历；`--calendar lunar` 时为农历年）。1900-2100 |
| --month | int | 是 | 出生月 1-12 |
| --day | int | 是 | 出生日 1-31 |
| --hour | int | 是 | 出生小时 0-23（24 小时制，**不是**时辰地支） |
| --gender | string | 是 | male / female |
| --minute | int | 否 | 出生分钟 0-59（配合 --longitude 做真太阳时） |
| --calendar | string | 否 | solar（默认）/ lunar |
| --leap | flag | 否 | 闰月（仅 --calendar lunar 有效） |
| --longitude | float | 否 | 出生地经度（东经正、西经负），启用真太阳时修正 |
| --tz | float | 否 | 时区偏移（UTC+8 = 8），配合 --longitude |
| --api_key | string | 否 | 可选 FSFSKey；免费排盘仅用于用户归属，不触发扣费 |

### 2. transits — 6 层运限（免费）
本命盘 + 6 层运限：大限 / 小限 / 流年 / 流月 / 流日 / 流时。共享上面所有出生参数，外加下面
的运限目标。不传目标则默认：当前公历年 + 本命农历月日 + 出生时辰。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --target-year | int | 否 | 流年目标公历年（默认当年） |
| --target-month | int | 否 | 流月目标农历月 1-12（默认本命农历月） |
| --target-day | int | 否 | 流日目标农历日 1-30（默认本命农历日） |
| --target-hour | int | 否 | 流时目标小时 0-23（默认出生时辰） |

### 3. reading — 郑大钱 AI 解读（付费，扣积分）
FateStar 解读路径：知识引擎 + 郑大钱人格。只有用户明确选择该服务，并确认理解可能扣积分后，才调用本命令。
普通命理问题不等于付费授权；默认先使用免费排盘数据，再把郑大钱解读作为可选项。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| (chart 的全部出生参数) | | 是 | year/month/day/hour/gender 必填 |
| --question | string | 是 | 要问郑大钱的问题（如「看我今年事业运，该不该跳槽？」） |
| --api_key | string | 否 | FSFSKey（否则取 .env / 环境变量 FATESTAR_API_KEY）。reading 未提供 Key 时停止调用 |

`reading` 可能扣积分；实际扣分与余额以接口响应为准。不要在调用前承诺具体费用，也不要在 `401` 或 `402` 后自动重试。

### 4. doc — 本接口规范（离线，不联网）

---

## 决策流程

```
用户给出生信息 (year/month/day/hour/gender)
  |
  +-- 只要命盘?                              → chart
  |
  +-- 要某年 / 某段时间的运?                  → transits (--target-year ...)
  |
  +-- 问命理问题                              → chart + Agent 自身模型解释（免费）
           |
           +-- 用户明确选择郑大钱并确认可能扣积分
                 → reading
                    |
                    +-- 401 / 402 → 停止，不重试；可继续免费 chart
```

`reading` 必须有明确付费授权。未授权、无 Key 或积分不足时，继续使用免费的 `chart` / `transits`。

## ⚠️ 双轨干支铁律

运限输出带两套干支，**严禁混用**：
- **真实干支**（万年历六十甲子）—— 对外讲日子（「X 日签约 / X 月运势」）用**这个**。
- **宫位编号**（紫微五虎遁）—— **仅推四化用**，严禁当日子说出口。

## 场景示例（可直接跑）

### 本命盘（免费）
```bash
{{LANG_INVOKE}} chart --year 1990 --month 7 --day 23 --hour 8 --gender male
```

### 真太阳时精修
```bash
{{LANG_INVOKE}} chart --year 1990 --month 7 --day 23 --hour 8 --minute 30 --gender male --longitude 121.5 --tz 8
```

### 2026 流年运限（免费）
```bash
{{LANG_INVOKE}} transits --year 1990 --month 7 --day 23 --hour 8 --gender male --target-year 2026
```

### 问郑大钱（付费，需 FSFSKey）
```bash
{{LANG_INVOKE}} reading --year 1990 --month 7 --day 23 --hour 8 --gender male --question "看我今年的事业运，该不该跳槽？"
```

### 农历输入
```bash
{{LANG_INVOKE}} chart --year 1990 --month 6 --day 2 --hour 8 --gender male --calendar lunar
```

---

## 错误处理

| HTTP | code | 含义 | Agent 该做什么 |
|------|------|------|----------------|
| 400 | INVALID_INPUT | 参数缺失/越界 | 修正参数重试 |
| 401 | UNAUTHORIZED | 解读 Key 缺失/无效（不降级匿名） | 停止调用，让用户确认或更换 Key |
| 402 | INSUFFICIENT_CREDITS | 积分不足（带 need/have） | 停止调用，不自动重试；可继续免费 `chart` |
| 429 | RATE_LIMITED | 请求过频（按 IP） | 告知用户稍后再试 |
| 500 / 502 | 服务端或生成错误 | 本次调用失败 | 不编造结果；付费请求不得自动重试 |

## 安全 & 隐私

- `doc` 命令纯本地，不发任何网络请求。
- 排盘只把出生信息发往 https://www.fatestar.top；如已配置 Key，会一并发送做用户归属，但接口仍免费。
- 不要打印、复述、记录或持久化真实 Key；除非用户明确要求，也不要保存出生信息与命盘结果。
- 所有网络请求标记 `skill/2.2.0`，用于后台区分 API / MCP / Skill。
- 解读额外发送你的 FSFSKey + 问题。Key 当密码对待：存 `.env` 或环境变量，别贴聊天框。
