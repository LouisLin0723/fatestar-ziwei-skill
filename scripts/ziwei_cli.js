#!/usr/bin/env node
/**
 * FateStar Ziwei CLI — Zi Wei Dou Shu (紫微斗数) charting + 郑大钱 AI reading.
 *
 *   chart     GET  /api/ziwei              (free, anonymous)
 *   transits  GET  /api/ziwei?transits=1   (free)
 *   reading   POST /api/ziwei/reading       (paid, needs fs_live_ key)
 *   doc       offline interface spec
 *
 * Zero third-party deps (Node built-in https/http). Node >= 12.
 */
"use strict";

const fs = require("fs");
const path = require("path");
const http = require("http");
const https = require("https");

function loadEnv() {
  // Priority: --api_key > .env file > environment variable > anonymous.
  const dir = __dirname;
  for (const envPath of [path.join(dir, ".env"), path.join(dir, "..", ".env")]) {
    if (!fs.existsSync(envPath)) continue;
    const text = fs.readFileSync(envPath, "utf-8").replace(/^﻿/, "");
    for (let line of text.split(/\r?\n/)) {
      line = line.trim();
      if (!line || line.startsWith("#") || !line.includes("=")) continue;
      const idx = line.indexOf("=");
      const key = line.slice(0, idx).trim();
      const val = line.slice(idx + 1).trim().replace(/^["']|["']$/g, "").trim();
      if (key && val) process.env[key] = val;
    }
  }
}
loadEnv();

// BEGIN GENERATED:CONSTANTS
const DEFAULT_API_BASE = "https://www.fatestar.top";
const CHART_PATH = "/api/ziwei";
const READING_PATH = "/api/ziwei/reading";
// END GENERATED:CONSTANTS

function apiBase() {
  return (process.env.FATESTAR_API_BASE || DEFAULT_API_BASE).replace(/\/+$/, "");
}

function buildBirthParams(args) {
  const p = {
    year: args.year,
    month: args.month,
    day: args.day,
    hour: args.hour,
    gender: args.gender,
    calendarType: args.calendar || "solar",
  };
  if (args.minute !== undefined) p.minute = args.minute;
  if (args.leap) p.isLeapMonth = "true";
  if (args.longitude !== undefined) p.longitude = args.longitude;
  if (args.tz !== undefined) p.timezoneOffset = args.tz;
  return p;
}

function safeJson(raw) {
  try { return JSON.parse(raw); } catch (e) { return { _raw: raw }; }
}

function request(method, urlStr, opts) {
  opts = opts || {};
  return new Promise((resolve, reject) => {
    const u = new URL(urlStr);
    const lib = u.protocol === "http:" ? http : https;
    const headers = { Accept: "application/json" };
    let payload;
    if (opts.body) {
      payload = JSON.stringify(opts.body);
      headers["Content-Type"] = "application/json";
      headers["Content-Length"] = Buffer.byteLength(payload);
    }
    if (opts.apiKey) headers["Authorization"] = `Bearer ${opts.apiKey}`;
    const req = lib.request(u, { method, headers, timeout: 40000 }, (res) => {
      let data = "";
      res.setEncoding("utf-8");
      res.on("data", (c) => (data += c));
      res.on("end", () => resolve({ status: res.statusCode, raw: data }));
    });
    req.on("error", reject);
    req.on("timeout", () => req.destroy(new Error("timeout")));
    if (payload) req.write(payload);
    req.end();
  });
}

function errFrom(raw, status) {
  let body = {};
  try { body = JSON.parse(raw); } catch (e) {}
  const err = (body && body.error) || {};
  const code = err.code || `HTTP_${status}`;
  const msg = err.message || (raw ? raw.slice(0, 500) : `HTTP ${status}`);
  process.stderr.write(`API Error [${code}]: ${msg}\n`);
  return 1;
}

async function getChart(query) {
  const url = apiBase() + CHART_PATH + "?" + new URLSearchParams(query).toString();
  try {
    return await request("GET", url, {});
  } catch (e) {
    process.stderr.write(`Connection Error: unable to reach ${apiBase()} (${e.message})\n`);
    process.exit(1);
  }
}

async function cmdChart(args) {
  const { status, raw } = await getChart(buildBirthParams(args));
  if (status !== 200) process.exit(errFrom(raw, status));
  process.stdout.write(raw + "\n");
}

async function cmdTransits(args) {
  const query = buildBirthParams(args);
  query.transits = "1";
  if (args["target-year"] !== undefined) query.targetYear = args["target-year"];
  if (args["target-month"] !== undefined) query.targetMonth = args["target-month"];
  if (args["target-day"] !== undefined) query.targetDay = args["target-day"];
  if (args["target-hour"] !== undefined) query.targetHour = args["target-hour"];
  const { status, raw } = await getChart(query);
  if (status !== 200) process.exit(errFrom(raw, status));
  process.stdout.write(raw + "\n");
}

async function cmdReading(args) {
  const question = (args.question || "").toString().trim();
  if (!question) {
    process.stderr.write("Error: --question is required for reading.\n");
    process.exit(1);
  }
  const apiKey = (args.api_key || process.env.FATESTAR_API_KEY || "").trim();
  if (!apiKey) {
    process.stderr.write(
      "郑大钱解读需要 fs_live_ key (尚未配置)。\n" +
      "请到 https://www.fatestar.top 注册免费会员 → 做新手任务领积分 →\n" +
      "开发者中心创建 fs_live_ key → 写进 .env (FATESTAR_API_KEY=) 或用 --api_key 传入。\n" +
      "在此之前可用 `chart` 免费排盘, 再自行解读。\n"
    );
    process.exit(2);
  }
  const body = buildBirthParams(args);
  body.question = question;
  let res;
  try {
    res = await request("POST", apiBase() + READING_PATH, { body, apiKey });
  } catch (e) {
    process.stderr.write(`Connection Error: unable to reach ${apiBase()} (${e.message})\n`);
    process.exit(1);
  }
  const { status, raw } = res;
  const resp = safeJson(raw);
  if (status === 200) {
    const data = resp.data || {};
    if (!data.reading) {
      process.stderr.write("郑大钱解读失败: 空回复 (未扣费), 请重试。\n");
      process.exit(1);
    }
    process.stdout.write(data.reading + "\n");
    if (data.creditsUsed !== undefined || data.balanceAfter !== undefined) {
      process.stderr.write(`\n---\n[积分] 本次扣除 ${data.creditsUsed}, 剩余 ${data.balanceAfter}\n`);
    }
    return;
  }
  const err = (resp && resp.error) || {};
  if (status === 401) {
    process.stderr.write("Key 无效或已吊销 (401)。请到 https://www.fatestar.top 开发者中心确认或重新申请 fs_live_ key。\n");
  } else if (status === 402) {
    process.stderr.write(
      `积分不足 (402, 需 ${err.need} / 有 ${err.have}), 未扣费。\n` +
      "请到 https://www.fatestar.top 充值, 或等北京时间 21:00 免费重置 (每日 3 积分)。\n" +
      "现在可改用 `chart` 拿命盘数据 + 自行解读兜底。\n"
    );
  } else {
    errFrom(raw, status);
  }
  process.exit(1);
}

// BEGIN GENERATED:DOC_SPEC
function renderDoc() {
  const shared = path.join(__dirname, "shared");
  let tpl = fs.readFileSync(path.join(shared, "doc_spec.md"), "utf-8");
  tpl = tpl.replace(/\{\{LANG_NAME\}\}/g, "Node.js");
  tpl = tpl.replace(/\{\{LANG_CODEBLOCK\}\}/g, "");
  tpl = tpl.replace(/\{\{LANG_INVOKE\}\}/g, "node scripts/ziwei_cli.js");
  return tpl;
}
// END GENERATED:DOC_SPEC

function cmdDoc() {
  process.stdout.write(renderDoc() + "\n");
}

const INT_FLAGS = new Set(["year", "month", "day", "hour", "minute", "target-year", "target-month", "target-day", "target-hour"]);
const FLOAT_FLAGS = new Set(["longitude", "tz"]);
const BOOL_FLAGS = new Set(["leap"]);

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) continue;
    const key = a.slice(2);
    if (BOOL_FLAGS.has(key)) { args[key] = true; continue; }
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) { args[key] = true; continue; }
    if (INT_FLAGS.has(key)) args[key] = parseInt(next, 10);
    else if (FLOAT_FLAGS.has(key)) args[key] = parseFloat(next);
    else args[key] = next;
    i++;
  }
  return args;
}

function requireBirth(args) {
  for (const k of ["year", "month", "day", "hour", "gender"]) {
    if (args[k] === undefined) {
      process.stderr.write(`Error: --${k} is required.\n`);
      process.exit(1);
    }
  }
  if (!["male", "female"].includes(args.gender)) {
    process.stderr.write("Error: --gender must be male or female.\n");
    process.exit(1);
  }
  if (args.calendar && !["solar", "lunar"].includes(args.calendar)) {
    process.stderr.write("Error: --calendar must be solar or lunar.\n");
    process.exit(1);
  }
}

async function main() {
  const argv = process.argv.slice(2);
  const command = argv[0];
  const args = parseArgs(argv.slice(1));
  switch (command) {
    case "chart": requireBirth(args); await cmdChart(args); break;
    case "transits": requireBirth(args); await cmdTransits(args); break;
    case "reading": requireBirth(args); await cmdReading(args); break;
    case "doc": case undefined: cmdDoc(); break;
    default:
      process.stderr.write(`Unknown command: ${command}. Use one of: chart, transits, reading, doc.\n`);
      process.exit(1);
  }
}

main();
