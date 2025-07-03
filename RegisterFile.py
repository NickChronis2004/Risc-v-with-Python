# Complete Register File implementation
# Contains both Register and RegisterFile classes

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
            print("\n[ERROR] Rich library not installed!")
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
    
    def get_register_info(self, reg_num):
        """Get complete register information"""
        if 0 <= reg_num < 16:
            reg = self.registers[reg_num]
            return (reg.name, reg.abi_name, reg.purpose)
        return ("INVALID", "INVALID", "Invalid register")


def main_test_rf():
    """Test the RegisterFile functionality"""
    print("=== Testing RegisterFile ===\n")
    
    # Create register file
    rf = RegisterFile()
    
    print("1. Initial state (all zeros) - Rich Display:")
    rf.display_registers_rich()
    
    print("\n2. Testing writes to various registers:")
    
    # Test writing to different register types
    rf.write(1, 0x1000)    # ra (return address)
    rf.write(2, 0x2000)    # sp (stack pointer)  
    rf.write(10, 42)       # a0 (function arg/return)
    rf.write(11, 100)      # a1 (function arg/return)
    rf.write(5, 0xFFFF)    # t0 (temporary)
    
    print("   - x1 (ra) = 0x1000")
    print("   - x2 (sp) = 0x2000") 
    print("   - x10 (a0) = 42")
    print("   - x11 (a1) = 100")
    print("   - x5 (t0) = 0xFFFF")
    
    rf.display_registers_rich()
    
    print("\n3. Testing x0 protection (should fail):")
    success = rf.write(0, 123)
    print(f"   - Trying to write 123 to x0: {'FAILED' if not success else 'SUCCESS'}")
    print(f"   - x0 value: {rf.read(0)} (should be 0)")
    
    print("\n4. Testing boundary conditions:")
    
    # Test invalid register numbers
    print(f"   - Reading x16 (invalid): {rf.read(16)}")
    print(f"   - Writing to x20 (invalid): {rf.write(20, 999)}")
    
    # Test 16-bit overflow
    rf.write(7, 0x10000)  # Should wrap to 0x0000
    print(f"   - Writing 0x10000 to x7, result: 0x{rf.read(7):04X}")
    
    print("\n5. Final state with Rich display:")
    rf.display_registers_rich()
    
    print("\n6. Register ABI Information:")
    for i in [0, 1, 2, 10, 11, 15]:
        reg_name, abi_name, purpose = rf.get_register_info(i)
        print(f"   - {reg_name} ({abi_name}): {purpose}")
    
    print("\n=== RegisterFile Test Complete ===")
    
    # Ask user which display they prefer
    print("\nWhich display do you prefer?")
    print("1. Rich (colorful)")
    print("2. Basic (ASCII art)")
    choice = input("Enter choice (1/2): ")
    
    if choice == "1":
        print("\n--- Rich Display ---")
        rf.display_registers_rich()
    else:
        print("\n--- Basic Display ---")
        rf.display_registers()


# Run the test
if __name__ == "__main__":
    main_test_rf()