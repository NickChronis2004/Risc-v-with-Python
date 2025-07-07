
"""
Basic Exception Classes για τον RISC-V Processor

Απλές exceptions για τα βασικά error cases:
- Memory access errors
- Invalid instructions
- Register access errors
- Execution errors
"""


class ProcessorException(Exception):
    """Base exception για processor errors"""
    
    def __init__(self, message: str, pc: int = None, instruction: int = None):
        self.message = message
        self.pc = pc
        self.instruction = instruction
        super().__init__(self.message)
    
    def __str__(self):
        result = f"ProcessorException: {self.message}"
        if self.pc is not None:
            result += f" (PC: 0x{self.pc:04X})"
        if self.instruction is not None:
            result += f" (Instruction: 0x{self.instruction:04X})"
        return result


class MemoryException(ProcessorException):
    """Memory access errors"""
    pass


class InvalidInstructionException(ProcessorException):
    """Invalid/unknown instruction errors"""
    pass


class RegisterException(ProcessorException):
    """Register access errors"""
    pass


class ExecutionException(ProcessorException):
    """General execution errors"""
    pass


class ProcessorErrorHandler:
    """
    Centralized error handling για τον processor
    
    Αποφασίζει αν θα πετάξει exception ή θα κάνει graceful recovery
    """
    
    def __init__(self, strict_mode=False):
        """
        Args:
            strict_mode (bool): Αν True, πετάει exceptions. Αν False, graceful recovery
        """
        self.strict_mode = strict_mode
        self.error_count = 0
        self.error_log = []
    
    def handle_memory_error(self, address: int, operation: str, pc: int = None):
        """Handle memory access errors"""
        message = f"Invalid memory {operation} at address 0x{address:04X}"
        self._log_error("MEMORY", message, pc)
        
        if self.strict_mode:
            raise MemoryException(message, pc)
        else:
            print(f"⚠️  {message} - Returning 0")
            return 0
    
    def handle_invalid_instruction(self, instruction: int, pc: int = None):
        """Handle invalid instruction errors"""
        message = f"Unknown instruction 0x{instruction:04X}"
        self._log_error("INSTRUCTION", message, pc)
        
        if self.strict_mode:
            raise InvalidInstructionException(message, pc, instruction)
        else:
            print(f"⚠️  {message} - Treating as NOP")
            return None  # Will be treated as NOP
    
    def handle_register_error(self, reg_num: int, operation: str, pc: int = None):
        """Handle register access errors"""
        message = f"Invalid register {operation}: x{reg_num}"
        self._log_error("REGISTER", message, pc)
        
        if self.strict_mode:
            raise RegisterException(message, pc)
        else:
            print(f"⚠️  {message} - Ignoring operation")
            return False
    
    def handle_execution_error(self, message: str, pc: int = None, instruction: int = None):
        """Handle general execution errors"""
        self._log_error("EXECUTION", message, pc)
        
        if self.strict_mode:
            raise ExecutionException(message, pc, instruction)
        else:
            print(f"⚠️  {message} - Continuing execution")
            return None
    
    def _log_error(self, error_type: str, message: str, pc: int = None):
        """Log error internally"""
        self.error_count += 1
        error_entry = {
            'count': self.error_count,
            'type': error_type,
            'message': message,
            'pc': pc,
            'timestamp': self.error_count  # Simple counter
        }
        self.error_log.append(error_entry)
        
        # Keep only last 10 errors
        if len(self.error_log) > 10:
            self.error_log.pop(0)
    
    def get_error_summary(self):
        """Get summary of all errors"""
        if not self.error_log:
            return "No errors recorded"
        
        summary = f"Total errors: {self.error_count}\n"
        summary += "Recent errors:\n"
        
        for error in self.error_log[-5:]:  # Last 5 errors
            pc_str = f" (PC: 0x{error['pc']:04X})" if error['pc'] is not None else ""
            summary += f"  {error['count']}. {error['type']}: {error['message']}{pc_str}\n"
        
        return summary
    
    def reset_errors(self):
        """Reset error log"""
        self.error_count = 0
        self.error_log = []


# Enhanced Memory classes με error handling
class EnhancedDataMemory:
    """DataMemory με προσθήκη error handling"""
    
    def __init__(self, size=1024, base_address=0x1000, error_handler=None):
        self.size = size
        self.base_address = base_address
        self.memory = [0] * size
        self.error_handler = error_handler or ProcessorErrorHandler()
    
    def read_word(self, address: int, pc: int = None) -> int:
        """Read με error handling"""
        if not self._is_valid_address(address):
            return self.error_handler.handle_memory_error(address, "read", pc)
        
        index = address - self.base_address
        return self.memory[index]
    
    def write_word(self, address: int, value: int, pc: int = None) -> bool:
        """Write με error handling"""
        if not self._is_valid_address(address):
            self.error_handler.handle_memory_error(address, "write", pc)
            return False
        
        index = address - self.base_address
        self.memory[index] = value & 0xFFFF
        return True
    
    def find_non_zero(self):
        """Find all non-zero values in memory"""
        non_zero = []
        for i, value in enumerate(self.memory):
            if value != 0:
                address = self.base_address + i
                non_zero.append((address, value))
        return non_zero

    def clear_memory(self):
        """Clear all memory"""
        self.memory = [0] * self.size
        print("🧹 Data memory cleared")
    
    def get_statistics(self):
        """Get memory statistics"""
        return {
            'total_accesses': self.access_count if hasattr(self, 'access_count') else 0,
            'reads': self.read_count if hasattr(self, 'read_count') else 0,
            'writes': self.write_count if hasattr(self, 'write_count') else 0,
            'size': self.size,
            'base_address': self.base_address
        }
    
    def _is_valid_address(self, address: int) -> bool:
        """Check if address is valid"""
        return self.base_address <= address < self.base_address + self.size


class EnhancedInstructionMemory:
    """InstructionMemory με προσθήκη error handling"""
    
    def __init__(self, size=1024, error_handler=None):
        self.size = size
        self.memory = [0] * size
        self.program_size = 0
        self.error_handler = error_handler or ProcessorErrorHandler()
    
    def read_instruction(self, address: int) -> int:
        """Read instruction με error handling"""
        if not (0 <= address < self.size):
            return self.error_handler.handle_memory_error(address, "instruction fetch", address)
        
        return self.memory[address]
    
    def get_program_size(self):
        """Get the size of loaded program"""
        return self.program_size

    def load_program(self, instructions, start_address=0):
        """Load program into memory"""
        if start_address < 0 or start_address >= self.size:
            if hasattr(self, 'error_handler'):
                self.error_handler.handle_execution_error(
                    f"Invalid program start address: 0x{start_address:04X}"
                )
            return False
        
        if len(instructions) + start_address > self.size:
            if hasattr(self, 'error_handler'):
                self.error_handler.handle_execution_error(
                    f"Program too large: {len(instructions)} instructions"
                )
            return False
        
        # Clear and load
        self.memory = [0] * self.size
        for i, instruction in enumerate(instructions):
            self.memory[start_address + i] = instruction & 0xFFFF
        
        self.program_size = len(instructions)
        return True
    
    def load_program(self, instructions: list, start_address=0):
        """Load program με validation"""
        if start_address < 0 or start_address >= self.size:
            self.error_handler.handle_execution_error(
                f"Invalid program start address: 0x{start_address:04X}"
            )
            return False
        
        if len(instructions) + start_address > self.size:
            self.error_handler.handle_execution_error(
                f"Program too large: {len(instructions)} instructions"
            )
            return False
        
        # Clear and load
        self.memory = [0] * self.size
        for i, instruction in enumerate(instructions):
            self.memory[start_address + i] = instruction & 0xFFFF
        
        self.program_size = len(instructions)
        return True


# Test functions
def test_error_handling():
    """Test error handling functionality"""
    print("🧪 Testing Error Handling")
    print("="*40)
    
    # Test strict mode
    print("\n1. Testing Strict Mode (exceptions):")
    strict_handler = ProcessorErrorHandler(strict_mode=True)
    
    try:
        strict_handler.handle_memory_error(0xFFFF, "read", pc=0x0010)
    except MemoryException as e:
        print(f"   ✅ Caught exception: {e}")
    
    # Test graceful mode  
    print("\n2. Testing Graceful Mode (recovery):")
    graceful_handler = ProcessorErrorHandler(strict_mode=False)
    
    result = graceful_handler.handle_memory_error(0xFFFF, "read", pc=0x0010)
    print(f"   ✅ Graceful recovery returned: {result}")
    
    # Test multiple errors
    print("\n3. Testing Multiple Errors:")
    graceful_handler.handle_invalid_instruction(0xDEAD, pc=0x0020)
    graceful_handler.handle_register_error(99, "write", pc=0x0030)
    
    print("\n4. Error Summary:")
    print(graceful_handler.get_error_summary())
    
    # Test enhanced memory
    print("\n5. Testing Enhanced Memory:")
    memory = EnhancedDataMemory(size=10, error_handler=graceful_handler)
    
    # Valid access
    memory.write_word(0x1000, 0x1234)
    value = memory.read_word(0x1000)
    print(f"   Valid access: wrote 0x1234, read 0x{value:04X}")
    
    # Invalid access
    memory.write_word(0x2000, 0x5678)  # Out of range
    value = memory.read_word(0x2000)   # Out of range
    
    print("\n6. Final Error Summary:")
    print(graceful_handler.get_error_summary())


if __name__ == "__main__":
    test_error_handling()