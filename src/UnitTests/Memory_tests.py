
"""
Unit Tests για το Memory System

Περιλαμβάνει:
- Test InstructionMemory functionality
- Test DataMemory functionality
- Test binary file loading
- Test address translation
- Test error handling
- Test memory statistics
"""

import os
import sys
import tempfile
from test_utils import add_src_to_path, configure_utf8_stdio

# Προσθήκη του parent directory στο Python path
configure_utf8_stdio()
add_src_to_path()

from Memory import InstructionMemory, DataMemory


class MemoryTests:
    """Test suite για το Memory System"""
    
    def __init__(self):
        self.test_count = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_test(self, test_name: str, test_func):
        """Εκτελεί ένα test"""
        self.test_count += 1
        print(f"\n🧪 Test {self.test_count}: {test_name}")
        print("─" * 50)
        
        try:
            test_func()
            self.passed_tests += 1
            print(f"✅ PASSED: {test_name}")
        except Exception as e:
            self.failed_tests += 1
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}")
    
    def test_instruction_memory_basic(self):
        """Test βασικών λειτουργιών InstructionMemory"""
        print("Testing InstructionMemory basic operations...")
        
        imem = InstructionMemory(size=256)
        
        # Test initial state
        if imem.size != 256:
            raise AssertionError(f"Size should be 256, got {imem.size}")
        
        if imem.program_size != 0:
            raise AssertionError("Program size should be 0 initially")
        
        # Test reading from empty memory
        instruction = imem.read_instruction(0)
        if instruction != 0:
            raise AssertionError("Empty memory should return 0")
        
        # Test loading program
        test_program = [0x510A, 0x5205, 0x0312, 0xF000]
        success = imem.load_program(test_program)
        if not success:
            raise AssertionError("Program loading should succeed")
        
        if imem.program_size != 4:
            raise AssertionError(f"Program size should be 4, got {imem.program_size}")
        
        # Test reading loaded instructions
        for i, expected in enumerate(test_program):
            instruction = imem.read_instruction(i)
            if instruction != expected:
                raise AssertionError(f"Instruction {i}: expected 0x{expected:04X}, got 0x{instruction:04X}")
        
        print(f"   ✓ Memory initialization works")
        print(f"   ✓ Program loading works")
        print(f"   ✓ Instruction reading works")
    
    def test_instruction_memory_boundary(self):
        """Test boundary conditions για InstructionMemory"""
        print("Testing InstructionMemory boundary conditions...")
        
        imem = InstructionMemory(size=10)  # Small memory για testing
        
        # Test invalid addresses
        invalid_addresses = [-1, 10, 100, 0xFFFF]
        for addr in invalid_addresses:
            instruction = imem.read_instruction(addr)
            if instruction != 0:
                raise AssertionError(f"Invalid address {addr} should return 0")
        
        # Test program too large
        large_program = [0x1234] * 15  # Larger than memory
        success = imem.load_program(large_program)
        if success:
            raise AssertionError("Loading oversized program should fail")
        
        # Test invalid start address
        success = imem.load_program([0x1234], start_address=20)
        if success:
            raise AssertionError("Invalid start address should fail")
        
        # Test maximum capacity
        max_program = [0x1000 + i for i in range(10)]
        success = imem.load_program(max_program)
        if not success:
            raise AssertionError("Loading max capacity program should succeed")
        
        print(f"   ✓ Invalid address handling works")
        print(f"   ✓ Oversized program detection works")
        print(f"   ✓ Maximum capacity works")
    
    def test_instruction_memory_binary_file(self):
        """Test binary file loading για InstructionMemory"""
        print("Testing InstructionMemory binary file operations...")
        
        imem = InstructionMemory(size=256)
        
        # Create temporary binary file
        test_data = [0x510A, 0x5205, 0x0312, 0xF000]
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as f:
            for instruction in test_data:
                f.write(instruction.to_bytes(2, byteorder='little'))
            temp_filename = f.name
        
        try:
            # Test loading binary file
            success = imem.load_from_binary_file(temp_filename)
            if not success:
                raise AssertionError("Binary file loading should succeed")
            
            # Verify loaded data
            for i, expected in enumerate(test_data):
                instruction = imem.read_instruction(i)
                if instruction != expected:
                    raise AssertionError(f"Binary data {i}: expected 0x{expected:04X}, got 0x{instruction:04X}")
            
            # Test loading non-existent file
            success = imem.load_from_binary_file("non_existent_file.bin")
            if success:
                raise AssertionError("Loading non-existent file should fail")
            
            print(f"   ✓ Binary file loading works")
            print(f"   ✓ Data verification works")
            print(f"   ✓ Error handling works")
            
        finally:
            # Cleanup
            os.unlink(temp_filename)
    
    def test_data_memory_basic(self):
        """Test βασικών λειτουργιών DataMemory"""
        print("Testing DataMemory basic operations...")
        
        dmem = DataMemory(size=256, base_address=0x1000)
        
        # Test initial state
        if dmem.size != 256:
            raise AssertionError(f"Size should be 256, got {dmem.size}")
        
        if dmem.base_address != 0x1000:
            raise AssertionError(f"Base address should be 0x1000, got 0x{dmem.base_address:04X}")
        
        # Test reading from empty memory
        value = dmem.read_word(0x1000)
        if value != 0:
            raise AssertionError("Empty memory should return 0")
        
        # Test writing and reading
        test_data = [
            (0x1000, 0x1234),
            (0x1001, 0x5678),
            (0x10FF, 0xABCD)  # Last valid address
        ]
        
        for address, value in test_data:
            success = dmem.write_word(address, value)
            if not success:
                raise AssertionError(f"Write to 0x{address:04X} should succeed")
            
            read_value = dmem.read_word(address)
            if read_value != value:
                raise AssertionError(f"Address 0x{address:04X}: expected 0x{value:04X}, got 0x{read_value:04X}")
        
        print(f"   ✓ Memory initialization works")
        print(f"   ✓ Write operations work")
        print(f"   ✓ Read operations work")
    
    def test_data_memory_address_translation(self):
        """Test address translation για DataMemory"""
        print("Testing DataMemory address translation...")
        
        dmem = DataMemory(size=10, base_address=0x2000)
        
        # Test valid addresses
        valid_addresses = [0x2000, 0x2005, 0x2009]  # 0x2009 = last valid
        for addr in valid_addresses:
            success = dmem.write_word(addr, 0x1234)
            if not success:
                raise AssertionError(f"Valid address 0x{addr:04X} should succeed")
        
        # Test invalid addresses (outside range)
        invalid_addresses = [0x1FFF, 0x200A, 0x3000, 0x0000]
        for addr in invalid_addresses:
            success = dmem.write_word(addr, 0x1234)
            if success:
                raise AssertionError(f"Invalid address 0x{addr:04X} should fail")
            
            value = dmem.read_word(addr)
            if value != 0:
                raise AssertionError(f"Invalid read should return 0, got 0x{value:04X}")
        
        print(f"   ✓ Valid address translation works")
        print(f"   ✓ Invalid address detection works")
    
    def test_data_memory_statistics(self):
        """Test statistics tracking για DataMemory"""
        print("Testing DataMemory statistics...")
        
        dmem = DataMemory(size=100)
        
        # Initial statistics
        stats = dmem.get_statistics()
        if stats['total_accesses'] != 0:
            raise AssertionError("Initial access count should be 0")
        
        if stats['reads'] != 0 or stats['writes'] != 0:
            raise AssertionError("Initial read/write counts should be 0")
        
        # Perform operations
        dmem.write_word(0x1000, 0x1111)  # 1 write
        dmem.write_word(0x1001, 0x2222)  # 1 write
        dmem.read_word(0x1000)           # 1 read
        dmem.read_word(0x1001)           # 1 read
        dmem.read_word(0x1000)           # 1 read
        
        # Check statistics
        stats = dmem.get_statistics()
        expected_reads = 3
        expected_writes = 2
        expected_total = 5
        
        if stats['reads'] != expected_reads:
            raise AssertionError(f"Expected {expected_reads} reads, got {stats['reads']}")
        
        if stats['writes'] != expected_writes:
            raise AssertionError(f"Expected {expected_writes} writes, got {stats['writes']}")
        
        if stats['total_accesses'] != expected_total:
            raise AssertionError(f"Expected {expected_total} total accesses, got {stats['total_accesses']}")
        
        print(f"   ✓ Statistics initialization works")
        print(f"   ✓ Read/write counting works")
        print(f"   ✓ Total access counting works")
    
    def test_data_memory_value_masking(self):
        """Test 16-bit value masking για DataMemory"""
        print("Testing DataMemory 16-bit value masking...")
        
        dmem = DataMemory(size=10)
        
        # Test large values that should be masked
        test_cases = [
            (0x10000, 0x0000),   # Should wrap to 0
            (0x12345, 0x2345),   # Should mask to lower 16 bits
            (0xFFFFF, 0xFFFF),   # Should mask to 0xFFFF
            (0xABCDE, 0xBCDE)    # Should mask to lower 16 bits
        ]
        
        for input_value, expected_output in test_cases:
            dmem.write_word(0x1000, input_value)
            stored_value = dmem.read_word(0x1000)
            
            if stored_value != expected_output:
                raise AssertionError(f"Input 0x{input_value:X}: expected 0x{expected_output:04X}, got 0x{stored_value:04X}")
        
        print(f"   ✓ Large value masking works")
        print(f"   ✓ 16-bit boundary enforcement works")
    
    def test_data_memory_clear_and_search(self):
        """Test clear και search λειτουργίες για DataMemory"""
        print("Testing DataMemory clear and search operations...")
        
        dmem = DataMemory(size=20)
        
        # Write some data
        test_data = [(0x1000, 0x1111), (0x1005, 0x2222), (0x1010, 0x3333)]
        for addr, value in test_data:
            dmem.write_word(addr, value)
        
        # Test find_non_zero
        non_zero = dmem.find_non_zero()
        if len(non_zero) != 3:
            raise AssertionError(f"Should find 3 non-zero values, found {len(non_zero)}")
        
        for (addr, value), (expected_addr, expected_value) in zip(non_zero, test_data):
            if addr != expected_addr or value != expected_value:
                raise AssertionError(f"Found (0x{addr:04X}, 0x{value:04X}), expected (0x{expected_addr:04X}, 0x{expected_value:04X})")
        
        # Test clear memory
        dmem.clear_memory()
        
        # Verify all values are 0
        for addr, _ in test_data:
            value = dmem.read_word(addr)
            if value != 0:
                raise AssertionError(f"After clear, address 0x{addr:04X} should be 0, got 0x{value:04X}")
        
        # Test find_non_zero after clear
        non_zero_after_clear = dmem.find_non_zero()
        if len(non_zero_after_clear) != 0:
            raise AssertionError(f"After clear, should find 0 non-zero values, found {len(non_zero_after_clear)}")
        
        print(f"   ✓ Non-zero value search works")
        print(f"   ✓ Memory clear works")
        print(f"   ✓ Search after clear works")
    
    def test_memory_integration(self):
        """Test integration μεταξύ InstructionMemory και DataMemory"""
        print("Testing InstructionMemory and DataMemory integration...")
        
        # Simulate realistic usage
        imem = InstructionMemory(size=64)
        dmem = DataMemory(size=64)
        
        # Load a program that uses both memories
        program = [
            0x510A,  # ADDI x1, x0, 10
            0x5205,  # ADDI x2, x0, 5
            0x0312,  # ADD x3, x1, x2
            0x9320,  # SW x3, 0(x2)     # Store result to data memory
            0x8420,  # LW x4, 0(x2)     # Load from data memory
            0xF000   # HALT
        ]
        
        success = imem.load_program(program)
        if not success:
            raise AssertionError("Program loading should succeed")
        
        # Simulate execution flow
        pc = 0
        
        # Fetch first instruction
        inst1 = imem.read_instruction(pc)
        if inst1 != 0x510A:
            raise AssertionError(f"First instruction should be 0x510A, got 0x{inst1:04X}")
        
        # Simulate SW operation (store to data memory)
        dmem.write_word(0x1005, 15)  # Store result of ADD (10+5=15)
        
        # Simulate LW operation (load from data memory)
        loaded_value = dmem.read_word(0x1005)
        if loaded_value != 15:
            raise AssertionError(f"Loaded value should be 15, got {loaded_value}")
        
        # Check that memories are independent
        imem_size = imem.get_program_size()
        dmem_stats = dmem.get_statistics()
        
        if imem_size != 6:
            raise AssertionError(f"Instruction memory should have 6 instructions, got {imem_size}")
        
        if dmem_stats['total_accesses'] != 2:  # 1 write + 1 read
            raise AssertionError(f"Data memory should have 2 accesses, got {dmem_stats['total_accesses']}")
        
        print(f"   ✓ Program loading and execution simulation works")
        print(f"   ✓ Independent memory operation works")
        print(f"   ✓ Memory statistics tracking works")
    
    def run_all_tests(self):
        """Εκτελεί όλα τα tests"""
        print("=" * 60)
        print("🧪 MEMORY SYSTEM UNIT TESTS")
        print("=" * 60)
        
        # Εκτέλεση όλων των tests
        self.run_test("Instruction Memory Basic", self.test_instruction_memory_basic)
        self.run_test("Instruction Memory Boundary", self.test_instruction_memory_boundary)
        self.run_test("Instruction Memory Binary File", self.test_instruction_memory_binary_file)
        self.run_test("Data Memory Basic", self.test_data_memory_basic)
        self.run_test("Data Memory Address Translation", self.test_data_memory_address_translation)
        self.run_test("Data Memory Statistics", self.test_data_memory_statistics)
        self.run_test("Data Memory Value Masking", self.test_data_memory_value_masking)
        self.run_test("Data Memory Clear and Search", self.test_data_memory_clear_and_search)
        self.run_test("Memory Integration", self.test_memory_integration)
        
        # Εμφάνιση αποτελεσμάτων
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        success_rate = (self.passed_tests / self.test_count) * 100 if self.test_count > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! 🎉")
        else:
            print(f"\n⚠️  {self.failed_tests} TESTS FAILED")
        
        print("=" * 60)
        
        return self.failed_tests == 0


def run_individual_test(test_name: str):
    """Εκτελεί ένα συγκεκριμένο test"""
    tests = MemoryTests()
    
    test_methods = {
        'imem_basic': tests.test_instruction_memory_basic,
        'imem_boundary': tests.test_instruction_memory_boundary,
        'imem_binary': tests.test_instruction_memory_binary_file,
        'dmem_basic': tests.test_data_memory_basic,
        'dmem_address': tests.test_data_memory_address_translation,
        'dmem_stats': tests.test_data_memory_statistics,
        'dmem_mask': tests.test_data_memory_value_masking,
        'dmem_clear': tests.test_data_memory_clear_and_search,
        'integration': tests.test_memory_integration
    }
    
    if test_name.lower() in test_methods:
        tests.run_test(test_name.capitalize(), test_methods[test_name.lower()])
    else:
        print(f"❌ Unknown test: {test_name}")
        print("Available tests:", list(test_methods.keys()))


def main():
    """Κύρια συνάρτηση"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        run_individual_test(test_name)
    else:
        # Εκτέλεση όλων των tests
        tests = MemoryTests()
        success = tests.run_all_tests()
        
        # Exit code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
