# PR-DRAFT — kinfo decoder pair (feature/kinfo-decoder)

**Status: DRAFT ONLY — do not post.** Nothing here has been opened as a PR, issue, or comment.
The owner must review and explicitly sign off before anything is submitted upstream.
Everything below the "cut here" line is the copy-pasteable PR content.

---8<--- cut here (title) ---------------------------------------------

tools: KData/KInfoTable decoder — kinfo_decode.py + kinfo_names.py (CE5 / SH-4)

---8<--- cut here (body) ---------------------------------------------

## What this adds

Two small, stdlib-only Python scripts under `tools/` that decode a **live Windows CE 5.0
(SH-4) KData/KInfoTable dump** — i.e. a raw RAM dump taken from an emulator session while
CE is booting or running. If you debug WinCE boots in the emulator, this turns an opaque
dword window into named kernel state: module-list head, page accounting, ROM-header
pointer, NLS code pages/locale, timezone bias, CeLog status — a quick "is the kernel
alive and what does it think" probe without attaching a debugger.

CE5 keeps the kernel's global state in `KDataStruct`; at **+0x300 (768) sits
`aInfo[32]` = the KInfoTable**, a dword array indexed by the `KINx` constants. Past
`aInfo`, `KData+0x380..0x400` is the interlocked-API code block — *not* more `aInfo` —
and the decoder labels it as such so nobody chases phantom indices 32+.

- **`tools/kinfo_names.py`** — the reference half:
  - `KINX_NAMES_WINCE500`: the full stock CE5 `KINx` index → name table for all 32
    `aInfo` entries, reconstructed and cross-validated (see provenance in the docstring).
  - `ROM_OVERRIDES`: calibration for a **customized vendor tree**. The unit's `nk.exe`
    was built from a modified `Dragon21/DRAGON` public tree (per the PDB build path), so
    its `pkfuncs.h` deviates from stock where the live dump demands it — e.g. `aInfo[0]`
    walks as the module list on this unit while stock puts `MODULES` at index 9, and
    `aInfo[9]` reads 0 on a live system with modules loaded. Decoding with overrides on
    still shows the stock name (`stock:…`) so deviations are flagged, not hidden.
  - Layout constants: `aInfo` at `KData+0x300`, 32 entries, interlocked block at `+0x380`.
  - Usable as a library (`kinx_name()`, the tables) or as its own CLI decoder.
- **`tools/kinfo_decode.py`** — the minimal standalone decoder: reads `aInfo[]` dwords
  at `KData+0x300` from a dump at a given offset and prints them. Ships with a one-entry
  built-in name map only; import `kinfo_names` when you want the full table.

## How it was validated

Live-verified against a **real emulator KData dump**, with three independent anchors
agreeing on the table's alignment:

1. **`[12] PTOC`** reads as a valid pointer to the ROM header (`ROMHDR`) — the classic
   KInfoTable landmark.
2. **`[26] CELOGSTATUS`** slot position calibrated independently from the `ksshx.h`
   equates (`CeLogStatus` at `KData+0x368`; `(0x368−0x300)/4 = 26`) — a byte offset from
   a different header landing exactly on the same slot.
3. **`[19] NLS_CP`** decodes as `OEM 437 << 16 | ANSI 1252` — a code-page pair that only
   makes sense in the NLS slot (`0x01b504e4`).

Corroborating sanity from the same dump: `[13] = &KData` (self-pointer) and
`[25] MINPAGEFREE (0x77d0) ≤ [4] PAGEFREE (0x77d6)`, as the semantics require.

## Usage

```sh
# full-name decode: 32 aInfo entries + the interlocked block boundary
python3 tools/kinfo_names.py ramdump.bin --off <KData-offset-in-dump> --count 48

# minimal standalone decoder (positional offset)
python3 tools/kinfo_decode.py ramdump.bin <KData-offset-in-dump> --count 32
```

`--count 48` (the `kinfo_names.py` default) covers all of `aInfo[32]` plus the start of
the interlocked-API block; slots ≥ 32 are labelled `INTERLOCKED_API[n]`.

## Sources

- **WINCE500 `nk/inc` headers + kernel writers** — `PRIVATE/WINCEOS/COREOS/NK/INC/kernel.h`
  documents the `KINx` indexing; the same tree's `physmem.c` (PROCARRAY, PAGESIZE,
  PFN_SHIFT/MASK, SECTIONS, MEMINFO, KDATA_ADDR, MINPAGEFREE), `loader.c` (PTOC,
  GWESHEAPINFO, TIMEZONEBIAS), `kwin32.c` (APISETS), `heap.c` (KHEAP, HEAP_WASTE),
  `kmisc.c` (NLS triple), and `schedule.c`/`kacl.c` (PTR_CURTOKEN) pin each slot's
  meaning by what the kernel actually writes there.
- **`ksshx.h` equates** — `CeLogStatus` at `KData+0x368` fixes index 26.
- **`reference/symbols` PDB struct dumps** (in this repo) — the expanded CodeView
  layouts confirm `KDataStruct.aInfo` at offset 768 (`0x300`), size 896 B.
- The `KINx` constants are `#define`s in the *public* `PUBLIC/COMMON/OAK/INC/pkfuncs.h`,
  which is absent from the public WINCE500 mirror (PRIVATE-only); the table was
  reconstructed from public copies of that header and cross-validated as described in
  `kinfo_names.py`'s provenance docstring.

---8<--- end cut here -------------------------------------------------

## Repo-convention checklist (what this repo asks for, and what was done)

The repo has **no CONTRIBUTING.md and no PR/issue template** (verified in the local
clone: only `README.md` and `toolchain/README.md`; the sole `.github` content anywhere is
vendored lwIP's CI). Conventions were inferred from the README and followed:

- **Self-contained / no external deps** — both scripts are pure Python 3 stdlib
  (`argparse`, `struct`, `sys`), matching the repo's "nothing external is needed" ethos.
- **Provenance documented in-file** — the `kinfo_names.py` docstring cites every source
  and the ROM-override evidence, in the spirit of the README's Notes on vendored SDK
  material (no new Microsoft-derived data is redistributed beyond names/offsets).
- **Repo layout** — `tools/` is new (this PR is its first content) and is not yet a row
  in the README's "Repository layout" table; offer to add one (see NOTE). `utils/` holds
  Windows-side build artifacts (`buildgdi.exe`, `postbuild_dc.bat`), so `tools/` for
  host-side Python analysis scripts keeps those concerns separate.

## NOTE — owner must confirm before posting

1. **CLA / DCO:** no CLA, DCO, or sign-off policy exists in the repo — confirm with the
   maintainer (maximqaxd) whether they expect a DCO `Signed-off-by` or anything else.
2. **Commit squashing:** the branch currently carries the two tool commits
   (`a2055ef`, `4740827`) plus the commit adding this draft file. Decide whether to
   squash to a single `tools: …` commit before opening the PR, and **drop this
   PR-DRAFT-…md file from the branch** (it is a working artifact, not repo content).
3. **Home for the scripts:** confirm `tools/` is acceptable vs. `utils/` (or elsewhere);
   optionally add a `tools/` row to the README repository-layout table in the same PR.
4. **Framing:** the repo badges CE 2.12; these tools target the CE5 layout of the
   customized `Dragon21` tree the emulator ROM actually runs. If the maintainer prefers,
   the body's first paragraph can lead with "CE5 layout, as used by the emulator's
   customized Dragon21 ROM" to preempt confusion.
5. Nothing has been posted anywhere — no PR, issue, branch comment, or external
   interaction. Posting requires explicit human signoff per the owner rule.
