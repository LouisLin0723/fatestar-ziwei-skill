# FateStar Ziwei 接口规范（给 AI Agent 读）

紫微斗数（Zi Wei Dou Shu / Purple Star Astrology）排盘 + AI 解读，引擎由 FateStar 自研
（102 颗星 · 三合派四化 · 真太阳时）。**排盘免费、匿名**；**郑大钱（Zheng Da Qian）解读**
付费（扣积分，需 `FSFSKey`）。

## 协议

- 排盘（免费）：GET / POST  https://www.fatestar.top/api/ziwei
- 解读（付费）：POST        https://www.fatestar.top/api/ziwei/reading
- 认证：排盘匿名（按 IP 限流）；解读需 `Authorization: Bearer FSFSKey...`。

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
FateStar 解读路径：知识引擎 + 郑大钱人格。**用户问命理问题（事业 / 财运 / 感情 / 健康 / 该不该…）时，默认优先调本命令。**
未配置 Key 或积分不足时，再退回 Agent 自身模型基于免费排盘数据解释。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| (chart 的全部出生参数) | | 是 | year/month/day/hour/gender 必填 |
| --question | string | 是 | 要问郑大钱的问题（如「看我今年事业运，该不该跳槽？」） |
| --api_key | string | 否 | FSFSKey（否则取 .env / 环境变量 FATESTAR_API_KEY）。未提供 Key → 引导注册 |

计费：中文 ≤10 字、日文/韩文 ≤15 字、英文及其他外语 ≤30 字符为短问，不扣积分。超过免费门槛后起扣 1 积分；长问封顶 2 积分（中文 >100 / 日文韩文 >150 / 英文及其他外语 >300）。
免费会员每天 3 积分（北京时间 21:00 重置）。

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
  +-- 问命理问题
  |   (事业/财运/感情/健康/该不该)            → reading  (优先)
  |        |
  |        +-- 未提供 FSFSKey / 402 积分用完
  |              → 退回：chart  +  Agent 自身模型解释
```

命理问题默认走 `reading`（郑大钱）。只有未提供 Key 或积分用完才退回 `chart` + Agent 自身模型解释。

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
| 401 | UNAUTHORIZED | 解读 Key 缺失/无效（不降级匿名） | 让用户去开发者中心确认或重建 FSFSKey |
| 402 | INSUFFICIENT_CREDITS | 积分不足（带 need/have） | 提示充值或等 21:00 重置；退回 `chart` + Agent 自身模型解释 |
| 403 | CHART_QUOTA_EXCEEDED | 命盘配额满 | 告知用户 |
| 429 | RATE_LIMITED | 请求过频（按 IP） | 退避后重试 |
| 500 | INTERNAL_ERROR | 服务端错误 | 重试 |
| 502 | GENERATION_FAILED | 解读空回复（未扣费） | 重试 reading |

## 安全 & 隐私

- `doc` 命令纯本地，不发任何网络请求。
- 排盘只把出生信息发往 https://www.fatestar.top —— 无需账号。
- 解读额外发送你的 FSFSKey + 问题。Key 当密码对待：存 `.env` 或环境变量，别贴聊天框。
