
"""
Unit Tests για το RegisterFile

Περιλαμβάνει:
- Test βασικών read/write operations
- Test x0 protection (hard-wired zero)
- Test ABI register names
- Test boundary conditions
- Test register information
- Test reset functionality
"""

import os
import sys

# Προσθήκη του parent directory στο Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RegisterFile import RegisterFile, Register


class RegisterFileTests:
    """Test suite για το RegisterFile"""
    
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
    
    def test_basic_read_write(self):
        """Test βασικών read/write operations"""
        print("Testing basic read/write operations...")
        
        rf = RegisterFile()
        
        # Test initial state (all zeros)
        for i in range(16):
            value = rf.read(i)
            if value != 0:
                raise AssertionError(f"Register x{i} should be 0 initially, got {value}")
        
        # Test writing to various registers
        test_values = [
            (1, 0x1234),   # ra
            (2, 0x8000),   # sp
            (10, 42),      # a0
            (11, 100),     # a1
            (5, 0xFFFF),   # t0
            (15, 255)      # a7
        ]
        
        for reg_num, value in test_values:
            success = rf.write(reg_num, value)
            if not success:
                raise AssertionError(f"Write to x{reg_num} should succeed")
            
            read_value = rf.read(reg_num)
            if read_value != value:
                raise AssertionError(f"x{reg_num}: Expected {value}, got {read_value}")
        
        print(f"   ✓ Initial state correct (all zeros)")
        print(f"   ✓ Write operations successful")
        print(f"   ✓ Read operations return correct values")
    
    def test_x0_protection(self):
        """Test x0 protection (hard-wired zero)"""
        print("Testing x0 protection...")
        
        rf = RegisterFile()
        
        # Test that x0 is initially 0
        if rf.read(0) != 0:
            raise AssertionError("x0 should be 0 initially")
        
        # Test that writing to x0 fails
        success = rf.write(0, 123)
        if success:
            raise AssertionError("Writing to x0 should fail")
        
        # Test that x0 remains 0 after attempted write
        if rf.read(0) != 0:
            raise AssertionError("x0 should remain 0 after write attempt")
        
        # Test multiple write attempts
        for value in [1, 0xFFFF, 42, 999]:
            success = rf.write(0, value)
            if success:
                raise AssertionError(f"Writing {value} to x0 should fail")
            
            if rf.read(0) != 0:
                raise AssertionError(f"x0 should remain 0 after writing {value}")
        
        print(f"   ✓ x0 is initially 0")
        print(f"   ✓ Writing to x0 fails")
        print(f"   ✓ x0 remains 0 after write attempts")
    
    def test_abi_register_names(self):
        """Test ABI register names resolution"""
        print("Testing ABI register names...")
        
        rf = RegisterFile()
        
        # Test ABI name mapping
        abi_tests = [
            ('zero', 0), ('ra', 1), ('sp', 2), ('gp', 3), ('tp', 4),
            ('t0', 5), ('t1', 6), ('t2', 7), ('s0', 8), ('s1', 9),
            ('a0', 10), ('a1', 11), ('a2', 12), ('a3', 13), ('a4', 14), ('a7', 15)
        ]
        
        for abi_name, expected_reg_num in abi_tests:
            reg_num = rf.get_register_by_name(abi_name)
            if reg_num != expected_reg_num:
                raise AssertionError(f"ABI '{abi_name}' should map to {expected_reg_num}, got {reg_num}")
        
        # Test x-style names
        for i in range(16):
            reg_num = rf.get_register_by_name(f'x{i}')
            if reg_num != i:
                raise AssertionError(f"'x{i}' should map to {i}, got {reg_num}")
        
        # Test case insensitivity
        case_tests = [('RA', 1), ('SP', 2), ('A0', 10), ('X5', 5)]
        for name, expected in case_tests:
            reg_num = rf.get_register_by_name(name)
            if reg_num != expected:
                raise AssertionError(f"'{name}' should map to {expected}, got {reg_num}")
        
        # Test invalid names
        invalid_names = ['x16', 'x20', 'invalid', 'xyz', '']
        for name in invalid_names:
            reg_num = rf.get_register_by_name(name)
            if reg_num != -1:
                raise AssertionError(f"Invalid name '{name}' should return -1, got {reg_num}")
        
        print(f"   ✓ ABI names map correctly")
        print(f"   ✓ x-style names work")
        print(f"   ✓ Case insensitive mapping works")
        print(f"   ✓ Invalid names return -1")
    
    def test_boundary_conditions(self):
        """Test boundary conditions"""
        print("Testing boundary conditions...")
        
        rf = RegisterFile()
        
        # Test invalid register numbers
        invalid_reads = [-1, 16, 20, 100]
        for reg_num in invalid_reads:
            value = rf.read(reg_num)
            if value != 0:
                raise AssertionError(f"Reading invalid register {reg_num} should return 0, got {value}")
        
        invalid_writes = [-1, 16, 20, 100]
        for reg_num in invalid_writes:
            success = rf.write(reg_num, 123)
            if success:
                raise AssertionError(f"Writing to invalid register {reg_num} should fail")
        
        # Test 16-bit value masking
        large_values = [0x10000, 0x12345, 0xFFFFF]
        for value in large_values:
            rf.write(5, value)  # Write to t0
            read_value = rf.read(5)
            expected = value & 0xFFFF
            if read_value != expected:
                raise AssertionError(f"Large value 0x{value:X} should be masked to 0x{expected:04X}, got 0x{read_value:04X}")
        
        # Test maximum and minimum values
        rf.write(10, 0xFFFF)  # Maximum 16-bit value
        if rf.read(10) != 0xFFFF:
            raise AssertionError("Maximum value 0xFFFF not stored correctly")
        
        rf.write(10, 0x0000)  # Minimum value
        if rf.read(10) != 0x0000:
            raise AssertionError("Minimum value 0x0000 not stored correctly")
        
        print(f"   ✓ Invalid register numbers handled correctly")
        print(f"   ✓ Large values are properly masked to 16-bit")
        print(f"   ✓ Maximum and minimum values work")
    
    def test_register_information(self):
        """Test register information retrieval"""
        print("Testing register information...")
        
        rf = RegisterFile()
        
        # Test valid register info
        expected_info = [
            (0, "x0", "zero", "Hard-wired zero"),
            (1, "x1", "ra", "Return address"),
            (2, "x2", "sp", "Stack pointer"),
            (10, "x10", "a0", "Function argument 0 / Return value 0"),
            (15, "x15", "a7", "System call number")
        ]
        
        for reg_num, exp_name, exp_abi, exp_purpose in expected_info:
            name, abi_name, purpose = rf.get_register_info(reg_num)
            if name != exp_name:
                raise AssertionError(f"x{reg_num} name: Expected '{exp_name}', got '{name}'")
            if abi_name != exp_abi:
                raise AssertionError(f"x{reg_num} ABI: Expected '{exp_abi}', got '{abi_name}'")
            if purpose != exp_purpose:
                raise AssertionError(f"x{reg_num} purpose: Expected '{exp_purpose}', got '{purpose}'")
        
        # Test invalid register info
        invalid_regs = [-1, 16, 20]
        for reg_num in invalid_regs:
            name, abi_name, purpose = rf.get_register_info(reg_num)
            if name != "INVALID":
                raise AssertionError(f"Invalid register {reg_num} should return 'INVALID' name")
        
        print(f"   ✓ Valid register information correct")
        print(f"   ✓ Invalid register information handled")
    
    def test_reset_functionality(self):
        """Test reset functionality"""
        print("Testing reset functionality...")
        
        rf = RegisterFile()
        
        # Write to several registers
        test_data = [(1, 100), (2, 200), (5, 0xFFFF), (10, 42), (15, 255)]
        for reg_num, value in test_data:
            rf.write(reg_num, value)
        
        # Verify values are written
        for reg_num, value in test_data:
            if rf.read(reg_num) != value:
                raise AssertionError(f"Setup failed: x{reg_num} should be {value}")
        
        # Reset all registers
        rf.reset_all()
        
        # Verify all registers are 0 (including x0)
        for i in range(16):
            value = rf.read(i)
            if value != 0:
                raise AssertionError(f"After reset, x{i} should be 0, got {value}")
        
        # Test that x0 is still protected after reset
        success = rf.write(0, 123)
        if success:
            raise AssertionError("x0 should still be protected after reset")
        
        print(f"   ✓ Reset clears all registers to 0")
        print(f"   ✓ x0 protection maintained after reset")
    
    def test_individual_register(self):
        """Test individual Register class"""
        print("Testing individual Register class...")
        
        # Test normal register
        reg = Register("x1", "ra", "Return address", 0, False)
        
        # Test initial state
        if reg.read() != 0:
            raise AssertionError("Register should be 0 initially")
        
        # Test write/read
        success = reg.write(123)
        if not success:
            raise AssertionError("Write should succeed for normal register")
        
        if reg.read() != 123:
            raise AssertionError("Read should return written value")
        
        # Test 16-bit masking
        reg.write(0x12345)
        expected = 0x2345
        if reg.read() != expected:
            raise AssertionError(f"Large value should be masked: expected 0x{expected:04X}, got 0x{reg.read():04X}")
        
        # Test read-only register (x0)
        ro_reg = Register("x0", "zero", "Hard-wired zero", 0, True)
        
        success = ro_reg.write(123)
        if success:
            raise AssertionError("Write should fail for read-only register")
        
        if ro_reg.read() != 0:
            raise AssertionError("Read-only register should remain 0")
        
        # Test reset
        reg.reset()
        if reg.read() != 0:
            raise AssertionError("Register should be 0 after reset")
        
        # Test read-only register reset (should not change)
        ro_reg.reset()
        if ro_reg.read() != 0:
            raise AssertionError("Read-only register should remain 0 after reset")
        
        print(f"   ✓ Normal register operations work")
        print(f"   ✓ Read-only register protection works")
        print(f"   ✓ 16-bit value masking works")
        print(f"   ✓ Reset functionality works")
    
    def test_edge_cases(self):
        """Test edge cases"""
        print("Testing edge cases...")
        
        rf = RegisterFile()
        
        # Test writing 0 to registers
        rf.write(5, 123)  # First write non-zero
        rf.write(5, 0)    # Then write zero
        if rf.read(5) != 0:
            raise AssertionError("Writing 0 should work")
        
        # Test multiple writes to same register
        values = [1, 100, 0xFFFF, 42, 0]
        for value in values:
            rf.write(10, value)
            if rf.read(10) != value:
                raise AssertionError(f"Multiple writes failed at value {value}")
        
        # Test all registers simultaneously
        for i in range(1, 16):  # Skip x0
            rf.write(i, i * 100)
        
        for i in range(1, 16):
            expected = i * 100
            if rf.read(i) != expected:
                raise AssertionError(f"Simultaneous write test failed for x{i}")
        
        print(f"   ✓ Writing 0 works correctly")
        print(f"   ✓ Multiple writes to same register work")
        print(f"   ✓ All registers can be written simultaneously")
    
    def run_all_tests(self):
        """Εκτελεί όλα τα tests"""
        print("=" * 60)
        print("🧪 REGISTER FILE UNIT TESTS")
        print("=" * 60)
        
        # Εκτέλεση όλων των tests
        self.run_test("Basic Read/Write", self.test_basic_read_write)
        self.run_test("x0 Protection", self.test_x0_protection)
        self.run_test("ABI Register Names", self.test_abi_register_names)
        self.run_test("Boundary Conditions", self.test_boundary_conditions)
        self.run_test("Register Information", self.test_register_information)
        self.run_test("Reset Functionality", self.test_reset_functionality)
        self.run_test("Individual Register", self.test_individual_register)
        self.run_test("Edge Cases", self.test_edge_cases)
        
        # Εμφάνιση αποτελεσμάτων
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {self.test_count}")
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
    tests = RegisterFileTests()
    
    test_methods = {
        'basic': tests.test_basic_read_write,
        'x0': tests.test_x0_protection,
        'abi': tests.test_abi_register_names,
        'boundary': tests.test_boundary_conditions,
        'info': tests.test_register_information,
        'reset': tests.test_reset_functionality,
        'register': tests.test_individual_register,
        'edge': tests.test_edge_cases
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
        tests = RegisterFileTests()
        success = tests.run_all_tests()
        
        # Exit code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()