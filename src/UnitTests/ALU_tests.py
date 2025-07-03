
"""
Unit Tests για την ALU (Arithmetic Logic Unit)

Περιλαμβάνει:
- Test αριθμητικών πράξεων (ADD, SUB)
- Test λογικών πράξεων (AND, OR, XOR)
- Test συγκρίσεων (EQ, NE)
- Test flags (zero, overflow, negative)
- Test boundary conditions
"""

import os
import sys

# Προσθήκη του parent directory στο Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ALU import ALU


class ALUTests:
    """Test suite για την ALU"""
    
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
    
    def test_arithmetic_operations(self):
        """Test αριθμητικών πράξεων"""
        print("Testing arithmetic operations (ADD, SUB)...")
        
        alu = ALU()
        
        # Test Addition
        result = alu.execute(100, 200, ALU.ALU_ADD)
        if result != 300:
            raise AssertionError(f"ADD: Expected 300, got {result}")
        
        result = alu.execute(0xFFFF, 1, ALU.ALU_ADD)
        if result != 0:  # Should wrap around
            raise AssertionError(f"ADD overflow: Expected 0, got {result}")
        
        if not alu.overflow_flag:
            raise AssertionError("Overflow flag should be set")
        
        # Test Subtraction
        result = alu.execute(500, 300, ALU.ALU_SUB)
        if result != 200:
            raise AssertionError(f"SUB: Expected 200, got {result}")
        
        result = alu.execute(10, 20, ALU.ALU_SUB)
        # Should handle negative properly (two's complement)
        expected = 0x10000 - 10  # 65526 in unsigned
        if result != expected:
            raise AssertionError(f"SUB negative: Expected {expected}, got {result}")
        
        print(f"   ✓ Addition and subtraction work correctly")
        print(f"   ✓ Overflow detection works")
        print(f"   ✓ Negative number handling works")
    
    def test_logical_operations(self):
        """Test λογικών πράξεων"""
        print("Testing logical operations (AND, OR, XOR)...")
        
        alu = ALU()
        
        # Test AND
        result = alu.execute(0xF0F0, 0x0F0F, ALU.ALU_AND)
        if result != 0x0000:
            raise AssertionError(f"AND: Expected 0x0000, got 0x{result:04X}")
        
        result = alu.execute(0xFFFF, 0xAAAA, ALU.ALU_AND)
        if result != 0xAAAA:
            raise AssertionError(f"AND: Expected 0xAAAA, got 0x{result:04X}")
        
        # Test OR
        result = alu.execute(0xF000, 0x000F, ALU.ALU_OR)
        if result != 0xF00F:
            raise AssertionError(f"OR: Expected 0xF00F, got 0x{result:04X}")
        
        result = alu.execute(0x0000, 0x0000, ALU.ALU_OR)
        if result != 0x0000:
            raise AssertionError(f"OR: Expected 0x0000, got 0x{result:04X}")
        
        # Test XOR
        result = alu.execute(0xFFFF, 0xAAAA, ALU.ALU_XOR)
        if result != 0x5555:
            raise AssertionError(f"XOR: Expected 0x5555, got 0x{result:04X}")
        
        result = alu.execute(0x1234, 0x1234, ALU.ALU_XOR)
        if result != 0x0000:
            raise AssertionError(f"XOR: Expected 0x0000, got 0x{result:04X}")
        
        print(f"   ✓ AND, OR, XOR operations work correctly")
        print(f"   ✓ Bit manipulation works as expected")
    
    def test_comparison_operations(self):
        """Test συγκρίσεων"""
        print("Testing comparison operations (EQ, NE)...")
        
        alu = ALU()
        
        # Test Equality
        result = alu.execute(42, 42, ALU.ALU_EQ)
        if result != 1:
            raise AssertionError(f"EQ: Expected 1, got {result}")
        
        result = alu.execute(42, 43, ALU.ALU_EQ)
        if result != 0:
            raise AssertionError(f"EQ: Expected 0, got {result}")
        
        result = alu.execute(0xFFFF, 0xFFFF, ALU.ALU_EQ)
        if result != 1:
            raise AssertionError(f"EQ: Expected 1, got {result}")
        
        # Test Not Equal
        result = alu.execute(42, 43, ALU.ALU_NE)
        if result != 1:
            raise AssertionError(f"NE: Expected 1, got {result}")
        
        result = alu.execute(100, 100, ALU.ALU_NE)
        if result != 0:
            raise AssertionError(f"NE: Expected 0, got {result}")
        
        print(f"   ✓ Equality and inequality comparisons work")
        print(f"   ✓ Edge cases (0xFFFF) handled correctly")
    
    def test_flags(self):
        """Test flags (zero, overflow, negative)"""
        print("Testing flags (zero, overflow, negative)...")
        
        alu = ALU()
        
        # Test Zero Flag
        alu.execute(0, 0, ALU.ALU_ADD)
        if not alu.zero_flag:
            raise AssertionError("Zero flag should be set for 0 + 0")
        
        alu.execute(42, 0, ALU.ALU_ADD)
        if alu.zero_flag:
            raise AssertionError("Zero flag should not be set for 42 + 0")
        
        # Test XOR with same numbers (should give 0)
        alu.execute(0x1234, 0x1234, ALU.ALU_XOR)
        if not alu.zero_flag:
            raise AssertionError("Zero flag should be set for A XOR A")
        
        # Test Overflow Flag
        alu.execute(0xFFFF, 1, ALU.ALU_ADD)
        if not alu.overflow_flag:
            raise AssertionError("Overflow flag should be set for 0xFFFF + 1")
        
        # Test Negative Flag (MSB = 1)
        alu.execute(0x8000, 0, ALU.ALU_ADD)  # 0x8000 has MSB = 1
        if not alu.negative_flag:
            raise AssertionError("Negative flag should be set for 0x8000")
        
        alu.execute(0x7FFF, 0, ALU.ALU_ADD)  # 0x7FFF has MSB = 0
        if alu.negative_flag:
            raise AssertionError("Negative flag should not be set for 0x7FFF")
        
        print(f"   ✓ Zero flag works correctly")
        print(f"   ✓ Overflow flag works correctly")
        print(f"   ✓ Negative flag works correctly")
    
    def test_boundary_conditions(self):
        """Test boundary conditions"""
        print("Testing boundary conditions...")
        
        alu = ALU()
        
        # Test with maximum values
        result = alu.execute(0xFFFF, 0xFFFF, ALU.ALU_ADD)
        expected = 0xFFFE  # (0xFFFF + 0xFFFF) & 0xFFFF = 0x1FFFE & 0xFFFF = 0xFFFE
        if result != expected:
            raise AssertionError(f"Max ADD: Expected 0x{expected:04X}, got 0x{result:04X}")
        
        # Test with minimum values  
        result = alu.execute(0, 0, ALU.ALU_SUB)
        if result != 0:
            raise AssertionError(f"Min SUB: Expected 0, got {result}")
        
        # Test mixed operations
        result = alu.execute(0xFFFF, 0x0000, ALU.ALU_AND)
        if result != 0x0000:
            raise AssertionError(f"Mixed AND: Expected 0x0000, got 0x{result:04X}")
        
        result = alu.execute(0x0000, 0xFFFF, ALU.ALU_OR)
        if result != 0xFFFF:
            raise AssertionError(f"Mixed OR: Expected 0xFFFF, got 0x{result:04X}")
        
        print(f"   ✓ Maximum value operations work")
        print(f"   ✓ Minimum value operations work")
        print(f"   ✓ Mixed boundary operations work")
    
    def test_operation_history(self):
        """Test operation history tracking"""
        print("Testing operation history tracking...")
        
        alu = ALU()
        
        # Perform several operations
        alu.execute(10, 20, ALU.ALU_ADD)
        alu.execute(50, 30, ALU.ALU_SUB)
        alu.execute(0xFF, 0x0F, ALU.ALU_AND)
        
        if alu.operations_count != 3:
            raise AssertionError(f"Operations count: Expected 3, got {alu.operations_count}")
        
        if len(alu.operation_history) != 3:
            raise AssertionError(f"History length: Expected 3, got {len(alu.operation_history)}")
        
        # Check first operation
        first_op = alu.operation_history[0]
        if first_op['op'] != 'ADD' or first_op['a'] != 10 or first_op['b'] != 20:
            raise AssertionError("First operation not recorded correctly")
        
        # Check last result
        if alu.last_result != (0xFF & 0x0F):
            raise AssertionError(f"Last result: Expected {0xFF & 0x0F}, got {alu.last_result}")
        
        print(f"   ✓ Operation counting works")
        print(f"   ✓ History tracking works")
        print(f"   ✓ Last result tracking works")
    
    def test_reset_functionality(self):
        """Test reset functionality"""
        print("Testing reset functionality...")
        
        alu = ALU()
        
        # Perform some operations
        alu.execute(100, 200, ALU.ALU_ADD)
        alu.execute(0xFFFF, 1, ALU.ALU_ADD)  # Cause overflow
        
        # Verify state changed
        if alu.operations_count == 0:
            raise AssertionError("Should have operations before reset")
        
        if not alu.overflow_flag:
            raise AssertionError("Should have overflow flag before reset")
        
        # Reset ALU
        alu.reset()
        
        # Verify reset state
        if alu.operations_count != 0:
            raise AssertionError(f"Operations count after reset: Expected 0, got {alu.operations_count}")
        
        if alu.last_result != 0:
            raise AssertionError(f"Last result after reset: Expected 0, got {alu.last_result}")
        
        if alu.zero_flag or alu.overflow_flag or alu.negative_flag:
            raise AssertionError("All flags should be False after reset")
        
        if len(alu.operation_history) != 0:
            raise AssertionError(f"History after reset: Expected empty, got {len(alu.operation_history)} items")
        
        print(f"   ✓ Reset clears all counters")
        print(f"   ✓ Reset clears all flags")
        print(f"   ✓ Reset clears history")
    
    def test_invalid_operations(self):
        """Test invalid operations"""
        print("Testing invalid operations...")
        
        alu = ALU()
        
        # Test invalid ALU control code
        result = alu.execute(10, 20, 0xFF)  # Invalid control code
        if result != 0:
            raise AssertionError(f"Invalid operation: Expected 0, got {result}")
        
        # Test very large inputs (should be masked to 16-bit)
        result = alu.execute(0x12345, 0x67890, ALU.ALU_ADD)
        # Should mask inputs: 0x2345 + 0x7890 = 0x9BD5
        expected = (0x2345 + 0x7890) & 0xFFFF
        if result != expected:
            raise AssertionError(f"Large input masking: Expected 0x{expected:04X}, got 0x{result:04X}")
        
        print(f"   ✓ Invalid operations return 0")
        print(f"   ✓ Large inputs are properly masked")
    
    def run_all_tests(self):
        """Εκτελεί όλα τα tests"""
        print("=" * 60)
        print("🧪 ALU UNIT TESTS")
        print("=" * 60)
        
        # Εκτέλεση όλων των tests
        self.run_test("Arithmetic Operations", self.test_arithmetic_operations)
        self.run_test("Logical Operations", self.test_logical_operations)
        self.run_test("Comparison Operations", self.test_comparison_operations)
        self.run_test("Flags", self.test_flags)
        self.run_test("Boundary Conditions", self.test_boundary_conditions)
        self.run_test("Operation History", self.test_operation_history)
        self.run_test("Reset Functionality", self.test_reset_functionality)
        self.run_test("Invalid Operations", self.test_invalid_operations)
        
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
    tests = ALUTests()
    
    test_methods = {
        'arithmetic': tests.test_arithmetic_operations,
        'logical': tests.test_logical_operations,
        'comparison': tests.test_comparison_operations,
        'flags': tests.test_flags,
        'boundary': tests.test_boundary_conditions,
        'history': tests.test_operation_history,
        'reset': tests.test_reset_functionality,
        'invalid': tests.test_invalid_operations
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
        tests = ALUTests()
        success = tests.run_all_tests()
        
        # Exit code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()