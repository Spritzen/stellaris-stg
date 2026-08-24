#!/usr/bin/env bash
# Runs once when the container is created or rebuilt.
set -euo pipefail

say() { printf '\n\033[1;36m==> %s\033[0m\n' "$1"; }
ok()  { printf '    \033[32m✓\033[0m %s\n' "$1"; }
bad() { printf '    \033[31m✗\033[0m %s\n' "$1"; }

say "Installing Claude Code CLI"
if command -v claude >/dev/null 2>&1; then
	ok "already present: $(claude --version 2>/dev/null || echo unknown)"
else
	npm install -g @anthropic-ai/claude-code >/dev/null 2>&1 \
		&& ok "installed $(claude --version 2>/dev/null || echo '')" \
		|| bad "npm install failed — run 'npm i -g @anthropic-ai/claude-code' manually"
fi

say "Installing GitHub CLI"
# Not in Debian bookworm's archive, so take the release .deb directly rather
# than adding an apt source for one package. Auth lives in ~/.config/gh, which
# is bind-mounted from the host -- so this reinstalls the binary on a rebuild
# but never asks you to log in again.
if command -v gh >/dev/null 2>&1; then
	ok "already present: $(gh --version 2>/dev/null | head -1)"
else
	tag=$(curl -fsSL --max-time 20 https://api.github.com/repos/cli/cli/releases/latest 2>/dev/null | jq -r .tag_name 2>/dev/null || echo '')
	if [ -n "$tag" ] && [ "$tag" != "null" ] \
		&& curl -fsSL --max-time 60 -o /tmp/gh.deb \
			"https://github.com/cli/cli/releases/latest/download/gh_${tag#v}_linux_amd64.deb" 2>/dev/null \
		&& sudo dpkg -i /tmp/gh.deb >/dev/null 2>&1; then
		rm -f /tmp/gh.deb
		ok "installed $(gh --version 2>/dev/null | head -1)"
	else
		bad "gh install failed — see README 'GitHub' for the manual steps"
	fi
fi

if gh auth status >/dev/null 2>&1; then
	ok "gh authenticated as $(gh api user --jq .login 2>/dev/null || echo '?') (token persisted in ~/.config/gh)"
else
	printf '    \033[33m!\033[0m gh not logged in — run: gh auth login && gh auth setup-git\n'
fi

say "Verifying mounts"
if [ -d "${STELLARIS_GAME_DIR}/common" ]; then
	ver=$(python3 -c "import json,sys;print(json.load(open('${STELLARIS_GAME_DIR}/launcher-settings.json'))['version'])" 2>/dev/null || echo '?')
	ok "game files      ${STELLARIS_GAME_DIR}  (${ver})"
else
	bad "game files missing at ${STELLARIS_GAME_DIR} — CWTools will fall back to its embedded cache"
fi

if [ -w "${PARADOX_MOD_DIR}" ]; then
	ok "paradox mod dir ${PARADOX_MOD_DIR}  (writable, $(find "${PARADOX_MOD_DIR}" -maxdepth 1 -name '*.mod' | wc -l) mods present)"
else
	bad "paradox mod dir ${PARADOX_MOD_DIR} not writable — 'make link' will fail"
fi

if [ -d "${CLAUDE_CONFIG_DIR}" ]; then
	n=$(find "${CLAUDE_CONFIG_DIR}/projects" -name '*.jsonl' 2>/dev/null | wc -l)
	ok "claude state    ${CLAUDE_CONFIG_DIR}  (${n} session transcripts, persisted)"
else
	bad "claude state dir missing at ${CLAUDE_CONFIG_DIR}"
fi

say "Verifying toolchain"
for tool in dotnet python3 convert rg jq git node; do
	if command -v "$tool" >/dev/null 2>&1; then
		ok "$(printf '%-8s' "$tool") $("$tool" --version 2>/dev/null | head -1)"
	else
		bad "$tool missing"
	fi
done

say "Checking outbound internet"
if curl -fsS --max-time 10 -o /dev/null https://api.anthropic.com/v1/models 2>/dev/null \
   || [ "$(curl -fsS --max-time 10 -o /dev/null -w '%{http_code}' https://api.anthropic.com 2>/dev/null)" != "000" ]; then
	ok "api.anthropic.com reachable"
else
	bad "api.anthropic.com unreachable"
fi
if curl -fsS --max-time 10 -o /dev/null https://github.com 2>/dev/null; then
	ok "github.com reachable (CWTools pulls rule updates from here)"
else
	bad "github.com unreachable"
fi

printf '\n\033[1;32mReady.\033[0m  make help  for the mod workflow.\n\n'
