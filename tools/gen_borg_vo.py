#!/usr/bin/env python3
"""Generate src/sound/sth_soundgroups.asset -- STG's owned copy of STNH's
advisor-voice soundgroups, with the l_vo_borg group rebuilt against 4.4's
current advisor sound names. Breen and Romulan groups are copied byte-identical
from the vendored file.

Run from the repo root. Idempotent.
"""
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Read STNH's own file, never stg-build/ -- src/ is applied last, so the built
# copy IS this script's previous output and reading it feeds output back in.
VENDORED = Path(".source/688086068/sound/sth_soundgroups.asset")
WAVDIR = Path("stg-build/sound/vo/ethics/vo_borg")
OUT = Path("src/sound/sth_soundgroups.asset")
VANILLA = Path("/stellaris/sound/soundgroups.asset")

# ── the authoritative set of advisor soundoverride names 4.4 accepts ─────────
vtext = VANILLA.read_text(encoding="utf-8", errors="replace")
VALID = set(re.findall(r'name\s*=\s*"(advisor_[A-Za-z0-9_]+)"', vtext))

wavs = {f for f in os.listdir(WAVDIR) if f.endswith(".wav")}


def stem_of(name):
    m = re.match(r"(.*?)_(\d+)$", name)
    return (m.group(1), int(m.group(2))) if m else (name, None)


# ── explicit rebinds: Borg wav -> the 4.4 name it should answer to ───────────
# Every one of these is a Borg clip STNH shipped but bound to a name 4.4 does
# not know, so the audio is on disk and silent. Confidence is recorded because
# the MEDIUM ones are judgement calls about what the clip says.
REBIND = {
    # HIGH -- pure renames. Paradox renamed the event, or STNH mistyped it.
    "advisor_notification_spacebourne_encounter_01.wav":
        ("advisor_notification_spaceborne_encounter_01", "HIGH",
         "STNH typo: 'spacebourne' for 'spaceborne'. This is the one "
         "assetfactory_audio.cpp:901 record in the 2026-08-08 run."),
    "advisor_notification_pre_sentient_uplifted_01.wav":
        ("advisor_notification_pre_sapient_uplifted_01", "HIGH",
         "Paradox renamed pre-sentient to pre-sapient game-wide."),
    "advisor_notification_survey_complete_01.wav":
        ("advisor_notification_system_survey_complete_02", "HIGH",
         "3.x name for what 4.4 calls system_survey_complete. _01 is a "
         "different Borg clip, so this lands as _02."),
    "advisor_notification_fleet_detected_01.wav":
        ("advisor_notification_hostile_fleet_detected_02", "HIGH",
         "3.x name; 4.4 qualifies it as hostile_. _01 already bound."),
    "advisor_notification_debri_analysed_01.wav":
        ("advisor_notification_debris_analysed_02", "HIGH",
         "STNH typo 'debri'. The correctly-spelled clip is a different "
         "recording already bound to _01, so this lands as _02."),
    "advisor_notification_enemy_invasion_progress_01.wav":
        ("advisor_notification_invasion_progress_02", "HIGH",
         "3.x name; 4.4 dropped the enemy_ qualifier. _01 already bound."),
    "advisor_notification_alien_vessel_detected_01.wav":
        ("advisor_notification_alien_vessel_encountered_02", "HIGH",
         "4.4 kept only 'encountered' of 3.x's detected/encountered pair."),

    # MEDIUM -- the clip has no same-named 4.4 slot, but a 4.4 slot means the
    # same thing. Recorded so a listener can overrule any of these by ear.
    "advisor_notification_planet_secured_01.wav":
        ("advisor_notification_invasion_success_02", "MEDIUM",
         "'Planet secured' is what 4.4 fires invasion_success for."),
    "advisor_notification_planet_lost_01.wav":
        ("advisor_notification_invasion_enemy_won_02", "MEDIUM",
         "'Planet lost' is the same event from our side."),
    "advisor_notification_upgrade_completed.wav":
        ("advisor_notification_ships_upgraded_02", "MEDIUM",
         "3.x's generic upgrade line; ships_upgraded is 4.4's only survivor."),
    "advisor_notification_ship_under_attack_01.wav":
        ("advisor_notification_station_under_attack_02", "MEDIUM",
         "3.x generic 'under attack'. science_ship_under_attack and "
         "colony_ship_under_attack both already have Borg _01 clips; "
         "station_under_attack does not have a second."),
    "construction_vessel_lost.wav":
        ("advisor_notification_construction_ship_destroyed_02", "MEDIUM",
         "Unbound STNH clip; the name states the event plainly."),

    # FLAVOUR -- clips STNH shipped and never bound to anything at all.
    "we_are_the_borg_01.wav":
        ("advisor_sample_vo_01", "HIGH",
         "advisor_sample_vo_01 is the clip the empire creator plays when you "
         "click a voice in the list. It was unbound, which is why picking "
         "Borg previewed the stock advisor."),
    "advisor_generic_phrase_01.wav":
        ("advisor_sample_vo_02", "HIGH",
         "4.4's name for the idle advisor line is advisor_sample_vo; the FILE "
         "vanilla points it at is still called advisor_generic_phrase. STNH "
         "commented these out because the old name errored, and never added "
         "the new one -- so all idle chatter played the stock advisor."),
    "advisor_generic_phrase_02.wav":
        ("advisor_sample_vo_03", "HIGH", "As advisor_sample_vo_02."),
    "advisor_generic_phrase_03.wav":
        ("advisor_sample_vo_04", "HIGH", "As advisor_sample_vo_02."),
    "resistance_is_futile.wav":
        ("advisor_notification_player_declare_war_02", "MEDIUM",
         "Unbound STNH clip. The advisor IS the Collective speaking to the "
         "player, so this reads as our own declaration of war."),
    "advisor_notification_planet_in_revolt_01.wav":
        ("advisor_notification_planet_in_revolt_02", "HIGH",
         "Same event, and the only oddity is vanilla's numbering: 4.4 declares "
         "planet_in_revolt as an overridable name from _02 up, so there is no "
         "_01 slot for STNH's correctly-named _01 file to land in. Without "
         "this the whole stem has an empty pool and all three variants fall "
         "through to the stock advisor."),
}

# ── aliases: one Borg clip answering to a SECOND 4.4 name ────────────────────
# Distinct from REBIND, which moves a clip from a dead name to a live one. Here
# the clip already serves its own event and is being lent to a near-identical
# one that has no Borg audio of its own.
ALIAS = {
    "advisor_notification_outpost_station_lost_01":
        ("advisor_notification_frontier_outpost_lost_01.wav", "MEDIUM",
         "4.4 carries both frontier_outpost_lost and outpost_station_lost and "
         "STNH recorded only the former. Same sentence either way."),
}

# Clips with no 4.4 slot at all. Listed so the next reader does not re-derive
# the search. Binding them anywhere would make the advisor say the wrong thing.
UNBOUND = {
    "advisor_notification_army_recruited_01.wav":
        "4.4 has no army-recruited advisor line.",
    "advisor_notification_spaceport_upgraded_01.wav":
        "Lost in the starbase rework; 4.4 has no upgrade line for it.",
    "advisor_notification_terraform_station_lost_01.wav":
        "4.4 enumerates station losses by type and has no terraform one.",
    "advisor_notification_special_project_available_01.wav":
        "4.4 has only special_project_COMPLETE; binding it would announce the "
        "wrong thing.",
    "we_are_the_borg_02.wav": "Spare; advisor_sample_vo has only 4 slots.",
    "we_are_the_borg_03.wav": "Spare; advisor_sample_vo has only 4 slots.",
    "biolog...wav":
        "Filename truncated in STNH's release, content unidentified. Not bound "
        "until someone listens to it.",
}

# ── resolve every 4.4 advisor name to a Borg wav, or leave it to vanilla ─────
assigned = {}          # 4.4 name -> (wav, reason)
used = set()

for wav, (target, conf, why) in REBIND.items():
    if wav not in wavs:
        sys.exit(f"REBIND names a wav that is not in {WAVDIR}: {wav}")
    if target not in VALID:
        sys.exit(f"REBIND target is not a 4.4 advisor name: {target}")
    if target in assigned:
        sys.exit(f"REBIND assigns {target} twice")
    assigned[target] = (wav, f"rebind/{conf}")
    used.add(wav)

for target, (wav, conf, why) in ALIAS.items():
    if wav not in wavs:
        sys.exit(f"ALIAS names a wav that is not in {WAVDIR}: {wav}")
    if target not in VALID:
        sys.exit(f"ALIAS target is not a 4.4 advisor name: {target}")
    if target in assigned:
        sys.exit(f"ALIAS collides with a REBIND on {target}")
    assigned[target] = (wav, f"alias/{conf}")
    used.add(wav)

# exact filename matches
for name in sorted(VALID):
    if name in assigned:
        continue
    if f"{name}.wav" in wavs:
        assigned[name] = (f"{name}.wav", "exact")
        used.add(f"{name}.wav")

# variant fill: a 4.4 name whose STEM has Borg audio but this variant does not.
# Vanilla picks among variants at random, so an unfilled variant is the stock
# advisor cutting in mid-game. Rotate whatever Borg clips the stem has.
pool = defaultdict(list)
for name, (wav, _) in sorted(assigned.items()):
    pool[stem_of(name)[0]].append(wav)

fills = 0
for name in sorted(VALID, key=lambda n: (stem_of(n)[0], stem_of(n)[1] or 0)):
    if name in assigned:
        continue
    s = stem_of(name)[0]
    if not pool.get(s):
        continue
    idx = stem_of(name)[1] or 1
    assigned[name] = (pool[s][(idx - 1) % len(pool[s])], "variant-fill")
    fills += 1

# ── emit ────────────────────────────────────────────────────────────────────
vend = VENDORED.read_text(encoding="utf-8", errors="replace").split("\n")

# The tail is every group EXCEPT l_vo_borg, carried through byte-identical.
# Select it by declared name: a positional rule ("first soundgroup after line
# N") silently re-emits l_vo_borg the moment the header length changes, which
# is the duplicate the 23:40 run logged at assetfactory_audio.cpp:778.
starts = [i for i, l in enumerate(vend) if l.startswith("soundgroup")]
if not starts:
    sys.exit(f"no soundgroup blocks found in {VENDORED}")


def group_name(i):
    for l in vend[i:i + 4]:
        m = re.match(r"\s*name\s*=\s*(\S+)", l)
        if m:
            return m.group(1)
    return None


tail_start = next((i for i in starts if group_name(i) != "l_vo_borg"), None)
if tail_start is None:
    sys.exit(f"{VENDORED} has no group other than l_vo_borg to carry through")
if any(group_name(i) == "l_vo_borg" for i in starts if i >= tail_start):
    sys.exit("l_vo_borg appears after the tail start; would emit a duplicate")
tail = "\n".join(vend[tail_start:])
carried = [group_name(i) for i in starts if i >= tail_start]

leftover = sorted(wavs - used)

hdr = []
A = hdr.append
A("# STG's copy of STNH's advisor-voice soundgroups. SHADOWS the vendored")
A("# sound/sth_soundgroups.asset harvested from Star Trek New Horizons (688086068).")
A("#")
A("# STNH's l_vo_borg was written against Stellaris 3.x and covered only 52 of")
A("# the 173 advisor sounds vanilla's l_machine overrides, so most of what a Borg")
A("# player heard was the stock advisor. Rebuilt here: renamed events, every")
A("# variant filled, STNH's four misspellings corrected.")
A("#")
A("# Owned in src/ rather than patched in vendor.yml because the Borg group is")
A("# rebuilt, not amended. l_vo_breen and l_vo_rom are carried through")
A("# byte-identical, so this copy is a superset and not a fork.")
A("#")
A("# Filename and l_vo_borg are STNH's, unprefixed: the file has to match to")
A("# shadow, and STH_advisor_voice_types.txt names the key verbatim. Decision 09.")
A("#")
A("# GENERATED by tools/gen_borg_vo.py against /stellaris/sound/soundgroups.asset.")
A("# Every name emitted below is checked to exist in vanilla first, because an")
A("# unknown name is an assetfactory_audio.cpp:901 record and a silent clip.")
A("#")
A(f"# COVERAGE: {len(assigned)} of {len(VALID)} advisor sounds "
  f"(STNH shipped 52), from {len(used)} of {len(wavs)} Borg wavs.")
A("#")
A("# STNH CLIPS DELIBERATELY LEFT UNBOUND -- 4.4 has no slot that means this:")
for w in sorted(UNBOUND):
    A(f"#   {w:52} {UNBOUND[w]}")
if leftover:
    for w in leftover:
        if w not in UNBOUND:
            A(f"#   {w:52} (unreviewed leftover)")
A("")

body = ["\n".join(hdr)]
body.append("########## borg\n")
body.append("soundgroup = \n{")
body.append("\tname = l_vo_borg")

cur = None
for name in sorted(assigned, key=lambda n: (stem_of(n)[0], stem_of(n)[1] or 0)):
    wav, why = assigned[name]
    s = stem_of(name)[0]
    if s != cur:
        cur = s
        body.append("")
    body.append("\tsoundoverride = {")
    body.append(f"\t\tname = \"{name}\"")
    body.append(f"\t\tfile = \"vo/ethics/vo_borg/{wav}\"")
    body.append("\t}")
body.append("}")
body.append("")
body.append(tail)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(body), encoding="utf-8")

print(f"wrote {OUT}")
print(f"  coverage      {len(assigned)}/{len(VALID)} advisor sounds (was 52)")
print(f"  exact         {sum(1 for v in assigned.values() if v[1]=='exact')}")
print(f"  rebound       {sum(1 for v in assigned.values() if v[1].startswith('rebind'))}")
print(f"  variant-fill  {fills}")
print(f"  borg wavs used {len(used)}/{len(wavs)}; unbound {len(leftover)}")
print(f"  carried through {', '.join(carried)}  (from {VENDORED})")
