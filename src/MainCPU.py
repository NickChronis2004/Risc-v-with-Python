from typing import Dict, Any, Optional, List
import os
import sys

# Import all our components
from RegisterFile import RegisterFile
from ALU import ALU
from Memory import InstructionMemory, DataMemory
from InstructionDecoder import InstructionDecoder
from ControlUnit import ControlUnit
from Assembler import RiscVAssembler, BinaryLoader


class RiscVProcessor:
    """
    Complete RISC-V 16-bit Processor
    
    Integrates all components into a working CPU:
    - RegisterFile (x0-x15)
    - ALU (arithmetic & logic operations)
    - InstructionMemory & DataMemory (Harvard architecture)
    - InstructionDecoder (binary → structured)
    - ControlUnit (control signal generation)
    - Program Counter & execution control
    """
    
    def __init__(self, instruction_memory_size=1024, data_memory_size=1024):
        """Initialize the complete processor"""
        
        print("🚀 Initializing RISC-V 16-bit Processor...")
        
        # Core components
        self.register_file = RegisterFile()
        self.alu = ALU()
        self.instruction_memory = InstructionMemory(instruction_memory_size)
        self.data_memory = DataMemory(data_memory_size)
        self.instruction_decoder = InstructionDecoder()
        self.control_unit = ControlUnit()
        
        # Processor state
        self.pc = 0                    # Program Counter
        self.cycle_count = 0           # Clock cycles executed
        self.instruction_count = 0     # Instructions executed
        self.halted = False           # Execution halted?
        
        # Execution history for debugging
        self.execution_history = []
        
        # Statistics
        self.stats = {
            "r_type_count": 0,
            "i_type_count": 0,
            "s_type_count": 0,
            "b_type_count": 0,
            "j_type_count": 0,
            "special_count": 0,
            "branches_taken": 0,
            "branches_not_taken": 0,
            "memory_reads": 0,
            "memory_writes": 0
        }
        
        print("✅ Processor initialized successfully!")
        print(f"   📄 Instruction Memory: {instruction_memory_size} words")
        print(f"   💾 Data Memory: {data_memory_size} words")
        print(f"   🗂️ Registers: 16 (x0-x15)")
        print(f"   ⚙️ ALU: 7 operations supported")
    
    def load_program_from_file(self, filename: str) -> bool:
        """
        Load program from assembly (.asm) or binary (.bin) file
        
        Args:
            filename: Path to .asm or .bin file
            
        Returns:
            bool: True if successful
        """
        try:
            if filename.endswith('.asm'):
                return self._load_from_assembly(filename)
            elif filename.endswith('.bin'):
                return self._load_from_binary(filename)
            else:
                print(f"❌ Unsupported file type: {filename}")
                return False
        except Exception as e:
            print(f"❌ Error loading program: {e}")
            return False
    
    def _load_from_assembly(self, filename: str) -> bool:
        """Load program from .asm file"""
        print(f"🔧 Assembling {filename}...")
        
        assembler = RiscVAssembler()
        machine_code = assembler.assemble_file(filename)
        
        if not machine_code:
            print("❌ Assembly failed!")
            return False
        
        return self.instruction_memory.load_program(machine_code)
    
    def _load_from_binary(self, filename: str) -> bool:
        """Load program from .bin file"""
        print(f"📂 Loading binary {filename}...")
        return self.instruction_memory.load_from_binary_file(filename)
    
    def load_program_direct(self, instructions: List[int]) -> bool:
        """Load program directly from list of instructions"""
        return self.instruction_memory.load_program(instructions)
    
    def step(self) -> bool:
        """
        Execute single instruction (one clock cycle)
        
        Returns:
            bool: True if execution should continue, False if halted
        """
        if self.halted:
            print("⏹️  Processor is halted")
            return False
        
        # Instruction Fetch
        instruction = self.instruction_memory.read_instruction(self.pc)
        if instruction == 0 and self.pc >= self.instruction_memory.get_program_size():
            print("⏹️  End of program reached")
            self.halted = True
            return False
        
        # Instruction Decode
        decoded = self.instruction_decoder.decode(instruction)
        
        if not decoded["valid"]:
            print(f"⚠️  Invalid instruction at PC=0x{self.pc:04X}: 0x{instruction:04X}")
            self.pc += 1
            self.cycle_count += 1
            return True
        
        # Generate Control Signals
        control_signals = self.control_unit.generate_control_signals(decoded)
        
        # Execute Instruction
        self._execute_instruction(decoded, control_signals)
        
        # Update statistics
        self._update_statistics(decoded, control_signals)
        
        # Log execution
        self._log_execution(decoded, control_signals)
        
        # Update counters
        self.cycle_count += 1
        self.instruction_count += 1
        
        return not self.halted
    
    def _execute_instruction(self, decoded: Dict, control_signals: Dict):
        """Execute the decoded instruction with control signals"""
        
        instruction_name = decoded["instruction_name"]
        
        # Handle different instruction types
        if decoded["type"] == "R":
            self._execute_r_type(decoded, control_signals)
        elif decoded["type"] == "I":
            if instruction_name == "LW":
                self._execute_load(decoded, control_signals)
            else:
                self._execute_i_type(decoded, control_signals)
        elif decoded["type"] == "S":
            self._execute_store(decoded, control_signals)
        elif decoded["type"] == "B":
            self._execute_branch(decoded, control_signals)
        elif decoded["type"] == "J":
            self._execute_jump(decoded, control_signals)
        elif decoded["type"] == "Special":
            self._execute_special(decoded, control_signals)
        
        # Update PC based on control signals
        self._update_pc(control_signals, decoded)
    
    def _execute_r_type(self, decoded: Dict, control_signals: Dict):
        """Execute R-type instruction (ADD, SUB, AND, OR, XOR)"""
        
        # Read source registers
        rs1_value = self.register_file.read(decoded["rs1"])
        rs2_value = self.register_file.read(decoded["rs2"])
        
        # Perform ALU operation
        alu_result = self.alu.execute(rs1_value, rs2_value, control_signals["alu_operation"])
        
        # Write result to destination register
        if control_signals["reg_write_enable"]:
            self.register_file.write(decoded["rd"], alu_result)
    
    def _execute_i_type(self, decoded: Dict, control_signals: Dict):
        """Execute I-type instruction (ADDI, ANDI, ORI)"""
        
        # Read source register
        rs1_value = self.register_file.read(decoded["rs1"])
        immediate = decoded["immediate"]
        
        # For ADDI, treat immediate as unsigned for positive values
        # This fixes the 4-bit signed issue where 10 becomes -6
        # Read source register and immediate
        rs1_value = self.register_file.read(decoded["rs1"])
        immediate = decoded["immediate"]
        
        # Perform ALU operation
        alu_result = self.alu.execute(rs1_value, immediate, control_signals["alu_operation"])
        
        # Write result to destination register
        if control_signals["reg_write_enable"]:
            self.register_file.write(decoded["rd"], alu_result)
    
    def _execute_load(self, decoded: Dict, control_signals: Dict):
        """Execute LW instruction"""
        
        # Calculate memory address: rs1 + offset
        base_address = self.register_file.read(decoded["rs1"])
        offset = decoded["offset"]
        
        # Handle negative offset
        # For load operations, treat offset as unsigned (0-15)
        # No sign extension needed - keep as is
        
        memory_address = (base_address + offset) & 0xFFFF
        
        # Convert to data memory address space (0x1000 base)
        data_address = 0x1000 + (memory_address & 0x3FF)  # Map to data memory range
        
        # Read from data memory
        data_value = self.data_memory.read_word(data_address)
        self.stats["memory_reads"] += 1
        
        # Write to destination register
        self.register_file.write(decoded["rd"], data_value)
    
    def _execute_store(self, decoded: Dict, control_signals: Dict):
        """Execute SW instruction"""
        
        # Calculate memory address: rs1 + offset
        base_address = self.register_file.read(decoded["rs1"])
        offset = decoded["offset"]
        
        # Handle negative offset
        # For store operations, treat offset as unsigned (0-15)  
        # No sign extension needed - keep as is
        
        memory_address = (base_address + offset) & 0xFFFF
        
        # Convert to data memory address space
        data_address = 0x1000 + (memory_address & 0x3FF)
        
        # Get data to store
        store_data = self.register_file.read(decoded["rs2"])
        
        # Write to data memory
        self.data_memory.write_word(data_address, store_data)
        self.stats["memory_writes"] += 1
    
    def _execute_branch(self, decoded: Dict, control_signals: Dict):
        """Execute branch instructions (BEQ, BNE)"""
        
        # Read comparison registers
        rs1_value = self.register_file.read(decoded["rs1"])
        rs2_value = self.register_file.read(decoded["rs2"])
        
        # Perform comparison
        comparison_result = self.alu.execute(rs1_value, rs2_value, control_signals["alu_operation"])
        
        # Branch taken if comparison is true (ALU returns 1)
        branch_taken = (comparison_result == 1)
        
        if branch_taken:
            # Update PC with branch target
            branch_offset = decoded["offset"]
            # Add offset to current PC (not PC+1, since PC will be incremented later)
            new_pc = (self.pc + branch_offset) & 0xFFFF
            self.pc = new_pc
            self.stats["branches_taken"] += 1
            self._pc_updated = True  # Flag to prevent double PC update
        else:
            self.stats["branches_not_taken"] += 1
            self._pc_updated = False
    
    def _execute_jump(self, decoded: Dict, control_signals: Dict):
        """Execute JAL instruction"""
        
        # Save return address (PC + 1) to destination register
        return_address = (self.pc + 1) & 0xFFFF
        self.register_file.write(decoded["rd"], return_address)
        
        # Jump to target address
        jump_offset = decoded["offset"]
        if jump_offset < 0:
            self.pc = (self.pc + jump_offset) & 0xFFFF
        else:
            self.pc = (self.pc + jump_offset) & 0xFFFF
        
        self._pc_updated = True  # Flag to prevent double PC update
    
    def _execute_special(self, decoded: Dict, control_signals: Dict):
        """Execute special instructions (NOP, HALT)"""
        
        if decoded["instruction_name"] == "HALT":
            print("🛑 HALT instruction executed")
            self.halted = True
        # NOP does nothing
    
    def _update_pc(self, control_signals: Dict, decoded: Dict):
        """Update Program Counter based on control signals"""
        
        # Check if PC was already updated (branches/jumps)
        if hasattr(self, '_pc_updated') and self._pc_updated:
            self._pc_updated = False
            return
        
        pc_update = control_signals.get("pc_update", "increment")
        
        if pc_update == "increment":
            self.pc = (self.pc + 1) & 0xFFFF
        elif pc_update == "conditional":
            # For conditional branches, if we reach here, branch was NOT taken
            # So we increment PC normally
            self.pc = (self.pc + 1) & 0xFFFF
        elif pc_update == "halt":
            self.halted = True
        # jump updates are handled in their respective execute functions
    
    def _update_statistics(self, decoded: Dict, control_signals: Dict):
        """Update execution statistics"""
        
        inst_type = decoded["type"]
        if inst_type in ["R"]:
            self.stats["r_type_count"] += 1
        elif inst_type in ["I"]:
            self.stats["i_type_count"] += 1
        elif inst_type in ["S"]:
            self.stats["s_type_count"] += 1
        elif inst_type in ["B"]:
            self.stats["b_type_count"] += 1
        elif inst_type in ["J"]:
            self.stats["j_type_count"] += 1
        elif inst_type in ["Special"]:
            self.stats["special_count"] += 1
    
    def _log_execution(self, decoded: Dict, control_signals: Dict):
        """Log execution for debugging"""
        
        log_entry = {
            "cycle": self.cycle_count,
            "pc": self.pc,
            "instruction": decoded["raw_instruction"],
            "assembly": decoded["assembly"],
            "type": decoded["type"]
        }
        
        self.execution_history.append(log_entry)
        
        # Keep only last 20 entries
        if len(self.execution_history) > 20:
            self.execution_history.pop(0)
    
    def run(self, max_cycles=1000) -> bool:
        """
        Run program until HALT or max cycles
        
        Args:
            max_cycles: Maximum number of cycles to prevent infinite loops
            
        Returns:
            bool: True if completed normally
        """
        print(f"▶️  Starting program execution (max {max_cycles} cycles)...")
        
        cycles_executed = 0
        
        while cycles_executed < max_cycles and not self.halted:
            if not self.step():
                break
            cycles_executed += 1
        
        if cycles_executed >= max_cycles:
            print(f"⏰ Execution stopped after {max_cycles} cycles (possible infinite loop)")
            return False
        else:
            print(f"✅ Program completed in {cycles_executed} cycles")
            return True
    
    def reset(self):
        """Reset processor to initial state"""
        print("🔄 Resetting processor...")
        
        self.pc = 0
        self.cycle_count = 0
        self.instruction_count = 0
        self.halted = False
        
        # Reset components
        self.register_file.reset_all()
        self.alu.reset()
        self.data_memory.clear_memory()
        
        # Clear statistics and history
        for key in self.stats:
            self.stats[key] = 0
        self.execution_history.clear()
        
        print("✅ Processor reset complete")
    
    def display_status(self):
        """Display current processor status"""
        print("\n" + "="*70)
        print("🖥️  RISC-V PROCESSOR STATUS")
        print("="*70)
        
        # Basic status
        status = "HALTED" if self.halted else "RUNNING"
        print(f"Status: {status}")
        print(f"PC: 0x{self.pc:04X} ({self.pc})")
        print(f"Cycles: {self.cycle_count}")
        print(f"Instructions: {self.instruction_count}")
        
        # Registers
        print(f"\n📊 Register File:")
        self.register_file.display_registers()
        
        # ALU Status
        print(f"\n⚙️ ALU Status:")
        self.alu.display_status()
        
        # Memory status
        print(f"\n💾 Data Memory (non-zero values):")
        non_zero = self.data_memory.find_non_zero()
        if non_zero:
            for addr, value in non_zero[:10]:  # Show first 10
                print(f"   [0x{addr:04X}]: 0x{value:04X} ({value})")
        else:
            print("   (No data stored)")
        
        print("="*70)
    
    def display_statistics(self):
        """Display execution statistics"""
        print("\n" + "="*60)
        print("📊 EXECUTION STATISTICS")
        print("="*60)
        
        total_instructions = sum([
            self.stats["r_type_count"],
            self.stats["i_type_count"], 
            self.stats["s_type_count"],
            self.stats["b_type_count"],
            self.stats["j_type_count"],
            self.stats["special_count"]
        ])
        
        print(f"Total Instructions: {total_instructions}")
        print(f"Total Cycles: {self.cycle_count}")
        if self.cycle_count > 0:
            print(f"CPI (Cycles Per Instruction): {self.cycle_count / max(total_instructions, 1):.2f}")
        
        print(f"\nInstruction Mix:")
        print(f"  R-Type: {self.stats['r_type_count']}")
        print(f"  I-Type: {self.stats['i_type_count']}")
        print(f"  S-Type: {self.stats['s_type_count']}")
        print(f"  B-Type: {self.stats['b_type_count']}")
        print(f"  J-Type: {self.stats['j_type_count']}")
        print(f"  Special: {self.stats['special_count']}")
        
        total_branches = self.stats["branches_taken"] + self.stats["branches_not_taken"]
        if total_branches > 0:
            branch_rate = (self.stats["branches_taken"] / total_branches) * 100
            print(f"\nBranch Statistics:")
            print(f"  Branches Taken: {self.stats['branches_taken']}")
            print(f"  Branches Not Taken: {self.stats['branches_not_taken']}")
            print(f"  Branch Rate: {branch_rate:.1f}%")
        
        print(f"\nMemory Operations:")
        print(f"  Memory Reads: {self.stats['memory_reads']}")
        print(f"  Memory Writes: {self.stats['memory_writes']}")
        
        print("="*60)
    
    def display_execution_trace(self, last_n=10):
        """Display recent execution trace"""
        print("\n" + "="*80)
        print("🕒 EXECUTION TRACE")
        print("="*80)
        
        trace_to_show = self.execution_history[-last_n:] if len(self.execution_history) > last_n else self.execution_history
        
        if not trace_to_show:
            print("No execution history available.")
            return
        
        print("Cycle | PC     | Instruction | Assembly")
        print("-"*50)
        
        for entry in trace_to_show:
            cycle = entry["cycle"]
            pc = entry["pc"]
            instruction = entry["instruction"]
            assembly = entry["assembly"]
            
            print(f"{cycle:<5} | 0x{pc:04X} | 0x{instruction:04X}      | {assembly}")
        
        print("="*80)


def demo_processor():
    """Demo of complete processor functionality"""
    print("🖥️  RISC-V Processor Demo")
    print("="*50)
    
    # Create processor
    processor = RiscVProcessor(instruction_memory_size=64, data_memory_size=64)
    
    # Create a simple test program
    print("\n📝 Creating test program...")
    test_program = [
        0x5107,  # ADDI x1, x0, 7      # x1 = 7 (avoiding negative interpretation)
        0x5205,  # ADDI x2, x0, 5      # x2 = 5
        0x0312,  # ADD x3, x1, x2      # x3 = x1 + x2 = 12
        0x1412,  # SUB x4, x1, x2      # x4 = x1 - x2 = 2
        0x9320,  # SW x3, 0(x2)        # Store x3 to memory[x2+0]
        0x8520,  # LW x5, 0(x2)        # Load from memory[x2+0] to x5
        0xA342,  # BEQ x3, x4, 2       # if x3 == x4 goto PC+2 (won't branch: 12 != 2)
        0xB341,  # BNE x3, x4, 1       # if x3 != x4 goto PC+1 (will branch: 12 != 2)
        0xE000,  # NOP                 # This should be skipped
        0xF000   # HALT                # Stop execution
    ]
    
    # Load program
    processor.load_program_direct(test_program)
    
    print("✅ Test program loaded:")
    print("   1. Set x1 = 7, x2 = 5")
    print("   2. Calculate x3 = x1 + x2 = 12")
    print("   3. Calculate x4 = x1 - x2 = 2")
    print("   4. Store x3 to memory")
    print("   5. Load from memory to x5")
    print("   6. Test branches (BEQ won't branch, BNE will)")
    print("   7. HALT")
    
    # Execute step by step for first few instructions
    print(f"\n🔍 Step-by-step execution:")
    for i in range(5):
        print(f"\n--- Step {i+1} ---")
        if not processor.step():
            break
        print(f"PC: 0x{processor.pc:04X}, Cycles: {processor.cycle_count}")
        
        # Show register changes
        non_zero_regs = []
        for reg in range(16):
            value = processor.register_file.read(reg)
            if value != 0:
                non_zero_regs.append(f"x{reg}=0x{value:04X}")
        if non_zero_regs:
            print(f"Registers: {', '.join(non_zero_regs)}")
    
    # Run the rest
    print(f"\n▶️  Running remaining instructions...")
    processor.run(max_cycles=100)
    
    # Show final status
    processor.display_status()
    processor.display_statistics()
    processor.display_execution_trace()


if __name__ == "__main__":
    demo_processor()