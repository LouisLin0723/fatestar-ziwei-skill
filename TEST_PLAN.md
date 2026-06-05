# FateStar Ziwei Skill 端到端测试计划

## 测试目标

验证以下功能在所有 4 个 CLI(Python / Node.js / PowerShell / Bash)上行为一致:

- `chart` 本命盘(公历 / 农历 / 真太阳时)
- `transits` 6 层运限 + 流年目标
- `reading` 郑大钱解读(有 key / 没 key 降级 / 402 积分用完)
- `doc` 离线接口规范渲染
- 错误处理(坏参数 / 未知命令)
- 中文输出无乱码(尤其 PowerShell 5.1 — 需 UTF-8 BOM)

## 前置条件

1. 已探测可用 runtime,或 `runtime.conf` 就位(优先级 Python > Node.js > Shell)
2. 测 `reading` 真解读需 `.env` 里有有效 `fs_live_` key(没有则只测降级路径)
3. `generate.py --check` 应 exit 0(4 个 CLI 的公共块一致)

---

## 第一组:chart 排盘(免费)

| # | 需求 | 预期 |
|---|---|---|
| 1 | `chart --year 1990 --month 7 --day 23 --hour 8 --gender male` | JSON,顶层含 `"data"`,内有 `基础` / `十二宫` / `本命四化` |
| 2 | 农历:加 `--calendar lunar` | 正常出盘 JSON |
| 3 | 真太阳时:加 `--minute 30 --longitude 121.5 --tz 8` | 正常出盘,`输入.真太阳时` = 已启用 |
| 4 | 女命:`--gender female` | 正常出盘 |

## 第二组:transits 运限(免费)

| # | 需求 | 预期 |
|---|---|---|
| 5 | `transits … --target-year 2026` | JSON 含 `运限`(大限 / 小限 / 流年 / 流月 / 流日 / 流时) |
| 6 | transits 不传 target | 默认当年 + 本命月日,正常出盘 |

## 第三组:reading 郑大钱解读

| # | 需求 | 预期 |
|---|---|---|
| 7 | `reading … --question "今年事业运?"`,**没配 key** | stderr 输出注册引导,exit code = 2 |
| 8 | reading 缺 `--question` | stderr「--question is required」,exit 1 |
| 9 | reading 有有效 key + 有积分(需真 key) | stdout 输出郑大钱解读全文;stderr 报扣除/剩余积分 |
| 10 | reading key 无效(乱填 fs_live_xxx) | 401 提示去开发者中心,exit 1 |

## 第四组:doc + 错误处理

| # | 需求 | 预期 |
|---|---|---|
| 11 | `doc` | 输出接口规范,首行 `# FateStar Ziwei 接口规范`,占位符已替换(无 `{{LANG_INVOKE}}`) |
| 12 | `chart --month 99 …`(越界) | `API Error [INVALID_INPUT]`,exit 1 |
| 13 | 未知命令 `foobar` | 「Unknown command」提示,exit 1 |
| 14 | 缺必填 `--gender` | 「--gender is required」,exit 1 |

## 第五组:跨 runtime 一致性

| # | 需求 | 预期 |
|---|---|---|
| 15 | 同一 chart 命令在 py / js / ps1 / sh 各跑一次 | 四者都返回同一命盘(同一 `data`) |
| 16 | PowerShell 5.1 跑 doc / chart | 中文无乱码(验证 `.ps1` 的 UTF-8 BOM 生效) |

---

## 通过标准

- 第 1-6、11、15、16 组输出符合预期,中文无乱码
- 第 7、12、13、14 组 exit code 与提示正确(降级 / 报错路径)
- `generate.py --check` exit 0
- 偶发 `Connection Error` / `Timeout` 不算失败(网络抖动),重试即可

## 执行方式

在另一个 session 加载 ziwei-paipan skill,AI 自动走平台探测 + CLI 路由,用自然语言描述上述场景即可;或直接按 `runtime.conf` 的命令逐条跑。
