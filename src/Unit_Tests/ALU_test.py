"""
Comprehensive Unit Tests for ALU (Arithmetic Logic Unit)

Tests include:
- Basic arithmetic operations (ADD, SUB)
- Logic operations (AND, OR, XOR)  
- Comparison operations (EQ, NE)
- Flag generation and validation
- Edge cases and boundary conditions
- Exception handling and invalid inputs
- Overflow/underflow scenarios
- Signed/unsigned behavior
"""
import sys
import unittest
from io import StringIO

# Import path fix
sys.path.append('..')

from ALU import ALU


class TestALUBasicOperations(unittest.TestCase):
    """Test basic ALU operations with normal inputs"""
    
    def setUp(self):
        """Setup ALU instance before each test"""
        self.alu = ALU()
    
    def test_alu_initialization(self):
        """Test ALU initialization state"""
        try:
            # Check initial state
            self.assertEqual(self.alu.last_result, 0, 
                           "FAIL: Initial last_result should be 0")
            self.assertFalse(self.alu.zero_flag, 
                           "FAIL: Initial zero_flag should be False")
            self.assertFalse(self.alu.overflow_flag, 
                           "FAIL: Initial overflow_flag should be False")
            self.assertFalse(self.alu.negative_flag, 
                           "FAIL: Initial negative_flag should be False")
            self.assertEqual(self.alu.operation_count, 0, 
                           "FAIL: Initial operation_count should be 0")
            self.assertEqual(len(self.alu.operation_history), 0, 
                           "FAIL: Initial operation_history should be empty")
            
            print("✅ PASS: ALU initialization test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: ALU initialization failed with error: {str(e)}")
    
    def test_arithmetic_operations(self):
        """Test ADD and SUB operations"""
        try:
            # Test ADD operation
            result = self.alu.execute(100, 200, self.alu.ALU_ADD)
            self.assertEqual(result, 300, 
                           f"FAIL: ADD 100 + 200 should equal 300, got {result}")
            self.assertEqual(self.alu.last_result, 300, 
                           f"FAIL: last_result should be 300, got {self.alu.last_result}")
            self.assertFalse(self.alu.zero_flag, 
                           "FAIL: zero_flag should be False for non-zero result")
            
            # Test SUB operation
            result = self.alu.execute(500, 200, self.alu.ALU_SUB)
            self.assertEqual(result, 300, 
                           f"FAIL: SUB 500 - 200 should equal 300, got {result}")
            
            # Test operation count
            self.assertEqual(self.alu.operation_count, 2, 
                           f"FAIL: After 2 operations, count should be 2, got {self.alu.operation_count}")
            
            print("✅ PASS: Arithmetic operations test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Arithmetic operations test failed with error: {str(e)}")
    
    def test_logic_operations(self):
        """Test AND, OR, XOR operations"""
        try:
            # Test AND operation
            result = self.alu.execute(0xFF00, 0x0F0F, self.alu.ALU_AND)
            expected = 0x0F00
            self.assertEqual(result, expected, 
                           f"FAIL: AND 0xFF00 & 0x0F0F should equal 0x{expected:04X}, got 0x{result:04X}")
            
            # Test OR operation
            result = self.alu.execute(0xF000, 0x000F, self.alu.ALU_OR)
            expected = 0xF00F
            self.assertEqual(result, expected, 
                           f"FAIL: OR 0xF000 | 0x000F should equal 0x{expected:04X}, got 0x{result:04X}")
            
            # Test XOR operation
            result = self.alu.execute(0xAAAA, 0x5555, self.alu.ALU_XOR)
            expected = 0xFFFF
            self.assertEqual(result, expected, 
                           f"FAIL: XOR 0xAAAA ^ 0x5555 should equal 0x{expected:04X}, got 0x{result:04X}")
            
            print("✅ PASS: Logic operations test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Logic operations test failed with error: {str(e)}")
    
    def test_comparison_operations(self):
        """Test EQ and NE comparison operations"""
        try:
            # Test EQ operation - equal values
            result = self.alu.execute(42, 42, self.alu.ALU_EQ)
            self.assertEqual(result, 1, 
                           f"FAIL: EQ 42 == 42 should return 1, got {result}")
            
            # Test EQ operation - different values
            result = self.alu.execute(42, 43, self.alu.ALU_EQ)
            self.assertEqual(result, 0, 
                           f"FAIL: EQ 42 == 43 should return 0, got {result}")
            
            # Test NE operation - different values
            result = self.alu.execute(100, 200, self.alu.ALU_NE)
            self.assertEqual(result, 1, 
                           f"FAIL: NE 100 != 200 should return 1, got {result}")
            
            # Test NE operation - equal values
            result = self.alu.execute(100, 100, self.alu.ALU_NE)
            self.assertEqual(result, 0, 
                           f"FAIL: NE 100 != 100 should return 0, got {result}")
            
            print("✅ PASS: Comparison operations test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Comparison operations test failed with error: {str(e)}")


class TestALUFlags(unittest.TestCase):
    """Test ALU flag generation and behavior"""
    
    def setUp(self):
        """Setup ALU instance before each test"""
        self.alu = ALU()
    
    def test_zero_flag(self):
        """Test zero flag generation"""
        try:
            # Test zero result
            result = self.alu.execute(5, 5, self.alu.ALU_SUB)
            self.assertEqual(result, 0, 
                           f"FAIL: SUB 5 - 5 should equal 0, got {result}")
            self.assertTrue(self.alu.zero_flag, 
                          "FAIL: zero_flag should be True for zero result")
            
            # Test non-zero result
            result = self.alu.execute(10, 5, self.alu.ALU_SUB)
            self.assertEqual(result, 5, 
                           f"FAIL: SUB 10 - 5 should equal 5, got {result}")
            self.assertFalse(self.alu.zero_flag, 
                           "FAIL: zero_flag should be False for non-zero result")
            
            # Test XOR with same values (should be zero)
            result = self.alu.execute(0x1234, 0x1234, self.alu.ALU_XOR)
            self.assertEqual(result, 0, 
                           f"FAIL: XOR 0x1234 ^ 0x1234 should equal 0, got 0x{result:04X}")
            self.assertTrue(self.alu.zero_flag, 
                          "FAIL: zero_flag should be True for XOR with same values")
            
            print("✅ PASS: Zero flag test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Zero flag test failed with error: {str(e)}")
    
    def test_overflow_flag(self):
        """Test overflow flag generation"""
        try:
            # Test overflow condition
            result = self.alu.execute(0xFFFF, 1, self.alu.ALU_ADD)
            self.assertEqual(result, 0, 
                           f"FAIL: ADD 0xFFFF + 1 should wrap to 0, got 0x{result:04X}")
            self.assertTrue(self.alu.overflow_flag, 
                          "FAIL: overflow_flag should be True for 0xFFFF + 1")
            
            # Test no overflow condition
            result = self.alu.execute(100, 200, self.alu.ALU_ADD)
            self.assertEqual(result, 300, 
                           f"FAIL: ADD 100 + 200 should equal 300, got {result}")
            self.assertFalse(self.alu.overflow_flag, 
                           "FAIL: overflow_flag should be False for 100 + 200")
            
            # Test maximum add without overflow
            result = self.alu.execute(0x7FFF, 0x7FFF, self.alu.ALU_ADD)
            self.assertEqual(result, 0xFFFE, 
                           f"FAIL: ADD 0x7FFF + 0x7FFF should equal 0xFFFE, got 0x{result:04X}")
            self.assertFalse(self.alu.overflow_flag, 
                           "FAIL: overflow_flag should be False for 0x7FFF + 0x7FFF")
            
            print("✅ PASS: Overflow flag test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Overflow flag test failed with error: {str(e)}")
    
    def test_negative_flag(self):
        """Test negative flag generation (MSB = 1)"""
        try:
            # Test negative result (MSB = 1)
            result = self.alu.execute(0x8000, 0, self.alu.ALU_ADD)
            self.assertEqual(result, 0x8000, 
                           f"FAIL: ADD 0x8000 + 0 should equal 0x8000, got 0x{result:04X}")
            self.assertTrue(self.alu.negative_flag, 
                          "FAIL: negative_flag should be True for result 0x8000")
            
            # Test positive result (MSB = 0)
            result = self.alu.execute(0x7FFF, 0, self.alu.ALU_ADD)
            self.assertEqual(result, 0x7FFF, 
                           f"FAIL: ADD 0x7FFF + 0 should equal 0x7FFF, got 0x{result:04X}")
            self.assertFalse(self.alu.negative_flag, 
                           "FAIL: negative_flag should be False for result 0x7FFF")
            
            # Test wrap-around to negative
            result = self.alu.execute(0x7FFF, 1, self.alu.ALU_ADD)
            self.assertEqual(result, 0x8000, 
                           f"FAIL: ADD 0x7FFF + 1 should equal 0x8000, got 0x{result:04X}")
            self.assertTrue(self.alu.negative_flag, 
                          "FAIL: negative_flag should be True for wrap-around to 0x8000")
            
            print("✅ PASS: Negative flag test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Negative flag test failed with error: {str(e)}")


class TestALUEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        """Setup ALU instance before each test"""
        self.alu = ALU()
    
    def test_boundary_values(self):
        """Test operations with boundary values"""
        try:
            # Test maximum 16-bit values
            result = self.alu.execute(0xFFFF, 0xFFFF, self.alu.ALU_ADD)
            self.assertEqual(result, 0xFFFE, 
                           f"FAIL: ADD 0xFFFF + 0xFFFF should wrap to 0xFFFE, got 0x{result:04X}")
            
            # Test minimum values
            result = self.alu.execute(0, 0, self.alu.ALU_ADD)
            self.assertEqual(result, 0, 
                           f"FAIL: ADD 0 + 0 should equal 0, got {result}")
            
            # Test subtraction underflow
            result = self.alu.execute(0, 1, self.alu.ALU_SUB)
            self.assertEqual(result, 0xFFFF, 
                           f"FAIL: SUB 0 - 1 should wrap to 0xFFFF, got 0x{result:04X}")
            
            # Test maximum subtraction
            result = self.alu.execute(0xFFFF, 0, self.alu.ALU_SUB)
            self.assertEqual(result, 0xFFFF, 
                           f"FAIL: SUB 0xFFFF - 0 should equal 0xFFFF, got 0x{result:04X}")
            
            print("✅ PASS: Boundary values test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Boundary values test failed with error: {str(e)}")
    
    def test_input_masking(self):
        """Test that inputs are properly masked to 16-bit"""
        try:
            # Test large input values that should be masked
            test_cases = [
                (0x10000, 0x1000, 0x0000, 0x1000, "Large first operand"),
                (0x1000, 0x10000, 0x1000, 0x0000, "Large second operand"), 
                (0x12345, 0x6789A, 0x2345, 0x789A, "Both operands large"),
                (0xFFFFF, 0xAAAAA, 0xFFFF, 0xAAAA, "Very large operands")
            ]
            
            for input_a, input_b, expected_a, expected_b, description in test_cases:
                # The actual operation result depends on masked values
                expected_result = (expected_a + expected_b) & 0xFFFF
                result = self.alu.execute(input_a, input_b, self.alu.ALU_ADD)
                
                self.assertEqual(result, expected_result, 
                               f"FAIL: {description} - ADD 0x{input_a:X} + 0x{input_b:X} "
                               f"should mask to 0x{expected_a:04X} + 0x{expected_b:04X} = 0x{expected_result:04X}, "
                               f"got 0x{result:04X}")
            
            print("✅ PASS: Input masking test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Input masking test failed with error: {str(e)}")
    
    def test_signed_unsigned_behavior(self):
        """Test signed vs unsigned interpretation"""
        try:
            # Test values that have different signed/unsigned interpretations
            test_cases = [
                (0x8000, 0x0001, "0x8000 + 1"),  # -32768 + 1 = -32767 (signed) or 32768 + 1 = 32769 (unsigned)
                (0xFFFF, 0x0001, "0xFFFF + 1"),  # -1 + 1 = 0 (signed) or 65535 + 1 = 0 (wrap)
                (0x7FFF, 0x0001, "0x7FFF + 1"),  # 32767 + 1 = 32768 (both interpretations)
            ]
            
            for a, b, description in test_cases:
                # Addition works the same for signed/unsigned in 2's complement
                result = self.alu.execute(a, b, self.alu.ALU_ADD)
                expected = (a + b) & 0xFFFF
                
                self.assertEqual(result, expected, 
                               f"FAIL: {description} should equal 0x{expected:04X}, got 0x{result:04X}")
                
                # Check that negative flag is set correctly
                if result & 0x8000:
                    self.assertTrue(self.alu.negative_flag, 
                                  f"FAIL: negative_flag should be True for result 0x{result:04X}")
                else:
                    self.assertFalse(self.alu.negative_flag, 
                                   f"FAIL: negative_flag should be False for result 0x{result:04X}")
            
            print("✅ PASS: Signed/unsigned behavior test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Signed/unsigned behavior test failed with error: {str(e)}")


class TestALUExceptions(unittest.TestCase):
    """Test exception handling and invalid inputs"""
    
    def setUp(self):
        """Setup ALU instance before each test"""
        self.alu = ALU()
    
    def test_invalid_operation_codes(self):
        """Test handling of invalid operation codes"""
        try:
            # Test invalid operation codes
            invalid_operations = [7, 8, 15, 255, -1, 0b1000, 0b1111]
            
            for invalid_op in invalid_operations:
                with self.assertRaises(ValueError, 
                                     msg=f"FAIL: Operation code {invalid_op} should raise ValueError"):
                    self.alu.execute(100, 200, invalid_op)
                
                # Verify ALU state is not corrupted after exception
                self.assertEqual(self.alu.last_result, 0, 
                               f"FAIL: last_result should remain 0 after exception, got {self.alu.last_result}")
                self.assertEqual(self.alu.operation_count, 0, 
                               f"FAIL: operation_count should remain 0 after exception, got {self.alu.operation_count}")
            
            print("✅ PASS: Invalid operation codes test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Invalid operation codes test failed with error: {str(e)}")
    
    def test_extreme_input_values(self):
        """Test behavior with extreme input values"""
        try:
            # Test with very large numbers (should be masked)
            result = self.alu.execute(0xFFFFFFFF, 0x12345678, self.alu.ALU_ADD)
            # Should be masked: 0xFFFF + 0x5678 = 0x5677 (with overflow)
            expected = (0xFFFF + 0x5678) & 0xFFFF
            self.assertEqual(result, expected, 
                           f"FAIL: Extreme large inputs should be masked and computed correctly")
            
            # Test with negative Python integers (should be masked to positive)
            result = self.alu.execute(-1, -2, self.alu.ALU_ADD)
            # -1 & 0xFFFF = 0xFFFF, -2 & 0xFFFF = 0xFFFE
            # 0xFFFF + 0xFFFE = 0x1FFFD & 0xFFFF = 0xFFFD
            expected = 0xFFFD
            self.assertEqual(result, expected, 
                           f"FAIL: Negative inputs should be masked to 16-bit, got 0x{result:04X}")
            
            print("✅ PASS: Extreme input values test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Extreme input values test failed with error: {str(e)}")
    
    def test_operation_history_tracking(self):
        """Test operation history and statistics tracking"""
        try:
            # Perform several operations
            operations = [
                (100, 200, self.alu.ALU_ADD, 300),
                (500, 200, self.alu.ALU_SUB, 300),
                (0xFF00, 0x0F0F, self.alu.ALU_AND, 0x0F00),
                (0xF000, 0x000F, self.alu.ALU_OR, 0xF00F),
                (42, 42, self.alu.ALU_EQ, 1)
            ]
            
            for i, (a, b, op, expected) in enumerate(operations, 1):
                result = self.alu.execute(a, b, op)
                self.assertEqual(result, expected, 
                               f"FAIL: Operation {i} result incorrect")
                
                # Check operation count
                self.assertEqual(self.alu.operation_count, i, 
                               f"FAIL: Operation count should be {i}, got {self.alu.operation_count}")
            
            # Check history tracking
            self.assertEqual(len(self.alu.operation_history), 5, 
                           f"FAIL: History should contain 5 operations, got {len(self.alu.operation_history)}")
            
            # Check first operation in history
            first_op = self.alu.operation_history[0]
            self.assertEqual(first_op['operation'], 'ADD', 
                           f"FAIL: First operation should be ADD, got {first_op['operation']}")
            self.assertEqual(first_op['operand_a'], 100, 
                           f"FAIL: First operation operand_a should be 100, got {first_op['operand_a']}")
            
            print("✅ PASS: Operation history tracking test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Operation history tracking test failed with error: {str(e)}")


class TestALUUtilityMethods(unittest.TestCase):
    """Test utility methods and helper functions"""
    
    def setUp(self):
        """Setup ALU instance before each test"""
        self.alu = ALU()
    
    def test_get_flags_method(self):
        """Test get_flags() method"""
        try:
            # Test initial flags
            flags = self.alu.get_flags()
            expected_flags = {'zero': False, 'overflow': False, 'negative': False}
            self.assertEqual(flags, expected_flags, 
                           f"FAIL: Initial flags should be {expected_flags}, got {flags}")
            
            # Test flags after zero result
            self.alu.execute(5, 5, self.alu.ALU_SUB)
            flags = self.alu.get_flags()
            self.assertTrue(flags['zero'], 
                          "FAIL: zero flag should be True after zero result")
            
            # Test flags after overflow
            self.alu.execute(0xFFFF, 1, self.alu.ALU_ADD)
            flags = self.alu.get_flags()
            self.assertTrue(flags['overflow'], 
                          "FAIL: overflow flag should be True after overflow")
            
            # Test flags after negative result
            self.alu.execute(0x8000, 0, self.alu.ALU_ADD)
            flags = self.alu.get_flags()
            self.assertTrue(flags['negative'], 
                          "FAIL: negative flag should be True for negative result")
            
            print("✅ PASS: Get flags method test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Get flags method test failed with error: {str(e)}")
    
    def test_reset_method(self):
        """Test reset() method"""
        try:
            # Perform some operations to change state
            self.alu.execute(100, 200, self.alu.ALU_ADD)
            self.alu.execute(0x7FFF, 1, self.alu.ALU_ADD)
            
            # Verify state has changed
            self.assertNotEqual(self.alu.last_result, 0, 
                              "FAIL: last_result should have changed before reset")
            self.assertGreater(self.alu.operation_count, 0, 
                             "FAIL: operation_count should be > 0 before reset")
            
            # Reset ALU
            self.alu.reset()
            
            # Verify reset state
            self.assertEqual(self.alu.last_result, 0, 
                           f"FAIL: last_result should be 0 after reset, got {self.alu.last_result}")
            self.assertEqual(self.alu.operation_count, 0, 
                           f"FAIL: operation_count should be 0 after reset, got {self.alu.operation_count}")
            self.assertFalse(self.alu.zero_flag, 
                           "FAIL: zero_flag should be False after reset")
            self.assertFalse(self.alu.overflow_flag, 
                           "FAIL: overflow_flag should be False after reset")
            self.assertFalse(self.alu.negative_flag, 
                           "FAIL: negative_flag should be False after reset")
            self.assertEqual(len(self.alu.operation_history), 0, 
                           f"FAIL: operation_history should be empty after reset, got {len(self.alu.operation_history)}")
            
            print("✅ PASS: Reset method test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Reset method test failed with error: {str(e)}")
    
    def test_statistics_method(self):
        """Test get_statistics() method"""
        try:
            # Test initial statistics
            stats = self.alu.get_statistics()
            self.assertIsInstance(stats, dict, 
                                "FAIL: get_statistics() should return a dictionary")
            self.assertIn('total_operations', stats, 
                        "FAIL: Statistics should include 'total_operations'")
            self.assertEqual(stats['total_operations'], 0, 
                           "FAIL: Initial total_operations should be 0")
            
            # Perform operations and check updated statistics
            self.alu.execute(100, 200, self.alu.ALU_ADD)
            self.alu.execute(0x8000, 0, self.alu.ALU_ADD)  # Negative result
            
            stats = self.alu.get_statistics()
            self.assertEqual(stats['total_operations'], 2, 
                           f"FAIL: total_operations should be 2, got {stats['total_operations']}")
            self.assertEqual(stats['last_result'], 0x8000, 
                           f"FAIL: last_result should be 0x8000, got 0x{stats['last_result']:04X}")
            self.assertTrue(stats['current_flags']['negative'], 
                          "FAIL: negative flag should be True in statistics")
            
            print("✅ PASS: Statistics method test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Statistics method test failed with error: {str(e)}")


def run_all_tests():
    """Run all ALU tests with detailed reporting"""
    print("🧪 RISC-V ALU Unit Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestALUBasicOperations,
        TestALUFlags, 
        TestALUEdgeCases,
        TestALUExceptions,
        TestALUUtilityMethods
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ALU TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, error in result.failures:
            print(f"  - {test}")
            print(f"    {error}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, error in result.errors:
            print(f"  - {test}")
            print(f"    {error}")
    
    if len(result.failures) == 0 and len(result.errors) == 0:
        print("\n🎉 ALL ALU TESTS PASSED! 🎉")
        print("✅ Basic operations working correctly")
        print("✅ Flag generation working correctly")
        print("✅ Edge cases handled properly")
        print("✅ Exception handling working correctly")
        print("✅ Utility methods working correctly")
        return True
    else:
        print(f"\n⚠️  {len(result.failures + result.errors)} ALU TESTS FAILED")
        return False


if __name__ == "__main__":
    run_all_tests()