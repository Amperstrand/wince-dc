#!/usr/bin/env python3
"""Decode a live Windows CE5 (SH4) KData/KInfoTable dump.

CE5 keeps the kernel's global state in KDataStruct; at +0x300 (768)
sits aInfo[] = KInfoTable, a dword array indexed by KINx constants
(PRIVATE/WINCEOS/COREOS/NK/INC/kernel.h uses them; values from the
WINCE500 source tree).

Usage: kinfo_decode.py DUMP BIN KDATA_OFF [--kdata 0x88679800]
  DUMP    binary RAM dump containing KData
  KDATA_OFF offset of KData within the dump
Field names not yet mapped are shown as KINX_<index>.
"""
import argparse, struct, sys

# Calibrated/known entries (WINCE500 source):
#   KINX_CELOGSTATUS = 26  (ksshx.h: CeLogStatus equ 0x368; (0x368-0x300)/4)
KNOWN = {
    26: "CELOGSTATUS",
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("dump")
    p.add_argument("off", type=lambda x: int(x, 0))
    p.add_argument("--count", type=int, default=48)
    a = p.parse_args()
    d = open(a.dump, "rb").read()
    base = a.off + 0x300
    for i in range(a.count):
        o = base + 4 * i
        if o + 4 > len(d):
            break
        v = struct.unpack_from("<I", d, o)[0]
        name = KNOWN.get(i, f"KINX_{i}")
        print(f"[{i:2d}] {name:20s} = {v:#010x}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
