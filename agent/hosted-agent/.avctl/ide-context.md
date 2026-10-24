# AVCTL IDE context

Hosted Agentverse agent. The user wants to **build, improve, deploy, check
logs, and iterate with you**. Edit locally and use AVCTL — do not clone
`agentverse-core` or run `make build`.

Read `.avctl/rules/hosted_agent_reference.md` before changing agent code.

## Commands

```bash
avctl auth status                  # if expired → avctl auth login
avctl hosting deploy               # stop (if needed) + upload + restart
avctl hosting logs                 # snapshot logs (prefer over -f)
avctl hosting stop
avctl hosting run                  # start only; no-op if already running
avctl hosting push                 # upload only — does not restart
```

## Rules

- Work from the agent directory (needs `.avctl/config.toml`). Address is there after first deployment.
- Default loop: **edit → `avctl hosting deploy` → `avctl hosting logs` → fix**.
- Prefer `deploy` over `push`. `deploy` handles stop/upload/restart. `push`
  only uploads — stop first if running, then `run` to apply.
- Do not use `logs -f` or `run -l` in automated loops (they hang).
- Only `.py` and `.env` are uploaded as code; `README.md` is synced separately.
- New deps must be in `avctl hosting packages` or deploy/push will fail.
