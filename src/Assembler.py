import re

class RiscVAssembler:
    def __init__(self):
        """
        Initialize the RISC-V Assembler
        
        Sets up opcode mappings, register mappings, and storage for labels
        """
        
        # Opcode mapping - 4-bit opcodes for our 16-bit processor
        self.opcodes = {
            # R-Type Instructions (ALU Operations)
            'ADD':  0x0,    # rd = rs1 + rs2
            'SUB':  0x1,    # rd = rs1 - rs2
            'AND':  0x2,    # rd = rs1 & rs2
            'OR':   0x3,    # rd = rs1 | rs2
            'XOR':  0x4,    # rd = rs1 ^ rs2
            
            # I-Type Instructions (Immediate)
            'ADDI': 0x5,    # rd = rs1 + imm
            'ANDI': 0x6,    # rd = rs1 & imm
            'ORI':  0x7,    # rd = rs1 | imm
            'LW':   0x8,    # rd = memory[rs1 + offset]
            
            # S-Type Instructions (Store)
            'SW':   0x9,    # memory[rs1 + offset] = rs2
            
            # B-Type Instructions (Branch)
            'BEQ':  0xA,    # if (rs1 == rs2) PC += offset
            'BNE':  0xB,    # if (rs1 != rs2) PC += offset
            
            # J-Type Instructions (Jump)
            'JAL':  0xC,    # rd = PC+1, PC += offset
            
            # Special Instructions
            'NOP':  0xE,    # No operation
            'HALT': 0xF     # Stop execution
        }
        
        # Register mapping - Support both x0-x15 and ABI names
        self.register_map = {
            # Standard register names
            'x0': 0, 'x1': 1, 'x2': 2, 'x3': 3, 'x4': 4, 'x5': 5, 'x6': 6, 'x7': 7,
            'x8': 8, 'x9': 9, 'x10': 10, 'x11': 11, 'x12': 12, 'x13': 13, 'x14': 14, 'x15': 15,
            
            # ABI (Application Binary Interface) names
            'zero': 0,   # Hard-wired zero
            'ra': 1,     # Return address
            'sp': 2,     # Stack pointer
            'gp': 3,     # Global pointer
            'tp': 4,     # Thread pointer
            't0': 5,     # Temporary 0
            't1': 6,     # Temporary 1
            't2': 7,     # Temporary 2
            's0': 8,     # Saved 0 / Frame pointer
            's1': 9,     # Saved 1
            'a0': 10,    # Argument 0 / Return value 0
            'a1': 11,    # Argument 1 / Return value 1
            'a2': 12,    # Argument 2
            'a3': 13,    # Argument 3
            'a4': 14,    # Argument 4
            'a7': 15     # System call number
        }
        
        # Storage for labels and their addresses
        self.labels = {}           # label_name -> address
        self.instructions = []     # List of parsed instructions
        self.machine_code = []     # Final machine code output

    def clean_line(self, line):
        """
        Clean up input line by removing comments and extra whitespace
        
        Args:
            line (str): Raw assembly line
            
        Returns:
            str: Cleaned line
        """
        # Remove comments (everything after #)
        if '#' in line:
            line = line.split('#')[0]
        
        # Remove leading/trailing whitespace
        line = line.strip()
        
        return line

    def extract_label(self, line):
        """
        Extract label from assembly line
        
        Args:
            line (str): Assembly line that might contain a label
            
        Returns:
            tuple: (label_name or None, remaining_instruction_line)
        """
        if ':' in line:
            # Split on first colon only
            parts = line.split(':', 1)
            label_name = parts[0].strip()
            
            # Get remaining instruction (if any)
            instruction_part = parts[1].strip() if len(parts) > 1 else ""
            
            return label_name, instruction_part
        
        # No label found
        return None, line

    def parse_instruction_line(self, line):
        """
        Parse instruction line into components
        
        Args:
            line (str): Clean instruction line (no labels, no comments)
            
        Returns:
            dict: Parsed instruction components or None if empty/invalid
        """
        if not line:
            return None
        
        # Replace commas with spaces for uniform parsing
        # "add x1, x2, x3" → "add x1  x2  x3"
        clean_line = re.sub(r'[,\s]+', ' ', line).strip()
        
        # Split on whitespace - this automatically handles multiple spaces
        parts = clean_line.split()
        
        if not parts:
            return None
        
        # First part is always the instruction
        instruction = parts[0].upper()
        
        # Remaining parts are operands
        operands = parts[1:]
        
        return {
            'instruction': instruction,
            'operands': operands,
            'original_line': line
        }

    def get_instruction_type(self, instruction):
        """
        Determine the type of instruction (R, I, S, B, J, Special)
        
        Args:
            instruction (str): Instruction name (e.g., 'ADD', 'ADDI')
            
        Returns:
            str: Instruction type ('R', 'I', 'S', 'B', 'J', 'Special')
        """
        r_type = ['ADD', 'SUB', 'AND', 'OR', 'XOR']
        i_type = ['ADDI', 'ANDI', 'ORI', 'LW']
        s_type = ['SW']
        b_type = ['BEQ', 'BNE']
        j_type = ['JAL']
        special = ['NOP', 'HALT']
        
        if instruction in r_type:
            return 'R'
        elif instruction in i_type:
            return 'I'
        elif instruction in s_type:
            return 'S'
        elif instruction in b_type:
            return 'B'
        elif instruction in j_type:
            return 'J'
        elif instruction in special:
            return 'Special'
        else:
            raise ValueError(f"Unknown instruction: {instruction}")

    def parse_register(self, reg_str):
        """
        Convert register string to register number
        
        Args:
            reg_str (str): Register name (e.g., 'x1', 'ra', 'zero')
            
        Returns:
            int: Register number (0-15)
        """
        reg_str = reg_str.lower().strip()
        
        if reg_str in self.register_map:
            return self.register_map[reg_str]
        else:
            raise ValueError(f"Unknown register: {reg_str}")

    def parse_immediate(self, imm_str):
        """
        Parse immediate value (supports decimal and hex)
        
        Args:
            imm_str (str): Immediate value string
            
        Returns:
            int: Immediate value (4-bit for our processor)
        """
        imm_str = imm_str.strip()
        
        # Handle hexadecimal (0x prefix)
        if imm_str.startswith('0x') or imm_str.startswith('0X'):
            value = int(imm_str, 16)
        else:
            # Handle decimal (including negative)
            value = int(imm_str)
        
        # Ensure 4-bit immediate (signed: -8 to +7, unsigned: 0 to 15)
        if value < -8 or value > 15:
            raise ValueError(f"Immediate value {value} out of 4-bit range (-8 to +15)")
        
        # Convert negative to 4-bit two's complement
        if value < 0:
            value = (1 << 4) + value  # Convert to unsigned 4-bit
        
        return value & 0xF  # Ensure 4-bit

    def assemble_file(self, filename):
        """
        Main function: assemble .asm file to machine code
        
        Args:
            filename (str): Path to assembly file
            
        Returns:
            list: List of 16-bit machine code instructions
        """
        try:
            # Read the assembly file
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            print(f"📂 Reading {filename}...")
            print(f"📄 Found {len(lines)} lines")
            
            # Clear previous state
            self.labels.clear()
            self.instructions.clear()
            self.machine_code.clear()
            
            # Pass 1: Find all labels and store instruction info
            print("🔍 Pass 1: Finding labels...")
            self._first_pass(lines)
            
            # Pass 2: Generate machine code
            print("🔧 Pass 2: Generating machine code...")
            self._second_pass()
            
            print(f"✅ Assembly complete! Generated {len(self.machine_code)} instructions")
            return self.machine_code
            
        except FileNotFoundError:
            print(f"❌ Error: File '{filename}' not found")
            return []
        except Exception as e:
            print(f"❌ Assembly error: {e}")
            return []

    def _first_pass(self, lines):
        """
        First pass: scan for labels and parse instructions
        
        Args:
            lines (list): List of assembly lines
        """
        address = 0
        
        for line_num, line in enumerate(lines, 1):
            try:
                # Clean the line
                clean_line = self.clean_line(line)
                
                # Skip empty lines
                if not clean_line:
                    continue
                
                # Extract label (if present)
                label, instruction_line = self.extract_label(clean_line)
                
                # Store label
                if label:
                    self.labels[label] = address
                    print(f"   📌 Label '{label}' at address {address}")
                
                # Parse instruction (if present)
                if instruction_line:
                    parsed = self.parse_instruction_line(instruction_line)
                    if parsed:
                        parsed['address'] = address
                        parsed['line_number'] = line_num
                        self.instructions.append(parsed)
                        address += 1
                        
            except Exception as e:
                print(f"❌ Error on line {line_num}: {e}")
                print(f"   Line: '{line.strip()}'")

    def _second_pass(self):
        """
        Second pass: convert parsed instructions to machine code
        """
        for instruction_info in self.instructions:
            try:
                machine_code = self.encode_instruction(instruction_info)
                self.machine_code.append(machine_code)
                
                # Debug output
                addr = instruction_info['address']
                orig = instruction_info['original_line']
                print(f"   {addr:02d}: {orig:<20} → 0x{machine_code:04X}")
                
            except Exception as e:
                line_num = instruction_info.get('line_number', '?')
                print(f"❌ Error encoding line {line_num}: {e}")

    def encode_instruction(self, instruction_info):
        """
        Convert parsed instruction to 16-bit machine code
        
        Args:
            instruction_info (dict): Parsed instruction information
            
        Returns:
            int: 16-bit machine code
        """
        instruction = instruction_info['instruction']
        operands = instruction_info['operands']
        
        # Get opcode
        if instruction not in self.opcodes:
            raise ValueError(f"Unknown instruction: {instruction}")
        
        opcode = self.opcodes[instruction]
        inst_type = self.get_instruction_type(instruction)
        
        # Encode based on instruction type
        if inst_type == 'R':
            return self._encode_r_type(opcode, operands)
        elif inst_type == 'I':
            return self._encode_i_type(opcode, operands, instruction)
        elif inst_type == 'S':
            return self._encode_s_type(opcode, operands)
        elif inst_type == 'B':
            return self._encode_b_type(opcode, operands, instruction_info['address'])
        elif inst_type == 'J':
            return self._encode_j_type(opcode, operands, instruction_info['address'])
        elif inst_type == 'Special':
            return self._encode_special(opcode)
        else:
            raise ValueError(f"Unknown instruction type: {inst_type}")

    def _encode_r_type(self, opcode, operands):
        """
        Encode R-type instruction: [opcode][rd][rs1][rs2]
        Format: ADD rd, rs1, rs2
        """
        if len(operands) != 3:
            raise ValueError(f"R-type instruction needs 3 operands, got {len(operands)}")
        
        rd = self.parse_register(operands[0])
        rs1 = self.parse_register(operands[1])
        rs2 = self.parse_register(operands[2])
        
        # 16-bit encoding: [4-bit opcode][4-bit rd][4-bit rs1][4-bit rs2]
        return (opcode << 12) | (rd << 8) | (rs1 << 4) | rs2

    def _encode_i_type(self, opcode, operands, instruction):
        """
        Encode I-type instruction: [opcode][rd][rs1][imm]
        Format: ADDI rd, rs1, imm  OR  LW rd, offset(rs1)
        """
        if instruction == 'LW':
            # Special case: LW rd, offset(rs1)
            if len(operands) != 2:
                raise ValueError("LW instruction needs format: LW rd, offset(rs1)")
            
            rd = self.parse_register(operands[0])
            
            # Parse memory operand: offset(rs1)
            mem_operand = operands[1]
            if '(' not in mem_operand or ')' not in mem_operand:
                raise ValueError(f"Invalid memory operand: {mem_operand}")
            
            # Extract offset and register
            offset_str = mem_operand.split('(')[0]
            rs1_str = mem_operand.split('(')[1].rstrip(')')
            
            offset = int(offset_str) if offset_str else 0
            rs1 = self.parse_register(rs1_str)
            
            # Ensure 4-bit offset
            offset = offset & 0xF
            
            return (opcode << 12) | (rd << 8) | (rs1 << 4) | offset
        else:
            # Regular I-type: ADDI, ANDI, ORI
            if len(operands) != 3:
                raise ValueError(f"I-type instruction needs 3 operands, got {len(operands)}")
            
            rd = self.parse_register(operands[0])
            rs1 = self.parse_register(operands[1])
            imm = self.parse_immediate(operands[2])
            
            return (opcode << 12) | (rd << 8) | (rs1 << 4) | imm

    def _encode_s_type(self, opcode, operands):
        """
        Encode S-type instruction: [opcode][rs2][rs1][offset]
        Format: SW rs2, offset(rs1)
        """
        if len(operands) != 2:
            raise ValueError("SW instruction needs format: SW rs2, offset(rs1)")
        
        rs2 = self.parse_register(operands[0])
        
        # Parse memory operand: offset(rs1)
        mem_operand = operands[1]
        if '(' not in mem_operand or ')' not in mem_operand:
            raise ValueError(f"Invalid memory operand: {mem_operand}")
        
        # Extract offset and register
        offset_str = mem_operand.split('(')[0]
        rs1_str = mem_operand.split('(')[1].rstrip(')')
        
        offset = int(offset_str) if offset_str else 0
        rs1 = self.parse_register(rs1_str)
        
        # Ensure 4-bit offset
        offset = offset & 0xF
        
        return (opcode << 12) | (rs2 << 8) | (rs1 << 4) | offset

    def _encode_b_type(self, opcode, operands, current_address):
        """
        Encode B-type instruction: [opcode][rs1][rs2][offset]
        Format: BEQ rs1, rs2, label
        """
        if len(operands) != 3:
            raise ValueError(f"Branch instruction needs 3 operands, got {len(operands)}")
        
        rs1 = self.parse_register(operands[0])
        rs2 = self.parse_register(operands[1])
        
        # Calculate branch offset
        target = operands[2]
        if target in self.labels:
            target_address = self.labels[target]
            # Relative offset: target - (current + 1)
            offset = (target_address - current_address - 1) & 0xF
        else:
            # Direct offset
            offset = int(target) & 0xF
        
        return (opcode << 12) | (rs1 << 8) | (rs2 << 4) | offset

    def _encode_j_type(self, opcode, operands, current_address):
        """
        Encode J-type instruction: [opcode][rd][offset]
        Format: JAL rd, label
        """
        if len(operands) != 2:
            raise ValueError(f"JAL instruction needs 2 operands, got {len(operands)}")
        
        rd = self.parse_register(operands[0])
        
        # Calculate jump offset
        target = operands[1]
        if target in self.labels:
            target_address = self.labels[target]
            # Relative offset (8-bit for J-type)
            offset = (target_address - current_address - 1) & 0xFF
        else:
            # Direct offset
            offset = int(target) & 0xFF
        
        return (opcode << 12) | (rd << 8) | offset

    def _encode_special(self, opcode):
        """
        Encode special instructions: NOP, HALT
        Format: [opcode][000000000000]
        """
        return opcode << 12

    def display_results(self):
        """Display assembly results for debugging"""
        print("\n" + "="*60)
        print("📊 ASSEMBLY RESULTS")
        print("="*60)
        
        if self.labels:
            print(f"\n📌 Labels ({len(self.labels)}):")
            for label, address in self.labels.items():
                print(f"   {label}: {address}")
        
        if self.machine_code:
            print(f"\n💾 Machine Code ({len(self.machine_code)} instructions):")
            for i, code in enumerate(self.machine_code):
                print(f"   {i:02d}: 0x{code:04X} ({code:016b})")
        
        print("="*60)