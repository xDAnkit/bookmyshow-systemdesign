#!/usr/bin/env python3
"""Shared guardrail hook for every AI tool (Claude Code, Cursor, Codex, Antigravity, Grok).

Reads the tool-call JSON on stdin. Exit 2 blocks the call.
Fails closed: any error blocks. Rules live in AGENTS.md. Keep both in sync.
"""
import json
import re
import shlex
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"  # file writes here need no approval
APPROVED = ROOT / ".agents" / "APPROVED"  # user creates this to say "go"
ALLOW_NET = ROOT / ".agents" / "ALLOW_NET"  # user touches this to open network
NET_TTL = 30 * 60  # seconds the network stays open after the touch

PROTECTED = re.compile(r"\.(agents|claude|cursor|codex|gemini|grok)(/|\b)")
NET_TOOLS = {"WebFetch", "WebSearch", "Artifact", "ArtifactComments", "ArtifactData", "PushNotification",
             "RemoteTrigger", "CronCreate", "CronDelete", "ListMcpResourcesTool", "ReadMcpResourceTool",
             "ReadMcpResourceDirTool"}
NET_NAME = re.compile(r"(?i)web|browser|fetch|http|url")
DELETE_TOOL = re.compile(r"(?i)(^|[_:\s])(delete|remove|rmdir|unlink)")
WRITE_NAME = re.compile(r"(?i)write|edit|create|replace|patch|insert|save|rename|move")
NOT_WRITE = re.compile(r"(?i)todo|task|plan")
PATH_KEY = re.compile(r"path|file|target|dir|uri")
DB_MCP = re.compile(r"(?i)prisma|mongo|postgres|mysql|redis|sqlite|supabase|neon|database|\bdb\b|sql")
SAFE_ABS = ("/dev/null", "/usr/bin/", "/bin/", "/usr/local/bin/", "/opt/homebrew/bin/")
SAFE_SCRIPT = ".agents/hooks/test_guard.py"  # the only script that may run without approval
GIT_RO = {"status", "diff", "log", "show", "branch"}
BRANCH_OK = {"-a", "-r", "-v", "-vv", "--list", "--show-current", "--all", "--remotes"}

START = r"(^|[;&|(`\s'\"/])"
WORD_END = r"(?=[\s'\"]|$)"

DB_DELETE = re.compile(
    r"(?i)\b(delete\s+from|drop\s+(table|database|schema|index|view|column|collection)"
    r"|truncate\s+table|alter\s+table\s+\S+\s+drop)\b"
    r"|\.(deleteOne|deleteMany|dropDatabase|dropCollection|findOneAndDelete|findByIdAndDelete"
    r"|findByIdAndRemove|destroy)\(|\bflush(all|db)\b|\bprisma\.\w+\.(delete|deleteMany)\(")

CMD_RULES = [
    (START + r"gh" + WORD_END, "gh commands are for the user only."),
    (START + r"(rm|rmdir|unlink|shred|trash|truncate)" + WORD_END
     + r"|\bfind\b.*\s-delete|os\.(remove|unlink|rmdir)|shutil\.rmtree|\bfs\.(rm|unlink)|rimraf",
     "Deleting files is not allowed."),
    (START + r"(mongo|mongosh|psql|pgcli|mysql|mycli|mariadb|redis-cli|sqlite3?|litecli|duckdb|sqlcmd|cqlsh"
     r"|clickhouse-client|mongodump|mongorestore|mongoimport|mongoexport|pg_dump|pg_restore|mysqldump)"
     + WORD_END
     + r"|\b(prisma\s+(migrate|db)|knex\s+(migrate|seed)|sequelize|typeorm\s+(migration|schema)|drizzle-kit)\b"
     r"|\bdocker(-compose|\s+compose)?\s+(exec|rm|rmi|kill|stop|restart|down|volume\s+rm|system\s+prune)\b",
     "Direct database access is not allowed."),
    (START + r"pnpm\s+(run\s+)?seed" + WORD_END + r"|scripts/seed",
     "Seeding writes to the database. The user runs it."),
    (DB_DELETE.pattern, "Database delete operations are not allowed."),
    (START + r"(python[\d.]*|node|perl|ruby|php)\b[^;&|]*\s-(c|e|E|r)\b"
     r"|" + START + r"(python[\d.]*|node|perl|ruby|php)\b[^;&|]*(<<|\s-\s*$)|\beval\b",
     "Inline interpreter code and eval are not allowed (cannot be inspected)."),
]
NET_CMD = re.compile(
    START + r"(curl|wget|nc|ncat|netcat|ssh|scp|sftp|rsync|ftp|telnet|ping|dig|nslookup|npx|pipx|apt|apt-get"
    r"|npm\s+(i|install|add|ci|publish|update|exec)|pnpm\s+(dlx|publish)"
    r"|yarn(\s+(add|install|dlx|publish|upgrade))?|bun\s+(i|install|add|x)|pip3?\s+(install|download)"
    r"|uv\s+(add|pip|sync|run)|brew\s+(install|update|upgrade|tap)|gem\s+install|cargo\s+(install|add|publish)"
    r"|go\s+(get|install)|docker\s+(pull|push|login|build|run))" + WORD_END + r"|https?://")
# touch and mkdir are allowed without APPROVED, but never on protected paths (see check_cmd).
MUTATE = re.compile(START + r"(cp|mv|tee|install|ln|chmod|chown|dd)" + WORD_END
                    + r"|>|\bsed\s+-i|\bperl\s+-i")
FREE_CREATE = re.compile(START + r"(touch|mkdir)" + WORD_END)
PNPM_SAFE = re.compile(
    r"(^|[;&|]\s*)pnpm\s+(install|i|add|update|up|run|dev|build|test|start|lint|typecheck)\b[^;&|>]*")
# Anything that runs a script or project task. A script can write or delete on its own.
RUNS = re.compile(
    START + r"((python[\d.]*|node|deno|ruby|perl|php|bash|sh|zsh)\s+(-\w+\s+)*([^\s;&|]+)"
    r"|(npm|yarn)\s+(run|test|start)\b|pnpm\s+(exec|dlx)\b|make\b)"
    r"|(^|[;&|(`]\s*)\./\S+")

STYLE = "claude"  # claude | cursor | antigravity: decides how a block is reported on stdout


def block(msg):
    if STYLE == "cursor":
        print(json.dumps({"permission": "deny", "user_message": msg, "agent_message": msg}))
    elif STYLE == "antigravity":
        print(json.dumps({"decision": "deny", "reason": msg}))
    print("BLOCKED by guardrail: " + msg + " Ask the user.", file=sys.stderr)
    sys.exit(2)


def inside_root(p):
    try:
        (ROOT / Path(p).expanduser()).resolve().relative_to(ROOT)
        return True
    except ValueError:
        return False


def in_src(p):
    try:
        (ROOT / Path(p).expanduser()).resolve().relative_to(SRC)
        return True
    except ValueError:
        return False


def net_allowed():
    return ALLOW_NET.exists() and time.time() - ALLOW_NET.stat().st_mtime < NET_TTL


def need_net(what):
    if not net_allowed():
        block(what + " talks to the outside world. User must run `touch .agents/ALLOW_NET` (open for 30 min).")


def need_approval():
    if not APPROVED.exists():
        block("No approved plan. Creating or changing anything needs the user's go-ahead.")


def check_git(cmd):
    """Read-only git only: status, diff, log, show, branch (list). Everything else is blocked."""
    for m in re.finditer(START + r"git(?=[\s'\"-]|$)", cmd):
        rest = re.split(r"[;&|\n]", cmd[m.end():], maxsplit=1)[0]
        args = rest.replace('"', " ").replace("'", " ").split()
        if args and args[0] == "--no-pager":
            args = args[1:]
        if not args or args[0] not in GIT_RO:
            block("Only read-only git (status, diff, log, show, branch list) is allowed. User runs the rest.")
        sub, extra = args[0], args[1:]
        if sub == "branch" and not set(extra) <= BRANCH_OK:
            block("git branch can only list branches.")
        if any(a.startswith("--output") for a in extra):
            block("git --output writes files and is not allowed.")


def check_runs(cmd):
    """Running a script is a hidden write. Needs approval, except the guard self-check."""
    if APPROVED.exists():
        return
    for m in RUNS.finditer(cmd):
        script = (m.group(5) or "").strip("'\"")
        if script.removeprefix("./") == SAFE_SCRIPT:
            continue
        block("Running scripts or project tasks needs the user's go-ahead (a script can write or delete).")


def check_cmd(cmd):
    check_git(cmd)
    for pattern, msg in CMD_RULES:
        if re.search(pattern, cmd):
            block(msg)
    if NET_CMD.search(cmd):
        need_net("This command")
    check_runs(cmd)
    plain = re.sub(r"\d?>&\d|>\s*/dev/null", "", cmd)
    plain = PNPM_SAFE.sub(" ", plain)
    # touch and mkdir are free, but never on guardrail files (agent must not self-approve).
    if FREE_CREATE.search(plain) and PROTECTED.search(cmd):
        block("Guardrail files are protected. Only the user may change them.")
    if MUTATE.search(plain):
        if PROTECTED.search(cmd):
            block("Guardrail files are protected. Only the user may change them.")
        need_approval()
    try:
        tokens = shlex.split(cmd)
    except ValueError:
        tokens = cmd.split()
    for tok in tokens:
        for part in tok.split("="):
            if "$HOME" in part or part.startswith("~") or part == ".." or "../" in part or part.startswith("/"):
                if part.startswith(SAFE_ABS):
                    continue
                if "$HOME" in part or not inside_root(part):
                    block("Going outside the project folder is not allowed.")


def check_path(path, write):
    if not inside_root(path):
        block("Going outside the project folder is not allowed.")
    if write:
        if PROTECTED.search(path):
            block("Guardrail files are protected. Only the user may change them.")
        if not in_src(path):
            need_approval()


def walk(o, key=""):
    """Yield (key, string) for every string inside a nested tool input."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, str(k))
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, key)
    elif isinstance(o, str):
        yield key, o


def normalize(d):
    """Return (tool_name, tool_input dict) for Claude, Cursor, Codex, Grok and Antigravity payloads."""
    tc = d.get("toolCall")
    if isinstance(tc, dict):  # Antigravity
        return str(tc.get("name", "")), tc.get("args") or {}
    tool = str(d.get("tool_name") or d.get("toolName") or "")
    ti = d.get("tool_input") or d.get("toolInput")
    if ti is None:  # Cursor shell and read hooks put fields at the top level
        ti = {k: d[k] for k in ("command", "file_path") if k in d}
    if isinstance(ti, str):
        try:
            ti = json.loads(ti)
        except ValueError:
            ti = {"command": ti}
    return tool, ti if isinstance(ti, dict) else {}


def check_patch(ti):
    """Codex apply_patch: the input is a patch text listing files."""
    patch = "\n".join(v for _, v in walk(ti))
    if re.search(r"^\*\*\* Delete File:", patch, re.M):
        block("Deleting files is not allowed.")
    for m in re.finditer(r"^\*\*\* (?:Add|Update) File: (.+)$|^\*\*\* Move to: (.+)$", patch, re.M):
        check_path((m.group(1) or m.group(2)).strip(), True)
    need_approval()
    if DB_DELETE.search(patch):
        block("Writing database delete code is not allowed. The user writes that part.")


def main():
    global STYLE
    d = json.load(sys.stdin)
    STYLE = "antigravity" if "toolCall" in d else "cursor" if "cursor_version" in d else "claude"
    tool, ti = normalize(d)
    if DELETE_TOOL.search(tool):
        block("Deleting files is not allowed.")
    if tool.startswith(("mcp__", "MCP")) or tool in NET_TOOLS or NET_NAME.search(tool):
        if DB_MCP.search(tool):
            block("Database tools are not allowed.")
        need_net("Tool " + tool)
    if tool == "apply_patch":
        return check_patch(ti)
    writing = bool(WRITE_NAME.search(tool)) and not NOT_WRITE.search(tool)
    strings = list(walk(ti))
    for key, val in strings:
        lk = key.lower()
        if "command" in lk or lk == "cmd":
            check_cmd(val)
        elif PATH_KEY.search(lk) and "content" not in lk:
            check_path(val, writing)
    if writing:
        paths = [v for k, v in strings if PATH_KEY.search(k.lower()) and "content" not in k.lower()]
        if not (paths and all(in_src(p) for p in paths)):
            need_approval()
        if any(DB_DELETE.search(v) for _, v in strings):
            block("Writing database delete code is not allowed. The user writes that part.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as e:  # fail closed
        block("Guard error, failing closed: " + repr(e))
