
from typing import Dict, Any, Optional
from ALU import ALU


class ControlUnit:
    """
    Control Unit for RISC-V 16-bit processor
    
    Takes decoded instructions and generates control signals
    for all components (ALU, Memory, RegisterFile, PC)
    """
    
    def __init__(self):
        """Initialize ControlUnit"""
        
        # Control signal statistics
        self.signal_count = 0
        self.signal_history = []
        
        # Control signal lookup table - The "heart" of the ControlUnit
        self.control_table = {
            # R-Type Instructions (Register-Register operations)
            "ADD": {
                "alu_operation": ALU.ALU_ADD,
                "alu_src_a": "register",      # ALU input A from register
                "alu_src_b": "register",      # ALU input B from register  
                "reg_write_enable": True,     # Write to destination register
                "reg_write_src": "alu",       # Data from ALU
                "mem_read": False,            # Don't read memory
                "mem_write": False,           # Don't write memory
                "branch": False,              # Not a branch instruction
                "jump": False,                # Not a jump instruction
                "pc_update": "increment"      # PC = PC + 1
            },
            "SUB": {
                "alu_operation": ALU.ALU_SUB,
                "alu_src_a": "register",
                "alu_src_b": "register",
                "reg_write_enable": True,
                "reg_write_src": "alu",
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "increment"
            },
            "AND": {
                "alu_operation": ALU.ALU_AND,
                "alu_src_a": "register",
                "alu_src_b": "register",
                "reg_write_enable": True,
                "reg_write_src": "alu",
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "increment"
            },
            "OR": {
                "alu_operation": ALU.ALU_OR,
                "alu_src_a": "register",
                "alu_src_b": "register",
                "reg_write_enable": True,
                "reg_write_src": "alu",
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "increment"
            },
            "XOR": {
                "alu_operation": ALU.ALU_XOR,
                "alu_src_a": "register",
                "alu_src_b": "register",
                "reg_write_enable": True,
                "reg_write_src": "alu",
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "increment"
            },
            
            # I-Type Instructions (Immediate operations)
            "ADDI": {
                "alu_operation": ALU.ALU_ADD,
                "alu_src_a": "register",      # rs1
                "alu_src_b": "immediate",     # immediate value
                "reg_write_enable": True,
                "reg_write_src": "alu",
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "increment"
            },
            "ANDI": {
                "alu_operation": ALU.ALU_AND,
                "alu_src_a": "register",
                "alu_src_b": "immediate",
                "reg_write_enable": True,
                "reg_write_src": "alu",
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "increment"
            },
            "ORI": {
                "alu_operation": ALU.ALU_OR,
                "alu_src_a": "register",
                "alu_src_b": "immediate",
                "reg_write_enable": True,
                "reg_write_src": "alu",
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "increment"
            },
            "LW": {
                "alu_operation": ALU.ALU_ADD,  # Calculate address: rs1 + offset
                "alu_src_a": "register",       # rs1 (base address)
                "alu_src_b": "immediate",      # offset
                "reg_write_enable": True,      # Write loaded data to rd
                "reg_write_src": "memory",     # Data from memory
                "mem_read": True,              # Read from memory
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "increment"
            },
            
            # S-Type Instructions (Store operations)
            "SW": {
                "alu_operation": ALU.ALU_ADD,  # Calculate address: rs1 + offset
                "alu_src_a": "register",       # rs1 (base address)
                "alu_src_b": "immediate",      # offset
                "reg_write_enable": False,     # Don't write to register
                "reg_write_src": None,
                "mem_read": False,
                "mem_write": True,             # Write to memory
                "branch": False,
                "jump": False,
                "pc_update": "increment"
            },
            
            # B-Type Instructions (Branch operations)
            "BEQ": {
                "alu_operation": ALU.ALU_EQ,   # Compare rs1 == rs2
                "alu_src_a": "register",       # rs1
                "alu_src_b": "register",       # rs2
                "reg_write_enable": False,     # Don't write to register
                "reg_write_src": None,
                "mem_read": False,
                "mem_write": False,
                "branch": True,                # This is a branch
                "jump": False,
                "pc_update": "conditional"     # PC depends on branch condition
            },
            "BNE": {
                "alu_operation": ALU.ALU_NE,   # Compare rs1 != rs2
                "alu_src_a": "register",       # rs1
                "alu_src_b": "register",       # rs2
                "reg_write_enable": False,
                "reg_write_src": None,
                "mem_read": False,
                "mem_write": False,
                "branch": True,
                "jump": False,
                "pc_update": "conditional"
            },
            
            # J-Type Instructions (Jump operations)
            "JAL": {
                "alu_operation": None,         # No ALU operation needed
                "alu_src_a": None,
                "alu_src_b": None,
                "reg_write_enable": True,      # Save return address
                "reg_write_src": "pc_plus_1",  # rd = PC + 1
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": True,                  # This is a jump
                "pc_update": "jump"            # PC = PC + offset
            },
            
            # Special Instructions
            "NOP": {
                "alu_operation": None,         # No operation
                "alu_src_a": None,
                "alu_src_b": None,
                "reg_write_enable": False,     # No register write
                "reg_write_src": None,
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "increment"       # Just increment PC
            },
            "HALT": {
                "alu_operation": None,
                "alu_src_a": None,
                "alu_src_b": None,
                "reg_write_enable": False,
                "reg_write_src": None,
                "mem_read": False,
                "mem_write": False,
                "branch": False,
                "jump": False,
                "pc_update": "halt"            # Stop execution
            }
        }
    
    def generate_control_signals(self, decoded_instruction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate control signals for a decoded instruction
        
        Args:
            decoded_instruction: Output from InstructionDecoder
            
        Returns:
            Dict: Control signals for all processor components
        """
        self.signal_count += 1
        
        if not decoded_instruction.get("valid", False):
            return self._generate_error_signals(decoded_instruction)
        
        instruction_name = decoded_instruction.get("instruction_name")
        
        if instruction_name not in self.control_table:
            return self._generate_error_signals(decoded_instruction)
        
        # Get base control signals from lookup table
        base_signals = self.control_table[instruction_name].copy()
        
        # Add instruction-specific information
        control_signals = {
            **base_signals,
            "instruction": decoded_instruction,
            "valid": True,
            "error": False
        }
        
        # Log this control signal generation
        self.signal_history.append({
            "count": self.signal_count,
            "instruction_name": instruction_name,
            "pc_update": base_signals.get("pc_update"),
            "mem_operation": self._get_memory_operation(base_signals),
            "reg_write": base_signals.get("reg_write_enable", False)
        })
        
        # Keep only last 10 entries
        if len(self.signal_history) > 10:
            self.signal_history.pop(0)
        
        return control_signals
    
    def _generate_error_signals(self, decoded_instruction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate safe control signals for invalid instructions"""
        return {
            "alu_operation": None,
            "alu_src_a": None,
            "alu_src_b": None,
            "reg_write_enable": False,
            "reg_write_src": None,
            "mem_read": False,
            "mem_write": False,
            "branch": False,
            "jump": False,
            "pc_update": "increment",  # Just move to next instruction
            "instruction": decoded_instruction,
            "valid": False,
            "error": True
        }
    
    def _get_memory_operation(self, signals: Dict[str, Any]) -> str:
        """Get string description of memory operation"""
        if signals.get("mem_read"):
            return "READ"
        elif signals.get("mem_write"):
            return "WRITE"
        else:
            return "NONE"
    
    def is_branch_instruction(self, control_signals: Dict[str, Any]) -> bool:
        """Check if instruction is a branch"""
        return control_signals.get("branch", False)
    
    def is_jump_instruction(self, control_signals: Dict[str, Any]) -> bool:
        """Check if instruction is a jump"""
        return control_signals.get("jump", False)
    
    def is_memory_instruction(self, control_signals: Dict[str, Any]) -> bool:
        """Check if instruction accesses memory"""
        return (control_signals.get("mem_read", False) or 
                control_signals.get("mem_write", False))
    
    def should_halt(self, control_signals: Dict[str, Any]) -> bool:
        """Check if execution should halt"""
        return control_signals.get("pc_update") == "halt"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get control unit statistics"""
        return {
            "total_signals_generated": self.signal_count,
            "history_size": len(self.signal_history)
        }
    
    def display_control_table(self):
        """Display the complete control table"""
        print("\n" + "="*80)
        print("🎛️  CONTROL UNIT LOOKUP TABLE")
        print("="*80)
        
        # Group by instruction type
        by_type = {}
        for inst_name, signals in self.control_table.items():
            # Determine type based on signals
            if signals.get("branch"):
                inst_type = "B-Type (Branch)"
            elif signals.get("jump"):
                inst_type = "J-Type (Jump)"
            elif signals.get("mem_read"):
                inst_type = "I-Type (Load)"
            elif signals.get("mem_write"):
                inst_type = "S-Type (Store)"
            elif signals.get("alu_src_b") == "immediate":
                inst_type = "I-Type (Immediate)"
            elif signals.get("alu_operation") is not None:
                inst_type = "R-Type (Register)"
            else:
                inst_type = "Special"
            
            if inst_type not in by_type:
                by_type[inst_type] = []
            by_type[inst_type].append((inst_name, signals))
        
        # Display each type
        for inst_type, instructions in by_type.items():
            print(f"\n📋 {inst_type}:")
            print("-" * 60)
            print("Instruction | ALU Op | Reg Write | Mem | PC Update")
            print("-" * 60)
            
            for inst_name, signals in instructions:
                alu_op = str(signals.get("alu_operation", "None"))[-7:]  # Last 7 chars
                reg_write = "✓" if signals.get("reg_write_enable") else "✗"
                mem_op = self._get_memory_operation(signals)
                pc_update = signals.get("pc_update", "unknown")
                
                print(f"{inst_name:<11} | {alu_op:<6} | {reg_write:<9} | {mem_op:<3} | {pc_update}")
        
        print("="*80)
    
    def display_signal_history(self, last_n=5):
        """Display recent control signal history"""
        print("\n" + "="*60)
        print("🕒 CONTROL SIGNAL HISTORY")
        print("="*60)
        
        history_to_show = self.signal_history[-last_n:] if len(self.signal_history) > last_n else self.signal_history
        
        if not history_to_show:
            print("No control signals generated yet.")
            return
        
        print("Count | Instruction | PC Update   | Memory | Reg Write")
        print("-" * 55)
        
        for entry in history_to_show:
            count = entry["count"]
            inst = entry["instruction_name"]
            pc_update = entry["pc_update"]
            mem_op = entry["mem_operation"]
            reg_write = "✓" if entry["reg_write"] else "✗"
            
            print(f"{count:<5} | {inst:<11} | {pc_update:<11} | {mem_op:<6} | {reg_write}")
        
        print("="*60)


def demo_control_unit():
    """Demo of ControlUnit functionality"""
    print("🎛️  ControlUnit Demo")
    print("="*40)
    
    control_unit = ControlUnit()
    
    # Show the control table
    control_unit.display_control_table()
    
    # Test with mock decoded instructions
    print(f"\n🧪 Testing Control Signal Generation:")
    print("="*70)
    
    test_instructions = [
        {
            "type": "R", "instruction_name": "ADD", "rd": 3, "rs1": 1, "rs2": 2, 
            "valid": True, "assembly": "add x3, x1, x2"
        },
        {
            "type": "I", "instruction_name": "ADDI", "rd": 1, "rs1": 0, "immediate": 10,
            "valid": True, "assembly": "addi x1, x0, 10"
        },
        {
            "type": "I", "instruction_name": "LW", "rd": 4, "rs1": 2, "offset": 0,
            "valid": True, "assembly": "lw x4, 0(x2)"
        },
        {
            "type": "B", "instruction_name": "BEQ", "rs1": 3, "rs2": 4, "offset": 2,
            "valid": True, "assembly": "beq x3, x4, 2"
        },
        {
            "type": "Special", "instruction_name": "HALT", "valid": True, "assembly": "halt"
        },
        {
            "type": "Invalid", "instruction_name": "UNKNOWN", "valid": False, "assembly": "unknown"
        }
    ]
    
    print("Assembly          | ALU Op | RegWr | MemR | MemW | Branch | Jump | PC Update")
    print("-" * 75)
    
    for decoded in test_instructions:
        signals = control_unit.generate_control_signals(decoded)
        
        assembly = decoded["assembly"]
        alu_op = str(signals.get("alu_operation", "None"))[-3:]
        reg_write = "✓" if signals.get("reg_write_enable") else "✗"
        mem_read = "✓" if signals.get("mem_read") else "✗"
        mem_write = "✓" if signals.get("mem_write") else "✗"
        branch = "✓" if signals.get("branch") else "✗"
        jump = "✓" if signals.get("jump") else "✗"
        pc_update = signals.get("pc_update", "unknown")[:8]
        
        print(f"{assembly:<17} | {alu_op:<6} | {reg_write:<5} | {mem_read:<4} | {mem_write:<4} | {branch:<6} | {jump:<4} | {pc_update}")
    
    # Show signal history
    control_unit.display_signal_history()
    
    # Show statistics
    stats = control_unit.get_statistics()
    print(f"\n📊 Control Unit Statistics:")
    print(f"   Total signals generated: {stats['total_signals_generated']}")
    print(f"   History size: {stats['history_size']}")


if __name__ == "__main__":
    demo_control_unit()