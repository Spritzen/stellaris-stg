.DEFAULT_GOAL := help
.PHONY: help sources-sync sources-status sources-diff sources-list \
        vendor provenance clean-vendor validate clutter clutter-vanilla docs \
        link mod-file unlink fix-bom dist game-version

# `make sources-diff ID=937289339`, `make sources-sync ID=...` to narrow to one
# source; `DEEP=1` makes status hash every file instead of trusting size+mtime.
ID ?=
DEEP ?=
ARGS ?=
DEEP_FLAG := $(if $(DEEP),--deep,)

MOD_ID ?= star_trek_galaxies
STELLARIS_GAME_DIR ?= /stellaris
# The live user data is ~/.local/share/Paradox Interactive/Stellaris, mounted at
# /paradox/stellaris -- the native-Linux location, live again since compatibility
# mode was turned off on 2026-08-02. NOT the Proton prefix under compatdata/281990
# -- see .docs/decisions/15-native-linux-runtime.md.
PARADOX_MOD_DIR ?= /paradox/stellaris/mod

# tools/*.py read these from the environment, so make must export them --
# otherwise `make link MOD_ID=foo` is silently ignored.
export MOD_ID STELLARIS_GAME_DIR PARADOX_MOD_DIR HOST_PARADOX_MOD_DIR

help: ## Show this help
	@printf '\n\033[1mStar Trek Galaxies\033[0m — Stellaris mod workflow\n\n'
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk -F':.*?## ' '{printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@printf '\n  \033[2m/workshop --sources-sync--> .source/ --vendor--> mod tree <--link-- $(PARADOX_MOD_DIR)\033[0m\n'
	@printf '  \033[2mVanilla reference: $(STELLARIS_GAME_DIR)\033[0m\n\n'

sources-sync: ## Snapshot the source mods from /workshop into .source/ (ID=<id> for one)
	@python3 tools/sources.py sync $(ID)

sources-status: ## Show what changed upstream since the snapshot (DEEP=1 to hash)
	@python3 tools/sources.py status $(DEEP_FLAG) $(ID)

sources-diff: ## Diff one source against upstream — needs ID=<workshop id>
	@test -n "$(ID)" || { echo "usage: make sources-diff ID=<workshop id>"; exit 2; }
	@python3 tools/sources.py diff $(DEEP_FLAG) $(ID)

sources-list: ## List the source mods currently snapshotted in .source/
	@python3 tools/sources.py list $(ID)

vendor: ## Rebuild the mod tree from .source/ + src/
	@python3 tools/vendor.py

provenance: ## Regenerate .docs/provenance.md from the last build
	@python3 tools/vendor.py --provenance

clean-vendor: ## Remove every generated file (hand-written content is untouched)
	@python3 tools/vendor.py --clean

validate: ## Check BOMs, brace balance, loc syntax and descriptor
	@python3 tools/validate.py

# The dual of validate: validate asks whether every reference resolves, this
# asks whether every file is referenced. ARGS=--list prints the paths;
# ARGS='--list gfx/models' narrows to one tier.
clutter: ## Census the built tree — reachable, shadowing, kept, or orphan
	@python3 tools/clutter.py $(ARGS)

# The false-positive floor. Nothing in a clutter finding means anything until
# you have read it against this: vanilla runs 2.67% unreferenced against itself.
clutter-vanilla: ## Run the same closure over /stellaris — the calibration floor
	@python3 tools/clutter.py --vanilla $(ARGS)

# The docs get the same treatment the mod gets. Checks that references resolve;
# it cannot check that prose is true. See .docs/style-guide.md.
docs: ## Check every doc link, code citation, nav card and index row
	@python3 tools/check_docs.py

link: validate ## Symlink the mod into the Paradox mod folder (one-time)
	@python3 tools/deploy.py

mod-file: ## Rewrite just the .mod descriptor, without relinking
	@python3 tools/deploy.py --mod-file

unlink: ## Remove the mod from the Paradox mod folder
	@python3 tools/deploy.py --clean

# src/, not stg-build/: the built tree is generated, and a BOM added there is
# lost on the next `make vendor` while validate keeps reporting it fixed.
fix-bom: ## Add the required UTF-8 BOM to every localisation file in src/
	@python3 -c "import pathlib; \
[ (p.write_bytes(b'\xef\xbb\xbf'+p.read_bytes()), print('  + BOM',p)) \
  for p in pathlib.Path('src/localisation').rglob('*.yml') \
  if not p.read_bytes().startswith(b'\xef\xbb\xbf') ]; \
print('src/localisation BOMs normalised')"

# Zips the built tree and nothing else, so the exclude list that guarded this
# is gone with the restructure -- see decision 13.
dist: validate ## Zip the built mod into dist/ (for archiving — STG is never published)
	@mkdir -p dist
	@rm -f dist/$(MOD_ID).zip
	@cd stg-build && zip -qr ../dist/$(MOD_ID).zip .
	@printf '  dist/$(MOD_ID).zip  (%s)\n' "$$(du -h dist/$(MOD_ID).zip | cut -f1)"

game-version: ## Print the installed Stellaris version
	@python3 -c "import json;d=json.load(open('$(STELLARIS_GAME_DIR)/launcher-settings.json'));\
print(d['version'], '| mods compat', d['modsCompatibilityVersion'])"
