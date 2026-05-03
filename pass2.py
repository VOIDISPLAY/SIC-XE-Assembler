# reads symbol table file 
def readsymbTable():
    symtable = {}
    with open('symbTable.txt', 'r') as f:
        lines = f.readlines()[2:]
        
        for line in lines:
            parts = line.split()
            if len (parts) >= 2:
                symtable[parts[0]] = parts[1]

    return symtable

#reads pool table file
def readpooltable():
    pooltbl = {}
    with open ("poolTable.txt" , "r") as f:
        lines = f.readlines()[2:]

        for line in lines:
            parts = line.split()
            if len(parts) >=2:
                pooltbl[parts[0]] = parts[1]
    
    return pooltbl

#reads Intermediate file 
def read_intermediate():
    loc = []
    label = []
    inst = []
    ref = []

    with open("intermediate.txt") as f:
        lines = f.readlines()[2:]

        for line in lines:
            parts = line.split()

            if len(parts) == 4:
                loc.append(parts[0])
                label.append(parts[1])
                inst.append(parts[2])
                ref.append(parts[3])
            elif len(parts) == 3:
                loc.append(parts[0])
                label.append("")
                inst.append(parts[1])
                ref.append(parts[2])

    return loc, label, inst, ref

# all Op codes
OPCODES = {
    "ADD": ["ADD", 3, 0x18],
    "ADDF": ["ADDF", 3, 0x58],
    "ADDR": ["ADDR", 2, 0x90],
    "AND": ["AND", 3, 0x40],
    "CLEAR": ["CLEAR", 2, 0xB4],
    "COMP": ["COMP", 3, 0x28],
    "COMPF": ["COMPF", 3, 0x88],
    "COMPR": ["COMPR", 2, 0xA0],
    "DIV": ["DIV", 3, 0x24],
    "DIVF": ["DIVF", 3, 0x64],
    "DIVR": ["DIVR", 2, 0x9C],
    "FIX": ["FIX", 1, 0xC4],
    "FLOAT": ["FLOAT", 1, 0xC0],
    "HIO": ["HIO", 1, 0xF4],
    "J": ["J", 3, 0x3C],
    "JEQ": ["JEQ", 3, 0x30],
    "JGT": ["JGT", 3, 0x34],
    "JLT": ["JLT", 3, 0x38],
    "JSUB": ["JSUB", 3, 0x48],
    "LDA": ["LDA", 3, 0x00],
    "LDB": ["LDB", 3, 0x68],
    "LDCH": ["LDCH", 3, 0x50],
    "LDF": ["LDF", 3, 0x70],
    "LDL": ["LDL", 3, 0x08],
    "LDS": ["LDS", 3, 0x6C],
    "LDT": ["LDT", 3, 0x74],
    "LDX": ["LDX", 3, 0x04],
    "LPS": ["LPS", 3, 0xD0],
    "MUL": ["MUL", 3, 0x20],
    "MULF": ["MULF", 3, 0x60],
    "MULR": ["MULR", 2, 0x98],
    "NORM": ["NORM", 1, 0xC8],
    "OR": ["OR", 3, 0x44],
    "RD": ["RD", 3, 0xD8],
    "RMO": ["RMO", 2, 0xAC],
    "RSUB": ["RSUB", 3, 0x4C],
    "SHIFTL": ["SHIFTL", 2, 0xA4],
    "SHIFTR": ["SHIFTR", 2, 0xA8],
    "SIO": ["SIO", 1, 0xF0],
    "SSK": ["SSK", 3, 0xEC],
    "STA": ["STA", 3, 0x0C],
    "STB": ["STB", 3, 0x78],
    "STCH": ["STCH", 3, 0x54],
    "STF": ["STF", 3, 0x80],
    "STI": ["STI", 3, 0xD4],
    "STL": ["STL", 3, 0x14],
    "STS": ["STS", 3, 0x7C],
    "STSW": ["STSW", 3, 0xE8],
    "STT": ["STT", 3, 0x84],
    "STX": ["STX", 3, 0x10],
    "SUB": ["SUB", 3, 0x1C],
    "SUBF": ["SUBF", 3, 0x5C],
    "SUBR": ["SUBR", 2, 0x94],
    "SVC": ["SVC", 2, 0xB0],
    "TD": ["TD", 3, 0xE0],
    "TIO": ["TIO", 1, 0xF8],
    "TIX": ["TIX", 3, 0x2C],
    "TIXR": ["TIXR", 2, 0xB8],
    "WD": ["WD", 3, 0xDC],
}

# regesters
registers = {
    "A": "0", "X": "1", "L": "2",
    "B": "3", "S": "4", "T": "5",
    "F": "6"
}

def GenerateOpcode(loc , inst , ref ,symtbl , pooltbl):
    objcode = []
    mod_records = []

    for i in range(len(inst)):
        op = inst[i].upper()
        operand = ref[i]

        #-----Directives "WORD , BYTE ,(RESW,RESB,START,END,BASE)"--------#

        if op =="WORD":
            obj =  hex(int(operand))[2:].zfill(6) 

        elif op == "BYTE":
            if operand.startswith("C"):
                obj = ''.join([hex(ord(c))[2:]  for c in operand  [2:-1] ])
            else:
                obj = operand [2:-1]
        elif op in ["RESW","RESB","START","END","BASE"]:
            obj = ""

        #---------Instruction formats 1,2,3,4-----------#
        else: