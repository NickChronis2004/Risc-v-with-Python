
"""
Comprehensive Unit Tests για Register και RegisterFile

Περιλαμβάνει:
- Register class testing (όλες οι μέθοδοι)
- RegisterFile class testing (read/write/validation)
- Edge cases και error conditions
- Detailed error reporting για debugging
"""

from RegisterFile import Register, RegisterFile  
import unittest
import sys
from io import StringIO


class TestRegister(unittest.TestCase):
    """Unit tests για την Register κλάση"""
    
    def setUp(self):
        """Setup που τρέχει πριν από κάθε test"""
        self.normal_reg = Register("x5", "t0", "Temporary register", read_only=False)
        self.readonly_reg = Register("x0", "zero", "Hard-wired zero", read_only=True)
    
    def test_register_initialization(self):
        """Test αρχικοποίησης register"""
        try:
            # Test normal register
            self.assertEqual(self.normal_reg.name, "x5", 
                           "FAIL: Register name not set correctly during initialization")
            self.assertEqual(self.normal_reg.abi_name, "t0", 
                           "FAIL: ABI name not set correctly during initialization")
            self.assertEqual(self.normal_reg.purpose, "Temporary register", 
                           "FAIL: Purpose not set correctly during initialization")
            self.assertEqual(self.normal_reg.value, 0x0000, 
                           "FAIL: Initial value should be 0x0000, got 0x{:04X}".format(self.normal_reg.value))
            self.assertEqual(self.normal_reg.bit_length, 16, 
                           "FAIL: Default bit length should be 16, got {}".format(self.normal_reg.bit_length))
            self.assertFalse(self.normal_reg.read_only, 
                           "FAIL: Normal register should not be read-only")
            
            # Test read-only register
            self.assertTrue(self.readonly_reg.read_only, 
                          "FAIL: x0 register should be read-only")
            
            print("✅ PASS: Register initialization test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Register initialization failed with unexpected error: {str(e)}")
    
    def test_register_read(self):
        """Test register read operations"""
        try:
            # Test initial read
            value = self.normal_reg.read()
            self.assertEqual(value, 0x0000, 
                           f"FAIL: Initial read should return 0x0000, got 0x{value:04X}")
            
            # Test read after write
            self.normal_reg.write(0x1234)
            value = self.normal_reg.read()
            self.assertEqual(value, 0x1234, 
                           f"FAIL: Read after write should return 0x1234, got 0x{value:04X}")
            
            # Test read-only register
            value = self.readonly_reg.read()
            self.assertEqual(value, 0x0000, 
                           f"FAIL: Read-only register should always return 0x0000, got 0x{value:04X}")
            
            print("✅ PASS: Register read test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Register read test failed with error: {str(e)}")
    
    def test_register_write(self):
        """Test register write operations"""
        try:
            # Test normal write
            result = self.normal_reg.write(0x5678)
            self.assertTrue(result, "FAIL: Write to normal register should return True (success)")
            self.assertEqual(self.normal_reg.read(), 0x5678, 
                           f"FAIL: Write value 0x5678 not stored correctly, got 0x{self.normal_reg.read():04X}")
            
            # Test write to read-only register
            result = self.readonly_reg.write(0x9999)
            self.assertFalse(result, "FAIL: Write to read-only register should return False")
            self.assertEqual(self.readonly_reg.read(), 0x0000, 
                           f"FAIL: Read-only register value changed after write attempt, got 0x{self.readonly_reg.read():04X}")
            
            print("✅ PASS: Register write test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Register write test failed with error: {str(e)}")
    
    def test_register_bit_masking(self):
        """Test 16-bit value masking"""
        try:
            # Test values that should be masked
            test_cases = [
                (0x10000, 0x0000, "Overflow value 0x10000 should wrap to 0x0000"),
                (0x12345, 0x2345, "Large value 0x12345 should be masked to 0x2345"),
                (0xFFFF, 0xFFFF, "Maximum 16-bit value 0xFFFF should remain unchanged"),
                (0xABCDE, 0xBCDE, "Large value 0xABCDE should be masked to 0xBCDE")
            ]
            
            for input_val, expected, description in test_cases:
                self.normal_reg.write(input_val)
                actual = self.normal_reg.read()
                self.assertEqual(actual, expected, 
                               f"FAIL: {description}. Expected 0x{expected:04X}, got 0x{actual:04X}")
            
            print("✅ PASS: Register bit masking test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Register bit masking test failed with error: {str(e)}")
    
    def test_register_reset(self):
        """Test register reset functionality"""
        try:
            # Test normal register reset
            self.normal_reg.write(0xDEAD)
            self.normal_reg.reset()
            self.assertEqual(self.normal_reg.read(), 0x0000, 
                           f"FAIL: Normal register reset should set value to 0x0000, got 0x{self.normal_reg.read():04X}")
            
            # Test read-only register reset (should not change)
            self.readonly_reg.reset()  # Should do nothing
            self.assertEqual(self.readonly_reg.read(), 0x0000, 
                           f"FAIL: Read-only register should remain 0x0000 after reset, got 0x{self.readonly_reg.read():04X}")
            
            print("✅ PASS: Register reset test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Register reset test failed with error: {str(e)}")
    
    def test_register_is_zero(self):
        """Test is_zero() method"""
        try:
            # Test with zero value
            self.assertTrue(self.normal_reg.is_zero(), 
                          "FAIL: is_zero() should return True for initial zero value")
            
            # Test with non-zero value
            self.normal_reg.write(42)
            self.assertFalse(self.normal_reg.is_zero(), 
                           "FAIL: is_zero() should return False for non-zero value 42")
            
            # Test after reset
            self.normal_reg.reset()
            self.assertTrue(self.normal_reg.is_zero(), 
                          "FAIL: is_zero() should return True after reset")
            
            print("✅ PASS: Register is_zero test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Register is_zero test failed with error: {str(e)}")


class TestRegisterFile(unittest.TestCase):
    """Unit tests για την RegisterFile κλάση"""
    
    def setUp(self):
        """Setup που τρέχει πριν από κάθε test"""
        self.rf = RegisterFile()
    
    def test_registerfile_initialization(self):
        """Test αρχικοποίησης RegisterFile"""
        try:
            # Test number of registers
            self.assertEqual(len(self.rf.registers), 16, 
                           f"FAIL: RegisterFile should have 16 registers, got {len(self.rf.registers)}")
            
            # Test x0 is read-only
            x0_info = self.rf.registers[0].get_info()
            self.assertTrue(x0_info['read_only'], 
                          "FAIL: x0 register should be read-only")
            self.assertEqual(x0_info['name'], "x0", 
                           f"FAIL: First register should be named 'x0', got '{x0_info['name']}'")
            self.assertEqual(x0_info['abi_name'], "zero", 
                           f"FAIL: x0 ABI name should be 'zero', got '{x0_info['abi_name']}'")
            
            # Test all registers start at 0
            for i, reg in enumerate(self.rf.registers):
                self.assertEqual(reg.read(), 0x0000, 
                               f"FAIL: Register x{i} should start with value 0x0000, got 0x{reg.read():04X}")
            
            # Test ABI mapping exists
            self.assertIsInstance(self.rf.abi_to_index, dict, 
                                "FAIL: abi_to_index should be a dictionary")
            self.assertEqual(len(self.rf.abi_to_index), 16, 
                           f"FAIL: abi_to_index should have 16 entries, got {len(self.rf.abi_to_index)}")
            
            print("✅ PASS: RegisterFile initialization test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: RegisterFile initialization failed with error: {str(e)}")
    
    def test_registerfile_read_by_number(self):
        """Test reading registers by number (0-15)"""
        try:
            # Test valid register numbers
            for i in range(16):
                value = self.rf.read(i)
                self.assertEqual(value, 0x0000, 
                               f"FAIL: Register x{i} should initially read 0x0000, got 0x{value:04X}")
            
            # Test after writing
            self.rf.write(5, 0x1234)
            value = self.rf.read(5)
            self.assertEqual(value, 0x1234, 
                           f"FAIL: Register x5 should read 0x1234 after write, got 0x{value:04X}")
            
            print("✅ PASS: RegisterFile read by number test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: RegisterFile read by number failed with error: {str(e)}")
    
    def test_registerfile_read_by_abi_name(self):
        """Test reading registers by ABI name"""
        try:
            # Test all valid ABI names (SKIP x0 because it's read-only)
            abi_tests = [
                ("ra", 1), ("sp", 2), ("gp", 3), ("tp", 4),
                ("t0", 5), ("t1", 6), ("t2", 7), ("s0", 8), ("s1", 9),
                ("a0", 10), ("a1", 11), ("a2", 12), ("a3", 13), ("a4", 14), ("a7", 15)
            ]
            
            for abi_name, expected_index in abi_tests:
                # Write unique value to register
                unique_value = 0x1000 + expected_index
                self.rf.write(expected_index, unique_value)
                
                # Read by ABI name and verify
                value = self.rf.read(abi_name)
                self.assertEqual(value, unique_value, 
                            f"FAIL: Reading register by ABI name '{abi_name}' (x{expected_index}) "
                            f"should return 0x{unique_value:04X}, got 0x{value:04X}")
            
            # Test x0 separately (should always be 0)
            self.rf.write(0, 0x9999)  # Try to write (should fail)
            value = self.rf.read("zero")
            self.assertEqual(value, 0x0000, 
                        f"FAIL: x0 should always be 0x0000, got 0x{value:04X}")
            
            print("✅ PASS: RegisterFile read by ABI name test completed successfully")
            
        except Exception as e: 
            self.fail(f"FAIL: RegisterFile read by ABI name failed with error: {str(e)}")
    
    def test_registerfile_write_operations(self):
        """Test write operations"""
        try:
            # Test write by number
            result = self.rf.write(10, 0x5678)
            self.assertTrue(result, "FAIL: Write to valid register x10 should return True")
            self.assertEqual(self.rf.read(10), 0x5678, 
                           f"FAIL: x10 should contain 0x5678 after write, got 0x{self.rf.read(10):04X}")
            
            # Test write by ABI name
            result = self.rf.write("t0", 0x9ABC)
            self.assertTrue(result, "FAIL: Write to valid register 't0' should return True")
            self.assertEqual(self.rf.read("t0"), 0x9ABC, 
                           f"FAIL: t0 should contain 0x9ABC after write, got 0x{self.rf.read('t0'):04X}")
            
            # Test write to x0 (should fail)
            result = self.rf.write(0, 0xDEAD)
            self.assertFalse(result, "FAIL: Write to x0 should return False (read-only)")
            self.assertEqual(self.rf.read(0), 0x0000, 
                           f"FAIL: x0 should remain 0x0000 after write attempt, got 0x{self.rf.read(0):04X}")
            
            # Test write to "zero" (should fail)
            result = self.rf.write("zero", 0xBEEF)
            self.assertFalse(result, "FAIL: Write to 'zero' should return False (read-only)")
            self.assertEqual(self.rf.read("zero"), 0x0000, 
                           f"FAIL: zero should remain 0x0000 after write attempt, got 0x{self.rf.read('zero'):04X}")
            
            print("✅ PASS: RegisterFile write operations test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: RegisterFile write operations failed with error: {str(e)}")
    
    def test_registerfile_invalid_identifiers(self):
        """Test error handling για invalid register identifiers"""
        try:
            # Capture stdout για error messages
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            # Test invalid register numbers
            invalid_numbers = [-1, 16, 20, 100, -5]
            for invalid_num in invalid_numbers:
                value = self.rf.read(invalid_num)
                self.assertEqual(value, 0, 
                               f"FAIL: Reading invalid register number {invalid_num} should return 0, got {value}")
                
                result = self.rf.write(invalid_num, 0x1234)
                self.assertFalse(result, 
                               f"FAIL: Writing to invalid register number {invalid_num} should return False, got {result}")
            
            # Test invalid ABI names
            invalid_names = ["x16", "invalid", "xyz", "", "t3", "a8"]
            for invalid_name in invalid_names:
                value = self.rf.read(invalid_name)
                self.assertEqual(value, 0, 
                               f"FAIL: Reading invalid ABI name '{invalid_name}' should return 0, got {value}")
                
                result = self.rf.write(invalid_name, 0x1234)
                self.assertFalse(result, 
                               f"FAIL: Writing to invalid ABI name '{invalid_name}' should return False, got {result}")
            
            # Test invalid types
            invalid_types = [1.5, None, [], {}, object()]
            for invalid_type in invalid_types:
                value = self.rf.read(invalid_type)
                self.assertEqual(value, 0, 
                               f"FAIL: Reading invalid type {type(invalid_type)} should return 0, got {value}")
                
                result = self.rf.write(invalid_type, 0x1234)
                self.assertFalse(result, 
                               f"FAIL: Writing to invalid type {type(invalid_type)} should return False, got {result}")
            
            # Restore stdout
            sys.stdout = old_stdout
            error_output = captured_output.getvalue()
            
            # Verify error messages were printed
            self.assertGreater(len(error_output), 0, 
                             "FAIL: Error messages should be printed for invalid identifiers")
            
            print("✅ PASS: RegisterFile invalid identifiers test completed successfully")
            
        except Exception as e:
            sys.stdout = old_stdout  # Restore stdout in case of error
            self.fail(f"FAIL: RegisterFile invalid identifiers test failed with error: {str(e)}")
    
    def test_registerfile_edge_cases(self):
        """Test edge cases"""
        try:
            # Test maximum values
            max_16bit = 0xFFFF
            self.rf.write(15, max_16bit)
            self.assertEqual(self.rf.read(15), max_16bit, 
                           f"FAIL: Maximum 16-bit value 0x{max_16bit:04X} should be stored correctly")
            
            # Test minimum values  
            self.rf.write(14, 0x0000)
            self.assertEqual(self.rf.read(14), 0x0000, 
                           "FAIL: Minimum value 0x0000 should be stored correctly")
            
            # Test value masking
            large_value = 0x123456
            expected_masked = 0x3456
            self.rf.write(13, large_value)
            actual = self.rf.read(13)
            self.assertEqual(actual, expected_masked, 
                           f"FAIL: Large value 0x{large_value:06X} should be masked to 0x{expected_masked:04X}, got 0x{actual:04X}")
            
            # Test writing same value multiple times
            for _ in range(5):
                result = self.rf.write(12, 0x5555)
                self.assertTrue(result, "FAIL: Multiple writes to same register should succeed")
                self.assertEqual(self.rf.read(12), 0x5555, 
                               "FAIL: Multiple writes should maintain correct value")
            
            print("✅ PASS: RegisterFile edge cases test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: RegisterFile edge cases test failed with error: {str(e)}")
    
    def test_registerfile_display(self):
        """Test display functionality"""
        try:
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            # Write some values and display
            self.rf.write(1, 0x1111)
            self.rf.write("t0", 0x2222)
            self.rf.write(10, 0x3333)
            
            # Call display
            self.rf.display_register_file()
            
            # Restore stdout and get output
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            
            # Verify output contains expected information
            self.assertIn("x0:", output, "FAIL: Display should include x0 register")
            self.assertIn("x1:", output, "FAIL: Display should include x1 register")
            self.assertIn("0x1111", output, "FAIL: Display should show written value 0x1111")
            self.assertIn("0x2222", output, "FAIL: Display should show written value 0x2222")
            self.assertIn("0x3333", output, "FAIL: Display should show written value 0x3333")
            
            print("✅ PASS: RegisterFile display test completed successfully")
            
        except Exception as e:
            sys.stdout = old_stdout  # Restore stdout in case of error
            self.fail(f"FAIL: RegisterFile display test failed with error: {str(e)}")


class TestIntegration(unittest.TestCase):
    """Integration tests για Register + RegisterFile"""
    
    def setUp(self):
        """Setup για integration tests"""
        self.rf = RegisterFile()
    
    def test_complete_workflow(self):
        """Test πλήρους workflow με όλες τις λειτουργίες"""
        try:
            # Simulate assembly operations: ADD x3, x1, x2
            # 1. Load values to x1 and x2
            self.rf.write("ra", 100)    # x1 = 100
            self.rf.write("sp", 200)    # x2 = 200
            
            # 2. Read values (simulating ALU read)
            val1 = self.rf.read(1)      # Read x1
            val2 = self.rf.read(2)      # Read x2
            
            # 3. Perform operation (simulating ALU)
            result = val1 + val2        # 100 + 200 = 300
            
            # 4. Write result back (simulating ALU write-back)
            success = self.rf.write("gp", result)  # x3 = 300
            
            # 5. Verify all operations
            self.assertEqual(val1, 100, f"FAIL: x1 should contain 100, got {val1}")
            self.assertEqual(val2, 200, f"FAIL: x2 should contain 200, got {val2}")
            self.assertTrue(success, "FAIL: Write to x3 should succeed")
            self.assertEqual(self.rf.read(3), 300, f"FAIL: x3 should contain 300, got {self.rf.read(3)}")
            
            # 6. Test x0 protection during workflow
            self.rf.write(0, 999)  # Should fail
            self.assertEqual(self.rf.read("zero"), 0, "FAIL: x0 should remain 0 throughout workflow")
            
            print("✅ PASS: Complete workflow integration test completed successfully")
            
        except Exception as e:
            self.fail(f"FAIL: Integration test failed with error: {str(e)}")


def run_all_tests():
    """Εκτελεί όλα τα tests με detailed reporting"""
    print("🧪 RISC-V RegisterFile Unit Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add Register tests
    test_suite.addTest(unittest.makeSuite(TestRegister))
    
    # Add RegisterFile tests
    test_suite.addTest(unittest.makeSuite(TestRegisterFile))
    
    # Add Integration tests
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if len(result.failures) == 0 and len(result.errors) == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return True
    else:
        print(f"\n⚠️  {len(result.failures + result.errors)} TESTS FAILED")
        return False

if __name__ == "__main__":
    unittest.main()  # Αυτό είναι το πιο απλό!