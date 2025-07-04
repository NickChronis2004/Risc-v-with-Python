
class Register:
    def __init__(self, name, abi_name, purpose, read_only=False, bit_length=16):
        self.name = name       # Name of the register
        self.abi_name = abi_name # ABI name is the nickname used to be more clear ,like t0 for x5 or ra for x1
        self.purpose = purpose    # Purpose of the register, e.g., "temporary", "return address"
        self.read_only = read_only # Indicates if the register is read-only ,for exampple the register x0 is read only
        self.bit_length = bit_length    # Sets the bit length of the register, default is 16 bits
        self.value = 0x0000 # Initial value of the register, default is 0x0000
        
    def read(self):
        return self.value
        
    def write(self, value):
        if self.read_only:
            return False
        self.value = value & ((1 << self.bit_length) - 1)  # Generic masking so it is not possible to write more than the bit length
        return True
    
    def reset(self):
        if not self.read_only:
            self.value = 0x0000

    def is_zero(self):
        return self.value == 0
    
    # info and debug methods
    def get_info(self):
        return {
            'name': self.name,
            'abi_name': self.abi_name,
            'purpose': self.purpose,
            'value': self.value,
            'read_only': self.read_only
        }
    
    def __str__(self):
        return f"{self.name}({self.abi_name}): 0x{self.value:04X} ({self.value})"

    def __repr__(self):
        return f"Register('{self.name}', '{self.abi_name}', value=0x{self.value:04X})"
    

# RegisterFile class to manage a collection of registers
# This class will hold multiple Register instances and provide methods to interact with them

class RegisterFile:
    def __init__(self):
        x0 = Register("x0", "zero", "Always zero, read-only", read_only=True)
        x1 = Register("x1", "ra", "Return address", read_only=False)
        x2 = Register("x2", "sp", "Stack pointer", read_only=False)
        x3 = Register("x3", "gp", "Global pointer", read_only=False)
        x4 = Register("x4", "tp", "Thread pointer", read_only=False)
        x5 = Register("x5", "t0", "Temporary register 0", read_only=False)
        x6 = Register("x6", "t1", "Temporary register 1", read_only=False)
        x7 = Register("x7", "t2", "Temporary register 2", read_only=False)
        x8 = Register("x8", "s0", "Saved register 0 (fp)", read_only=False)
        x9 = Register("x9", "s1", "Saved register 1", read_only=False)
        x10 = Register("x10", "a0", "Function argument/return value 0", read_only=False)
        x11 = Register("x11", "a1", "Function argument/return value 1", read_only=False)
        x12 = Register("x12", "a2", "Function argument 2", read_only=False)
        x13 = Register("x13", "a3", "Function argument 3", read_only=False)
        x14 = Register("x14", "a4", "Function argument 4", read_only=False)
        x15 = Register("x15", "a7", "System call number", read_only=False) 
        
        self.registers = [x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, 
                         x10, x11, x12, x13, x14, x15]
        
        # ABI name to index mapping
        self.abi_to_index = {
            "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,
            "t0": 5, "t1": 6, "t2": 7, "s0": 8, "s1": 9,
            "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14, "a7": 15
        }

    def read(self, reg_identifier):
        if isinstance(reg_identifier, int):
            if 0 <= reg_identifier < 16:
                return self.registers[reg_identifier].read()
        elif isinstance(reg_identifier, str):
            if reg_identifier in self.abi_to_index:
                index = self.abi_to_index[reg_identifier]
                return self.registers[index].read()
        
        print(f"Error: Invalid register identifier '{reg_identifier}'")
        return 0

    def write(self, reg_identifier, value):
        if isinstance(reg_identifier, int):
            if 0 <= reg_identifier < 16:
                return self.registers[reg_identifier].write(value)
        elif isinstance(reg_identifier, str):
            if reg_identifier in self.abi_to_index:
                index = self.abi_to_index[reg_identifier]
                return self.registers[index].write(value)
        
        print(f"Error: Invalid register identifier '{reg_identifier}'")
        return False

    def get_non_zero_registers(self):
        """Returns list of registers with non-zero values"""
        non_zero = []
        for i, reg in enumerate(self.registers):
            if not reg.is_zero():
                non_zero.append((i, reg.name, reg.abi_name, reg.value))
        return non_zero

    def display_register_file(self):  
        for i, reg in enumerate(self.registers):
            print(f"x{i}: {reg}")