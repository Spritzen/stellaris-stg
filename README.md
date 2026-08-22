# Star Trek Galaxies

A Star Trek total conversion for **Stellaris 4.4.x "Pegasus"**, built by vendoring
49 Workshop mods into one standalone mod tree, developed in a VS Code dev
container.

- **New here?** [Getting started](#getting-started) below.
- **Working on content?** [`.docs/README.md`](.docs/README.md) is the
  documentation map — it routes by what you are doing, and it is the source of
  truth for everything this file only summarises.
- **An AI session?** [`CLAUDE.md`](CLAUDE.md) first.

---

## The one idea to hold

STG is **standalone**. It does not sit on top of 49 mods at runtime and hope the
load order behaves — it vendors its own copy of every source mod, and the merge
is resolved **at build time**, in a declared order you can read.

That splits the repo cleanly in two:

| | |
|---|---|
| **Inputs** — hand-written, tracked in git | `vendor.yml`, `src/`, `tools/`, `.docs/`, `Makefile` |
| **Outputs** — generated, never hand-edited, not tracked | `stg-build/`, `.source/`, `.vendor-manifest.json` |

`stg-build/` **is the mod** — the game's own directory layout plus
`descriptor.mod`, produced entirely by `make vendor`. The repo root is *not* the
mod root ([decision 13](.docs/decisions/13-build-dir-and-symlink-deploy.md)).

**Editing a file under `stg-build/` is always wrong.** It is discarded by the
next `make vendor` and invisible in review. Every change goes through `src/` or
through `vendor.yml`. `make validate` fails on the ones it can detect.

---

## What you need

On the **host** (not the container):

- Docker, and VS Code with the
  [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  extension.
- **Stellaris 4.4.x installed via Steam**, and run at least once so the launcher
  has created its user-data folder.
- The source mods subscribed and downloaded. Subscribing needs the Steam client,
  which is host-side — the container can only read what Steam has already
  fetched. [`.docs/planning/subscribed-mods.md`](.docs/planning/subscribed-mods.md)
  lists them.
- ~45 GB free on the same filesystem as the repo (22 GB of sources + a ~15 GB
  build). On btrfs or XFS this is almost entirely reflinked and costs nearly
  nothing real — see [Disk](#disk-and-why-the-numbers-lie).

## Getting started

### 1. Point the container at your host paths

`.devcontainer/devcontainer.json` hardcodes four host paths under `/home/odin`.
**Change them to yours before the first build** — a bind mount whose source does
not exist is a build error, not an empty directory.

| Mount source to edit | What it is |
|---|---|
| `…/Steam/steamapps/common/Stellaris` | vanilla game files → `/stellaris`, read-only |
| `…/Steam/steamapps/workshop/content/281990` | subscribed mods → `/workshop`, read-only |
| `…/Paradox Interactive/Stellaris` | **live** user data → `/paradox/stellaris`, read-write |
| `~/.claude`, `~/.config/gh` | persisted Claude and GitHub auth |

Also set `containerEnv.HOST_WORKSPACE` to this repo's absolute path **on the
host**. The Stellaris launcher runs outside the container, so `make link` writes
host-side paths and cannot infer that one.

```bash
mkdir -p ~/.config/gh          # the gh mount needs its source to exist
```

**Which user-data folder is live depends on how Steam runs the game**, and
getting it wrong produces a flawless mod folder that nothing reads. Ask the game
rather than guessing:

```bash
python3 -c "import json;print(json.load(open(
  '<steam>/steamapps/common/Stellaris/launcher-settings.json'))['gameDataPath'])"
# $LINUX_DATA_HOME  -> native Linux build: ~/.local/share/Paradox Interactive/Stellaris
# %USER_DOCUMENTS%  -> Windows build under Proton: inside the compatdata prefix
```

Both directories usually exist on disk and only one is live. `make link` checks
that the mount and the installed build agree and refuses if they don't
([decision 15](.docs/decisions/15-native-linux-runtime.md);
[decision 07](.docs/decisions/07-launcher-local-mod-registration.md) is the
session this cost).

### 2. Open the container

`F1` → **Dev Containers: Reopen in Container**. The first build takes a few
minutes. `post-create.sh` then prints a check of the toolchain, the mounts, the
network and your `gh` login — **read it**, it is the fastest place to catch a
wrong mount.

### 3. Build it

```bash
make                 # the workflow, printed from the Makefile itself
make sources-sync    # pin the source mods from /workshop into .source/      (~1 min)
make vendor          # build stg-build/ from .source/ + src/                    (~70 s)
make validate        # does every name resolve against the merged tree?
make link            # ONE-TIME: symlink stg-build/ into the Paradox mod folder
```

Then restart the Paradox launcher, add **Star Trek Galaxies** to a playset, and
launch.

---

## The daily loop

```bash
make vendor && make validate
```

That is the whole thing. The mod folder holds a **symlink** to `stg-build/`, so
a rebuild is live the moment it finishes — there is no copy step to forget, and
the deployed tree cannot go stale. `make link` is needed once, or again only if
the mod folder is wiped.

The game still needs a restart to reload script.

### Which check to run after what

| You changed… | Run |
|---|---|
| anything in `src/` | `make validate` |
| `vendor.yml` — what is harvested | `make vendor && make validate && make clutter` |
| a localisation file | `make validate` (and `make fix-bom` if it flags a BOM) |
| a `tools/gen_*.py` or `tools/fix_*.py` | `make gen-check` — a correct generator reproduces `src/` exactly |
| documentation, or a code comment citing it | `make docs` |
| nothing — you just want the state | `make sources-status` |

[Every target, with what each one proves and does not prove](.docs/guides/workflow.md).

### What "validates clean" is worth

`make validate` answers *do the names resolve against the merged tree* — it does
not answer *does it render, is it the right size, does the game like it*. It
once reported `ok — 0 warnings` against a build throwing ~8,780 runtime errors.

**The game runs on the host.** Container-side you validate structure, never
behaviour. After a live run the evidence is `/paradox/stellaris/logs/error.log`
— read it before saying anything about how the run went
([procedure](.docs/guides/live-runs.md)).

---

## Making a change

Content is hand-written into `src/`, which is overlaid **after** every source mod
and always wins. Three kinds of file live there, and the kind decides the name:

| Filename | Means |
|---|---|
| `stg_*` | our own content — species classes, name lists, prescripted empires, loc |
| `stg_*.asset` / `.gfx` | **declare, don't shadow** — a new file adding what a vendored one lacks |
| `<vanilla_name>.txt` | shadows vanilla or a source outright — **requires a header comment** saying what it overrides and why, and `make validate` enforces that |

To change something a **source mod** ships, you do not edit the source. You add
a `patches:`, `renames:` or `resample_to_vanilla:` entry in `vendor.yml`, or you
shadow it from `src/`. That keeps the change replayable and visible in review.

**Before writing script, read vanilla.** `/stellaris` is the reference for
everything, and guessing at an effect, trigger or scope name produces a file the
game silently drops with no error at all —
[how to ground a change](.docs/guides/writing-script.md#before-writing-script-read-vanilla).

Localisation is UTF-8 **with BOM**, and keys need a `:0` version. `make fix-bom`
fixes `src/localisation/` when you forget.

---

## Source mods

`/workshop` is your live Steam subscription. **It is not a build input.**
`make vendor` reads `.source/` — a snapshot taken on purpose — so a mod updating
on Steam is something you diff and accept, never something that silently changes
your next rebuild.

```bash
make sources-status              # what changed upstream since the snapshot
make sources-status DEEP=1       # hash every file instead of trusting size+mtime
make sources-diff ID=937289339   # read the change
make sources-sync ID=937289339   # accept it — then: make vendor && make validate
make sources-list                # what is pinned right now
```

`sources.lock.yml` records which revision of each source is pinned, and **is**
tracked in git. `.source/` itself is not.

`/workshop` is still worth reading — it is how you check whether something you
are about to overwrite is already touched by another mod:

```bash
rg -l "pop_job_" /workshop            # which mods touch pop jobs
ls /workshop/*/descriptor.mod | wc -l # a few mods ship as .zip instead
```

### Disk, and why the numbers lie

`.source/` is 22 GB across 51 mods — the 49 the build vendors, plus two ambient
soundtracks kept snapshotted after
[decision 11](.docs/decisions/11-drop-cinematic-camera-and-ambient-soundtracks.md)
dropped them from the harvest. `stg-build/` is a further ~15 GB. But on this
machine `/workshop` and the repo are the same btrfs subvolume, so the snapshot
**reflinks** — the copy shares extents with the original and takes about a
second. `tools/sources.py` uses `cp --reflink=auto`, which degrades silently to a
real copy on any filesystem without reflink support (ext4, NTFS). There it costs
the full 22 GB and several minutes.
[Decision 09](.docs/decisions/09-source-snapshot.md).

### A source mod is never dropped to silence its errors

Errors get **fixed**. A source is dropped only on content grounds, never by
quoting an error count —
[decision 12](.docs/decisions/12-fix-source-errors-dont-drop.md).

---

## Testing in-game

Stellaris and the launcher are host-side. `make link` symlinks `stg-build/` into
the Paradox mod folder and writes the `.mod` descriptor the launcher reads.

The symlink's target is a **host** path, which is why it reads as *broken* from
inside the container. That is correct. Do not "fix" it.

Back up `launcher-v2.sqlite` before anything writes to `/paradox/stellaris` —
your playsets live in there.

---

## Troubleshooting

| Symptom | Cause |
|---|---|
| Container build fails on a mount | A host path in `devcontainer.json` doesn't exist. See [step 1](#1-point-the-container-at-your-host-paths). |
| `make link` refuses, naming the Proton prefix | The mounted user-data folder and the installed build disagree. Flip Steam's compatibility toggle back, or update the mount and rebuild the container. |
| Launcher doesn't list the mod | `HOST_WORKSPACE` is unset or wrong, so the `.mod` file points nowhere real. [Deployment](.docs/guides/deployment.md). |
| A `src/` edit had no effect in-game | You edited `stg-build/` instead, or the game wasn't restarted. |
| An edit vanished after a rebuild | It was under `stg-build/`. Move it to `src/`. |
| `make validate` flags a missing BOM | `make fix-bom` — and note it fixes `src/`, not the built tree. |
| `make docs` fails on a dangling link | A `.docs/` link, nav-card `Then:` hop, or code citation no longer resolves. |
| Everything is clean but the game logs errors | Expected. See [what validates clean is worth](#what-validates-clean-is-worth). |

---

## GitHub

The repo lives at **`stellaris-stg`**, private. `gh` is installed by
`post-create.sh` and its token is bind-mounted from the host at `~/.config/gh`,
so you log in **once** and it survives every container rebuild:

```bash
gh auth login          # HTTPS + browser is fine; the token lands in ~/.config/gh
gh auth setup-git      # makes that token git's credential helper, so push works
gh auth status         # what post-create.sh checks on every rebuild
```

### What is and is not tracked

`.gitignore` is the authority — read it rather than this list. In summary git
tracks `vendor.yml`, `src/`, `sources.lock.yml`, `tools/`, `.docs/`, the
`Makefile` and `.devcontainer/`; it ignores every generated tree.

That means **no vendored content is ever committed** — not one byte of a source
mod, not one byte of vanilla. `vendor.yml` is a manifest of path rules that
*names* what to harvest; the harvesting happens on your machine, from mods you
are subscribed to. This matters: STG vendors STNH assets under a licence that
forbids redistribution, and the repo stays private for the same reason.

**STG is never published as a mod.** `make dist` exists to archive a build, not
to upload one.

A practical consequence: a fresh clone is `vendor.yml` + `src/` + `tools/` and
nothing else. Getting from there to a playable mod means Steam subscriptions,
`make sources-sync`, and `make vendor` — the repo is the recipe, not the meal.

### No CI

`make validate` and `make clutter` need `stg-build/` and `/stellaris`, and
neither exists on a runner. `make docs` is the only check that would run there —
run it locally instead, and keep it at zero.

---

## Side note: running this on a Windows host

Everything here is developed against a Linux host, and the container is the same
Debian image either way. What changes is the four host paths and two assumptions
that don't survive the crossing. **This is untested** — treat it as a starting
point, not a recipe.

**Docker Desktop with the WSL2 backend.** The paths in `devcontainer.json` become
Windows paths, which Docker accepts with forward slashes or via `${localEnv:…}`:

```jsonc
"source=${localEnv:ProgramFiles(x86)}/Steam/steamapps/common/Stellaris,target=/stellaris,type=bind,readonly",
"source=${localEnv:USERPROFILE}/Documents/Paradox Interactive/Stellaris,target=/paradox/stellaris,type=bind",
```

Stellaris on Windows keeps its user data in
`%USERPROFILE%\Documents\Paradox Interactive\Stellaris` — no Proton prefix
involved, because there is no Proton.

Three things that will actually bite:

1. **`make link` will refuse.** `tools/deploy.py` decides the launcher path form
   from `launcher-settings.json:gameDataPath`. A Windows install reports
   `%USER_DOCUMENTS%`, and the script then expects the mount to sit inside a
   Wine prefix — which on real Windows it never does, so its platform/mount
   agreement check fails by design. Set `MOD_PATH` to override the written path
   outright (`C:/Users/<you>/Documents/Paradox Interactive/Stellaris/mod/star_trek_galaxies`).
   Making this a first-class case means teaching `deploy.py` a third platform,
   not patching around it.
2. **The symlink may not survive.** Creating a symlink from inside the container
   onto a bind-mounted Windows drive is unreliable, and the whole
   [decision 13](.docs/decisions/13-build-dir-and-symlink-deploy.md) deploy model
   rests on it. If it fails, the fallback is copying `stg-build/` into the mod
   folder after every build — which reintroduces exactly the staleness that
   decision was written to eliminate, so automate it, don't do it by hand.
3. **Disk and speed, for real.** No reflinks on NTFS: `make sources-sync` copies
   22 GB properly. And bind mounts that cross the Windows/WSL2 filesystem
   boundary are slow enough to dominate a build. Keeping the repo *inside* the
   WSL2 filesystem fixes the build's speed but puts it on the far side of the
   boundary from the game — which the Steam mounts have to cross regardless.

The honest summary: the container, the toolchain, `make vendor`, `make validate`,
`make clutter` and `make docs` should all work unchanged. **Deployment is the
part that needs work**, and it needs it in `deploy.py`, not in a wrapper script.

---

## What's in the container

| Tool | Why |
|---|---|
| CWTools (MD edition) | Paradox script language server — live validation and autocomplete against your real vanilla files, not its stale embedded cache |
| .NET 8 runtime | Runs the CWTools server |
| Claude Code CLI + extension | Sessions persist across rebuilds |
| GitHub CLI (`gh`) | Repo, issues, PRs; auth persisted via `~/.config/gh` |
| Python 3 + PyYAML + Pillow | Everything in `tools/` |
| ImageMagick | DDS ⇄ PNG texture conversion |
| ripgrep, jq, make, git, zip | General work |

Networking is the Docker default bridge — full outbound internet, no firewall
script.

### Persistent Claude sessions

`CLAUDE_CONFIG_DIR` points at `/home/vscode/.claude`, bind-mounted from your host
`~/.claude`. Transcripts, credentials and history are shared with the host and
survive container rebuilds — no re-login, and a session started on the host
resumes inside the container with `claude --continue`.

Your host UID is 1000 and the container's `vscode` user is UID 1000, so mounted
files keep correct ownership. If your host UID differs, that is the first thing
to check when a mount looks read-only.

---

## Layout

```
vendor.yml            which source mods to vendor, in what order — hand-written
sources.lock.yml      which revision of each is pinned — generated
.source/              the pinned source mods — generated, not tracked
src/                  hand-written STG content, applied last and always wins
  descriptor.mod        mod metadata the launcher reads
stg-build/            THE MOD — generated by make vendor, never hand-edited  ┐
  common/               game rules — the bulk of a total conversion          │
  events/               scripted events                                      │
  localisation/english/ UTF-8 *with BOM*, keys need a :0 version             │
  gfx/ interface/       art and UI                                           ┘
tools/                dev scripts, not shipped
.docs/                all documentation — start at .docs/README.md (the map)
.devcontainer/        container definition, not shipped
```

[Every path, what generates it, and whether it may be hand-edited](.docs/reference/repo-layout.md).

---

## Where to go next

| I want to… | Go to |
|---|---|
| start work without breaking something | [.docs/guides/working-rules.md](.docs/guides/working-rules.md) |
| know the project's state | [.docs/planning/status.md](.docs/planning/status.md) |
| know what to work on next | [.docs/planning/open-questions.md](.docs/planning/open-questions.md) |
| write content in `src/` | [.docs/guides/writing-script.md](.docs/guides/writing-script.md) |
| understand the build's design | [.docs/architecture/README.md](.docs/architecture/README.md) |
| understand or write a check | [.docs/validation/README.md](.docs/validation/README.md) |
| read `error.log` after a live run | [.docs/guides/live-runs.md](.docs/guides/live-runs.md) |
| check whether a question is settled | [.docs/decisions/README.md](.docs/decisions/README.md) |
| look up a term | [.docs/reference/glossary.md](.docs/reference/glossary.md) |
