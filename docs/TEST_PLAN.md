# FateStar Ziwei Skill 端到端测试计划

## 测试目标

验证以下功能在所有 4 个 CLI（Python / Node.js / PowerShell / Bash）上行为一致：

- `chart` 本命盘（公历 / 农历 / 真太阳时）
- `transits` 6 层运限 + 流年目标
- `reading` 郑大钱解读（有 Key / 未配置 Key 引导 / 402 积分用完）
- `doc` 离线接口规范渲染
- 错误处理（坏参数 / 未知命令）
- 中文输出无乱码（尤其 PowerShell 5.1，需 UTF-8 BOM）
- 每个网络请求都带 `X-FateStar-Client: skill/2.2.0`
- 配置 Key 后，免费 chart/transits 也带 Authorization，但仍不扣积分

## 前置条件

1. 已探测可用 runtime，或 `runtime.conf` 就位（优先级 Python > Node.js > Shell）
2. 真实 `reading` 测试必须先取得操作者明确批准并确认测试积分预算，再使用 `.env` 中的有效 `FSFSKey`；否则只测未配置 Key 的停止路径
3. `generate.py --check` 应 exit 0（4 个 CLI 的公共块一致）

---

## 第一组：chart 排盘（免费）

| # | 需求 | 预期 |
|---|---|---|
| 1 | `chart --year 1990 --month 7 --day 23 --hour 8 --gender male` | JSON，顶层含 `"data"`，内有 `基础` / `十二宫` / `本命四化` |
| 2 | 农历：加 `--calendar lunar` | 正常出盘 JSON |
| 3 | 真太阳时：加 `--minute 30 --longitude 121.5 --tz 8` | 正常出盘，`输入.真太阳时` = 已启用 |
| 4 | 女命：`--gender female` | 正常出盘 |

## 第二组：transits 运限（免费）

| # | 需求 | 预期 |
|---|---|---|
| 5 | `transits … --target-year 2026` | JSON 含 `运限`（大限 / 小限 / 流年 / 流月 / 流日 / 流时） |
| 6 | transits 不传 target | 默认当年 + 本命月日，正常出盘 |

## 第三组：reading 郑大钱解读

| # | 需求 | 预期 |
|---|---|---|
| 7 | `reading … --question "今年事业运？"`，**未配置 Key** | stderr 输出注册引导，exit code = 2 |
| 8 | reading 缺 `--question` | stderr「--question is required」，exit 1 |
| 9 | 经明确批准后，reading 使用有效 Key + 测试积分 | stdout 输出郑大钱解读全文；stderr 报实际扣除/剩余积分 |
| 10 | reading Key 无效（乱填 FSFSKeyxxx） | 401 提示去开发者中心，exit 1 |

## 第四组：doc + 错误处理

| # | 需求 | 预期 |
|---|---|---|
| 11 | `doc` | 输出接口规范，首行 `# FateStar Ziwei 接口规范`，占位符已替换（无 `{{LANG_INVOKE}}`） |
| 12 | `chart --month 99 …`（越界） | `API Error [INVALID_INPUT]`，exit 1 |
| 13 | 未知命令 `foobar` | 「Unknown command」提示，exit 1 |
| 14 | 缺必填 `--gender` | 「--gender is required」，exit 1 |

## 第五组：跨 runtime 一致性

| # | 需求 | 预期 |
|---|---|---|
| 15 | 同一 chart 命令在 py / js / ps1 / sh 各跑一次 | 四者都返回同一命盘（同一 `data`） |
| 16 | PowerShell 5.1 跑 doc / chart | 中文无乱码（验证 `.ps1` 的 UTF-8 BOM 生效） |
| 17 | 用本地 mock API 跑 py / js / ps1 / sh 的 chart | 四者都发送 `X-FateStar-Client: skill/2.2.0` |
| 18 | 配置测试 Key后跑免费 chart | 请求带 Authorization；响应仍走免费 chart，不触发 reading |

---

## 通过标准

- 第 1-6、11、15、16 项输出符合预期，中文无乱码
- 第 7、12、13、14 项 exit code 与提示正确（未配置 Key / 报错路径）
- 第 9 项只有在已批准真实付费测试时才是必测项
- `generate.py --check` exit 0
- 偶发 `Connection Error` / `Timeout` 需记录；免费调用可重试一次，付费 `reading` 不得自动重试

## 执行方式

在另一个 session 加载 ziwei-paipan Skill，AI 自动走平台探测 + CLI 路由，用自然语言描述上述场景即可；或直接按 `runtime.conf` 的命令逐条跑。
