class ALU:
    """
    Arithmetic Logic Unit for 16-bit RISC-V processor
    
    Supports:
    - Arithmetic operations: ADD, SUB
    - Logic operations: AND, OR, XOR  
    - Comparison operations: EQ (equal), NE (not equal)
    - Flag generation: Zero, Overflow, Negative
    """
    
    # Operation codes (3-bit)
    ALU_ADD = 0b000    # Addition
    ALU_SUB = 0b001    # Subtraction
    ALU_AND = 0b010    # Bitwise AND
    ALU_OR  = 0b011    # Bitwise OR
    ALU_XOR = 0b100    # Bitwise XOR
    ALU_EQ  = 0b101    # Equal comparison
    ALU_NE  = 0b110    # Not equal comparison
    
    def __init__(self):
        """
        Initialize ALU with default state
        
        All state variables start at safe default values:
        - Results start at 0
        - Flags start as False (no special conditions)
        - Counters start at 0
        """
        # Result tracking
        self.last_result = 0           # Last operation result (16-bit)
        
        # Status flags
        self.zero_flag = False         # True when result is 0
        self.overflow_flag = False     # True when arithmetic overflow occurs
        self.negative_flag = False     # True when result is negative (MSB = 1)
        
        # Statistics
        self.operation_count = 0       # Number of operations performed
        self.operation_history = []    # History of recent operations (for debugging)
    
    def execute(self, a, b, operation):
        """
        Main ALU execution method
        
        Args:
            a (int): First operand (16-bit)
            b (int): Second operand (16-bit)  
            operation (int): Operation code (3-bit)
            
        Returns:
            int: Result of operation (16-bit)
            
        Raises:
            ValueError: If operation code is invalid
        """
        # Ensure inputs are 16-bit
        a = a & 0xFFFF
        b = b & 0xFFFF
        
        # Reset flags before operation
        self.overflow_flag = False
        
        # Get operation function
        op_function = self.recognize_operation(operation)
        if op_function is None:
            raise ValueError(f"Unknown operation code: {operation}")
        
        # Execute operation
        result = op_function(a, b)
        
        # Update ALU state
        self.last_result = result & 0xFFFF  # Ensure 16-bit result
        self.operation_count += 1
        self._update_flags(self.last_result)
        self._log_operation(a, b, operation, self.last_result)
        
        return self.last_result
    
    def add(self, a, b):
        """
        16-bit addition with overflow detection
        
        Args:
            a, b (int): 16-bit operands
            
        Returns:
            int: Sum (may be > 16-bit before masking)
        """
        result = a + b
        
        # Check for overflow (result exceeds 16-bit range)
        if result > 0xFFFF:
            self.overflow_flag = True
        
        return result
    
    def sub(self, a, b):
        """
        16-bit subtraction with underflow handling
        
        Args:
            a, b (int): 16-bit operands
            
        Returns:
            int: Difference (converted to unsigned if negative)
        """
        result = a - b
        
        # Handle negative results using two's complement
        if result < 0:
            result = result + 0x10000  # Convert to unsigned 16-bit representation
        
        return result
    
    def and_op(self, a, b):
        """Bitwise AND operation"""
        return a & b
    
    def or_op(self, a, b):
        """Bitwise OR operation"""
        return a | b
    
    def xor(self, a, b):
        """Bitwise XOR operation"""
        return a ^ b
    
    def beq(self, a, b):
        """
        Branch if equal comparison
        
        Returns:
            int: 1 if equal, 0 if not equal
        """
        return 1 if a == b else 0
    
    def neq(self, a, b):
        """
        Branch if not equal comparison
        
        Returns:
            int: 1 if not equal, 0 if equal
        """
        return 1 if a != b else 0
    
    def recognize_operation(self, operation):
        """
        Map operation code to corresponding method
        
        Args:
            operation (int): 3-bit operation code
            
        Returns:
            function: Operation method or None if invalid
        """
        operations_map = {
            self.ALU_ADD: self.add,
            self.ALU_SUB: self.sub,
            self.ALU_AND: self.and_op,
            self.ALU_OR:  self.or_op,
            self.ALU_XOR: self.xor,
            self.ALU_EQ:  self.beq,
            self.ALU_NE:  self.neq
        }
        
        return operations_map.get(operation, None)
    
    def _update_flags(self, result):
        """
        Update status flags based on operation result
        
        Args:
            result (int): 16-bit operation result
        """
        # Zero flag: True if result is 0
        self.zero_flag = (result == 0)
        
        # Negative flag: True if MSB (bit 15) is 1
        self.negative_flag = (result & 0x8000) != 0
        
        # Note: overflow_flag is set in individual operations
    
    def _log_operation(self, a, b, operation, result):
        """
        Log operation for debugging and statistics
        
        Args:
            a, b (int): Operands
            operation (int): Operation code
            result (int): Result
        """
        operation_names = {
            self.ALU_ADD: "ADD", self.ALU_SUB: "SUB", self.ALU_AND: "AND",
            self.ALU_OR: "OR", self.ALU_XOR: "XOR", self.ALU_EQ: "EQ", self.ALU_NE: "NE"
        }
        
        log_entry = {
            'operation': operation_names.get(operation, f"OP_{operation}"),
            'operand_a': a,
            'operand_b': b,
            'result': result,
            'flags': {
                'zero': self.zero_flag,
                'overflow': self.overflow_flag,
                'negative': self.negative_flag
            }
        }
        
        self.operation_history.append(log_entry)
        
        # Keep only last 10 operations
        if len(self.operation_history) > 10:
            self.operation_history.pop(0)
    
    def get_flags(self):
        """
        Get current ALU flags
        
        Returns:
            dict: Current flag states
        """
        return {
            'zero': self.zero_flag,
            'overflow': self.overflow_flag,
            'negative': self.negative_flag
        }
    
    def reset(self):
        """Reset ALU to initial state"""
        self.last_result = 0
        self.zero_flag = False
        self.overflow_flag = False
        self.negative_flag = False
        self.operation_count = 0
        self.operation_history.clear()
    
    def get_statistics(self):
        """
        Get ALU operation statistics
        
        Returns:
            dict: Statistics about ALU usage
        """
        return {
            'total_operations': self.operation_count,
            'last_result': self.last_result,
            'current_flags': self.get_flags(),
            'history_size': len(self.operation_history)
        }
    
    def display_status(self):
        """Display current ALU status for debugging"""
        print("=" * 50)
        print("ALU STATUS")
        print("=" * 50)
        print(f"Last Result: 0x{self.last_result:04X} ({self.last_result})")
        print(f"Zero Flag:   {'✓' if self.zero_flag else '✗'}")
        print(f"Overflow:    {'✓' if self.overflow_flag else '✗'}")
        print(f"Negative:    {'✓' if self.negative_flag else '✗'}")
        print(f"Operations:  {self.operation_count}")
        print("=" * 50)
    
    def display_history(self, count=5):
        """
        Display recent operation history
        
        Args:
            count (int): Number of recent operations to show
        """
        print("=" * 60)
        print("ALU OPERATION HISTORY")
        print("=" * 60)
        
        if not self.operation_history:
            print("No operations performed yet.")
            return
        
        recent_ops = self.operation_history[-count:]
        
        for i, op in enumerate(recent_ops, 1):
            print(f"{i}. {op['operation']} 0x{op['operand_a']:04X}, 0x{op['operand_b']:04X} → 0x{op['result']:04X}")
            flags = op['flags']
            flag_str = f"   Flags: Z={flags['zero']}, O={flags['overflow']}, N={flags['negative']}"
            print(flag_str)
        
        print("=" * 60)