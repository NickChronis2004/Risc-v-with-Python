import re
import sys
from typing import List, Dict, Optional, Tuple


def _configure_console_encoding():
    """Keep emoji/status output from crashing on non-UTF-8 Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass


_configure_console_encoding()


class RiscVAssembler:
    """
    RISC-V Assembler για 16-bit επεξεργαστή
    
    Διαβάζει αρχεία .asm και τα μετατρέπει σε machine code
    Παράγει binary (.bin) και hex (.hex) αρχεία
    """
    
    def __init__(self):
        self.labels = {}        # Λάβελ -> διεύθυνση
        self.instructions = []  # Λίστα εντολών
        self.machine_code = []  # Binary εντολές
        self.current_line = 0
        
        # Opcodes για 16-bit processor (4-bit opcode)
        self.opcodes = {
            'ADD':  0b0000,   # R-type
            'SUB':  0b0001,   # R-type
            'AND':  0b0010,   # R-type
            'OR':   0b0011,   # R-type
            'XOR':  0b0100,   # R-type
            'ADDI': 0b0101,   # I-type
            'ANDI': 0b0110,   # I-type
            'ORI':  0b0111,   # I-type
            'LW':   0b1000,   # I-type
            'SW':   0b1001,   # S-type
            'BEQ':  0b1010,   # B-type
            'BNE':  0b1011,   # B-type
            'JAL':  0b1100,   # J-type
            'NOP':  0b1110,   # Special
            'HALT': 0b1111    # Special
        }
        
        # Register mapping (ABI names to numbers)
        self.register_map = {
            'x0': 0, 'zero': 0,
            'x1': 1, 'ra': 1,
            'x2': 2, 'sp': 2,
            'x3': 3, 'gp': 3,
            'x4': 4, 'tp': 4,
            'x5': 5, 't0': 5,
            'x6': 6, 't1': 6,
            'x7': 7, 't2': 7,
            'x8': 8, 's0': 8,
            'x9': 9, 's1': 9,
            'x10': 10, 'a0': 10,
            'x11': 11, 'a1': 11,
            'x12': 12, 'a2': 12,
            'x13': 13, 'a3': 13,
            'x14': 14, 'a4': 14,
            'x15': 15, 'a7': 15
        }
    
    def assemble_file(self, filename: str) -> List[int]:
        """
        Κύρια συνάρτηση: διαβάζει αρχείο .asm και επιστρέφει machine code
        
        Args:
            filename (str): Όνομα αρχείου .asm
            
        Returns:
            List[int]: Λίστα με 16-bit εντολές
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            print(f"📂 Assembling file: {filename}")
            print(f"📝 Lines: {len(lines)}")
            
            return self._assemble_lines(lines)
            
        except FileNotFoundError:
            print(f"❌ File {filename} not found!")
            return []
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return []
    
    def _assemble_lines(self, lines: List[str]) -> List[int]:
        """
        Κύρια διαδικασία assembling
        
        Args:
            lines (List[str]): Γραμμές κώδικα
            
        Returns:
            List[int]: Machine code
        """
        self.labels = {}
        self.instructions = []
        self.machine_code = []
        
        # Pass 1: Εύρεση labels
        print("\n🔍 Pass 1: Finding labels...")
        self._find_labels(lines)
        
        # Pass 2: Μετατροπή σε machine code
        print("\n🔧 Pass 2: Converting to machine code...")
        self._convert_to_machine_code(lines)
        
        return self.machine_code
    
    def _find_labels(self, lines: List[str]):
        """Πρώτο πέρασμα: βρίσκει labels"""
        address = 0
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            
            # Αγνοούμε κενές γραμμές και comments
            if not line or line.startswith('#'):
                continue
            
            # Αν έχει label (τελειώνει με :)
            if ':' in line:
                parts = line.split(':', 1)
                label = parts[0].strip()
                self.labels[label] = address
                print(f"   📌 Label '{label}' at address {address}")
                
                # Αν έχει εντολή στην ίδια γραμμή
                if len(parts) > 1 and parts[1].strip():
                    address += 1
            else:
                # Κανονική εντολή
                address += 1
    
    def _convert_to_machine_code(self, lines: List[str]):
        """Δεύτερο πέρασμα: μετατροπή σε machine code"""
        address = 0
        
        for line_num, line in enumerate(lines):
            original_line = line.strip()
            
            # Αγνοούμε κενές γραμμές και comments
            if not original_line or original_line.startswith('#'):
                continue
            
            # Αφαιρούμε label αν υπάρχει
            if ':' in original_line:
                parts = original_line.split(':', 1)
                if len(parts) > 1:
                    line = parts[1].strip()
                else:
                    continue
            else:
                line = original_line
            
            # Αν δεν έχει εντολή, συνεχίζουμε
            if not line:
                continue
            
            # Αφαιρούμε comment από τη γραμμή
            if '#' in line:
                line = line.split('#')[0].strip()
            
            # Parsing εντολής
            try:
                instruction = self._parse_instruction(line, address)
                if instruction is not None:
                    self.machine_code.append(instruction)
                    print(f"   📄 {address:02d}: {original_line:<20} → 0x{instruction:04X}")
                    address += 1
                else:
                    print(f"   ❌ Line {line_num+1}: Unknown instruction '{line}'")
            except Exception as e:
                print(f"   ❌ Line {line_num+1}: Error '{e}'")
    
    def _parse_instruction(self, line: str, address: int) -> Optional[int]:
        """Αναλύει μια εντολή και επιστρέφει machine code"""
        parts = line.upper().replace(',', '').split()
        
        if not parts:
            return None
        
        opcode_str = parts[0]
        
        if opcode_str not in self.opcodes:
            return None
        
        opcode = self.opcodes[opcode_str]
        
        # R-Type: ADD rd, rs1, rs2
        if opcode_str in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
            if len(parts) != 4:
                raise ValueError(f"R-type needs 3 registers: {line}")
            
            rd = self._parse_register(parts[1])
            rs1 = self._parse_register(parts[2])
            rs2 = self._parse_register(parts[3])
            
            return self._encode_r_type(opcode, rd, rs1, rs2)
        
        # I-Type: ADDI rd, rs1, imm
        elif opcode_str in ['ADDI', 'ANDI', 'ORI']:
            if len(parts) != 4:
                raise ValueError(f"I-type needs 2 registers + immediate: {line}")
            
            rd = self._parse_register(parts[1])
            rs1 = self._parse_register(parts[2])
            raw_imm = self._parse_integer(parts[3])

            if opcode_str == 'ADDI' and raw_imm < 0:
                imm = self._encode_negative_addi_immediate(raw_imm)
                return self._encode_i_type(0xD, rd, rs1, imm)

            imm = self._parse_immediate(parts[3])
            
            return self._encode_i_type(opcode, rd, rs1, imm)
        
        # Load: LW rd, offset(rs1)
        elif opcode_str == 'LW':
            if len(parts) != 3:
                raise ValueError(f"LW needs rd, offset(rs1): {line}")
            
            rd = self._parse_register(parts[1])
            offset, rs1 = self._parse_memory_operand(parts[2])
            
            return self._encode_i_type(opcode, rd, rs1, offset)
        
        # Store: SW rs2, offset(rs1)
        elif opcode_str == 'SW':
            if len(parts) != 3:
                raise ValueError(f"SW needs rs2, offset(rs1): {line}")
            
            rs2 = self._parse_register(parts[1])
            offset, rs1 = self._parse_memory_operand(parts[2])
            
            return self._encode_s_type(opcode, rs2, rs1, offset)
        
        # Branch: BEQ rs1, rs2, label
        elif opcode_str in ['BEQ', 'BNE']:
            if len(parts) != 4:
                raise ValueError(f"Branch needs 2 registers + label: {line}")
            
            rs1 = self._parse_register(parts[1])
            rs2 = self._parse_register(parts[2])
            offset = self._parse_branch_target(parts[3], address)
            
            return self._encode_b_type(opcode, rs1, rs2, offset)
        
        # Jump: JAL rd, label
        elif opcode_str == 'JAL':
            if len(parts) != 3:
                raise ValueError(f"JAL needs rd, label: {line}")
            
            rd = self._parse_register(parts[1])
            offset = self._parse_jump_target(parts[2], address)
            
            return self._encode_j_type(opcode, rd, offset)
        
        # Special: NOP, HALT
        elif opcode_str in ['NOP', 'HALT']:
            return opcode << 12  # Μόνο opcode
        
        return None
    
    def _parse_register(self, reg_str: str) -> int:
        """Μετατρέπει register string σε αριθμό"""
        reg_str = reg_str.lower()
        
        if reg_str in self.register_map:
            return self.register_map[reg_str]
        
        raise ValueError(f"Unknown register: {reg_str}")
    
    def _parse_immediate(self, imm_str: str) -> int:
        """Μετατρέπει immediate value με proper sign handling"""
        try:
            return self._parse_integer(imm_str) & 0xF
            
        except ValueError:
            raise ValueError(f"Invalid immediate value: {imm_str}")

    def _parse_integer(self, value_str: str) -> int:
        """Parse decimal or hex integer strings, preserving sign."""
        value_str = value_str.strip().lower()

        if value_str.startswith('-0x'):
            return -int(value_str[3:], 16)
        if value_str.startswith('0x'):
            return int(value_str, 16)
        return int(value_str)

    def _encode_negative_addi_immediate(self, immediate: int) -> int:
        """Encode ADDI with a negative immediate as internal SUBI."""
        magnitude = abs(immediate)
        if magnitude > 0xF:
            raise ValueError(f"Negative ADDI immediate out of range: {immediate}")
        return magnitude
    
    def _parse_memory_operand(self, operand: str) -> Tuple[int, int]:
        """Αναλύει memory operand όπως: 4(x2) ή (x2)"""
        if '(' not in operand:
            raise ValueError(f"Invalid memory format: {operand}")
        
        parts = operand.split('(')
        offset_str = parts[0] if parts[0] else '0'
        reg_str = parts[1].rstrip(')')
        
        offset = int(offset_str) & 0xF  # 4-bit offset
        rs1 = self._parse_register(reg_str)
        
        return offset, rs1
    
    def _parse_branch_target(self, target: str, current_addr: int) -> int:
        """Αναλύει branch target (label ή offset) για B-type (4-bit)

        Συντονισμένο με την υλοποίηση CPU όπου το PC ενημερώνεται ως
        pc = pc + offset (και παρακάμπτεται το αυτόματο increment στον ίδιο κύκλο).
        Άρα offset = target_addr - current_addr.
        """
        target = target.lower()

        if target in self.labels:
            target_addr = self.labels[target]
            offset = (target_addr - current_addr) & 0xF
            return offset
        else:
            return int(target) & 0xF

    def _parse_jump_target(self, target: str, current_addr: int) -> int:
        """Αναλύει jump target (label ή offset) για J-type (8-bit)"""
        t = target.lower()
        if t in self.labels:
            target_addr = self.labels[t]
            return (target_addr - current_addr) & 0xFF
        return int(target) & 0xFF
    
    def _encode_r_type(self, opcode: int, rd: int, rs1: int, rs2: int) -> int:
        """Κωδικοποίηση R-type: [4-bit opcode][4-bit rd][4-bit rs1][4-bit rs2]"""
        return (opcode << 12) | (rd << 8) | (rs1 << 4) | rs2
    
    def _encode_i_type(self, opcode: int, rd: int, rs1: int, imm: int) -> int:
        """Κωδικοποίηση I-type: [4-bit opcode][4-bit rd][4-bit rs1][4-bit imm]"""
        return (opcode << 12) | (rd << 8) | (rs1 << 4) | (imm & 0xF)
    
    def _encode_s_type(self, opcode: int, rs2: int, rs1: int, imm: int) -> int:
        """Κωδικοποίηση S-type: [4-bit opcode][4-bit rs2][4-bit rs1][4-bit imm]"""
        return (opcode << 12) | (rs2 << 8) | (rs1 << 4) | (imm & 0xF)
    
    def _encode_b_type(self, opcode: int, rs1: int, rs2: int, offset: int) -> int:
        """Κωδικοποίηση B-type: [4-bit opcode][4-bit rs1][4-bit rs2][4-bit offset]"""
        return (opcode << 12) | (rs1 << 8) | (rs2 << 4) | (offset & 0xF)
    
    def _encode_j_type(self, opcode: int, rd: int, offset: int) -> int:
        """Κωδικοποίηση J-type: [4-bit opcode][4-bit rd][8-bit offset]"""
        return (opcode << 12) | (rd << 8) | (offset & 0xFF)
    
    def save_binary_file(self, filename: str) -> bool:
        """Αποθηκεύει το machine code σε binary αρχείο"""
        try:
            with open(filename, 'wb') as f:
                for instruction in self.machine_code:
                    f.write(instruction.to_bytes(2, byteorder='little'))
            
            print(f"💾 Binary file saved: {filename}")
            print(f"📊 Size: {len(self.machine_code) * 2} bytes ({len(self.machine_code)} instructions)")
            return True
            
        except Exception as e:
            print(f"❌ Error saving binary: {e}")
            return False
    
    def save_hex_file(self, filename: str) -> bool:
        """Αποθηκεύει το machine code σε hex αρχείο"""
        try:
            with open(filename, 'w') as f:
                f.write("# Machine Code - Hex Format\n")
                f.write("# Address: Instruction (Binary)\n")
                f.write("#" + "-"*40 + "\n")
                
                for i, instruction in enumerate(self.machine_code):
                    f.write(f"{i:04X}: {instruction:04X} ({instruction:016b})\n")
            
            print(f"📄 Hex file saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving hex: {e}")
            return False
    
    def display_summary(self):
        """Εμφανίζει σύνοψη assembly"""
        print("\n" + "="*60)
        print("📊 ASSEMBLY SUMMARY")
        print("="*60)
        
        if self.labels:
            print(f"\n📌 LABELS ({len(self.labels)}):")
            for label, addr in self.labels.items():
                print(f"   {label}: {addr}")
        
        if self.machine_code:
            print(f"\n💾 MACHINE CODE ({len(self.machine_code)} instructions):")
            for i, code in enumerate(self.machine_code):
                print(f"   {i:02d}: 0x{code:04X} ({code:016b})")
        
        print("="*60)


class BinaryLoader:
    """Φορτώνει binary αρχεία που δημιουργήθηκαν από τον Assembler"""
    
    @staticmethod
    def load_binary_file(filename: str) -> List[int]:
        """Φορτώνει binary αρχείο"""
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            
            instructions = []
            for i in range(0, len(data), 2):
                if i + 1 < len(data):
                    instruction = int.from_bytes(data[i:i+2], byteorder='little')
                    instructions.append(instruction)
            
            print(f"📂 Loaded binary file: {filename}")
            print(f"📊 Size: {len(data)} bytes ({len(instructions)} instructions)")
            
            return instructions
            
        except FileNotFoundError:
            print(f"❌ Binary file {filename} not found!")
            return []
        except Exception as e:
            print(f"❌ Error loading binary: {e}")
            return []
    
    @staticmethod
    def display_binary_content(instructions: List[int]):
        """Εμφανίζει το περιεχόμενο του binary αρχείου"""
        print("\n" + "="*50)
        print("📊 BINARY FILE CONTENT")
        print("="*50)
        
        for i, instruction in enumerate(instructions):
            print(f"   {i:02d}: 0x{instruction:04X} ({instruction:016b})")
        
        print("="*50)


# Κύρια συνάρτηση για command line χρήση
def main():
    """Κύρια συνάρτηση για χρήση από command line"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python Assembler.py <input.asm> [output_prefix]")
        print("Example: python Assembler.py program.asm program")
        return
    
    input_file = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.asm', '')
    
    # Δημιουργία assembler
    assembler = RiscVAssembler()
    
    # Assembly
    machine_code = assembler.assemble_file(input_file)
    
    if not machine_code:
        print("❌ Assembly failed!")
        return
    
    # Εμφάνιση summary
    assembler.display_summary()
    
    # Αποθήκευση αρχείων
    print("\n🔧 Saving output files...")
    assembler.save_binary_file(f"{output_prefix}.bin")
    assembler.save_hex_file(f"{output_prefix}.hex")
    
    print(f"\n✅ Assembly complete!")
    print(f"📁 Files generated:")
    print(f"   - {output_prefix}.bin (binary machine code)")
    print(f"   - {output_prefix}.hex (hex machine code)")


if __name__ == "__main__":
    main()
