import math
import os

file=open("in.txt","r", encoding="utf-8-sig")
label=[]
inst=[]
ref=[]
loc_ctr=[]
symtbl={}
pooltbl={}
blcktbl = {}
blcktbl_end = {}
blck_name = []
def isformfour(bombo:str):
    return bombo[0]=="+"
def ispool(bookie:str):
    return bookie[0].startswith("&")
def get_pool_length_and_objcode(var):
    if var.upper().startswith("&C'"):
        content = var[3:-1]                                    
        length = len(content)
        objcode = ''.join(format(ord(c), '02X') for c in content)
    else:
        content = var[3:-1]                                    
        length = math.ceil(len(content) / 2)
        objcode = content.upper()
    return length, objcode
def print_pool_table():
    print("\nPool Table")
    print(f"{'Pool Variable':<15}{'Address':<10}{'Length':<10}{'Object Code'}")
    print(f"{'-'*15}{'-'*10}{'-'*10}{'-'*10}")
    for k, v in pooltbl.items():
        length, objcode = get_pool_length_and_objcode(k)
        print(f"{k:<15}{v:<10}{length:<10}{objcode}")
def print_symbol_table():
    print("\nSymbol Table")
    print(f"{'Symbol':<15}{'Address'}")
    print(f"{'-'*15}{'-'*10}")

    for k, v in symtbl.items():
        print(f"{k:<15}{v}")
def print_intermediate_table():
    print("\nIntermediate Table")
    print(f"{'Address':<10}{'Label':<12}{'Instruction':<15}{'Reference'}")
    print(f"{'-'*10}{'-'*12}{'-'*15}{'-'*10}")

    for i in range(len(label)):
        print(f"{loc_ctr[i]:<10}{label[i]:<12}{inst[i]:<15}{ref[i]}")
one_output = r"C:\\Users\\youse\\SIC-XE-Assembler\\pass1out"
def write_intermediate_file():
    with open(os.path.join(one_output, "intermediate.txt"), "w") as f:
        f.write(f"{'Address':<10}{'Label':<12}{'Instruction':<15}{'Reference'}\n")
        f.write(f"{'-'*10}{'-'*12}{'-'*15}{'-'*10}\n")

        for i in range(len(label)):
            f.write(f"{loc_ctr[i]:<10}{label[i]:<12}{inst[i]:<15}{ref[i]}\n")


def write_symbol_table_file():
    with open(os.path.join(one_output, "symbTable.txt"), "w") as f:
        f.write(f"{'Symbol':<15}{'Address'}\n")
        f.write(f"{'-'*15}{'-'*10}\n")

        for k, v in symtbl.items():
            f.write(f"{k:<15}{v}\n")


def write_pool_table_file():
    with open(os.path.join(one_output, "poolTable.txt"), "w") as f:
        f.write(f"{'Pool Variable':<15}{'Address':<10}{'Length':<10}{'Object Code'}\n")
        f.write(f"{'-'*15}{'-'*10}{'-'*10}{'-'*10}\n")
        for k, v in pooltbl.items():
            length, objcode = get_pool_length_and_objcode(k)
            f.write(f"{k:<15}{v:<10}{length:<10}{objcode}\n")
def print_block_table():
    print("\nBlock Table")
    print(f"{'Block':<15}{'Number':<15}{'Address':<10}{'Size'}")
    print(f"{'-'*15}{'-'*15}{'-'*10}{'-'*10}")
    for idx, (k, v) in enumerate(blcktbl.items()):
        size = blcktbl_end[k] if k in blcktbl_end else "0000"
        print(f"{k:<15}{idx:<15}{v:<10}{size}")
    # total program length
    last_block = list(blcktbl.keys())[-1]
    total = int(blcktbl[last_block], 16) + int(blcktbl_end[last_block], 16)
    print(f"\nTotal program length: {hex(total)[2:].upper()}")
def write_block_table_file():
    with open(os.path.join(one_output, "blckTable.txt"), "w") as f:
        f.write(f"{'Block':<15}{'Number':<15}{'Address':<10}{'Size'}\n")
        f.write(f"{'-'*15}{'-'*15}{'-'*10}{'-'*10}\n")
        for idx, (k, v) in enumerate(blcktbl.items()):
            size = blcktbl_end[k] if k in blcktbl_end else "0000"
            f.write(f"{k:<15}{idx:<15}{v:<10}{size}\n")
        last_block = list(blcktbl.keys())[-1]
        total = int(blcktbl[last_block], 16) + int(blcktbl_end[last_block], 16)
        f.write(f"\nTotal program length: {hex(total)[2:].upper()}\n")
def readf():
    for i in file:
        l=i.split()
        if len(l)==3:
            label.append(l[0])
            inst.append(l[1])
            ref.append(l[2])
        elif len(l)==2:
            label.append("")
            inst.append(l[0])
            ref.append(l[1])
        else:
            label.append("")
            inst.append(l[0])
            ref.append("")
def display():
    print("Label\tInstruction\tReference")
    for i in range(len(label)):
        print(f"{loc_ctr[i]}\t{label[i]}\t{inst[i]}\t{ref[i]}")

def pass1():
        block_order = []                        
        block_order.append("DEFAULT")        
        current_block = "DEFAULT"
        blcktbl.clear()                 
        blcktbl_end.clear()             
        blcktbl["DEFAULT"] = "0000"
        blcktbl_end["DEFAULT"] = "0000"
        
        j = 0
        loc_ctr.append(hex(int(ref[0], 16))[2:].zfill(4))
        for i in inst:
            blck_name.append(current_block)
            if ref[j].startswith("&") and ref[j] not in pooltbl:
                pooltbl[ref[j]] = loc_ctr[j]
            if i.upper() == "START":
                loc_ctr.append(hex(int(ref[0], 16))[2:].zfill(4))
            elif i.upper() == "USE":
                blcktbl_end[current_block] = loc_ctr[j]
                target = ref[j] if ref[j] != "" else "DEFAULT"
                if target in blcktbl:
                    next_addr = blcktbl_end[target]          
                else:
                    blcktbl[target] = loc_ctr[j]
                    block_order.append(target)                                   
                    next_addr = "0000"                         
                current_block = target
                loc_ctr.append(next_addr)
            elif i.upper()=="word".upper():
                loc_ctr.append(hex(int(loc_ctr[j],16)+int('3',16))[2:].zfill(4))
            elif i.upper()=="resw".upper():
                loc_ctr.append(hex(int(loc_ctr[j],16)+(int(ref[j])*3))[2:].zfill(4))
            elif i.upper()=="resb".upper():
                loc_ctr.append(hex(int(loc_ctr[j],16)+(int(ref[j])*1))[2:].zfill(4))
            elif i.upper()=="byte".upper():
                if ref[j].startswith('c') or ref[j].startswith('C'):
                    loc_ctr.append(hex(int(loc_ctr[j],16) + len(ref[j]) - 3)[2:].zfill(4))
                else:
                    loc_ctr.append(hex(int(loc_ctr[j],16)+math.ceil((len(ref[j])-3)/2))[2:].zfill(4))
            elif i.upper() == "CLEAR":                                          
                loc_ctr.append(hex(int(loc_ctr[j],16)+2)[2:].zfill(4))
            elif i.upper() == "BASE":
                loc_ctr.append(loc_ctr[j])
            elif i.upper() == "END":
                loc_ctr.append(loc_ctr[j])
            else:
                if isformfour(i.upper()):
                    loc_ctr.append(hex(int(loc_ctr[j],16)+4)[2:].zfill(4))
                else:
                    loc_ctr.append(hex(int(loc_ctr[j],16)+3)[2:].zfill(4))
            j+=1
            blcktbl_end[current_block] = loc_ctr[j]
        blcktbl_end[current_block] = loc_ctr[j]
        cdata_index = block_order.index("CDATA")
        pool_start = 0
        for block in block_order[:cdata_index]:
            pool_start += int(blcktbl_end[block], 16)
        current_pool_addr = pool_start
        for var in pooltbl:
            pooltbl[var] = hex(current_pool_addr)[2:].zfill(4)
            if var.upper().startswith("&C'"):
                size = len(var) - 4
            else:
                size = math.ceil((len(var) - 4) / 2)
            current_pool_addr += size
        blcktbl["CDATA"] = hex(current_pool_addr)[2:].zfill(4)
        # add POOL block to blcktbl
        pool_size = current_pool_addr - pool_start
        blcktbl_end["POOL"] = hex(pool_size)[2:].zfill(4)
        # insert POOL before CDATA in blcktbl
        new_blcktbl = {}
        for k, v in blcktbl.items():
            if k == "CDATA":
                new_blcktbl["POOL"] = hex(pool_start)[2:].zfill(4)
            new_blcktbl[k] = v
        blcktbl.clear()
        blcktbl.update(new_blcktbl)        
        cumulative = current_pool_addr
        for block in block_order[cdata_index:]:
            blcktbl[block] = hex(cumulative)[2:].zfill(4)
            cumulative += int(blcktbl_end[block], 16)               
        print("block_order:", block_order)
        print("blcktbl_end:", blcktbl_end)
        print("pooltbl:", pooltbl)
        print_intermediate_table()        
        print_intermediate_table()
        # display()
        for x in range(len(label)):
            if label[x] != "" and label[x] != "" and inst[x].upper() != "START":
                block_of_label = blck_name[x]
                block_start = int(blcktbl[block_of_label], 16)
                relative_addr = int(loc_ctr[x], 16) if loc_ctr[x] not in ('0', '') else 0
                real_addr = block_start + relative_addr
                symtbl[label[x]] = hex(real_addr)[2:].zfill(4)
        for z in symtbl.keys():
            print(z,"\t",symtbl[z])
for k in pooltbl.keys():
    print(k,"\t",pooltbl[k])
       
readf()
pass1()
print_pool_table()
print_symbol_table()
write_intermediate_file()
write_symbol_table_file()
write_pool_table_file()
write_block_table_file()
#print  (symtbl)
# print (loc_ctr)
# print (pooltbl)