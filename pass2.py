import re
import sys
import os


# Opcode table (hex_opcode_byte, default_format)
OPCODES = {
    "FIX":    (0xC4, 1), "FLOAT":  (0xC0, 1), "HIO":    (0xF4, 1),
    "NORM":   (0xC8, 1), "SIO":    (0xF0, 1), "TIO":    (0xF8, 1),

    "ADDR":   (0x90, 2), "CLEAR":  (0xB4, 2), "COMPR":  (0xA0, 2),
    "DIVR":   (0x9C, 2), "MULR":   (0x98, 2), "RMO":    (0xAC, 2),
    "SHIFTL": (0xA4, 2), "SHIFTR": (0xA8, 2), "SUBR":   (0x94, 2),
    "SVC":    (0xB0, 2), "TIXR":   (0xB8, 2),

    "ADD":    (0x18, 3), "ADDF":   (0x58, 3), "AND":    (0x40, 3),
    "MUL":    (0x20, 3), "STX":    (0x10, 3), "SUB":    (0x1C, 3),
    "COMPF":  (0x88, 3), "DIV":    (0x24, 3), "MULF":   (0x60, 3),
    "OR":     (0x44, 3), "TIX":    (0x2C, 3), "WD":     (0xDC, 3),
    "RD":     (0xD8, 3), "RSUB":   (0x4C, 3), "SSK":    (0xEC, 3),
    "STA":    (0x0C, 3), "STB":    (0x78, 3), "STCH":   (0x54, 3),
    "STF":    (0x80, 3), "STI":    (0xD4, 3), "STL":    (0x14, 3),
    "COMP":   (0x28, 3), "SUBF":   (0x5C, 3), "TD":     (0xE0, 3),
    "DIVF":   (0x64, 3), "J":      (0x3C, 3), "JEQ":    (0x30, 3),
    "JGT":    (0x34, 3), "JLT":    (0x38, 3), "JSUB":   (0x48, 3),
    "LDA":    (0x00, 3), "LDB":    (0x68, 3), "LDCH":   (0x50, 3),
    "LDF":    (0x70, 3), "LDL":    (0x08, 3), "LDS":    (0x6C, 3),
    "LDT":    (0x74, 3), "LDX":    (0x04, 3), "LPS":    (0xD0, 3),
    "STS":    (0x7C, 3), "STSW":   (0xE8, 3), "STT":    (0x84, 3),
}

REGISTERS = {"A": 0, "X": 1, "L": 2, "B": 3, "S": 4, "T": 5, "F": 6}

# boundaries for parsing intermediate file columns
COL_LOC  = (0,  18)
COL_SYM  = (18, 27)
COL_INST = (27, 41)
COL_REF  = (41, None)


# Parse intermediate file
def read_intermediate(path="pass1out/intermediate.txt"):
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()[2:]

    for raw in lines:
        if not raw.strip():
            continue
        line = raw.expandtabs()
        line = line + " " * max(0, 60 - len(line))

        loc    = line[COL_LOC[0]:  COL_LOC[1]].strip()
        symbol = line[COL_SYM[0]:  COL_SYM[1]].strip()
        inst   = line[COL_INST[0]: COL_INST[1]].strip().upper()
        ref    = line[COL_REF[0]:             ].strip()

        if not inst:
            continue

        rows.append({"loc": loc, "symbol": symbol, "inst": inst,
                     "ref": ref, "_raw": raw})
    return rows


# Read symbTable.txt
def read_symtab(path="pass1out/symbTable.txt"):
    symtbl = {}
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()[1:]  
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            symtbl[parts[0]] = parts[1]
    return symtbl


# Read poolTable.txt
def read_pooltab(path="pass1out/poolTable.txt"):
    pooltbl = {}
    if not os.path.exists(path):
        return pooltbl
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()[1:]  
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            pooltbl[parts[0]] = parts[1]
    return pooltbl


# Literal resolver
def resolve_literal(key: str, pooltbl: dict) -> int:
    if key in pooltbl:
        return int(pooltbl[key], 16)
    m = re.match(r"C'(.+)'", key, re.IGNORECASE)
    if m:
        val = 0
        for ch in m.group(1):
            val = (val << 8) | ord(ch)
        return val
    m = re.match(r"X'([0-9A-Fa-f]+)'", key, re.IGNORECASE)
    if m:
        return int(m.group(1), 16)
    raise ValueError(f"Unknown literal: {key!r}")


def resolve_operand(operand: str, symtbl: dict, pooltbl: dict) -> int:
    if not operand:
        return 0
    if operand.startswith("&"):
        return resolve_literal(operand[1:], pooltbl)
    if re.fullmatch(r"[0-9]+", operand):
        return int(operand)
    if operand in symtbl:
        return int(symtbl[operand], 16)
    try:
        return int(operand, 16)
    except ValueError:
        return 0


def next_loc(rows, current_idx: int) -> int:
    for j in range(current_idx + 1, len(rows)):
        if rows[j]["loc"]:
            return int(rows[j]["loc"], 16)
    loc = rows[current_idx]["loc"]
    return (int(loc, 16) + 3) if loc else 0


# Object code
def object_code(rows, symtbl, pooltbl):
    objcodes    = []
    mod_records = []
    base_val    = None

    for i, row in enumerate(rows):
        loc     = row["loc"]
        inst    = row["inst"]
        operand = row["ref"]
        obj     = ""

        # Non-directives
        if inst in ("START", "END", "USE", "RESW", "RESB", "EQU"):
            objcodes.append("")
            continue

        if inst == "BASE":
            sym = operand.strip()
            if sym in symtbl:
                base_val = int(symtbl[sym], 16)
            objcodes.append("")
            continue

        if inst == "NOBASE":
            base_val = None
            objcodes.append("")
            continue

        if inst == "WORD":
            try:
                val = int(operand)
            except ValueError:
                val = int(operand, 16)
            obj = f"{val & 0xFFFFFF:06X}"
            objcodes.append(obj)
            continue

        if inst == "BYTE":
            m_c = re.match(r"C'(.+)'", operand, re.IGNORECASE)
            m_x = re.match(r"X'([0-9A-Fa-f]+)'", operand, re.IGNORECASE)
            if m_c:
                obj = "".join(f"{ord(c):02X}" for c in m_c.group(1))
            elif m_x:
                obj = m_x.group(1).upper()
            objcodes.append(obj)
            continue

        # instructions
        is_fmt4  = inst.startswith("+")
        mnemonic = inst.lstrip("+")

        if mnemonic not in OPCODES:
            objcodes.append("")
            continue

        opcode_val, default_fmt = OPCODES[mnemonic]
        fmt = 4 if is_fmt4 else default_fmt

        # Format 1
        if fmt == 1:
            obj = f"{opcode_val:02X}"
            objcodes.append(obj)
            continue

        # Format 2
        if fmt == 2:
            regs = [r.strip() for r in operand.split(",")]
            r1   = REGISTERS.get(regs[0], 0)
            r2   = REGISTERS.get(regs[1], 0) if len(regs) > 1 else 0
            obj  = f"{opcode_val:02X}{r1:X}{r2:X}"
            objcodes.append(obj)
            continue

        # Format 3 / 4
        n = i_flag = 1
        x = b = p = e = 0

        is_immediate_numeric = False
        if operand.startswith("#"):
            n, i_flag = 0, 1
            operand   = operand[1:]
            is_immediate_numeric = re.fullmatch(r"[0-9]+", operand) is not None
        elif operand.startswith("@"):
            n, i_flag = 1, 0
            operand   = operand[1:]

        if operand.upper().endswith(",X"):
            x       = 1
            operand = operand[:-2]

        addr    = resolve_operand(operand, symtbl, pooltbl)
        op_byte = (opcode_val & 0xFC) | (n << 1) | i_flag

        if fmt == 4:
            e     = 1
            flags = (x << 3) | (b << 2) | (p << 1) | e
            obj   = f"{op_byte:02X}{flags:X}{addr:05X}"
            if loc:
                mod_addr = int(loc, 16) + 1
                mod_records.append(f"{mod_addr:06X} 05")
        else:
            if is_immediate_numeric:
                disp_field = addr & 0xFFF
            else:
                nloc       = next_loc(rows, i)
                disp       = addr - nloc

                if -2048 <= disp <= 2047:
                    p          = 1
                    disp_field = disp & 0xFFF
                elif base_val is not None and 0 <= (addr - base_val) <= 4095:
                    b          = 1
                    disp_field = addr - base_val
                else:
                    disp_field = addr & 0xFFF

            flags = (x << 3) | (b << 2) | (p << 1) | e
            obj   = f"{op_byte:02X}{flags:X}{disp_field:03X}"

        objcodes.append(obj.upper())

    return objcodes, mod_records


# Write out_pass2.txt
def write_pass2(rows, objcodes, path="out_pass2.txt"):
    hdr = (f"{'Location counter':<18}{'Symbol':<9}"
           f"{'Instructions':<14}{'Reference':<14}Obj. code")
    sep = ("─" * 16 + "  " + "─" * 7 + "  " + "─" * 12 + "  " +
           "─" * 12 + "  " + "─" * 14)

    with open(path, "w", encoding="utf-8") as f:
        f.write(hdr + "\n")
        f.write(sep + "\n")
        for row, obj in zip(rows, objcodes):
            f.write(
                f"{row['loc']:<18}{row['symbol']:<9}"
                f"{row['inst']:<14}{row['ref']:<14}{obj}\n"
            )

# Write HTME.txt
def write_htme(rows, objcodes, mod_records, symtbl, path="HTME.txt"):
    MAX_BYTES = 30

    prog_name = "      "
    for row in rows:
        if row["symbol"]:
            prog_name = row["symbol"][:6].ljust(6)
            break

    prog_start = 0
    for row in rows:
        if row["loc"]:
            prog_start = int(row["loc"], 16)
            break

    max_end = prog_start
    for row, obj in zip(rows, objcodes):
        if row["loc"]:
            a = int(row["loc"], 16)

            if obj:
                s = len(obj) // 2
                end_addr = a + s
                if end_addr > max_end:
                    max_end = end_addr

            elif row["inst"] == "RESW":
                try:
                    words = int(row["ref"])
                    end_addr = a + (words * 3) 
                    if end_addr > max_end:
                        max_end = end_addr
                except ValueError:
                    pass
            elif row["inst"] == "RESB":
                try:
                    bytes_val = int(row["ref"])
                    end_addr = a + bytes_val
                    if end_addr > max_end:
                        max_end = end_addr
                except ValueError:
                    pass
    prog_len = max_end - prog_start

    pairs = sorted(
        [(int(r["loc"], 16), obj.upper())
         for r, obj in zip(rows, objcodes)
         if r["loc"] and obj],
        key=lambda t: t[0]
    )

    text_records = []
    if pairs:
        run_start = pairs[0][0]
        run_objs  = []
        run_bytes = 0
        for addr, obj in pairs:
            obj_bytes = len(obj) // 2
            if addr != run_start + run_bytes or run_bytes + obj_bytes > MAX_BYTES:
                if run_objs:
                    text_records.append((run_start, list(run_objs)))
                run_start = addr
                run_objs  = []
                run_bytes = 0
            run_objs.append(obj)
            run_bytes += obj_bytes
        if run_objs:
            text_records.append((run_start, list(run_objs)))

    exec_start = prog_start
    for row in rows:
        if row["inst"] == "END" and row["ref"]:
            sym = row["ref"].strip()
            if sym in symtbl:
                exec_start = int(symtbl[sym], 16)
            break

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"H^{prog_name}^{prog_start:06X}^{prog_len:06X}\n")
        for t_start, t_objs in text_records:
            combined   = "".join(t_objs)
            byte_count = len(combined) // 2
            f.write(f"T^{t_start:06X}^{byte_count:02X}^{'^ '.join(t_objs)}\n")
        for mr in mod_records:
            addr_str, half_bytes = mr.split()
            f.write(f"M^{addr_str.upper()}^{half_bytes}\n")
        f.write(f"E^{exec_start:06X}\n")


def main():
    inter_path = sys.argv[1] if len(sys.argv) > 1 else "pass1out/intermediate.txt"
    sym_path   = sys.argv[2] if len(sys.argv) > 2 else "pass1out/symbTable.txt"
    pool_path  = sys.argv[3] if len(sys.argv) > 3 else "pass1out/poolTable.txt"

    rows    = read_intermediate(inter_path)
    symtbl  = read_symtab(sym_path)
    pooltbl = read_pooltab(pool_path)

    objcodes, mod_records = object_code(rows, symtbl, pooltbl)
    write_pass2(rows, objcodes)
    write_htme(rows, objcodes, mod_records, symtbl)


if __name__ == "__main__":
    main()