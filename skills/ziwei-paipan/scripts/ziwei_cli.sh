#!/usr/bin/env bash
# FateStar Ziwei CLI - Zi Wei Dou Shu (紫微斗数) charting + 郑大钱 AI reading.
#
#   chart     GET  /api/ziwei              (free, anonymous)
#   transits  GET  /api/ziwei?transits=1   (free)
#   reading   POST /api/ziwei/reading       (paid, needs FSFSKey)
#   doc       offline interface spec
#
# Requires: bash 4+, curl. (reading extracts cleanest output when jq is present.)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

load_env() {
  # Priority: --api_key > .env file > environment variable > anonymous.
  local f
  for f in "$SCRIPT_DIR/.env" "$SCRIPT_DIR/../.env"; do
    [ -f "$f" ] || continue
    while IFS= read -r line || [ -n "$line" ]; do
      line="${line#"${line%%[![:space:]]*}"}"        # ltrim
      case "$line" in ""|\#*) continue;; esac
      case "$line" in *=*) ;; *) continue;; esac
      local key="${line%%=*}"
      local val="${line#*=}"
      key="${key#"${key%%[![:space:]]*}"}"; key="${key%"${key##*[![:space:]]}"}"
      val="${val#"${val%%[![:space:]]*}"}"; val="${val%"${val##*[![:space:]]}"}"
      val="${val#[\"\']}"; val="${val%[\"\']}"
      [ -n "$key" ] && [ -n "$val" ] && export "$key=$val"
    done < "$f"
  done
}
load_env

# BEGIN GENERATED:CONSTANTS
DEFAULT_API_BASE="https://www.fatestar.top"
CHART_PATH="/api/ziwei"
READING_PATH="/api/ziwei/reading"
CLIENT_ID="skill/2.2.0"
# END GENERATED:CONSTANTS

api_base() {
  local b="${FATESTAR_API_BASE:-$DEFAULT_API_BASE}"
  echo "${b%/}"
}

declare -A ARGS

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --leap) ARGS[leap]=1; shift;;
      --*)
        local key="${1#--}"
        if [ $# -ge 2 ] && [ "${2#--}" = "$2" ]; then
          ARGS[$key]="$2"; shift 2
        else
          ARGS[$key]=1; shift
        fi;;
      *) shift;;
    esac
  done
}

require_birth() {
  local k
  for k in year month day hour gender; do
    if [ -z "${ARGS[$k]:-}" ]; then echo "Error: --$k is required." >&2; exit 1; fi
  done
  case "${ARGS[gender]}" in male|female) ;; *) echo "Error: --gender must be male or female." >&2; exit 1;; esac
  if [ -n "${ARGS[calendar]:-}" ]; then
    case "${ARGS[calendar]}" in solar|lunar) ;; *) echo "Error: --calendar must be solar or lunar." >&2; exit 1;; esac
  fi
}

build_birth_query() {
  local cal="${ARGS[calendar]:-solar}"
  local q="year=${ARGS[year]}&month=${ARGS[month]}&day=${ARGS[day]}&hour=${ARGS[hour]}&gender=${ARGS[gender]}&calendarType=$cal"
  [ -n "${ARGS[minute]:-}" ]    && q="$q&minute=${ARGS[minute]}"
  [ -n "${ARGS[leap]:-}" ]      && q="$q&isLeapMonth=true"
  [ -n "${ARGS[longitude]:-}" ] && q="$q&longitude=${ARGS[longitude]}"
  [ -n "${ARGS[tz]:-}" ]        && q="$q&timezoneOffset=${ARGS[tz]}"
  echo "$q"
}

RESP_STATUS=""
RESP_BODY=""

api_call() {
  # $1=method $2=url $3=body $4=apikey ; sets RESP_STATUS / RESP_BODY
  local curl_args=(-s -m 40 -w $'\n%{http_code}' -H "Accept: application/json" -H "X-FateStar-Client: $CLIENT_ID")
  [ -n "$4" ] && curl_args+=(-H "Authorization: Bearer $4")
  if [ "$1" = "POST" ]; then
    curl_args+=(-X POST -H "Content-Type: application/json" --data "$3")
  fi
  local out
  if ! out=$(curl "${curl_args[@]}" "$2"); then
    echo "Connection Error: unable to reach $(api_base)" >&2; exit 1
  fi
  RESP_STATUS="${out##*$'\n'}"
  RESP_BODY="${out%$'\n'*}"
}

has_jq() { command -v jq >/dev/null 2>&1; }

err_from() {
  # $1=raw $2=status
  local code="HTTP_$2" msg="$1"
  if has_jq; then
    local c m
    c=$(printf '%s' "$1" | jq -r '.error.code // empty' 2>/dev/null)
    m=$(printf '%s' "$1" | jq -r '.error.message // empty' 2>/dev/null)
    [ -n "$c" ] && code="$c"
    [ -n "$m" ] && msg="$m"
  fi
  echo "API Error [$code]: $msg" >&2
}

cmd_chart() {
  local key="${ARGS[api_key]:-${FATESTAR_API_KEY:-}}"
  api_call GET "$(api_base)$CHART_PATH?$(build_birth_query)" "" "$key"
  if [ "$RESP_STATUS" != "200" ]; then err_from "$RESP_BODY" "$RESP_STATUS"; exit 1; fi
  printf '%s\n' "$RESP_BODY"
}

cmd_transits() {
  local q key; q="$(build_birth_query)&transits=1"; key="${ARGS[api_key]:-${FATESTAR_API_KEY:-}}"
  [ -n "${ARGS[target-year]:-}" ]  && q="$q&targetYear=${ARGS[target-year]}"
  [ -n "${ARGS[target-month]:-}" ] && q="$q&targetMonth=${ARGS[target-month]}"
  [ -n "${ARGS[target-day]:-}" ]   && q="$q&targetDay=${ARGS[target-day]}"
  [ -n "${ARGS[target-hour]:-}" ]  && q="$q&targetHour=${ARGS[target-hour]}"
  api_call GET "$(api_base)$CHART_PATH?$q" "" "$key"
  if [ "$RESP_STATUS" != "200" ]; then err_from "$RESP_BODY" "$RESP_STATUS"; exit 1; fi
  printf '%s\n' "$RESP_BODY"
}

build_reading_body() {
  local cal="${ARGS[calendar]:-solar}"
  if has_jq; then
    local filter='{year:($year|tonumber),month:($month|tonumber),day:($day|tonumber),hour:($hour|tonumber),gender:$gender,calendarType:$cal,question:$q}'
    [ -n "${ARGS[minute]:-}" ]    && filter="$filter + {minute:(\$minute|tonumber)}"
    [ -n "${ARGS[leap]:-}" ]      && filter="$filter + {isLeapMonth:true}"
    [ -n "${ARGS[longitude]:-}" ] && filter="$filter + {longitude:(\$lon|tonumber)}"
    [ -n "${ARGS[tz]:-}" ]        && filter="$filter + {timezoneOffset:(\$tz|tonumber)}"
    jq -nc \
      --arg year "${ARGS[year]}" --arg month "${ARGS[month]}" --arg day "${ARGS[day]}" \
      --arg hour "${ARGS[hour]}" --arg gender "${ARGS[gender]}" --arg cal "$cal" \
      --arg q "${ARGS[question]:-}" --arg minute "${ARGS[minute]:-}" \
      --arg lon "${ARGS[longitude]:-}" --arg tz "${ARGS[tz]:-}" \
      "$filter"
  else
    # Minimal fallback (no jq): core params + question, basic escaping.
    local q="${ARGS[question]:-}"
    q="${q//\\/\\\\}"; q="${q//\"/\\\"}"
    printf '{"year":%s,"month":%s,"day":%s,"hour":%s,"gender":"%s","calendarType":"%s","question":"%s"}' \
      "${ARGS[year]}" "${ARGS[month]}" "${ARGS[day]}" "${ARGS[hour]}" "${ARGS[gender]}" "$cal" "$q"
  fi
}

cmd_reading() {
  local question="${ARGS[question]:-}"
  if [ -z "$question" ]; then echo "Error: --question is required for reading." >&2; exit 1; fi
  local key="${ARGS[api_key]:-${FATESTAR_API_KEY:-}}"
  if [ -z "$key" ]; then
    {
      echo "郑大钱解读需要 FSFSKey（尚未配置）。"
      echo "请到 https://www.fatestar.top 注册免费会员 → 做新手任务领积分 →"
      echo "开发者中心创建 FSFSKey → 写进 .env (FATESTAR_API_KEY=) 或用 --api_key 传入。"
      echo "在此之前可用 \`chart\` 免费排盘，再由 Agent 自身模型解释。"
    } >&2
    exit 2
  fi
  api_call POST "$(api_base)$READING_PATH" "$(build_reading_body)" "$key"
  if [ "$RESP_STATUS" = "200" ]; then
    if has_jq; then
      local reading; reading=$(printf '%s' "$RESP_BODY" | jq -r '.data.reading // empty')
      if [ -z "$reading" ]; then echo "郑大钱解读失败：空回复（未扣费），请重试。" >&2; exit 1; fi
      printf '%s\n' "$reading"
      local used after; used=$(printf '%s' "$RESP_BODY" | jq -r '.data.creditsUsed // empty'); after=$(printf '%s' "$RESP_BODY" | jq -r '.data.balanceAfter // empty')
      echo "" >&2; echo "---" >&2; echo "[积分] 本次扣除 $used, 剩余 $after" >&2
    else
      # No jq: emit the raw JSON; the agent can read .data.reading itself.
      printf '%s\n' "$RESP_BODY"
    fi
    return
  fi
  case "$RESP_STATUS" in
    401) echo "Key 无效或已失效 (401)。请到 https://www.fatestar.top 开发者中心确认或重新申请 FSFSKey。" >&2;;
    402)
      local need have
      if has_jq; then need=$(printf '%s' "$RESP_BODY" | jq -r '.error.need // empty'); have=$(printf '%s' "$RESP_BODY" | jq -r '.error.have // empty'); fi
      {
        echo "积分不足 (402, 需 ${need:-?} / 有 ${have:-?}), 未扣费。"
        echo "请到 https://www.fatestar.top 查看当前积分与可用选项。"
        echo "不要自动重试 \`reading\`；现在可改用免费 \`chart\` 拿命盘数据。"
      } >&2;;
    *) err_from "$RESP_BODY" "$RESP_STATUS";;
  esac
  exit 1
}

# BEGIN GENERATED:DOC_SPEC
_cmd_doc() {
  local tpl
  tpl=$(cat "$SCRIPT_DIR/shared/doc_spec.md")
  tpl="${tpl//\{\{LANG_NAME\}\}/Bash}"
  tpl="${tpl//\{\{LANG_CODEBLOCK\}\}/bash}"
  tpl="${tpl//\{\{LANG_INVOKE\}\}/bash scripts/ziwei_cli.sh}"
  printf '%s\n' "$tpl"
}
# END GENERATED:DOC_SPEC

main() {
  local command="${1:-}"
  shift || true
  parse_args "$@"
  case "$command" in
    chart) require_birth; cmd_chart;;
    transits) require_birth; cmd_transits;;
    reading) require_birth; cmd_reading;;
    doc|"") _cmd_doc;;
    *) echo "Unknown command: $command. Use one of: chart, transits, reading, doc." >&2; exit 1;;
  esac
}

main "$@"
