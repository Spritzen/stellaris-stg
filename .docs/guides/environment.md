# Environment — mounts, container, and the host boundary

> **What** — the five mounts, which are writable, and the line between what the
> container can do and what only the host can.
> **Open when** — reading or writing anything outside the repo, or about to
> claim something about the game install.
> **Then** — [Deployment](deployment.md) · [Live runs](live-runs.md) · [decision 15](../decisions/15-native-linux-runtime.md)

Everything runs inside the dev container. Five mounts matter:

| Path | Mode | What it is |
|---|---|---|
| `/stellaris` | read-only | Vanilla game files. **The reference for everything.** |
| `/workshop` | read-only | Subscribed Steam Workshop mods. Upstream for `.source/`, plus conflict checks and prior art. **Not a build input** — `make vendor` reads `.source/`. |
| `/paradox/stellaris` | read-write | **Live** Stellaris user data: `mod/` (deploy target), `launcher-v2.sqlite` (mod registry + playsets), `logs/error.log`. |
| `~/.claude` | read-write | Persisted Claude sessions, shared with the host. |
| `~/.config/gh` | read-write | Persisted GitHub CLI token, shared with the host — `gh auth login` once, and it survives every rebuild. |

Both Steam mounts are read-only by design. **Never try to write there.**

The last two are the same idea twice: state that would otherwise be recreated on
every container rebuild lives on the host instead. `post-create.sh` reports
whether each is present and authenticated.

## Which user-data folder is live

Stellaris here is the **native Linux build** — Steam's compatibility mode was
turned off on 2026-08-02 — so the launcher's user data lives at
`~/.local/share/Paradox Interactive/Stellaris`, *not* in the Proton prefix under
`steamapps/compatdata/281990/…`.

Both folders exist on this disk and only one is live; **the installed depot
decides which**, so never assert it from memory:

```bash
python3 -c "import json;print(json.load(open('/stellaris/launcher-settings.json'))['gameDataPath'])"
# $LINUX_DATA_HOME  = native Linux    %USER_DOCUMENTS% = Proton
```

`/stellaris/launcher-settings.json:gameDataPath` is the authority. Deploying
into the wrong one produces a flawless mod folder that nothing reads, and has
cost a session before. [Decision 15](../decisions/15-native-linux-runtime.md) is
the current story; [decision 07](../decisions/07-launcher-local-mod-registration.md)
is the same failure from the other side.

## Check /workshop before shadowing a vanilla file

Before overwriting a vanilla file, check whether a subscribed mod already touches
it — and say so:

```bash
rg -l "<filename>" /workshop
```

Some Workshop mods ship as a `.zip`; those need unzipping to a temp dir before
you can grep them.

## What only the host can do

Steam and the Paradox Launcher run on the **host**, so subscribing to a mod is
something you can neither do nor verify from here. The game runs there too —
see [Live runs](live-runs.md) for what that means for any claim about behaviour.

STG itself is **never published**. It is personal, permanently, and it contains
STNH assets whose licence forbids redistribution
([scope](../planning/scope.md#on-stnhs-licence)).
