#!/usr/bin/env python3
"""Run: python3 .agents/hooks/test_guard.py"""
import json
import subprocess
from pathlib import Path

GUARD = Path(__file__).with_name("guard.py")
AGENTS = GUARD.parents[1]
approved = (AGENTS / "APPROVED").exists()
net_open = (AGENTS / "ALLOW_NET").exists()


def run(payload):
    return subprocess.run(["python3", str(GUARD)], input=json.dumps(payload), text=True, capture_output=True)


def claude(tool, **inp):
    return {"tool_name": tool, "tool_input": inp}


def bash(c):
    return claude("Bash", command=c)


def cursor_shell(c):
    return {"cursor_version": "1", "command": c, "cwd": "/x", "transcript_path": "/Users/x/t.json"}


def antigravity(c):
    return {"toolCall": {"name": "run_command", "args": {"CommandLine": c}}, "workspacePaths": ["/x"]}


def grok(c):
    return {"toolName": "Bash", "toolInput": {"command": c}, "workspaceRoot": "/x"}


def patch(body):
    return {"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n" + body + "\n*** End Patch"}}


# Built from parts so this file never contains a literal database delete.
FLUSH = "flush" + "all"
DEL_FROM = "DELETE " + "FROM users"
DEL_MANY = "db.x.delete" + "Many({})"

# Always blocked, whatever the approval state.
BLOCKED = [
    bash("git commit -m x"), bash("git push"), bash("git add ."), bash("git pull"), bash("git reset --hard"),
    bash("git branch -D x"), bash("git -c core.pager=x status"), bash("/usr/bin/git push"),
    bash('sh -c "git push"'), bash("ls && git push"), bash("gh pr list"),
    bash("rm -rf node_modules"), bash("find . -name x -delete"), bash("/bin/rm a"),
    bash("psql -c 'select 1'"), bash("mongosh"), bash("redis-cli " + FLUSH),
    bash("echo '" + DEL_FROM + "'"), bash("echo '" + DEL_MANY + "'"),
    bash("docker exec db psql"), bash("prisma migrate dev"),
    bash("python3 -c 'print(1)'"), bash("node -e 'x'"), bash("eval ls"),
    bash("pnpm run seed"), bash("pnpm seed"), bash("node scripts/seed.ts"),
    bash("pnpm run build > .claude/x"), bash("pnpm install; touch .agents/APPROVED"),
    bash("cat ../secret"), bash("ls ~/Documents"), bash("cat /etc/hosts"),
    claude("Write", file_path="/tmp/a.txt", content="x"),
    claude("Write", file_path=".agents/hooks/guard.py", content="x"),
    claude("Write", file_path="src/a.js", content=DEL_MANY),
    claude("Write", file_path="src/a.sql", content=DEL_FROM),
    claude("Read", file_path="/etc/hosts"),
    claude("mcp__prisma__query"), claude("mcp__postgres__run"),
    # Cursor
    cursor_shell("git push"), cursor_shell("rm a"),
    {"cursor_version": "1", "tool_name": "Delete", "tool_input": {"file_path": "a.txt"}},
    {"cursor_version": "1", "tool_name": "Write", "tool_input": {"file_path": "/tmp/x", "content": "x"}},
    {"cursor_version": "1", "file_path": "/etc/hosts", "content": "x"},
    # Codex
    patch("*** Delete File: a.txt"), patch("*** Add File: ../x.txt\n+x"), patch("*** Update File: .claude/settings.json"),
    # Grok
    grok("git push"), grok("rm a"),
    # Antigravity
    antigravity("git push"), antigravity("rm a"),
    {"toolCall": {"name": "write_to_file", "args": {"TargetFile": "/tmp/x", "CodeContent": "x"}}},
]
ALLOWED = [
    bash("ls -la"), bash("cat README.md"), bash("cat ./README.md"), bash("grep -r foo . 2>&1"),
    bash("git status"), bash("git diff | head"), bash("git log --oneline"), bash("git branch -a"),
    bash("git --no-pager show"),
    bash("python3 .agents/hooks/test_guard.py"),
    bash("pnpm install"), bash("pnpm add fastify"), bash("pnpm add -D typescript@7 oxlint"),
    bash("pnpm run build"), bash("pnpm dev"), bash("pnpm test"),
    bash("pnpm run typecheck && pnpm run lint"),
    claude("Read", file_path="README.md"),
    cursor_shell("git status"), grok("git status"), antigravity("git status"),
]
# Depends on approval / network switches.
if not approved:
    BLOCKED += [bash("echo hi > a.txt"), claude("Write", file_path="a.txt", content="x"),
                bash("python3 script.py"), bash("node app.js"), bash("bash run.sh"), bash("./run.sh"),
                bash("pnpm exec tsc"), bash("pnpm dlx x"), bash("npm run build"), bash("npm test"), bash("make"), bash("python3 -I x.py"),
                patch("*** Add File: a.txt\n+x"),
                {"toolCall": {"name": "write_to_file", "args": {"TargetFile": "a.txt", "CodeContent": "x"}}},
                {"cursor_version": "1", "tool_name": "Write", "tool_input": {"file_path": "a.txt", "content": "x"}}]
if not net_open:
    BLOCKED += [bash("pnpm publish"), bash("curl example.com"), bash("npm install"), bash("pip install x"),
                claude("WebFetch", url="https://x.com"), claude("mcp__shopify__list"), claude("Artifact"),
                {"toolCall": {"name": "read_url_content", "args": {"Url": "https://x.com"}}}]

for payload in BLOCKED:
    assert run(payload).returncode == 2, f"should block: {payload}"
for payload in ALLOWED:
    assert run(payload).returncode == 0, f"should allow: {payload}"

# Each tool must get the block message in the format it understands.
out = run(antigravity("git push")).stdout
assert json.loads(out)["decision"] == "deny", "antigravity needs decision=deny on stdout"
out = run(cursor_shell("git push")).stdout
assert json.loads(out)["permission"] == "deny", "cursor needs permission=deny on stdout"
assert "BLOCKED" in run(bash("git push")).stderr, "claude, codex, grok read stderr"

r = subprocess.run(["python3", str(GUARD)], input="not json", text=True, capture_output=True)
assert r.returncode == 2, "must fail closed"
print(f"guard ok ({len(BLOCKED)} blocked, {len(ALLOWED)} allowed, fail-closed)")
