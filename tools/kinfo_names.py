#!/usr/bin/env python3
"""KINx (KInfoTable / KData.aInfo index) names for Windows CE 5.0 (SH4).

Provenance
----------
The KINx constants are #defines (not a C enum) in the *public* header

    PUBLIC/COMMON/OAK/INC/pkfuncs.h      ("indices for UserKInfo array")

That PUBLIC tree is NOT part of the Arquivotheca/WinCE-src_20201004 mirror
(every branch root contains only PRIVATE/; verified on WINCE500 and WINCE300:
all 33 files that mention KINX_ there merely *use* the names, none defines
them). The table below is the stock WinCE5 layout, reconstructed from public
copies of pkfuncs.h (CE4.2 text in Phrack #63; CE5-era copies e.g. hjgode/
cn51_reset_enet with the CE5-only KINX_PTR_CURTOKEN/KINX_TIMECHANGECOUNT/
KINX_CRITSEC_ADJUST + SECURE_SECTION 0x61 additions) and cross-validated
against the mirror's own kernel code (PRIVATE/WINCEOS/COREOS/NK/KERNEL/
physmem.c writes PROCARRAY/PAGESIZE/PFN_SHIFT/PFN_MASK/SECTIONS/MEMINFO/
KDATA_ADDR/MINPAGEFREE; loader.c writes PTOC/GWESHEAPINFO/TIMEZONEBIAS;
kwin32.c writes APISETS; heap.c writes KHEAP/HEAP_WASTE; kmisc.c writes the
NLS triple; schedule.c/kacl.c write PTR_CURTOKEN; nkshx.h equates
CeLogStatus at KData+0x368 => index 26) and against the live unit dump
(slots 1,3,4,11,12,13,15,19,20,21,22,24,25,26 match stock semantics exactly;
e.g. [19]=0x01b504e4 = NLS_CP(OEM 437<<16 | ANSI 1252), [13]=&KData
self-pointer, [25]=0x77d0 <= [4]=0x77d6 MINPAGEFREE<=PAGEFREE, [26]=0).

The unit's nk.exe was built from a customized tree (PDB build path:
e:\\Dragon21\\public\\DRAGON\\cesysgen\\... — a vendor "DRAGON" public tree),
so its pkfuncs.h deviates from stock where the live dump demands it: see
ROM_OVERRIDES (aInfo[0] walks as the module list on this unit while stock
puts MODULES at 9; aInfo[9]=0 there although modules are loaded).

Layout constants: KDataStruct.aInfo[32] at KData+0x300..+0x380 (nkshx.h and
the ROM PDB agree); KData+0x380..0x400 is the interlocked-API code block,
not aInfo.
"""

# Stock Windows CE 5.0 KINx index -> name (definer: PUBLIC/COMMON/OAK/INC/pkfuncs.h)
KINX_NAMES_WINCE500 = {
    0:  "PROCARRAY",       # address of process array (PROCESS ProcArray[MAX_PROCESSES])
    1:  "PAGESIZE",        # system page size (live: 0x1000)
    2:  "PFN_SHIFT",       # shift for page # in PTE
    3:  "PFN_MASK",        # mask for page # in PTE (live: 0x1ffff000)
    4:  "PAGEFREE",        # # of free physical pages (live: 0x77d6)
    5:  "SYSPAGES",        # # of pages used by kernel
    6:  "KHEAP",           # ptr to kernel heap array (live ptr)
    7:  "SECTIONS",        # ptr to SectionTable array
    8:  "MEMINFO",         # ptr to system MemoryInfo struct (live ptr)
    9:  "MODULES",         # ptr to module list
    10: "DLL_LOW",         # lower bound of DLL shared space
    11: "NUMPAGES",        # total # of RAM pages (live: 0x7c67)
    12: "PTOC",            # ptr to ROM table of contents / ROMHDR (live: ROM hdr addr)
    13: "KDATA_ADDR",      # kernel mode version of KData (live: &KData itself)
    14: "GWESHEAPINFO",    # current amount of gwes heap in use
    15: "TIMEZONEBIAS",    # fast timezone bias info (live: 480 min = UTC+8)
    16: "PENDEVENTS",      # ptr to PendEvents1 (CE5; CE4.2 comment said bitmask)
    17: "KERNRESERVE",     # number of kernel reserved pages
    18: "API_MASK",        # bit mask for registered api sets
    19: "NLS_CP",          # hiword OEM cp, loword ANSI cp (live: 437 / 1252)
    20: "NLS_SYSLOC",      # default system locale (live: 0x409)
    21: "NLS_USERLOC",     # default user locale (live: 0x409)
    22: "HEAP_WASTE",      # kernel heap wasted space (live: 0x24)
    23: "DEBUGGER",        # for use by debugger for protocol communication
    24: "APISETS",         # APIset pointers = SystemAPISets (live ptr)
    25: "MINPAGEFREE",     # watermark of min # of free pages (live: 0x77d0)
    26: "CELOGSTATUS",     # CeLog status flags (ksshx.h: KData+0x368)
    27: "NKSECTION",       # address of NKSection
    28: "PTR_CURTOKEN",    # current token handle (CE5; was PWR_EVTS in CE4.2)
    29: "TIMECHANGECOUNT", # # of times time changed
    30: "CRITSEC_ADJUST",  # iterations for convoy-reduction scheme (default 32)
    31: "NKSIG",           # last KINFO entry; "NKSG" (0x4E4B5347) when NK ready
}

AINFO_OFF = 0x300          # KDataStruct.aInfo offset
AINFO_COUNT = 32           # aInfo[32] .. KData+0x380
INTERLOCKED_API_OFF = 0x380  # KData+0x380..0x400: interlocked API code, NOT aInfo

# Calibration for THIS unit's ROM (customized "Dragon21/DRAGON" CE5 build).
# Evidence: caller-verified walk of aInfo[0] as module list; aInfo[9]=0 on a
# live system with modules loaded; slots 2,5,7,10,18,27,31 are 0 where stock
# requires non-zero (PFN_SHIFT, SYSPAGES, SECTIONS, DLL_LOW, API_MASK,
# NKSECTION, NKSIG) => the ROM's pkfuncs.h is a modified variant.
ROM_OVERRIDES = {
    0:  "MODULES",   # module-list head on this unit (stock: PROCARRAY @0, MODULES @9)
    9:  None,        # unused/zero in this ROM (stock: MODULES)
}


def kinx_name(index, rom=True):
    """Name for aInfo[index]; rom=True applies this unit's calibration."""
    if rom:
        if index in ROM_OVERRIDES:
            ov = ROM_OVERRIDES[index]
            return ov if ov else "<unused-in-ROM>"
    return KINX_NAMES_WINCE500.get(index, "KINX_%d" % index)


if __name__ == "__main__":
    import argparse, struct
    p = argparse.ArgumentParser(description="decode KData dump aInfo[] (CE5)")
    p.add_argument("dump")
    p.add_argument("--off", type=lambda x: int(x, 0), default=0, help="KData offset in dump")
    p.add_argument("--count", type=int, default=48)
    a = p.parse_args()
    # slots zero in the live dump where stock CE5 would have a value
    zero_in_rom = {2, 5, 7, 10, 17, 18, 27, 30, 31}
    d = open(a.dump, "rb").read()
    for i in range(a.count):
        o = a.off + AINFO_OFF + 4 * i
        v = struct.unpack_from("<I", d, o)[0]
        if i < AINFO_COUNT:
            n = kinx_name(i)
            if i in ROM_OVERRIDES and ROM_OVERRIDES[i] != KINX_NAMES_WINCE500.get(i):
                n += " (stock:%s)" % KINX_NAMES_WINCE500[i]
            elif i in zero_in_rom:
                n += " (stock; 0 in ROM => likely unused)"
        else:
            n = "INTERLOCKED_API[%d]" % (i - AINFO_COUNT)
        print("[%2d] %-48s = 0x%08x" % (i, n, v))
