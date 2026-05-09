from memory_visualizer import Memory

def parse_hex_bytes(hex_string):
    bytes_list = []
    for i in range(0, len(hex_string), 2):
        byte = int(hex_string[i:i+2], 16)
        bytes_list.append(byte)
    return bytes_list

def load_htme(filename):
    memory = Memory()
    with open(filename, "r") as file:
        lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        parts = line.split('^')
        record_type = parts[0]
        if record_type == 'H':
            continue
        elif record_type == 'T':
            start_address = int(parts[1], 16)
            object_codes = parts[3:]
            all_bytes = []
            for obj in object_codes:
                obj = obj.strip()
                if obj != "":
                    all_bytes.extend(parse_hex_bytes(obj))
            memory.load_bytes(start_address, all_bytes)
        elif record_type == 'M':
            address = int(parts[1], 16)
            length = int(parts[2], 16)
            memory.modify(address, length)
        elif record_type == 'E':
            continue
    return memory