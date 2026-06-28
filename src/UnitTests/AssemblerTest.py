"""
Unit Tests για τον RISC-V Assembler

Περιλαμβάνει:
- Test βασικών εντολών
- Test labels και branches
- Test binary file generation
- Test complete workflow
"""

import sys
import tempfile
from pathlib import Path
from test_utils import add_src_to_path, configure_utf8_stdio

# Προσθήκη του parent directory στο Python path
configure_utf8_stdio()
add_src_to_path()

from Assembler import RiscVAssembler, BinaryLoader
from MainCPU import RiscVProcessor


class AssemblerTests:
    """Test suite για τον RISC-V Assembler"""
    
    def __init__(self):
        self.test_count = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def _write_temp_asm(self, temp_dir, filename, content):
        asm_path = Path(temp_dir) / filename
        asm_path.write_text(content, encoding='utf-8')
        return asm_path

    def _assemble_temp_asm(self, assembler, filename, content):
        with tempfile.TemporaryDirectory() as temp_dir:
            asm_path = self._write_temp_asm(temp_dir, filename, content)
            return assembler.assemble_file(str(asm_path))

    def _binary_roundtrip(self, assembler, content):
        with tempfile.TemporaryDirectory() as temp_dir:
            asm_path = self._write_temp_asm(temp_dir, 'test_binary.asm', content)
            bin_path = Path(temp_dir) / 'test_binary.bin'
            original_code = assembler.assemble_file(str(asm_path))
            assembler.save_binary_file(str(bin_path))
            loader = BinaryLoader()
            return original_code, loader.load_binary_file(str(bin_path))

    def _generate_hex_content(self, assembler, content):
        with tempfile.TemporaryDirectory() as temp_dir:
            asm_path = self._write_temp_asm(temp_dir, 'test_hex.asm', content)
            hex_path = Path(temp_dir) / 'test_hex.hex'
            assembler.assemble_file(str(asm_path))
            assembler.save_hex_file(str(hex_path))
            if not hex_path.exists():
                raise AssertionError("Hex file was not created")
            return hex_path.read_text(encoding='utf-8')

    def _compile_and_save_outputs(self, assembler, content):
        with tempfile.TemporaryDirectory() as temp_dir:
            asm_path = self._write_temp_asm(temp_dir, 'test_complete.asm', content)
            bin_path = Path(temp_dir) / 'test_complete.bin'
            hex_path = Path(temp_dir) / 'test_complete.hex'
            machine_code = assembler.assemble_file(str(asm_path))
            assembler.save_binary_file(str(bin_path))
            assembler.save_hex_file(str(hex_path))
            return machine_code
    
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
    
    def test_basic_instructions(self):
        """Test βασικών εντολών"""
        print("Testing basic R-type and I-type instructions...")
        
        test_code = """
        # Basic instruction test
        addi x1, x0, 10    # I-type
        addi x2, x0, 5     # I-type
        add x3, x1, x2     # R-type
        sub x4, x1, x2     # R-type
        and x5, x1, x2     # R-type
        or x6, x1, x2      # R-type
        halt
        """
        
        assembler = RiscVAssembler()
        
        # Αποθήκευση test αρχείου
        with tempfile.TemporaryDirectory() as temp_dir:
            asm_path = self._write_temp_asm(temp_dir, 'test_basic.asm', test_code)
            machine_code = assembler.assemble_file(str(asm_path))
        
        # Έλεγχος αποτελεσμάτων
        expected_instructions = 7
        if len(machine_code) != expected_instructions:
            raise AssertionError(f"Expected {expected_instructions} instructions, got {len(machine_code)}")
        
        # Έλεγχος συγκεκριμένων εντολών
        if machine_code[0] != 0x510A:  # addi x1, x0, 10
            raise AssertionError(f"Expected 0x510A, got 0x{machine_code[0]:04X}")
        
        if machine_code[2] != 0x0312:  # add x3, x1, x2
            raise AssertionError(f"Expected 0x0312, got 0x{machine_code[2]:04X}")
        
        print(f"   ✓ Generated {len(machine_code)} instructions correctly")
    
    def test_labels_and_branches(self):
        """Test labels και branch εντολών"""
        print("Testing labels and branch instructions...")
        
        test_code = """
        # Label and branch test
        main:
            addi x1, x0, 5
            addi x2, x0, 5
            beq x1, x2, equal
            addi x3, x0, 1    # Should be skipped
        equal:
            addi x4, x0, 2
            halt
        """
        
        assembler = RiscVAssembler()
        
        # Αποθήκευση test αρχείου
        with tempfile.TemporaryDirectory() as temp_dir:
            asm_path = self._write_temp_asm(temp_dir, 'test_labels.asm', test_code)
            machine_code = assembler.assemble_file(str(asm_path))
        
        # Έλεγχος labels
        if 'main' not in assembler.labels:
            raise AssertionError("Label 'main' not found")
        
        if 'equal' not in assembler.labels:
            raise AssertionError("Label 'equal' not found")
        
        if assembler.labels['main'] != 0:
            raise AssertionError(f"Label 'main' should be at address 0, got {assembler.labels['main']}")
        
        if assembler.labels['equal'] != 4:
            raise AssertionError(f"Label 'equal' should be at address 4, got {assembler.labels['equal']}")
        
        print(f"   ✓ Labels found: {assembler.labels}")
        print(f"   ✓ Generated {len(machine_code)} instructions")
    
    def test_memory_operations(self):
        """Test memory operations (LW/SW)"""
        print("Testing memory operations...")
        
        test_code = """
        # Memory operations test
        addi x1, x0, 10
        sw x1, 0(x2)      # Store x1 to memory[x2+0]
        lw x3, 0(x2)      # Load from memory[x2+0] to x3
        sw x3, 4(x2)      # Store x3 to memory[x2+4]
        halt
        """
        
        assembler = RiscVAssembler()
        
        # Αποθήκευση test αρχείου
        with tempfile.TemporaryDirectory() as temp_dir:
            asm_path = self._write_temp_asm(temp_dir, 'test_memory.asm', test_code)
            machine_code = assembler.assemble_file(str(asm_path))
        
        # Έλεγχος εντολών
        if len(machine_code) != 5:
            raise AssertionError(f"Expected 5 instructions, got {len(machine_code)}")
        
        # Έλεγχος SW εντολής (opcode 0x9)
        sw_instruction = machine_code[1]
        if (sw_instruction >> 12) != 0x9:
            raise AssertionError(f"SW instruction opcode should be 0x9, got 0x{sw_instruction >> 12:X}")
        
        # Έλεγχος LW εντολής (opcode 0x8)
        lw_instruction = machine_code[2]
        if (lw_instruction >> 12) != 0x8:
            raise AssertionError(f"LW instruction opcode should be 0x8, got 0x{lw_instruction >> 12:X}")
        
        print(f"   ✓ Memory operations encoded correctly")
    
    def test_binary_file_generation(self):
        """Test binary file generation και loading"""
        print("Testing binary file generation and loading...")
        
        test_code = """
        # Binary file test
        addi x1, x0, 15
        addi x2, x0, 10
        add x3, x1, x2
        halt
        """
        
        assembler = RiscVAssembler()
        
        # Αποθήκευση test αρχείου
        original_code, loaded_code = self._binary_roundtrip(assembler, test_code)
        
        # Σύγκριση
        if len(original_code) != len(loaded_code):
            raise AssertionError(f"Length mismatch: {len(original_code)} vs {len(loaded_code)}")
        
        for i, (orig, loaded) in enumerate(zip(original_code, loaded_code)):
            if orig != loaded:
                raise AssertionError(f"Instruction {i}: 0x{orig:04X} vs 0x{loaded:04X}")
        
        print(f"   ✓ Binary file saved and loaded correctly")
        print(f"   ✓ {len(original_code)} instructions verified")
    
    def test_hex_file_generation(self):
        """Test hex file generation"""
        print("Testing hex file generation...")
        
        test_code = """
        # Hex file test
        addi x1, x0, 1
        addi x2, x0, 2
        halt
        """
        
        assembler = RiscVAssembler()
        
        # Αποθήκευση test αρχείου
        content = self._generate_hex_content(assembler, test_code)
        
        if '5101' not in content:  # addi x1, x0, 1 → 0x5101
            raise AssertionError("Expected instruction not found in hex file")
        
        print(f"   ✓ Hex file created and contains correct data")
    
    def test_error_handling(self):
        """Test error handling"""
        print("Testing error handling...")
        
        assembler = RiscVAssembler()
        
        # Test 1: Invalid register
        try:
            assembler._parse_register('x99')
            raise AssertionError("Should have failed on invalid register")
        except ValueError:
            print("   ✓ Invalid register detection works")
        
        # Test 2: Invalid instruction
        invalid_code = """
        invalid_instruction x1, x2, x3
        """
        
        machine_code = self._assemble_temp_asm(assembler, 'test_invalid.asm', invalid_code)
        
        if len(machine_code) != 0:
            raise AssertionError("Should have produced no valid instructions")
        
        print("   ✓ Invalid instruction handling works")
    
    def test_complete_program(self):
        """Test πλήρους προγράμματος"""
        print("Testing complete program...")
        
        test_code = """
        # Complete program test
        # Calculate factorial of 3
        main:
            addi x1, x0, 3      # n = 3
            addi x2, x0, 1      # result = 1
            
        loop:
            beq x1, x0, done    # if n == 0, goto done
            and x3, x1, x2      # temp = n & result (using AND as multiply substitute)
            addi x2, x3, 0      # result = temp
            addi x1, x1, -1     # n = n - 1 (using -1 as 15 in 4-bit)
            bne x1, x0, loop    # if n != 0, goto loop
            
        done:
            sw x2, 0(x0)        # store result
            halt
        """
        
        assembler = RiscVAssembler()
        
        # Αποθήκευση test αρχείου
        machine_code = self._compile_and_save_outputs(assembler, test_code)
        
        # Έλεγχος ότι το πρόγραμμα compiled
        if len(machine_code) == 0:
            raise AssertionError("Program should have compiled successfully")
        
        # Έλεγχος labels
        expected_labels = ['main', 'loop', 'done']
        for label in expected_labels:
            if label not in assembler.labels:
                raise AssertionError(f"Label '{label}' not found")
        
        print(f"   ✓ Complete program compiled successfully")
        print(f"   ✓ {len(machine_code)} instructions generated")
        print(f"   ✓ Labels: {assembler.labels}")
        
        print(f"   ✓ Output files generated")
    
    def test_abi_register_names(self):
        """Test ABI register names"""
        print("Testing ABI register names...")
        
        test_code = """
        # ABI register test
        addi ra, zero, 1    # x1 = 1
        addi sp, zero, 2    # x2 = 2  
        add a0, ra, sp      # x10 = x1 + x2
        add a1, t0, t1      # x11 = x5 + x6
        halt
        """
        
        assembler = RiscVAssembler()
        
        # Αποθήκευση test αρχείου
        machine_code = self._assemble_temp_asm(assembler, 'test_abi.asm', test_code)
        
        # Έλεγχος ότι τα ABI names μετατράπηκαν σωστά
        if len(machine_code) != 5:
            raise AssertionError(f"Expected 5 instructions, got {len(machine_code)}")
        
        # Έλεγχος πρώτης εντολής: addi ra, zero, 1 → addi x1, x0, 1
        first_instruction = machine_code[0]
        if first_instruction != 0x5101:  # opcode=5, rd=1, rs1=0, imm=1
            raise AssertionError(f"Expected 0x5101, got 0x{first_instruction:04X}")
        
        print(f"   ✓ ABI register names work correctly")

    def test_negative_addi_execution(self):
        """Test negative ADDI source operands execute as subtraction."""
        print("Testing negative ADDI execution...")

        test_code = """
        addi x1, x0, 2
        loop:
            addi x1, x1, -1
            bne x1, x0, loop
            halt
        """

        assembler = RiscVAssembler()

        machine_code = self._assemble_temp_asm(assembler, 'test_negative_addi.asm', test_code)

        if machine_code[1] != 0xD111:
            raise AssertionError(f"Expected internal SUBI 0xD111, got 0x{machine_code[1]:04X}")

        processor = RiscVProcessor(16, 16)
        processor.load_program_direct(machine_code)
        success = processor.run(max_cycles=20)

        if not success or not processor.halted:
            raise AssertionError("Loop with negative ADDI should terminate")

        final_value = processor.register_file.read(1)
        if final_value != 0:
            raise AssertionError(f"x1 should be 0, got {final_value}")

        print("   Negative ADDI decrements and loop terminates")

    def run_all_tests(self):
        """Εκτελεί όλα τα tests"""
        print("=" * 60)
        print("🧪 RISC-V ASSEMBLER UNIT TESTS")
        print("=" * 60)
        
        # Εκτέλεση όλων των tests
        self.run_test("Basic Instructions", self.test_basic_instructions)
        self.run_test("Labels and Branches", self.test_labels_and_branches)
        self.run_test("Memory Operations", self.test_memory_operations)
        self.run_test("Binary File Generation", self.test_binary_file_generation)
        self.run_test("Hex File Generation", self.test_hex_file_generation)
        self.run_test("Error Handling", self.test_error_handling)
        self.run_test("Complete Program", self.test_complete_program)
        self.run_test("ABI Register Names", self.test_abi_register_names)
        self.run_test("Negative ADDI Execution", self.test_negative_addi_execution)
        
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
    tests = AssemblerTests()
    
    test_methods = {
        'basic': tests.test_basic_instructions,
        'labels': tests.test_labels_and_branches,
        'memory': tests.test_memory_operations,
        'binary': tests.test_binary_file_generation,
        'hex': tests.test_hex_file_generation,
        'error': tests.test_error_handling,
        'complete': tests.test_complete_program,
        'abi': tests.test_abi_register_names,
        'negative-addi': tests.test_negative_addi_execution
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
        tests = AssemblerTests()
        success = tests.run_all_tests()
        
        # Exit code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
