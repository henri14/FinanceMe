#!/usr/bin/env bash
# Interactive menu for the Acme FinanceMe AI demo.
# Designed to run inside the docker compose `menu` service.

cd "$(dirname "$0")"

VAULT_URL="${VAULT_URL:-http://localhost:8000}"

# ── Colours ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

# ── Helpers ────────────────────────────────────────────────────────────────────
_ok()   { echo -e "  ${GREEN}✔${NC}  $1"; }
_fail() { echo -e "  ${RED}✘${NC}  $1"; }
_info() { echo -e "  ${YELLOW}→${NC}  $1"; }
_pause(){ echo ""; read -rp "  Press Enter to return to the menu…"; }

_header() {
    clear
    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║      Acme FinanceMe — AI Demo  v1        ║${NC}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  Prometheus metrics: ${BLUE}http://localhost:9090${NC}"
    echo ""
}

# ── 0  Prerequisites ───────────────────────────────────────────────────────────
check_prerequisites() {
    echo ""
    echo -e "${BOLD}Checking prerequisites…${NC}"
    echo ""
    local all_ok=true

    # OPENAI_API_KEY — env var or .env file
    local api_key="${OPENAI_API_KEY:-}"
    if [ -n "$api_key" ]; then
        _ok "OPENAI_API_KEY is set in the environment"
    elif [ -f ".env" ] && grep -q "^OPENAI_API_KEY=" .env; then
        api_key=$(grep "^OPENAI_API_KEY=" .env | head -1 | cut -d'=' -f2- | tr -d '"'"'")
        _ok "OPENAI_API_KEY is defined in .env"
    else
        _fail "OPENAI_API_KEY is not set — add it to the environment or to a .env file"
        all_ok=false
    fi

    if [ -n "$api_key" ] && [ "${api_key:0:3}" != "sk-" ]; then
        _fail "OPENAI_API_KEY does not look valid (expected it to start with sk-)"
        all_ok=false
    fi

    # Vault reachable (corpus is ingested by vault on startup)
    if curl -sf "${VAULT_URL}/metrics" > /dev/null 2>&1; then
        _ok "Vault RAG service is reachable at ${VAULT_URL}"
        _ok "Corpus is ingested and ready"
    else
        _fail "Vault RAG service is not reachable at ${VAULT_URL}"
        all_ok=false
    fi

    echo ""
    if $all_ok; then
        _ok "All prerequisites met — ready to run the missions!"
    else
        _fail "Please resolve the issues above before running the missions."
    fi
}

# ── 1  Chat client ─────────────────────────────────────────────────────────────
mission_1() {
    echo ""
    echo -e "${BOLD}Mission 1 — Simple Chat Client${NC}"
    echo ""
    echo "  The chat client will start in a moment."
    echo "  Suggested first message:  Hello"
    echo "  Type  exit  to end the session and return to this menu."
    echo ""
    read -rp "  Press Enter to launch…"
    echo ""
    uv run python src/cli.py chat || true
}

# ── 2  RAG evaluation ──────────────────────────────────────────────────────────
mission_2() {
    echo ""
    echo -e "${BOLD}Mission 2 — RAG Evaluation${NC}"
    echo ""
    echo "  Runs each evaluation question twice:"
    echo "    • Once answered by the raw LLM with no policy context"
    echo "    • Once answered via the Vault RAG service"
    echo "  Results are scored 1 (pass) / 0 (fail) and shown in a table."
    echo ""
    read -rp "  Press Enter to start…"
    echo ""
    uv run python eval/run.py || true
}

# ── 3  Operations Agent ────────────────────────────────────────────────────────
_run_scenario() {
    local app_id="$1" question="$2" expected_status="$3" label="$4"

    printf "  %-52s" "$label"
    local output
    if output=$(uv run python src/cli.py copilot "$app_id" "$question" 2>/dev/null); then
        local status
        status=$(printf '%s' "$output" \
            | python3 -c "import sys,json; print(json.load(sys.stdin)['AgentStatus'])" 2>/dev/null \
            || echo "parse-error")
        if [ "$status" = "$expected_status" ]; then
            echo -e "${GREEN}PASS${NC}"
            return 0
        else
            echo -e "${RED}FAIL${NC}  (got: $status)"
            return 1
        fi
    else
        echo -e "${RED}FAIL${NC}  (agent returned an error)"
        return 1
    fi
}

mission_3() {
    echo ""
    echo -e "${BOLD}Mission 3 — Operations Agent Tests${NC}"
    echo ""
    echo "  Runs 5 loan-application scenarios through the Copilot agent and"
    echo "  checks that each one produces the expected outcome."
    echo ""
    read -rp "  Press Enter to start…"
    echo ""
    echo -e "  ${BOLD}Scenario                                             Result${NC}"
    echo "  ──────────────────────────────────────────────────────────────"

    local passed=0 failed=0

    _run_scenario "A-1423" \
        "This application has been in verification for 4 days, what should I do?" \
        "plan generated" \
        "A-1423  stuck in verification (4 days)" \
        && passed=$((passed + 1)) || failed=$((failed + 1))

    _run_scenario "A-2001" \
        "What is the current status of this application?" \
        "plan generated" \
        "A-2001  within SLA" \
        && passed=$((passed + 1)) || failed=$((failed + 1))

    _run_scenario "A-3050" \
        "Customer is unresponsive, what are our options?" \
        "plan generated" \
        "A-3050  hardship / unresponsive customer" \
        && passed=$((passed + 1)) || failed=$((failed + 1))

    _run_scenario "A-4100" \
        "Any outstanding actions on this application?" \
        "plan generated" \
        "A-4100  settled loan" \
        && passed=$((passed + 1)) || failed=$((failed + 1))

    _run_scenario "A-9999" \
        "What should I do with this application?" \
        "requires human intervention" \
        "A-9999  application not found" \
        && passed=$((passed + 1)) || failed=$((failed + 1))

    local total=$((passed + failed))
    echo "  ──────────────────────────────────────────────────────────────"
    if [ "$failed" -eq 0 ]; then
        _ok "All tests passed: $passed/$total"
    else
        _fail "$failed test(s) failed — $passed/$total passed"
    fi
}

# ── Main menu loop ─────────────────────────────────────────────────────────────
while true; do
    _header
    echo "  0)  Check prerequisites"
    echo "  1)  Mission 1 — Simple chat client"
    echo "  2)  Mission 2 — RAG evaluation"
    echo "  3)  Mission 3 — Operations Agent tests"
    echo "  q)  Quit"
    echo ""
    read -rp "  Select an option: " choice

    case "$choice" in
        0) check_prerequisites; _pause ;;
        1) mission_1;           _pause ;;
        2) mission_2;           _pause ;;
        3) mission_3;           _pause ;;
        q|Q) echo ""; echo "  Goodbye!"; echo ""; exit 0 ;;
        *) echo ""; echo -e "  ${YELLOW}Unknown option — please enter 0, 1, 2, 3, or q.${NC}"; sleep 1 ;;
    esac
done
