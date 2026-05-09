MEMORY_SIZE = 0x2000

class Memory:
    def __init__(self):
        self.mem = [0x00] * MEMORY_SIZE

    def load_bytes(self, start_addr, byte_list):
        for i, byte in enumerate(byte_list):
            if start_addr + i < MEMORY_SIZE:
                self.mem[start_addr + i] = byte

    def modify(self, address, length):
        num_bytes = (length + 1) // 2
        value = 0
        for i in range(num_bytes):
            value = (value << 8) | self.mem[address + i]
            
        for i in reversed(range(num_bytes)):
            self.mem[address + i] = value & 0xFF
            value >>= 8