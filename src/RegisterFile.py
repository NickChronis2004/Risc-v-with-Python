
class Register:
    """
    Represents a single 16-bit register
    """
    
    def __init__(self, name="", abi_name="", purpose="", initial_value=0, read_only=False):
        """
        Creates a 16-bit register
        
        Args:
            name (str): Register name (e.g. "x0", "x1")
            abi_name (str): ABI name (e.g. "zero", "ra", "sp")
            purpose (str): Register purpose description
            initial_value (int): Initial value (default: 0)
            read_only (bool): If True, cannot be modified (for x0)
        """
        self.name = name
        self.abi_name = abi_name
        self.purpose = purpose
        self.read_only = read_only
        self._value = initial_value & 0xFFFF  # Only 16 bits
    
    def read(self):
        """
        Reads the register value
        
        Returns:
            int: Register value (0-65535)
        """
        return self._value
    
    def write(self, value):
        """
        Writes value to register
        
        Args:
            value (int): New value
            
        Returns:
            bool: True if write succeeded, False if read-only
        """
        if self.read_only:
            return False
        
        self._value = value & 0xFFFF  # Keep only 16 bits
        return True
    
    def reset(self):
        """Resets register to 0 (unless read-only)"""
        if not self.read_only:
            self._value = 0
    
    def __str__(self):
        """String representation for debugging"""
        return f"{self.name}({self.abi_name}): 0x{self._value:04X} ({self._value}) - {self.purpose}"
    
    def __repr__(self):
        return f"Register(name='{self.name}', abi='{self.abi_name}', value=0x{self._value:04X})"


class RegisterFile:
    """
    Register file with 16 registers (x0-x15)
    Mapped from 32-register RISC-V to 16-register simplified version
    """
    
    def __init__(self):
        """Initialize 16 registers x0-x15 with RISC-V ABI mappings"""
        self.registers = []
        
        # Register mappings: (name, abi_name, purpose, read_only)
        register_specs = [
            ("x0", "zero", "Hard-wired zero", True),
            ("x1", "ra", "Return address", False),
            ("x2", "sp", "Stack pointer", False),
            ("x3", "gp", "Global pointer", False),
            ("x4", "tp", "Thread pointer", False),
            ("x5", "t0", "Temporary register 0", False),
            ("x6", "t1", "Temporary register 1", False),
            ("x7", "t2", "Temporary register 2", False),
            ("x8", "s0", "Saved register 0 / Frame pointer", False),
            ("x9", "s1", "Saved register 1", False),
            ("x10", "a0", "Function argument 0 / Return value 0", False),
            ("x11", "a1", "Function argument 1 / Return value 1", False),
            ("x12", "a2", "Function argument 2", False),
            ("x13", "a3", "Function argument 3", False),
            ("x14", "a4", "Function argument 4", False),
            ("x15", "a7", "System call number", False)  # Mapped from x17 in RISC-V
        ]
        
        # Create registers with their properties
        for name, abi_name, purpose, read_only in register_specs:
            self.registers.append(Register(name, abi_name, purpose, 0, read_only))
    
    def read(self, reg_num):
        """
        Read value from register
        
        Args:
            reg_num (int): Register number (0-15)
            
        Returns:
            int: Register value, or 0 if invalid register number
        """
        if 0 <= reg_num < 16:
            return self.registers[reg_num].read()
        return 0
    
    def write(self, reg_num, value):
        """
        Write value to register
        
        Args:
            reg_num (int): Register number (0-15)
            value (int): Value to write
            
        Returns:
            bool: True if write succeeded, False if failed (x0 or invalid reg)
        """
        if 0 <= reg_num < 16:
            return self.registers[reg_num].write(value)
        return False
    
    def reset_all(self):
        """Reset all registers to 0 (except x0 which stays 0)"""
        for register in self.registers:
            register.reset()
    
    def get_register_info(self, reg_num):
        """Get complete register information"""
        if 0 <= reg_num < 16:
            reg = self.registers[reg_num]
            return (reg.name, reg.abi_name, reg.purpose)
        return ("INVALID", "INVALID", "Invalid register")
    
    def get_register_by_name(self, name):
        """Get register number by name (x0-x15) or ABI name (zero, ra, etc.)"""
        name = name.lower()
        
        # Direct register names (x0-x15)
        if name.startswith('x') and name[1:].isdigit():
            reg_num = int(name[1:])
            if 0 <= reg_num < 16:
                return reg_num
        
        # ABI names
        abi_map = {
            'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7, 's0': 8, 's1': 9,
            'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a7': 15
        }
        
        return abi_map.get(name, -1)
    
    def display_registers_rich(self):
        """Display registers using Rich library for beautiful terminal output"""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.text import Text
            from rich import box
            
            console = Console()
            
            # Create main table
            table = Table(
                title="[bold cyan]REGISTER FILE[/bold cyan]",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold magenta"
            )
            
            # Add columns for 4x4 grid
            for i in range(4):
                table.add_column(f"Register {i}", justify="center", style="white", min_width=12)
            
            # Add rows (4 registers per row)
            for row in range(4):
                row_data = []
                for col in range(4):
                    reg_idx = row * 4 + col
                    if reg_idx < 16:
                        reg = self.registers[reg_idx]
                        value = reg.read()
                        
                        # Color coding based on register type
                        if reg_idx == 0:  # x0 (zero)
                            color = "dim"
                        elif reg.abi_name in ["ra", "sp"]:  # Important registers
                            color = "bold yellow"
                        elif reg.abi_name.startswith("a"):  # Arguments
                            color = "green"
                        elif reg.abi_name.startswith("t"):  # Temporaries
                            color = "blue"
                        elif reg.abi_name.startswith("s"):  # Saved
                            color = "red"
                        else:
                            color = "white"
                        
                        # Format register info
                        reg_text = Text()
                        reg_text.append(f"{reg.name}\n", style=f"bold {color}")
                        reg_text.append(f"({reg.abi_name})\n", style=f"italic {color}")
                        reg_text.append(f"0x{value:04X}\n", style=f"{color}")
                        reg_text.append(f"{value}", style=f"dim {color}")
                        
                        row_data.append(reg_text)
                    else:
                        row_data.append("")
                
                table.add_row(*row_data)
            
            console.print(table)
            
        except ImportError:
            print("\n[WARNING] Rich library not installed!")
            print("Install with: pip install rich")
            print("Falling back to basic display...\n")
            self.display_registers()
    
    def display_registers(self):
        """Display registers in a nice table format like RARS with ABI names"""
        print("┌" + "─" * 75 + "┐")
        print("│" + " " * 30 + "REGISTER FILE" + " " * 30 + "│")
        print("├" + "─" * 75 + "┤")
        
        # Print registers in 4x4 grid
        for row in range(4):
            # Register names line (x0, x1, etc.)
            names_line = "│ "
            for col in range(4):
                reg_idx = row * 4 + col
                if reg_idx < 16:
                    names_line += f"{self.registers[reg_idx].name:>3} "
                else:
                    names_line += "    "
                names_line += "│ "
            names_line += "│"
            print(names_line)
            
            # ABI names line (ra, sp, etc.)
            abi_line = "│ "
            for col in range(4):
                reg_idx = row * 4 + col
                if reg_idx < 16:
                    abi_name = self.registers[reg_idx].abi_name
                    abi_line += f"{abi_name:>3} "
                else:
                    abi_line += "    "
                abi_line += "│ "
            abi_line += "│"
            print(abi_line)
            
            # Values line (hex)
            hex_line = "│ "
            for col in range(4):
                reg_idx = row * 4 + col
                if reg_idx < 16:
                    value = self.registers[reg_idx].read()
                    hex_line += f"{value:04X}"
                else:
                    hex_line += "    "
                hex_line += "│ "
            hex_line += "│"
            print(hex_line)
            
            # Values line (decimal)
            dec_line = "│ "
            for col in range(4):
                reg_idx = row * 4 + col
                if reg_idx < 16:
                    value = self.registers[reg_idx].read()
                    dec_line += f"{value:>4}"
                else:
                    dec_line += "    "
                dec_line += "│ "
            dec_line += "│"
            print(dec_line)
            
            # Separator line (except last)
            if row < 3:
                print("├" + ("─" * 4 + "┼ ") * 4 + "┤")
        
        print("└" + "─" * 75 + "┘")
    
    def display_summary(self):
        """Display a summary of register states"""
        print("\n" + "="*60)
        print("📊 REGISTER FILE SUMMARY")
        print("="*60)
        
        non_zero_regs = []
        for i, reg in enumerate(self.registers):
            value = reg.read()
            if value != 0:
                non_zero_regs.append((i, reg.name, reg.abi_name, value))
        
        if non_zero_regs:
            print(f"\n📍 Non-zero registers ({len(non_zero_regs)}):")
            for reg_num, name, abi_name, value in non_zero_regs:
                print(f"   {name}({abi_name}): 0x{value:04X} ({value})")
        else:
            print("\n📍 All registers are zero")
        
        print(f"\n📊 Total registers: 16")
        print(f"📊 Active registers: {len(non_zero_regs)}")
        print("="*60)


# Κύρια συνάρτηση για demo
def main():
    """Demo του RegisterFile"""
    print("RegisterFile Demo - RISC-V 16-bit Processor")
    print("=" * 45)
    
    rf = RegisterFile()
    
    print("\n1. Αρχική κατάσταση:")
    rf.display_registers()
    
    print("\n2. Γράφοντας σε μερικά registers...")
    rf.write(1, 0x1234)   # ra
    rf.write(2, 0x8000)   # sp  
    rf.write(10, 42)      # a0
    rf.write(11, 100)     # a1
    
    print("\n3. Κατάσταση μετά τις εγγραφές:")
    rf.display_registers()
    
    print("\n4. Summary:")
    rf.display_summary()
    
    print("\n5. Test x0 protection:")
    success = rf.write(0, 999)
    print(f"   Trying to write 999 to x0: {'FAILED' if not success else 'SUCCESS'}")
    print(f"   x0 value: {rf.read(0)}")


if __name__ == "__main__":
    main()