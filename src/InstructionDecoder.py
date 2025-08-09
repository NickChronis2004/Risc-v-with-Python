
from typing import Dict, Optional, Any


class InstructionDecoder:
    """
    Instruction Decoder για RISC-V 16-bit processor
    
    Αποκωδικοποιεί 16-bit binary instructions σε structured format
    Υποστηρίζει όλους τους τύπους εντολών: R, I, S, B, J, Special
    """
    
    def __init__(self):
        """Αρχικοποίηση InstructionDecoder"""
        
        # Instruction Set Architecture - Κεντρικός πίνακας εντολών
        self.isa_table = {
            # R-Type Instructions (Register-Register)
            0x0: {"name": "ADD",  "type": "R", "description": "Add"},
            0x1: {"name": "SUB",  "type": "R", "description": "Subtract"},
            0x2: {"name": "AND",  "type": "R", "description": "Bitwise AND"},
            0x3: {"name": "OR",   "type": "R", "description": "Bitwise OR"},
            0x4: {"name": "XOR",  "type": "R", "description": "Bitwise XOR"},
            
            # I-Type Instructions (Immediate)
            0x5: {"name": "ADDI", "type": "I", "description": "Add Immediate"},
            0x6: {"name": "ANDI", "type": "I", "description": "AND Immediate"},
            0x7: {"name": "ORI",  "type": "I", "description": "OR Immediate"},
            0x8: {"name": "LW",   "type": "I", "description": "Load Word"},
            
            # S-Type Instructions (Store)
            0x9: {"name": "SW",   "type": "S", "description": "Store Word"},
            
            # B-Type Instructions (Branch)
            0xA: {"name": "BEQ",  "type": "B", "description": "Branch if Equal"},
            0xB: {"name": "BNE",  "type": "B", "description": "Branch if Not Equal"},
            
            # J-Type Instructions (Jump)
            0xC: {"name": "JAL",  "type": "J", "description": "Jump and Link"},
            
            # Special Instructions
            0xE: {"name": "NOP",  "type": "Special", "description": "No Operation"},
            0xF: {"name": "HALT", "type": "Special", "description": "Halt Execution"}
        }
        
        # Statistics
        self.decode_count = 0
        self.decode_history = []
    
    def decode(self, instruction: int) -> Dict[str, Any]:
        """
        Κύρια συνάρτηση αποκωδικοποίησης
        
        Args:
            instruction (int): 16-bit binary instruction
            
        Returns:
            Dict: Structured instruction data
        """
        self.decode_count += 1
        
        # Ensure 16-bit
        instruction = instruction & 0xFFFF
        
        # Extract opcode (bits 15-12)
        opcode = (instruction >> 12) & 0xF
        
        # Check if instruction exists
        if opcode not in self.isa_table:
            return self._create_invalid_instruction(instruction, opcode)
        
        # Get instruction info
        inst_info = self.isa_table[opcode]
        
        # Decode based on type
        if inst_info["type"] == "R":
            decoded = self._decode_r_type(instruction, opcode, inst_info)
        elif inst_info["type"] == "I":
            decoded = self._decode_i_type(instruction, opcode, inst_info)
        elif inst_info["type"] == "S":
            decoded = self._decode_s_type(instruction, opcode, inst_info)
        elif inst_info["type"] == "B":
            decoded = self._decode_b_type(instruction, opcode, inst_info)
        elif inst_info["type"] == "J":
            decoded = self._decode_j_type(instruction, opcode, inst_info)
        elif inst_info["type"] == "Special":
            decoded = self._decode_special_type(instruction, opcode, inst_info)
        else:
            decoded = self._create_invalid_instruction(instruction, opcode)
        
        # Add to history
        self.decode_history.append(decoded)
        
        return decoded
    
    def _decode_r_type(self, instruction: int, opcode: int, inst_info: Dict) -> Dict[str, Any]:
        """
        Decode R-Type instruction: [opcode][rd][rs1][rs2]
        Format: ADD rd, rs1, rs2
        """
        rd  = (instruction >> 8) & 0xF   # Bits 11-8: Destination register
        rs1 = (instruction >> 4) & 0xF   # Bits 7-4:  Source register 1
        rs2 = instruction & 0xF          # Bits 3-0:  Source register 2
        
        return {
            "type": "R",
            "opcode": opcode,
            "instruction_name": inst_info["name"],
            "description": inst_info["description"],
            "rd": rd,
            "rs1": rs1,
            "rs2": rs2,
            "immediate": None,
            "offset": None,
            "raw_instruction": instruction,
            "assembly": f"{inst_info['name'].lower()} x{rd}, x{rs1}, x{rs2}",
            "valid": True
        }
    
    def _decode_i_type(self, instruction: int, opcode: int, inst_info: Dict) -> Dict[str, Any]:
        """
        Decode I-Type instruction: [opcode][rd][rs1][imm]
        Format: ADDI rd, rs1, imm OR LW rd, offset(rs1)
        """
        rd  = (instruction >> 8) & 0xF   # Bits 11-8: Destination register
        rs1 = (instruction >> 4) & 0xF   # Bits 7-4:  Source register 1
        imm = instruction & 0xF          # Bits 3-0:  Immediate value (4-bit)
        
        # For this ISA subset:
        # - ADDI/ANDI/ORI use unsigned 4-bit immediates (0..15)
        # - LW encodes offset in imm, also treated as unsigned (0..15)
        inst_name = inst_info['name']
        final_imm = imm
            
        # Different assembly format for LW
        if inst_info["name"] == "LW":
            assembly = f"lw x{rd}, {final_imm}(x{rs1})"
            offset = final_imm
        else:
            assembly = f"{inst_info['name'].lower()} x{rd}, x{rs1}, {final_imm}"
            offset = None
        
        return {
            "type": "I",
            "opcode": opcode,
            "instruction_name": inst_info["name"],
            "description": inst_info["description"],
            "rd": rd,
            "rs1": rs1,
            "rs2": None,
            "immediate": final_imm,
            "offset": offset,
            "raw_instruction": instruction,
            "assembly": assembly,
            "valid": True
        }
        
    def _decode_s_type(self, instruction: int, opcode: int, inst_info: Dict) -> Dict[str, Any]:
        """
        Decode S-Type instruction: [opcode][rs2][rs1][imm]
        Format: SW rs2, offset(rs1)
        """
        rs2 = (instruction >> 8) & 0xF   # Bits 11-8: Source register 2 (data)
        rs1 = (instruction >> 4) & 0xF   # Bits 7-4:  Source register 1 (address)
        imm = instruction & 0xF          # Bits 3-0:  Offset (4-bit)
        
        # For SW operations, treat offset as unsigned (0-15)
        # SW is used for array indexing, not relative addressing
        signed_offset = imm  # Keep as unsigned (0-15)
        
        assembly = f"sw x{rs2}, {signed_offset}(x{rs1})"
        
        return {
            "type": "S",
            "opcode": opcode,
            "instruction_name": inst_info["name"],
            "description": inst_info["description"],
            "rd": None,
            "rs1": rs1,
            "rs2": rs2,
            "immediate": None,
            "offset": signed_offset,
            "raw_instruction": instruction,
            "assembly": assembly,
            "valid": True
        }
    
    def _decode_b_type(self, instruction: int, opcode: int, inst_info: Dict) -> Dict[str, Any]:
        """
        Decode B-Type instruction: [opcode][rs1][rs2][offset]
        Format: BEQ rs1, rs2, offset
        """
        rs1    = (instruction >> 8) & 0xF   # Bits 11-8: Source register 1
        rs2    = (instruction >> 4) & 0xF   # Bits 7-4:  Source register 2
        offset = instruction & 0xF          # Bits 3-0:  Branch offset
        
        # Handle signed offset
        if offset & 0x8:
            signed_offset = offset - 16
        else:
            signed_offset = offset
        
        assembly = f"{inst_info['name'].lower()} x{rs1}, x{rs2}, {signed_offset}"
        
        return {
            "type": "B",
            "opcode": opcode,
            "instruction_name": inst_info["name"],
            "description": inst_info["description"],
            "rd": None,
            "rs1": rs1,
            "rs2": rs2,
            "immediate": None,
            "offset": signed_offset,
            "raw_instruction": instruction,
            "assembly": assembly,
            "valid": True
        }
    
    def _decode_j_type(self, instruction: int, opcode: int, inst_info: Dict) -> Dict[str, Any]:
        """
        Decode J-Type instruction: [opcode][rd][offset]
        Format: JAL rd, offset
        """
        rd     = (instruction >> 8) & 0xF   # Bits 11-8: Destination register
        offset = instruction & 0xFF         # Bits 7-0:  Jump offset (8-bit)
        
        # Handle signed offset (8-bit signed: -128 to +127)
        if offset & 0x80:
            signed_offset = offset - 256
        else:
            signed_offset = offset
        
        assembly = f"jal x{rd}, {signed_offset}"
        
        return {
            "type": "J",
            "opcode": opcode,
            "instruction_name": inst_info["name"],
            "description": inst_info["description"],
            "rd": rd,
            "rs1": None,
            "rs2": None,
            "immediate": None,
            "offset": signed_offset,
            "raw_instruction": instruction,
            "assembly": assembly,
            "valid": True
        }
    
    def _decode_special_type(self, instruction: int, opcode: int, inst_info: Dict) -> Dict[str, Any]:
        """
        Decode Special instructions: NOP, HALT
        """
        assembly = inst_info["name"].lower()
        
        return {
            "type": "Special",
            "opcode": opcode,
            "instruction_name": inst_info["name"],
            "description": inst_info["description"],
            "rd": None,
            "rs1": None,
            "rs2": None,
            "immediate": None,
            "offset": None,
            "raw_instruction": instruction,
            "assembly": assembly,
            "valid": True
        }
    
    def _create_invalid_instruction(self, instruction: int, opcode: int) -> Dict[str, Any]:
        """Create structure for invalid/unknown instructions"""
        return {
            "type": "Invalid",
            "opcode": opcode,
            "instruction_name": "UNKNOWN",
            "description": f"Unknown instruction with opcode 0x{opcode:X}",
            "rd": None,
            "rs1": None,
            "rs2": None,
            "immediate": None,
            "offset": None,
            "raw_instruction": instruction,
            "assembly": f"unknown 0x{instruction:04X}",
            "valid": False
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get decoder statistics"""
        return {
            "total_decoded": self.decode_count,
            "history_size": len(self.decode_history)
        }
    
    def display_instruction_set(self):
        """Display supported instruction set"""
        print("\n" + "="*60)
        print("📋 SUPPORTED INSTRUCTION SET")
        print("="*60)
        
        by_type = {}
        for opcode, info in self.isa_table.items():
            inst_type = info["type"]
            if inst_type not in by_type:
                by_type[inst_type] = []
            by_type[inst_type].append((opcode, info))
        
        for inst_type, instructions in by_type.items():
            print(f"\n📌 {inst_type}-Type Instructions:")
            for opcode, info in instructions:
                print(f"   0x{opcode:X}: {info['name']:<4} - {info['description']}")
        
        print("="*60)
    
    def display_decode_history(self, last_n=5):
        """Display recent decode history"""
        print("\n" + "="*70)
        print("🕒 DECODE HISTORY")
        print("="*70)
        
        history_to_show = self.decode_history[-last_n:] if len(self.decode_history) > last_n else self.decode_history
        
        if not history_to_show:
            print("No instructions decoded yet.")
            return
        
        print("Raw      | Type | Name | Assembly")
        print("-"*40)
        
        for decoded in history_to_show:
            raw = decoded["raw_instruction"]
            inst_type = decoded["type"]
            name = decoded["instruction_name"]
            assembly = decoded["assembly"]
            
            print(f"0x{raw:04X}   | {inst_type:<4} | {name:<4} | {assembly}")
        
        print("="*70)


def demo_instruction_decoder():
    """Demo του InstructionDecoder"""
    print("🧠 InstructionDecoder Demo")
    print("="*40)
    
    decoder = InstructionDecoder()
    
    # Show supported instructions
    decoder.display_instruction_set()
    
    # Test instructions from our assembler
    test_instructions = [
        (0x510A, "ADDI x1, x0, 10"),
        (0x5205, "ADDI x2, x0, 5"),
        (0x0312, "ADD x3, x1, x2"),
        (0x1412, "SUB x4, x1, x2"),
        (0x9320, "SW x3, 0(x2)"),
        (0x8420, "LW x4, 0(x2)"),
        (0xA341, "BEQ x3, x4, 1"),
        (0xE000, "NOP"),
        (0xF000, "HALT"),
        (0xD000, "Invalid instruction")  # Unknown opcode
    ]
    
    print(f"\n🔍 Decoding {len(test_instructions)} test instructions:")
    print("="*70)
    print("Raw      | Expected          | Decoded")
    print("-"*70)
    
    for raw_inst, expected in test_instructions:
        decoded = decoder.decode(raw_inst)
        
        status = "✅" if decoded["valid"] else "❌"
        print(f"0x{raw_inst:04X}   | {expected:<17} | {decoded['assembly']} {status}")
    
    # Show decode history
    decoder.display_decode_history()
    
    # Show statistics
    stats = decoder.get_statistics()
    print(f"\n📊 Decoder Statistics:")
    print(f"   Total decoded: {stats['total_decoded']}")
    print(f"   History size: {stats['history_size']}")


if __name__ == "__main__":
    demo_instruction_decoder()