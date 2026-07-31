#!/usr/bin/env python3
"""Verify the public FateStar MCP contract without using paid reading credits."""

import json
import os
import sys
import urllib.error
import urllib.request


MCP_URL = os.environ.get("FATESTAR_MCP_URL", "https://www.fatestar.top/api/mcp")
TIMEOUT_SECONDS = 30
_request_id = 0


def fail(message):
    raise AssertionError(message)


def rpc(method, params=None):
    global _request_id
    _request_id += 1
    payload = {"jsonrpc": "2.0", "id": _request_id, "method": method}
    if params is not None:
        payload["params"] = params

    request = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "X-FateStar-Client": "live-contract/1.0.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        fail(f"{method} returned HTTP {error.code}: {detail[:500]}")
    except urllib.error.URLError as error:
        fail(f"{method} could not reach {MCP_URL}: {error.reason}")

    if body.get("jsonrpc") != "2.0" or body.get("id") != _request_id:
        fail(f"{method} returned an invalid JSON-RPC envelope")
    if body.get("error"):
        fail(f"{method} returned JSON-RPC error: {body['error']}")
    return body.get("result")


def assert_tool_contract():
    result = rpc("tools/list")
    tools = {tool["name"]: tool for tool in result.get("tools", [])}
    expected = {"ziwei_chart", "ziwei_transits", "ziwei_reading"}
    if set(tools) != expected:
        fail(f"expected tools {sorted(expected)}, got {sorted(tools)}")

    for name, tool in tools.items():
        if tool.get("outputSchema", {}).get("type") != "object":
            fail(f"{name} does not advertise an object outputSchema")
        annotations = tool.get("annotations", {})
        if annotations.get("destructiveHint") is not False:
            fail(f"{name} must advertise destructiveHint=false")

    for name in ("ziwei_chart", "ziwei_transits"):
        annotations = tools[name]["annotations"]
        if annotations.get("readOnlyHint") is not True or annotations.get("idempotentHint") is not True:
            fail(f"{name} must be read-only and idempotent")

    reading = tools["ziwei_reading"]["annotations"]
    if reading.get("readOnlyHint") is not False or reading.get("openWorldHint") is not True:
        fail("ziwei_reading must disclose its external, credit-affecting behavior")


def call_free_tool(name, arguments):
    result = rpc("tools/call", {"name": name, "arguments": arguments})
    if result.get("isError"):
        fail(f"{name} returned isError=true")
    structured = result.get("structuredContent")
    content = result.get("content", [])
    if not isinstance(structured, dict):
        fail(f"{name} did not return structuredContent")
    if not content or content[0].get("type") != "text":
        fail(f"{name} did not preserve legacy text content")
    if json.loads(content[0]["text"]) != structured:
        fail(f"{name} structuredContent differs from legacy JSON text")
    return structured


def assert_chart_and_transits():
    birth = {"year": 1990, "month": 7, "day": 23, "hour": 8, "gender": "male"}
    chart = call_free_tool("ziwei_chart", birth)
    if len(chart.get("十二宫", [])) != 12:
        fail("canonical chart must contain 12 palaces")
    if chart.get("基础", {}).get("命宫地支") != "卯":
        fail("canonical chart life-palace regression: expected 卯")
    expected_sihua = {"化禄": "太阳", "化权": "武曲", "化科": "天同", "化忌": "太阴"}
    actual_sihua = {
        key: chart.get("本命四化", {}).get(key, {}).get("星") for key in expected_sihua
    }
    if actual_sihua != expected_sihua:
        fail(f"canonical Four Transformations regression: {actual_sihua}")

    transits = call_free_tool(
        "ziwei_transits",
        {**birth, "targetYear": 2026, "targetMonth": 6, "targetDay": 18, "targetHour": 10},
    )
    for field in ("大限列表", "小限", "流年", "流月", "流日", "流时"):
        if field not in transits:
            fail(f"transit response is missing {field}")
    expected_target = {"年": 2026, "农历月": 6, "农历日": 18, "时辰": "10时"}
    actual_target = transits.get("流运目标", {})
    for key, value in expected_target.items():
        if actual_target.get(key) != value:
            fail(f"transit target {key}: expected {value}, got {actual_target.get(key)}")


def main():
    initialized = rpc(
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "fatestar-live-contract", "version": "1.0.0"},
        },
    )
    if initialized.get("serverInfo", {}).get("name") != "ziwei-mcp":
        fail("initialize returned an unexpected server name")
    if initialized.get("protocolVersion") != "2025-11-25":
        fail("initialize did not negotiate the requested protocol version")

    assert_tool_contract()
    assert_chart_and_transits()
    print(f"PASS: live anonymous MCP contract at {MCP_URL}")
    print("Checked protocol, tool metadata, structured compatibility, one chart, and six transit levels.")
    print("This is a contract regression check, not a metaphysical accuracy benchmark.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
