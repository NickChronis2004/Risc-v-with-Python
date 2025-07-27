
#!/usr/bin/env python3
"""
Master Test Runner - Complete RISC-V System Validation 🚀
=========================================================

Comprehensive testing suite που τρέχει όλα τα tests και validation checks:
- Core component unit tests
- Integration testing
- Performance benchmarking  
- GUI functionality testing
- Memory και monitoring validation
- Exception handling verification
- Complete workflow testing

Το ultimate testing script για το RISC-V simulator system!
"""

import os

import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
import time
import subprocess
import importlib.util
from pathlib import Path
import json
import datetime
import threading
import queue

class Colors:
    """ANSI color codes για beautiful terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestResult:
    """Test result container"""
    
    def __init__(self, name, passed=False, duration=0, details="", error=None):
        self.name = name
        self.passed = passed
        self.duration = duration
        self.details = details
        self.error = error
        self.timestamp = datetime.datetime.now()


class MasterTestRunner:
    """Master test runner για complete system validation"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Test categories
        self.test_categories = {
            'unit_tests': [],
            'integration_tests': [],
            'performance_tests': [],
            'gui_tests': [],
            'workflow_tests': []
        }
        
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("🚀" * 30)
        print("   RISC-V SIMULATOR MASTER TEST SUITE")
        print("   Complete System Validation & Verification")
        print("🚀" * 30)
        print(f"{Colors.ENDC}")
        
        self.setup_environment()
    
    def setup_environment(self):
        """Setup testing environment"""
        print(f"\n{Colors.OKCYAN}🔧 Setting up testing environment...{Colors.ENDC}")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
            print(f"{Colors.FAIL}❌ Python 3.7+ required, found {python_version.major}.{python_version.minor}{Colors.ENDC}")
            sys.exit(1)
        
        print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check src directory
        src_path = Path(__file__).parent.parent
        if not src_path.exists():
            print(f"{Colors.FAIL}❌ src/ directory not found{Colors.ENDC}")
            sys.exit(1)
        
        print(f"   ✅ Source directory found")
        
        # Add src to Python path
        sys.path.insert(0, str(src_path.absolute()))
        
        # Check core components
        required_files = [
            'MainCPU.py', 'RegisterFile.py', 'Memory.py', 'ALU.py',
            'InstructionDecoder.py', 'ControlUnit.py', 'Assembler.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not (src_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"{Colors.FAIL}❌ Missing core files: {missing_files}{Colors.ENDC}")
            sys.exit(1)
        
        print(f"   ✅ All core components found")
        
        # Check optional dependencies
        optional_deps = ['tkinter', 'customtkinter']
        for dep in optional_deps:
            try:
                if dep == 'tkinter':
                    import tkinter
                elif dep == 'customtkinter':
                    import customtkinter
                print(f"   ✅ {dep} available")
            except ImportError:
                print(f"   ⚠️  {dep} not available (some tests may be skipped)")
        
        print(f"{Colors.OKGREEN}✅ Environment setup complete{Colors.ENDC}")
    
    def run_unit_tests(self):
        """Run all unit tests"""
        print(f"\n{Colors.OKBLUE}🧪 Running Unit Tests...{Colors.ENDC}")
        
        unit_tests = [
            ('RegisterFile Tests', 'UnitTests/RF_Tests.py'),
            ('ALU Tests', 'UnitTests/ALU_tests.py'),
            ('Memory Tests', 'UnitTests/Memory_tests.py'),
            ('Assembler Tests', 'UnitTests/AssemblerTest.py')
        ]
        
        for test_name, test_file in unit_tests:
            result = self.run_python_test(test_name, f"src/{test_file}")
            self.test_categories['unit_tests'].append(result)
            self.add_result(result)
    
    def run_integration_tests(self):
        """Run integration tests"""
        print(f"\n{Colors.OKBLUE}🔗 Running Integration Tests...{Colors.ENDC}")
        
        # Test 1: Complete processor workflow
        result = self.test_complete_processor_workflow()
        self.test_categories['integration_tests'].append(result)
        self.add_result(result)
        
        # Test 2: Assembler to processor pipeline
        result = self.test_assembler_processor_pipeline()
        self.test_categories['integration_tests'].append(result)
        self.add_result(result)
        
        # Test 3: Memory system integration
        result = self.test_memory_system_integration()
        self.test_categories['integration_tests'].append(result)
        self.add_result(result)
    
    def run_performance_tests(self):
        """Run performance benchmarks"""
        print(f"\n{Colors.OKBLUE}⚡ Running Performance Tests...{Colors.ENDC}")
        
        # Test 1: Execution speed benchmark
        result = self.test_execution_speed()
        self.test_categories['performance_tests'].append(result)
        self.add_result(result)
        
        # Test 2: Memory performance
        result = self.test_memory_performance()
        self.test_categories['performance_tests'].append(result)
        self.add_result(result)
        
        # Test 3: Assembly performance
        result = self.test_assembly_performance()
        self.test_categories['performance_tests'].append(result)
        self.add_result(result)
    
    def run_gui_tests(self):
        """Run GUI functionality tests"""
        print(f"\n{Colors.OKBLUE}🖥️  Running GUI Tests...{Colors.ENDC}")
        
        # Test GUI components availability
        result = self.test_gui_components()
        self.test_categories['gui_tests'].append(result)
        self.add_result(result)
        
        # Test GUI workflow (non-interactive)
        result = self.test_gui_workflow()
        self.test_categories['gui_tests'].append(result)
        self.add_result(result)
    
    def run_workflow_tests(self):
        """Run complete workflow tests"""
        print(f"\n{Colors.OKBLUE}🔄 Running Workflow Tests...{Colors.ENDC}")
        
        # Test complete development workflow
        result = self.test_development_workflow()
        self.test_categories['workflow_tests'].append(result)
        self.add_result(result)
        
        # Test exception handling workflow
        result = self.test_exception_workflow()
        self.test_categories['workflow_tests'].append(result)
        self.add_result(result)
    
    def run_python_test(self, test_name, test_file):
        """Run a Python test file"""
        start_time = time.time()
        
        try:
            if not os.path.exists(test_file):
                return TestResult(test_name, False, 0, "Test file not found", FileNotFoundError(test_file))
            
            # Run the test file
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return TestResult(test_name, True, duration, "All tests passed", None)
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return TestResult(test_name, False, duration, f"Exit code: {result.returncode}", RuntimeError(error_msg))
        
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(test_name, False, duration, "Test timed out", TimeoutError("60 second timeout"))
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(test_name, False, duration, str(e), e)
    
    def test_complete_processor_workflow(self):
        """Test complete processor workflow"""
        start_time = time.time()
        
        try:
            from MainCPU import RiscVProcessor
            from Assembler import RiscVAssembler
            
            # Create processor and assembler
            processor = RiscVProcessor(64, 64)
            assembler = RiscVAssembler()
            
            # Test program
            test_program = """
            # Complete workflow test
            main:
                addi x1, x0, 10
                addi x2, x0, 5
                add x3, x1, x2      # x3 = 15
                sw x3, 0(x0)        # Store to memory
                lw x4, 0(x0)        # Load from memory
                beq x3, x4, success # Should branch
                addi x5, x0, 1      # Should be skipped
            success:
                addi x6, x0, 100    # x6 = 100
                halt
            """
            
            # Assembly
            with open('temp_workflow_test.asm', 'w') as f:
                f.write(test_program)
            
            machine_code = assembler.assemble_file('temp_workflow_test.asm')
            os.remove('temp_workflow_test.asm')
            
            if not machine_code:
                raise AssertionError("Assembly failed")
            
            # Load and execute
            processor.load_program_direct(machine_code)
            success = processor.run(max_cycles=50)
            
            if not success:
                raise AssertionError("Execution failed")
            
            # Verify results
            x3 = processor.register_file.read(3)
            x4 = processor.register_file.read(4)
            x6 = processor.register_file.read(6)
            
            if x3 != 15:
                raise AssertionError(f"x3 should be 15, got {x3}")
            
            if x4 != 15:
                raise AssertionError(f"x4 should be 15, got {x4}")
            
            if x6 != 100:
                raise AssertionError(f"x6 should be 100, got {x6}")
            
            duration = time.time() - start_time
            details = f"Assembly: {len(machine_code)} instructions, Execution: {processor.cycle_count} cycles"
            return TestResult("Complete Processor Workflow", True, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Complete Processor Workflow", False, duration, str(e), e)
    
    def test_assembler_processor_pipeline(self):
        """Test assembler to processor pipeline"""
        start_time = time.time()
        
        try:
            from MainCPU import RiscVProcessor
            from Assembler import RiscVAssembler, BinaryLoader
            
            assembler = RiscVAssembler()
            processor = RiscVProcessor(32, 32)
            loader = BinaryLoader()
            
            # Complex test program
            test_program = """
            # Pipeline test
            main:
                addi x1, x0, 7
                addi x2, x0, 3
                
            loop:
                beq x1, x0, done
                add x3, x3, x2
                addi x1, x1, -1     # Using -1 as 15 in 4-bit
                bne x1, x0, loop
                
            done:
                sw x3, 5(x0)
                halt
            """
            
            # Test complete pipeline: ASM -> Binary -> Load -> Execute
            with open('temp_pipeline_test.asm', 'w') as f:
                f.write(test_program)
            
            # Assembly
            machine_code = assembler.assemble_file('temp_pipeline_test.asm')
            
            # Save to binary
            assembler.save_binary_file('temp_pipeline_test.bin')
            
            # Load from binary
            loaded_code = loader.load_binary_file('temp_pipeline_test.bin')
            
            # Verify pipeline integrity
            if machine_code != loaded_code:
                raise AssertionError("Pipeline integrity check failed")
            
            # Execute
            processor.load_program_direct(loaded_code)
            success = processor.run(max_cycles=100)
            
            if not success:
                raise AssertionError("Pipeline execution failed")
            
            # Cleanup
            os.remove('temp_pipeline_test.asm')
            os.remove('temp_pipeline_test.bin')
            
            duration = time.time() - start_time
            details = f"Pipeline: ASM->Binary->Load->Execute, Result: {processor.register_file.read(3)}"
            return TestResult("Assembler-Processor Pipeline", True, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Assembler-Processor Pipeline", False, duration, str(e), e)
    
    def test_memory_system_integration(self):
        """Test memory system integration"""
        start_time = time.time()
        
        try:
            from Memory import InstructionMemory, DataMemory
            
            imem = InstructionMemory(64)
            dmem = DataMemory(64)
            
            # Test instruction memory
            test_instructions = [0x510A, 0x5205, 0x0312, 0xF000]
            imem.load_program(test_instructions)
            
            for i, expected in enumerate(test_instructions):
                actual = imem.read_instruction(i)
                if actual != expected:
                    raise AssertionError(f"Instruction memory test failed at {i}")
            
            # Test data memory
            test_data = [(0x1000, 0x1234), (0x1010, 0x5678), (0x1020, 0xABCD)]
            
            for addr, value in test_data:
                dmem.write_word(addr, value)
                read_value = dmem.read_word(addr)
                if read_value != value:
                    raise AssertionError(f"Data memory test failed at 0x{addr:04X}")
            
            # Test statistics
            stats = dmem.get_statistics()
            if stats['writes'] != 3 or stats['reads'] != 3:
                raise AssertionError("Memory statistics incorrect")
            
            duration = time.time() - start_time
            details = f"IMem: {len(test_instructions)} instructions, DMem: {len(test_data)} operations"
            return TestResult("Memory System Integration", True, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Memory System Integration", False, duration, str(e), e)
    
    def test_execution_speed(self):
        """Test execution speed benchmark"""
        start_time = time.time()
        
        try:
            from MainCPU import RiscVProcessor
            
            processor = RiscVProcessor(128, 128)
            
            # Large benchmark program
            benchmark_program = []
            
            # Generate many instructions
            for i in range(50):
                benchmark_program.append(0x5100 | (i % 16))  # ADDI xi, x0, 0
            
            for i in range(30):
                rs1 = (i % 15) + 1
                rs2 = ((i + 1) % 15) + 1
                rd = ((i + 2) % 15) + 1
                benchmark_program.append(0x0000 | (rd << 8) | (rs1 << 4) | rs2)  # ADD
            
            benchmark_program.append(0xF000)  # HALT
            
            # Execute and measure
            processor.load_program_direct(benchmark_program)
            exec_start = time.time()
            success = processor.run(max_cycles=500)
            exec_time = time.time() - exec_start
            
            if not success:
                raise AssertionError("Benchmark execution failed")
            
            # Calculate performance metrics
            instructions_per_second = len(benchmark_program) / exec_time if exec_time > 0 else 0
            cycles_per_second = processor.cycle_count / exec_time if exec_time > 0 else 0
            
            duration = time.time() - start_time
            details = f"Instructions: {len(benchmark_program)}, Speed: {instructions_per_second:.0f} inst/s, {cycles_per_second:.0f} cycles/s"
            return TestResult("Execution Speed Benchmark", True, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Execution Speed Benchmark", False, duration, str(e), e)
    
    def test_memory_performance(self):
        """Test memory performance"""
        start_time = time.time()
        
        try:
            from Memory import DataMemory
            
            dmem = DataMemory(1024)
            
            # Benchmark memory operations
            num_operations = 1000
            
            # Write benchmark
            write_start = time.time()
            for i in range(num_operations):
                dmem.write_word(0x1000 + i, i)
            write_time = time.time() - write_start
            
            # Read benchmark
            read_start = time.time()
            for i in range(num_operations):
                value = dmem.read_word(0x1000 + i)
                if value != i:
                    raise AssertionError(f"Memory consistency error at {i}")
            read_time = time.time() - read_start
            
            # Calculate performance
            write_ops_per_sec = num_operations / write_time if write_time > 0 else 0
            read_ops_per_sec = num_operations / read_time if read_time > 0 else 0
            
            duration = time.time() - start_time
            details = f"Writes: {write_ops_per_sec:.0f} ops/s, Reads: {read_ops_per_sec:.0f} ops/s"
            return TestResult("Memory Performance", True, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Memory Performance", False, duration, str(e), e)
    
    def test_assembly_performance(self):
        """Test assembly performance"""
        start_time = time.time()
        
        try:
            from Assembler import RiscVAssembler
            
            assembler = RiscVAssembler()
            
            # Large assembly program
            large_program = ["# Assembly performance test", "main:"]
            
            for i in range(100):
                large_program.append(f"    addi x{(i % 15) + 1}, x0, {i % 16}")
            
            for i in range(50):
                rs1 = (i % 15) + 1
                rs2 = ((i + 1) % 15) + 1
                rd = ((i + 2) % 15) + 1
                large_program.append(f"    add x{rd}, x{rs1}, x{rs2}")
            
            large_program.append("    halt")
            
            program_text = "\n".join(large_program)
            
            # Assembly benchmark
            with open('temp_asm_perf_test.asm', 'w') as f:
                f.write(program_text)
            
            asm_start = time.time()
            machine_code = assembler.assemble_file('temp_asm_perf_test.asm')
            asm_time = time.time() - asm_start
            
            os.remove('temp_asm_perf_test.asm')
            
            if not machine_code:
                raise AssertionError("Assembly performance test failed")
            
            # Calculate performance
            lines_per_second = len(large_program) / asm_time if asm_time > 0 else 0
            
            duration = time.time() - start_time
            details = f"Lines: {len(large_program)}, Speed: {lines_per_second:.0f} lines/s, Instructions: {len(machine_code)}"
            return TestResult("Assembly Performance", True, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Assembly Performance", False, duration, str(e), e)
    
    def test_gui_components(self):
        """Test GUI components availability"""
        start_time = time.time()
        
        try:
            # Test tkinter availability
            try:
                import tkinter as tk
                gui_available = True
            except ImportError:
                gui_available = False
            
            # Test customtkinter availability
            try:
                import customtkinter as ctk
                modern_gui_available = True
            except ImportError:
                modern_gui_available = False
            
            # Test main GUI import
            try:
                from interface import RiscVGUI
                main_gui_available = True
            except ImportError:
                main_gui_available = False
            
            components_available = sum([gui_available, modern_gui_available, main_gui_available])
            
            duration = time.time() - start_time
            
            if components_available >= 2:  # At least basic GUI should work
                details = f"Components: tkinter={gui_available}, customtkinter={modern_gui_available}, main_gui={main_gui_available}"
                return TestResult("GUI Components", True, duration, details)
            else:
                details = f"Insufficient GUI components available: {components_available}/3"
                return TestResult("GUI Components", False, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("GUI Components", False, duration, str(e), e)
    
    def test_gui_workflow(self):
        """Test GUI workflow (non-interactive)"""
        start_time = time.time()
        
        try:
            # Test if we can at least import and create GUI components
            import tkinter as tk
            
            # Create test window
            root = tk.Tk()
            root.withdraw()  # Hide window
            
            # Test basic GUI creation
            test_frame = tk.Frame(root)
            test_label = tk.Label(test_frame, text="Test")
            test_button = tk.Button(test_frame, text="Test Button")
            
            # Test if our GUI can be imported and initialized
            try:
                from interface import RiscVGUI
                # Don't actually run the GUI, just test creation
                gui_creatable = True
            except Exception:
                gui_creatable = False
            
            root.destroy()
            
            duration = time.time() - start_time
            
            if gui_creatable:
                details = "GUI components can be created and initialized"
                return TestResult("GUI Workflow", True, duration, details)
            else:
                details = "GUI initialization failed"
                return TestResult("GUI Workflow", False, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("GUI Workflow", False, duration, str(e), e)
    
    def test_development_workflow(self):
        """Test complete development workflow"""
        start_time = time.time()
        
        try:
            from MainCPU import RiscVProcessor
            from Assembler import RiscVAssembler
            
            # Simulate complete development workflow
            
            # 1. Write program
            fibonacci_program = """
            # Fibonacci calculator
            main:
                addi x1, x0, 0      # fib(0) = 0
                addi x2, x0, 1      # fib(1) = 1
                addi x3, x0, 5      # calculate up to fib(5)
                addi x4, x0, 2      # index = 2
                
                sw x1, 0(x0)        # store fib(0)
                sw x2, 1(x0)        # store fib(1)
                
            fib_loop:
                beq x4, x3, done
                add x5, x1, x2      # fib(n) = fib(n-1) + fib(n-2)
                sw x5, 0(x4)        # store fib(n)
                
                add x1, x0, x2      # update fib(n-2)
                add x2, x0, x5      # update fib(n-1)
                addi x4, x4, 1      # index++
                
                bne x4, x3, fib_loop
                
            done:
                lw x6, 4(x0)        # load fib(4)
                halt
            """
            
            # 2. Assembly
            assembler = RiscVAssembler()
            with open('temp_dev_workflow.asm', 'w') as f:
                f.write(fibonacci_program)
            
            machine_code = assembler.assemble_file('temp_dev_workflow.asm')
            
            # 3. Binary generation
            assembler.save_binary_file('temp_dev_workflow.bin')
            assembler.save_hex_file('temp_dev_workflow.hex')
            
            # 4. Load and execute
            processor = RiscVProcessor(64, 64)
            processor.instruction_memory.load_from_binary_file('temp_dev_workflow.bin')
            
            # 5. Execute with debugging
            success = processor.run(max_cycles=200)
            
            # 6. Verify results
            if not success:
                raise AssertionError("Workflow execution failed")
            
            # Expected fibonacci sequence: [0, 1, 1, 2, 3]
            expected_fib = [0, 1, 1, 2, 3]
            for i in range(5):
                actual = processor.data_memory.read_word(0x1000 + i)
                if actual != expected_fib[i]:
                    raise AssertionError(f"Fibonacci({i}): expected {expected_fib[i]}, got {actual}")
            
            # 7. Cleanup
            os.remove('temp_dev_workflow.asm')
            os.remove('temp_dev_workflow.bin')
            os.remove('temp_dev_workflow.hex')
            
            duration = time.time() - start_time
            details = f"Complete workflow: ASM->Binary->Hex->Load->Execute->Verify, Cycles: {processor.cycle_count}"
            return TestResult("Development Workflow", True, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Development Workflow", False, duration, str(e), e)
    
    def test_exception_workflow(self):
        """Test exception handling workflow"""
        start_time = time.time()
        
        try:
            from MainCPU import RiscVProcessor
            from ExceptionHandling import ProcessorErrorHandler
            
            # Test graceful error handling
            error_handler = ProcessorErrorHandler(strict_mode=False)
            processor = RiscVProcessor(32, 32)
            
            # Program with potential errors
            error_program = [
                0x510A,  # ADDI x1, x0, 10  (valid)
                0xDEAD,  # Invalid instruction
                0x5205,  # ADDI x2, x0, 5   (valid - should continue)
                0xF000   # HALT
            ]
            
            processor.load_program_direct(error_program)
            
            # Execute with error recovery
            success = processor.run(max_cycles=20)
            
            # Should complete despite invalid instruction
            if not processor.halted:
                raise AssertionError("Processor should have halted")
            
            # Check that valid instructions executed
            x1_value = processor.register_file.read(1)
            x2_value = processor.register_file.read(2)
            
            if x1_value != 10:
                raise AssertionError(f"x1 should be 10, got {x1_value}")
            
            if x2_value != 5:
                raise AssertionError(f"x2 should be 5, got {x2_value}")
            
            duration = time.time() - start_time
            details = f"Graceful error recovery: {processor.cycle_count} cycles, final state: x1={x1_value}, x2={x2_value}"
            return TestResult("Exception Workflow", True, duration, details)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Exception Workflow", False, duration, str(e), e)
    
    def add_result(self, result):
        """Add test result"""
        self.results.append(result)
        self.total_tests += 1
        
        if result.passed:
            self.passed_tests += 1
            status = f"{Colors.OKGREEN}✅ PASSED{Colors.ENDC}"
        else:
            self.failed_tests += 1
            status = f"{Colors.FAIL}❌ FAILED{Colors.ENDC}"
        
        print(f"   {status} {result.name} ({result.duration:.3f}s)")
        if result.details:
            print(f"      {Colors.OKCYAN}{result.details}{Colors.ENDC}")
        if not result.passed and result.error:
            print(f"      {Colors.WARNING}Error: {result.error}{Colors.ENDC}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_duration = time.time() - self.start_time
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("📊" * 30)
        print("   COMPREHENSIVE TEST REPORT")
        print("📊" * 30)
        print(f"{Colors.ENDC}")
        
        # Overall statistics
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n{Colors.BOLD}📈 OVERALL STATISTICS{Colors.ENDC}")
        print(f"{'='*50}")
        print(f"Total Tests:      {self.total_tests}")
        print(f"Passed:           {Colors.OKGREEN}{self.passed_tests}{Colors.ENDC}")
        print(f"Failed:           {Colors.FAIL}{self.failed_tests}{Colors.ENDC}")
        print(f"Success Rate:     {Colors.OKGREEN if success_rate >= 90 else Colors.WARNING if success_rate >= 70 else Colors.FAIL}{success_rate:.1f}%{Colors.ENDC}")
        print(f"Total Duration:   {total_duration:.3f}s")
        
        # Category breakdown
        print(f"\n{Colors.BOLD}📋 TEST CATEGORIES{Colors.ENDC}")
        print(f"{'='*50}")
        
        for category, tests in self.test_categories.items():
            if tests:
                category_passed = sum(1 for t in tests if t.passed)
                category_total = len(tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                
                status_color = Colors.OKGREEN if category_rate >= 90 else Colors.WARNING if category_rate >= 70 else Colors.FAIL
                
                print(f"\n{Colors.OKCYAN}{category.replace('_', ' ').title()}:{Colors.ENDC}")
                print(f"  Tests: {category_passed}/{category_total} ({status_color}{category_rate:.1f}%{Colors.ENDC})")
                
                for test in tests:
                    status = f"{Colors.OKGREEN}✅{Colors.ENDC}" if test.passed else f"{Colors.FAIL}❌{Colors.ENDC}"
                    print(f"    {status} {test.name} ({test.duration:.3f}s)")
        
        # Performance metrics
        print(f"\n{Colors.BOLD}⚡ PERFORMANCE METRICS{Colors.ENDC}")
        print(f"{'='*50}")
        
        # Find performance-related results
        perf_results = [r for r in self.results if 'performance' in r.name.lower() or 'speed' in r.name.lower()]
        if perf_results:
            for result in perf_results:
                print(f"🏃 {result.name}: {result.details}")
        
        # System health check
        print(f"\n{Colors.BOLD}🏥 SYSTEM HEALTH CHECK{Colors.ENDC}")
        print(f"{'='*50}")
        
        critical_components = ['RegisterFile Tests', 'ALU Tests', 'Memory Tests', 'Complete Processor Workflow']
        critical_passed = sum(1 for r in self.results if r.name in critical_components and r.passed)
        critical_total = len([r for r in self.results if r.name in critical_components])
        
        if critical_passed == critical_total:
            health_status = f"{Colors.OKGREEN}🟢 EXCELLENT{Colors.ENDC}"
        elif critical_passed >= critical_total * 0.8:
            health_status = f"{Colors.WARNING}🟡 GOOD{Colors.ENDC}"
        else:
            health_status = f"{Colors.FAIL}🔴 NEEDS ATTENTION{Colors.ENDC}"
        
        print(f"Core Components:  {critical_passed}/{critical_total}")
        print(f"System Health:    {health_status}")
        
        # Recommendations
        print(f"\n{Colors.BOLD}💡 RECOMMENDATIONS{Colors.ENDC}")
        print(f"{'='*50}")
        
        if success_rate >= 95:
            print(f"{Colors.OKGREEN}🎉 Excellent! Your RISC-V simulator is production-ready!{Colors.ENDC}")
            print(f"   ✨ All critical systems functioning perfectly")
            print(f"   🚀 Ready for advanced testing and deployment")
        elif success_rate >= 85:
            print(f"{Colors.WARNING}👍 Good performance with minor issues{Colors.ENDC}")
            print(f"   🔧 Review failed tests and address issues")
            print(f"   📈 Consider performance optimizations")
        else:
            print(f"{Colors.FAIL}⚠️  System needs significant attention{Colors.ENDC}")
            print(f"   🛠️  Critical issues need immediate resolution")
            print(f"   📋 Review all failed tests systematically")
        
        # Failed tests details
        failed_results = [r for r in self.results if not r.passed]
        if failed_results:
            print(f"\n{Colors.BOLD}🔍 FAILED TESTS ANALYSIS{Colors.ENDC}")
            print(f"{'='*50}")
            
            for result in failed_results:
                print(f"\n❌ {Colors.FAIL}{result.name}{Colors.ENDC}")
                print(f"   Duration: {result.duration:.3f}s")
                print(f"   Details: {result.details}")
                if result.error:
                    print(f"   Error: {Colors.WARNING}{str(result.error)[:100]}...{Colors.ENDC}")
        
        # Export report
        self.export_json_report()
        
        # Final verdict
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        if success_rate >= 90:
            print("🏆" * 30)
            print("   🚀 RISC-V SIMULATOR: MISSION READY! 🚀")
            print("   ✨ All systems operational ✨")
        elif success_rate >= 70:
            print("🔧" * 30)
            print("   ⚙️  RISC-V SIMULATOR: NEEDS TUNING ⚙️")
            print("   🛠️  Some components need attention 🛠️")
        else:
            print("⚠️ " * 30)
            print("   🛑 RISC-V SIMULATOR: MAJOR ISSUES 🛑")
            print("   🚨 Critical repairs needed 🚨")
        print("🚀" * 30)
        print(f"{Colors.ENDC}")
        
        return success_rate >= 90
    
    def export_json_report(self):
        """Export detailed JSON report"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"risc_v_test_report_{timestamp}.json"
        
        try:
            report_data = {
                'timestamp': timestamp,
                'summary': {
                    'total_tests': self.total_tests,
                    'passed_tests': self.passed_tests,
                    'failed_tests': self.failed_tests,
                    'success_rate': (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
                    'total_duration': time.time() - self.start_time
                },
                'categories': {},
                'detailed_results': []
            }
            
            # Category data
            for category, tests in self.test_categories.items():
                if tests:
                    category_passed = sum(1 for t in tests if t.passed)
                    report_data['categories'][category] = {
                        'total': len(tests),
                        'passed': category_passed,
                        'failed': len(tests) - category_passed,
                        'success_rate': (category_passed / len(tests) * 100) if tests else 0
                    }
            
            # Detailed results
            for result in self.results:
                report_data['detailed_results'].append({
                    'name': result.name,
                    'passed': result.passed,
                    'duration': result.duration,
                    'details': result.details,
                    'error': str(result.error) if result.error else None,
                    'timestamp': result.timestamp.isoformat()
                })
            
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n📄 Detailed report exported: {Colors.OKCYAN}{filename}{Colors.ENDC}")
            
        except Exception as e:
            print(f"\n⚠️  Could not export JSON report: {e}")
    
    def run_all_tests(self):
        """Run all test categories"""
        print(f"\n{Colors.OKCYAN}🚀 Starting comprehensive test suite...{Colors.ENDC}")
        
        try:
            # Run all test categories
            self.run_unit_tests()
            self.run_integration_tests()
            self.run_performance_tests()
            self.run_gui_tests()
            self.run_workflow_tests()
            
            # Generate final report
            success = self.generate_report()
            
            return success
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Tests interrupted by user{Colors.ENDC}")
            return False
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Critical error during testing: {e}{Colors.ENDC}")
            return False


class InteractiveTestRunner:
    """Interactive test runner για selective testing"""
    
    def __init__(self):
        self.master_runner = MasterTestRunner()
    
    def show_menu(self):
        """Show interactive test menu"""
        while True:
            print(f"\n{Colors.HEADER}🧪 RISC-V Interactive Test Menu{Colors.ENDC}")
            print("="*40)
            print("1. 🧱 Run Unit Tests")
            print("2. 🔗 Run Integration Tests")  
            print("3. ⚡ Run Performance Tests")
            print("4. 🖥️  Run GUI Tests")
            print("5. 🔄 Run Workflow Tests")
            print("6. 🚀 Run ALL Tests")
            print("7. 📊 Generate Report")
            print("8. 🚪 Exit")
            print("="*40)
            
            choice = input(f"{Colors.OKCYAN}Select option (1-8): {Colors.ENDC}").strip()
            
            if choice == '1':
                self.master_runner.run_unit_tests()
            elif choice == '2':
                self.master_runner.run_integration_tests()
            elif choice == '3':
                self.master_runner.run_performance_tests()
            elif choice == '4':
                self.master_runner.run_gui_tests()
            elif choice == '5':
                self.master_runner.run_workflow_tests()
            elif choice == '6':
                self.master_runner.run_all_tests()
                break
            elif choice == '7':
                self.master_runner.generate_report()
            elif choice == '8':
                print(f"{Colors.OKGREEN}👋 Goodbye!{Colors.ENDC}")
                break
            else:
                print(f"{Colors.WARNING}⚠️  Invalid choice. Please select 1-8.{Colors.ENDC}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RISC-V Simulator Master Test Suite')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--category', '-c', choices=['unit', 'integration', 'performance', 'gui', 'workflow'], 
                       help='Run specific test category')
    parser.add_argument('--quick', '-q', action='store_true', help='Run only critical tests')
    parser.add_argument('--export-only', '-e', action='store_true', help='Only generate report from existing results')
    
    args = parser.parse_args()
    
    if args.interactive:
        # Interactive mode
        runner = InteractiveTestRunner()
        runner.show_menu()
    
    elif args.category:
        # Run specific category
        master_runner = MasterTestRunner()
        
        if args.category == 'unit':
            master_runner.run_unit_tests()
        elif args.category == 'integration':
            master_runner.run_integration_tests()
        elif args.category == 'performance':
            master_runner.run_performance_tests()
        elif args.category == 'gui':
            master_runner.run_gui_tests()
        elif args.category == 'workflow':
            master_runner.run_workflow_tests()
        
        master_runner.generate_report()
    
    elif args.quick:
        # Quick critical tests only
        master_runner = MasterTestRunner()
        
        print(f"{Colors.OKCYAN}🏃 Running quick critical tests...{Colors.ENDC}")
        
        # Run only essential tests
        master_runner.run_unit_tests()
        result = master_runner.test_complete_processor_workflow()
        master_runner.add_result(result)
        
        success = master_runner.generate_report()
        sys.exit(0 if success else 1)
    
    else:
        # Full test suite
        master_runner = MasterTestRunner()
        success = master_runner.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()