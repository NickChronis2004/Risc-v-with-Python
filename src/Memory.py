
from typing import List, Optional


class InstructionMemory:
    """
    Instruction Memory για RISC-V 16-bit processor
    
    - Read-only μνήμη για instructions
    - Φορτώνει machine code από binary files
    - Μέγεθος: 1024 words (16-bit each)
    - Διευθύνσεις: 0x0000 - 0x03FF
    """
    
    def __init__(self, size=1024):
        """
        Αρχικοποίηση Instruction Memory
        
        Args:
            size (int): Μέγεθος σε words (default: 1024)
        """
        self.size = size
        self.memory = [0] * size  # Initialize με zeros
        self.program_size = 0     # Πόσες εντολές έχουν φορτωθεί
        
        print(f"📄 Instruction Memory initialized: {size} words ({size * 2} bytes)")
    
    def load_program(self, instructions: List[int], start_address=0):
        """
        Φορτώνει πρόγραμμα στη μνήμη
        
        Args:
            instructions (List[int]): Λίστα με 16-bit εντολές
            start_address (int): Αρχική διεύθυνση (default: 0)
            
        Returns:
            bool: True αν επιτυχής φόρτωση
        """
        if start_address < 0 or start_address >= self.size:
            print(f"❌ Invalid start address: 0x{start_address:04X}")
            return False
        
        if len(instructions) + start_address > self.size:
            print(f"❌ Program too large: {len(instructions)} instructions, available space: {self.size - start_address}")
            return False
        
        # Καθαρισμός μνήμης
        self.memory = [0] * self.size
        
        # Φόρτωση εντολών
        for i, instruction in enumerate(instructions):
            self.memory[start_address + i] = instruction & 0xFFFF
        
        self.program_size = len(instructions)
        
        print(f"✅ Program loaded: {len(instructions)} instructions at 0x{start_address:04X}")
        return True
    
    def load_from_binary_file(self, filename: str):
        """
        Φορτώνει πρόγραμμα από binary αρχείο
        
        Args:
            filename (str): Όνομα binary αρχείου
            
        Returns:
            bool: True αν επιτυχής φόρτωση
        """
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            
            # Μετατροπή bytes σε 16-bit instructions
            instructions = []
            for i in range(0, len(data), 2):
                if i + 1 < len(data):
                    # Little-endian 16-bit
                    instruction = int.from_bytes(data[i:i+2], byteorder='little')
                    instructions.append(instruction)
            
            return self.load_program(instructions)
            
        except FileNotFoundError:
            print(f"❌ Binary file not found: {filename}")
            return False
        except Exception as e:
            print(f"❌ Error loading binary file: {e}")
            return False
    
    def read_instruction(self, address: int) -> int:
        """
        Διαβάζει εντολή από τη μνήμη
        
        Args:
            address (int): Διεύθυνση (0-1023)
            
        Returns:
            int: 16-bit εντολή ή 0 αν invalid address
        """
        if 0 <= address < self.size:
            return self.memory[address]
        
        print(f"⚠️  Invalid instruction address: 0x{address:04X}")
        return 0  # Return NOP για invalid address
    
    def get_program_size(self) -> int:
        """Επιστρέφει το μέγεθος του φορτωμένου προγράμματος"""
        return self.program_size
    
    def display_memory(self, start=0, count=16):
        """
        Εμφανίζει περιεχόμενο instruction memory
        
        Args:
            start (int): Αρχική διεύθυνση
            count (int): Πόσες εντολές να εμφανίσει
        """
        print("\n" + "="*60)
        print("📄 INSTRUCTION MEMORY")
        print("="*60)
        print("Address  | Instruction | Binary           | Disassembly")
        print("-"*60)
        
        for i in range(count):
            addr = start + i
            if addr >= self.size:
                break
                
            instruction = self.memory[addr]
            if instruction == 0 and addr >= self.program_size:
                continue  # Skip empty memory after program
                
            print(f"0x{addr:04X}   | 0x{instruction:04X}      | {instruction:016b} | {self._disassemble(instruction)}")
        
        print("="*60)
    
    def _disassemble(self, instruction: int) -> str:
        """
        Απλή disassembly για visualization
        (Θα βελτιωθεί όταν φτιάξουμε τον InstructionDecoder)
        """
        if instruction == 0:
            return "NOP / Empty"
        
        opcode = (instruction >> 12) & 0xF
        
        opcode_names = {
            0x0: "ADD", 0x1: "SUB", 0x2: "AND", 0x3: "OR", 0x4: "XOR",
            0x5: "ADDI", 0x6: "ANDI", 0x7: "ORI", 0x8: "LW", 0x9: "SW",
            0xA: "BEQ", 0xB: "BNE", 0xC: "JAL", 0xE: "NOP", 0xF: "HALT"
        }
        
        return opcode_names.get(opcode, f"UNK(0x{opcode:X})")


class DataMemory:
    """
    Data Memory για RISC-V 16-bit processor
    
    - Read/Write μνήμη για δεδομένα
    - Υποστηρίζει LW/SW operations
    - Μέγεθος: 1024 words (16-bit each)
    - Διευθύνσεις: 0x1000 - 0x13FF (logical)
    """
    
    def __init__(self, size=1024, base_address=0x1000):
        """
        Αρχικοποίηση Data Memory
        
        Args:
            size (int): Μέγεθος σε words (default: 1024)
            base_address (int): Βασική διεύθυνση (default: 0x1000)
        """
        self.size = size
        self.base_address = base_address
        self.memory = [0] * size
        self.access_count = 0     # Στατιστικά προσβάσεων
        self.write_count = 0
        self.read_count = 0
        
        print(f"💾 Data Memory initialized: {size} words at 0x{base_address:04X}-0x{base_address + size - 1:04X}")
    
    def _address_to_index(self, address: int) -> Optional[int]:
        """
        Μετατρέπει logical address σε memory index
        
        Args:
            address (int): Logical address
            
        Returns:
            Optional[int]: Memory index ή None αν invalid
        """
        if self.base_address <= address < self.base_address + self.size:
            return address - self.base_address
        return None
    
    def read_word(self, address: int) -> int:
        """
        Διαβάζει 16-bit word από τη μνήμη (LW operation)
        
        Args:
            address (int): Logical address
            
        Returns:
            int: 16-bit value ή 0 αν invalid address
        """
        index = self._address_to_index(address)
        if index is not None:
            value = self.memory[index]
            self.read_count += 1
            self.access_count += 1
            print(f"📖 Memory Read: [0x{address:04X}] → 0x{value:04X}")
            return value
        
        print(f"⚠️  Invalid read address: 0x{address:04X}")
        return 0
    
    def write_word(self, address: int, value: int) -> bool:
        """
        Γράφει 16-bit word στη μνήμη (SW operation)
        
        Args:
            address (int): Logical address
            value (int): 16-bit value
            
        Returns:
            bool: True αν επιτυχής εγγραφή
        """
        index = self._address_to_index(address)
        if index is not None:
            old_value = self.memory[index]
            self.memory[index] = value & 0xFFFF
            self.write_count += 1
            self.access_count += 1
            print(f"✏️  Memory Write: [0x{address:04X}] 0x{old_value:04X} → 0x{value & 0xFFFF:04X}")
            return True
        
        print(f"⚠️  Invalid write address: 0x{address:04X}")
        return False
    
    def clear_memory(self):
        """Καθαρίζει όλη τη μνήμη"""
        self.memory = [0] * self.size
        print("🧹 Data memory cleared")
    
    def get_statistics(self) -> dict:
        """Επιστρέφει στατιστικά προσβάσεων"""
        return {
            'total_accesses': self.access_count,
            'reads': self.read_count,
            'writes': self.write_count,
            'size': self.size,
            'base_address': self.base_address
        }
    
    def display_memory(self, start_offset=0, count=16):
        """
        Εμφανίζει περιεχόμενο data memory
        
        Args:
            start_offset (int): Offset από base address
            count (int): Πόσες διευθύνσεις να εμφανίσει
        """
        print("\n" + "="*50)
        print("💾 DATA MEMORY")
        print("="*50)
        print("Address  | Value  | Decimal")
        print("-"*30)
        
        for i in range(count):
            index = start_offset + i
            if index >= self.size:
                break
                
            address = self.base_address + index
            value = self.memory[index]
            
            if value != 0:  # Εμφάνιση μόνο non-zero values
                print(f"0x{address:04X}   | 0x{value:04X} | {value:>5}")
        
        # Στατιστικά
        stats = self.get_statistics()
        print("-"*30)
        print(f"Reads: {stats['reads']}, Writes: {stats['writes']}, Total: {stats['total_accesses']}")
        print("="*50)
    
    def find_non_zero(self) -> List[tuple]:
        """
        Βρίσκει όλες τις non-zero τιμές στη μνήμη
        
        Returns:
            List[tuple]: (address, value) pairs
        """
        non_zero = []
        for i, value in enumerate(self.memory):
            if value != 0:
                address = self.base_address + i
                non_zero.append((address, value))
        return non_zero


# Demo και testing functions
def demo_memory_system():
    """Demo του memory system"""
    print("🚀 Memory System Demo")
    print("="*40)
    
    # 1. Δημιουργία memories
    imem = InstructionMemory(size=256)  # Μικρότερο για demo
    dmem = DataMemory(size=256)
    
    # 2. Mock program data
    mock_program = [
        0x510A,  # ADDI x1, x0, 10
        0x5205,  # ADDI x2, x0, 5  
        0x0312,  # ADD x3, x1, x2
        0x9320,  # SW x3, 0(x2)
        0xF000   # HALT
    ]
    
    print("\n📋 Loading mock program...")
    imem.load_program(mock_program)
    
    print("\n📄 Instruction Memory Contents:")
    imem.display_memory(count=8)
    
    print("\n💾 Testing Data Memory...")
    # Mock data operations
    dmem.write_word(0x1000, 0x1234)
    dmem.write_word(0x1001, 0x5678)
    dmem.write_word(0x1002, 0xABCD)
    
    print("\n📖 Reading from Data Memory...")
    value1 = dmem.read_word(0x1000)
    value2 = dmem.read_word(0x1001)
    
    print("\n💾 Data Memory Contents:")
    dmem.display_memory(count=8)
    
    print("\n📊 Memory Statistics:")
    stats = dmem.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    demo_memory_system()