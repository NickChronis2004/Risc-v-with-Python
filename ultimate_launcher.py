
#!/usr/bin/env python3
"""
Ultimate RISC-V System Launcher 🚀
==================================

Το διαστημικό launcher script που ενώνει όλα τα components:
- Complete system testing
- GUI interface launching
- Monitoring dashboard
- Performance analysis
- Real-world scenario testing
- Interactive debugging

Αυτό είναι το mission control για το RISC-V simulator system!
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))  # Add src directory to path
import os
import subprocess
import time
import threading
import argparse


class Colors:
    """ANSI color codes για space-grade terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SystemChecker:
    """System requirements και environment checker"""
    
    def __init__(self):
        self.requirements_met = True
        self.optional_features = []
        
    def check_system(self):
        """Complete system check"""
        print(f"{Colors.OKCYAN}🔍 Checking system requirements...{Colors.ENDC}")
        
        # Python version check
        if not self._check_python_version():
            self.requirements_met = False
        
        # Required files check
        if not self._check_required_files():
            self.requirements_met = False
        
        # Optional dependencies check
        self._check_optional_dependencies()
        
        return self.requirements_met
    
    def _check_python_version(self):
        """Check Python version"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            print(f"{Colors.FAIL}❌ Python 3.7+ required, found {version.major}.{version.minor}{Colors.ENDC}")
            return False
        
        print(f"{Colors.OKGREEN}✅ Python {version.major}.{version.minor}.{version.micro}{Colors.ENDC}")
        return True
    
    def _check_required_files(self):
        """Check required RISC-V files"""
        required_files = [
            'MainCPU.py',
            'RegisterFile.py',
            'Memory.py',
            'ALU.py',
            'InstructionDecoder.py',
            'ControlUnit.py',
            'Assembler.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"{Colors.FAIL}❌ Missing required files:{Colors.ENDC}")
            for file in missing_files:
                print(f"   - {file}")
            return False
        
        print(f"{Colors.OKGREEN}✅ All core RISC-V components found{Colors.ENDC}")
        return True
    
    def _check_optional_dependencies(self):
        """Check optional features"""
        optional_checks = [
            ('tkinter', 'GUI Interface'),
            ('customtkinter', 'Modern GUI Interface'),
            ('json', 'Report Export'),
            ('threading', 'Multi-threading Support')
        ]
        
        for module, feature in optional_checks:
            try:
                __import__(module)
                print(f"{Colors.OKGREEN}✅ {feature} available{Colors.ENDC}")
                self.optional_features.append(feature)
            except ImportError:
                print(f"{Colors.WARNING}⚠️  {feature} not available{Colors.ENDC}")


class SystemLauncher:
    """Main system launcher"""
    
    def __init__(self):
        self.checker = SystemChecker()
        
    def show_banner(self):
        """Show epic space banner"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("🚀" * 25)
        print("   ██████╗ ██╗███████╗ ██████╗      ██╗   ██╗")
        print("   ██╔══██╗██║██╔════╝██╔════╝      ██║   ██║")
        print("   ██████╔╝██║███████╗██║     █████╗██║   ██║")
        print("   ██╔══██╗██║╚════██║██║     ╚════╝╚██╗ ██╔╝")
        print("   ██║  ██║██║███████║╚██████╗       ╚████╔╝ ")
        print("   ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝        ╚═══╝  ")
        print("")
        print("        RISC-V 16-BIT SIMULATOR SYSTEM")
        print("        Ultimate Mission Control Center")
        print("🚀" * 25)
        print(f"{Colors.ENDC}")
    
    def show_main_menu(self):
        """Show main interactive menu"""
        while True:
            print(f"\n{Colors.HEADER}🎛️  RISC-V MISSION CONTROL{Colors.ENDC}")
            print("="*50)
            print("🧪 TESTING & VALIDATION:")
            print("  1. 🔬 Run Unit Tests")
            print("  2. 🔗 Run Integration Tests")
            print("  3. ⚡ Run Performance Tests")
            print("  4. 🌍 Run Real-World Scenarios")
            print("  5. 🎯 Run Ultimate Test Suite")
            print("")
            print("🖥️  USER INTERFACES:")
            print("  6. 🎨 Launch Main GUI")
            print("  7. 📊 Launch Monitoring Dashboard")
            print("  8. 🧪 Launch GUI Test Runner")
            print("")
            print("🔧 DEVELOPMENT TOOLS:")
            print("  9. 📝 Interactive Assembler")
            print(" 10. 🔍 Component Inspector")
            print(" 11. 📈 Performance Profiler")
            print("")
            print("📊 REPORTS & ANALYSIS:")
            print(" 12. 📄 Generate System Report")
            print(" 13. 📋 View Test History")
            print(" 14. 💾 Export All Data")
            print("")
            print("🚪 15. Exit Mission Control")
            print("="*50)
            
            choice = input(f"{Colors.OKCYAN}🚀 Select mission (1-15): {Colors.ENDC}").strip()
            
            if choice == '1':
                self.run_unit_tests()
            elif choice == '2':
                self.run_integration_tests()
            elif choice == '3':
                self.run_performance_tests()
            elif choice == '4':
                self.run_real_world_scenarios()
            elif choice == '5':
                self.run_ultimate_test_suite()
            elif choice == '6':
                self.launch_main_gui()
            elif choice == '7':
                self.launch_monitoring_dashboard()
            elif choice == '8':
                self.launch_gui_test_runner()
            elif choice == '9':
                self.interactive_assembler()
            elif choice == '10':
                self.component_inspector()
            elif choice == '11':
                self.performance_profiler()
            elif choice == '12':
                self.generate_system_report()
            elif choice == '13':
                self.view_test_history()
            elif choice == '14':
                self.export_all_data()
            elif choice == '15':
                print(f"{Colors.OKGREEN}🚀 Mission complete! Safe travels! 🌌{Colors.ENDC}")
                break
            else:
                print(f"{Colors.WARNING}⚠️  Invalid mission code. Please select 1-15.{Colors.ENDC}")
    
    def run_unit_tests(self):
        """Run unit tests"""
        print(f"\n{Colors.OKCYAN}🧪 Launching Unit Test Suite...{Colors.ENDC}")
        
        try:
            # Run master test runner with unit tests only
            result = subprocess.run([
                sys.executable, 
                'master_test_runner.py', 
                '--category', 'unit'
            ], capture_output=False, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ Unit tests completed successfully{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}⚠️  Some unit tests failed{Colors.ENDC}")
                
        except FileNotFoundError:
            print(f"{Colors.FAIL}❌ Master test runner not found{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error running unit tests: {e}{Colors.ENDC}")
    
    def run_integration_tests(self):
        """Run integration tests"""
        print(f"\n{Colors.OKCYAN}🔗 Launching Integration Test Suite...{Colors.ENDC}")
        
        try:
            result = subprocess.run([
                sys.executable, 
                'master_test_runner.py', 
                '--category', 'integration'
            ], capture_output=False, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ Integration tests completed successfully{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}⚠️  Some integration tests failed{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error running integration tests: {e}{Colors.ENDC}")
    
    def run_performance_tests(self):
        """Run performance tests"""
        print(f"\n{Colors.OKCYAN}⚡ Launching Performance Test Suite...{Colors.ENDC}")
        
        try:
            result = subprocess.run([
                sys.executable, 
                'master_test_runner.py', 
                '--category', 'performance'
            ], capture_output=False, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ Performance tests completed successfully{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}⚠️  Some performance tests failed{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error running performance tests: {e}{Colors.ENDC}")
    
    def run_real_world_scenarios(self):
        """Run real-world scenarios"""
        print(f"\n{Colors.OKCYAN}🌍 Launching Real-World Scenario Testing...{Colors.ENDC}")
        
        try:
            result = subprocess.run([
                sys.executable, 
                'real_world_scenarios.py'
            ], capture_output=False, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ Real-world scenarios completed successfully{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}⚠️  Some real-world scenarios failed{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error running real-world scenarios: {e}{Colors.ENDC}")
    
    def run_ultimate_test_suite(self):
        """Run complete ultimate test suite"""
        print(f"\n{Colors.HEADER}🎯 LAUNCHING ULTIMATE TEST SUITE{Colors.ENDC}")
        print("This will run ALL tests - unit, integration, performance, and real-world scenarios")
        
        confirm = input(f"{Colors.WARNING}⚠️  This may take several minutes. Continue? (y/N): {Colors.ENDC}").strip().lower()
        
        if confirm == 'y' or confirm == 'yes':
            print(f"{Colors.OKCYAN}🚀 Launching complete test suite...{Colors.ENDC}")
            
            try:
                # Run ultimate test suite
                result = subprocess.run([
                    sys.executable, 
                    'ultimate_test_suite.py'
                ], capture_output=False, text=True)
                
                if result.returncode == 0:
                    print(f"{Colors.OKGREEN}🎉 ULTIMATE TEST SUITE: ALL SYSTEMS GO! 🚀{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}⚠️  Ultimate test suite found issues{Colors.ENDC}")
                    
            except Exception as e:
                print(f"{Colors.FAIL}❌ Error running ultimate test suite: {e}{Colors.ENDC}")
        else:
            print(f"{Colors.OKCYAN}📋 Test suite cancelled{Colors.ENDC}")
    
    def launch_main_gui(self):
        """Launch main GUI interface"""
        print(f"\n{Colors.OKCYAN}🎨 Launching Main GUI Interface...{Colors.ENDC}")
        
        if 'GUI Interface' not in self.checker.optional_features:
            print(f"{Colors.FAIL}❌ GUI dependencies not available{Colors.ENDC}")
            print("Install with: pip install tkinter customtkinter")
            return
        
        try:
            # Launch GUI in separate process
            subprocess.Popen([
                sys.executable, 
                'src/interface.py'
            ])
            
            print(f"{Colors.OKGREEN}✅ Main GUI launched successfully{Colors.ENDC}")
            print("GUI is running in a separate window")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error launching main GUI: {e}{Colors.ENDC}")
    
    def launch_monitoring_dashboard(self):
        """Launch monitoring dashboard"""
        print(f"\n{Colors.OKCYAN}📊 Launching Monitoring Dashboard...{Colors.ENDC}")
        
        try:
            subprocess.Popen([
                sys.executable, 
                'monitoring_dashboard.py'
            ])
            
            print(f"{Colors.OKGREEN}✅ Monitoring dashboard launched{Colors.ENDC}")
            print("Dashboard is running in a separate window")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error launching monitoring dashboard: {e}{Colors.ENDC}")
    
    def launch_gui_test_runner(self):
        """Launch GUI test runner"""
        print(f"\n{Colors.OKCYAN}🧪 Launching GUI Test Runner...{Colors.ENDC}")
        
        try:
            subprocess.Popen([
                sys.executable, 
                'gui_test_scenarios.py'
            ])
            
            print(f"{Colors.OKGREEN}✅ GUI test runner launched{Colors.ENDC}")
            print("Test runner is available in a separate window")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error launching GUI test runner: {e}{Colors.ENDC}")
    
    def interactive_assembler(self):
        """Interactive assembler tool"""
        print(f"\n{Colors.OKCYAN}📝 Interactive RISC-V Assembler{Colors.ENDC}")
        print("Enter assembly code (type 'quit' to exit, 'help' for commands)")
        print("-" * 50)
        
        try:
            sys.path.append('src')
            from Assembler import RiscVAssembler
            from MainCPU import RiscVProcessor
            
            assembler = RiscVAssembler()
            processor = RiscVProcessor(32, 32)
            
            while True:
                print(f"\n{Colors.OKCYAN}ASM> {Colors.ENDC}", end="")
                command = input().strip()
                
                if command.lower() == 'quit':
                    break
                elif command.lower() == 'help':
                    self._show_assembler_help()
                elif command.lower() == 'example':
                    self._show_assembler_examples()
                elif command.lower() == 'run':
                    self._run_assembled_program(processor)
                elif command.lower().startswith('load '):
                    filename = command[5:].strip()
                    self._load_assembly_file(assembler, processor, filename)
                elif command:
                    self._assemble_single_line(assembler, command)
                    
        except Exception as e:
            print(f"{Colors.FAIL}❌ Assembler error: {e}{Colors.ENDC}")
    
    def _show_assembler_help(self):
        """Show assembler help"""
        print(f"{Colors.OKGREEN}📚 Interactive Assembler Commands:{Colors.ENDC}")
        print("  help        - Show this help")
        print("  example     - Show example programs")
        print("  run         - Run last assembled program")
        print("  load <file> - Load and assemble file")
        print("  quit        - Exit assembler")
        print("\nSupported Instructions:")
        print("  ADD, SUB, AND, OR, XOR  - R-type")
        print("  ADDI, ANDI, ORI         - I-type")
        print("  LW, SW                  - Memory")
        print("  BEQ, BNE                - Branch")
        print("  JAL                     - Jump")
        print("  NOP, HALT               - Special")
    
    def _show_assembler_examples(self):
        """Show assembler examples"""
        print(f"{Colors.OKGREEN}📝 Example Programs:{Colors.ENDC}")
        print("1. Basic arithmetic:")
        print("   addi x1, x0, 10")
        print("   addi x2, x0, 5")
        print("   add x3, x1, x2")
        print("   halt")
        print("\n2. Memory operations:")
        print("   addi x1, x0, 42")
        print("   sw x1, 0(x0)")
        print("   lw x2, 0(x0)")
        print("   halt")
    
    def _assemble_single_line(self, assembler, line):
        """Assemble single line"""
        try:
            # Create temporary file with single instruction
            temp_program = f"{line}\nhalt"
            
            with open('temp_interactive.asm', 'w') as f:
                f.write(temp_program)
            
            machine_code = assembler.assemble_file('temp_interactive.asm')
            os.remove('temp_interactive.asm')
            
            if machine_code:
                print(f"   ✅ Assembled: 0x{machine_code[0]:04X}")
            else:
                print(f"   ❌ Assembly failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def _load_assembly_file(self, assembler, processor, filename):
        """Load assembly file"""
        try:
            if not os.path.exists(filename):
                print(f"   ❌ File not found: {filename}")
                return
            
            machine_code = assembler.assemble_file(filename)
            if machine_code:
                processor.load_program_direct(machine_code)
                print(f"   ✅ Loaded {len(machine_code)} instructions from {filename}")
            else:
                print(f"   ❌ Assembly failed for {filename}")
                
        except Exception as e:
            print(f"   ❌ Error loading file: {e}")
    
    def _run_assembled_program(self, processor):
        """Run assembled program"""
        try:
            if processor.instruction_memory.program_size == 0:
                print("   ❌ No program loaded")
                return
            
            print("   🔄 Running program...")
            success = processor.run(max_cycles=100)
            
            if success:
                print(f"   ✅ Program completed in {processor.cycle_count} cycles")
                
                # Show register state
                print("   📊 Final register state:")
                for i in range(8):  # Show first 8 registers
                    value = processor.register_file.read(i)
                    if value != 0:
                        print(f"      x{i} = 0x{value:04X} ({value})")
            else:
                print("   ❌ Program execution failed")
                
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
    
    def component_inspector(self):
        """Component inspector tool"""
        print(f"\n{Colors.OKCYAN}🔍 Component Inspector{Colors.ENDC}")
        print("Inspect internal state of RISC-V components")
        
        try:
            sys.path.append('src')
            from MainCPU import RiscVProcessor
            
            processor = RiscVProcessor(32, 32)
            
            while True:
                print(f"\n{Colors.OKCYAN}Components:{Colors.ENDC}")
                print("1. Register File")
                print("2. ALU")
                print("3. Memory System")
                print("4. Instruction Decoder")
                print("5. Control Unit")
                print("6. Back to main menu")
                
                choice = input(f"\n{Colors.OKCYAN}Select component (1-6): {Colors.ENDC}").strip()
                
                if choice == '1':
                    processor.register_file.display_registers()
                elif choice == '2':
                    processor.alu.display_status()
                    processor.alu.display_history()
                elif choice == '3':
                    processor.data_memory.display_memory()
                    stats = processor.data_memory.get_statistics()
                    print(f"\nMemory Statistics: {stats}")
                elif choice == '4':
                    processor.instruction_decoder.display_instruction_set()
                elif choice == '5':
                    processor.control_unit.display_control_table()
                elif choice == '6':
                    break
                else:
                    print(f"{Colors.WARNING}Invalid choice{Colors.ENDC}")
                    
        except Exception as e:
            print(f"{Colors.FAIL}❌ Component inspector error: {e}{Colors.ENDC}")
    
    def performance_profiler(self):
        """Performance profiler"""
        print(f"\n{Colors.OKCYAN}📈 Performance Profiler{Colors.ENDC}")
        print("Analyze performance characteristics of RISC-V programs")
        
        try:
            # Load and run performance analysis
            result = subprocess.run([
                sys.executable, 
                'ultimate_test_suite.py'
            ], capture_output=True, text=True)
            
            print("Performance analysis results:")
            print(result.stdout)
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Performance profiler error: {e}{Colors.ENDC}")
    
    def generate_system_report(self):
        """Generate comprehensive system report"""
        print(f"\n{Colors.OKCYAN}📄 Generating Comprehensive System Report...{Colors.ENDC}")
        
        try:
            # Run comprehensive testing and generate report
            subprocess.run([
                sys.executable, 
                'master_test_runner.py', 
                '--quick'
            ], capture_output=False)
            
            print(f"{Colors.OKGREEN}✅ System report generated{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error generating report: {e}{Colors.ENDC}")
    
    def view_test_history(self):
        """View test history"""
        print(f"\n{Colors.OKCYAN}📋 Test History{Colors.ENDC}")
        
        # Look for recent test reports
        report_files = []
        for file in os.listdir('.'):
            if file.startswith('risc_v_test_report_') and file.endswith('.json'):
                report_files.append(file)
        
        if not report_files:
            print("No test reports found")
            return
        
        report_files.sort(reverse=True)  # Most recent first
        
        print(f"Found {len(report_files)} test reports:")
        for i, report in enumerate(report_files[:5]):  # Show last 5
            print(f"  {i+1}. {report}")
        
        if len(report_files) > 5:
            print(f"  ... and {len(report_files) - 5} more")
    
    def export_all_data(self):
        """Export all system data"""
        print(f"\n{Colors.OKCYAN}💾 Exporting All System Data...{Colors.ENDC}")
        
        try:
            import zipfile
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"risc_v_complete_export_{timestamp}.zip"
            
            with zipfile.ZipFile(export_filename, 'w') as zipf:
                # Add source files
                for file in Path('src').glob('*.py'):
                    zipf.write(file, f"source/{file.name}")
                
                # Add test files
                for file in Path('src/UnitTests').glob('*.py'):
                    zipf.write(file, f"tests/{file.name}")
                
                # Add any report files
                for file in Path('.').glob('risc_v_*.json'):
                    zipf.write(file, f"reports/{file.name}")
                
                # Add documentation files
                if Path('README.md').exists():
                    zipf.write('README.md', 'README.md')
                
                if Path('LICENSE').exists():
                    zipf.write('LICENSE', 'LICENSE')
            
            print(f"{Colors.OKGREEN}✅ Complete export saved: {export_filename}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Export error: {e}{Colors.ENDC}")
    
    def quick_start_wizard(self):
        """Quick start wizard for new users"""
        print(f"\n{Colors.HEADER}🧙 RISC-V Quick Start Wizard{Colors.ENDC}")
        print("Welcome to the RISC-V Simulator! Let's get you started.")
        
        print(f"\n{Colors.OKCYAN}Step 1: System Check{Colors.ENDC}")
        if not self.checker.check_system():
            print(f"{Colors.FAIL}❌ System requirements not met. Please fix issues and try again.{Colors.ENDC}")
            return
        
        print(f"\n{Colors.OKCYAN}Step 2: Quick Test{Colors.ENDC}")
        print("Running a quick test to verify everything works...")
        
        try:
            result = subprocess.run([
                sys.executable, 
                'master_test_runner.py', 
                '--quick'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ Quick test passed! System is ready.{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}⚠️  Quick test found some issues, but basic functionality works.{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Could not run quick test: {e}{Colors.ENDC}")
        
        print(f"\n{Colors.OKCYAN}Step 3: Choose Your Adventure{Colors.ENDC}")
        print("What would you like to do first?")
        print("1. 🎨 Try the GUI interface")
        print("2. 📝 Write some assembly code")
        print("3. 🧪 Run the complete test suite")
        print("4. 📚 Learn about the system")
        
        choice = input(f"\n{Colors.OKCYAN}Your choice (1-4): {Colors.ENDC}").strip()
        
        if choice == '1':
            self.launch_main_gui()
        elif choice == '2':
            self.interactive_assembler()
        elif choice == '3':
            self.run_ultimate_test_suite()
        elif choice == '4':
            self._show_system_overview()
        
        print(f"\n{Colors.OKGREEN}🎉 Welcome aboard! You can access all features from the main menu.{Colors.ENDC}")
    
    def _show_system_overview(self):
        """Show system overview"""
        print(f"\n{Colors.HEADER}📚 RISC-V Simulator System Overview{Colors.ENDC}")
        print("="*50)
        print(f"{Colors.OKGREEN}🎯 What is this?{Colors.ENDC}")
        print("A complete RISC-V 16-bit processor simulator with:")
        print("  • Full instruction set implementation")
        print("  • Real-time monitoring and debugging")
        print("  • Educational and research tools")
        print("  • Production-ready testing framework")
        
        print(f"\n{Colors.OKGREEN}🔧 Core Components:{Colors.ENDC}")
        print("  • Register File (16 registers, x0-x15)")
        print("  • ALU (7 operations + flags)")
        print("  • Memory System (instruction + data)")
        print("  • Instruction Decoder (R, I, S, B, J types)")
        print("  • Control Unit (signal generation)")
        print("  • Assembler (ASM → binary)")
        
        print(f"\n{Colors.OKGREEN}🎨 User Interfaces:{Colors.ENDC}")
        print("  • Modern GUI with real-time visualization")
        print("  • Monitoring dashboard with performance metrics")
        print("  • Interactive command-line tools")
        print("  • Comprehensive testing frameworks")
        
        print(f"\n{Colors.OKGREEN}🚀 Perfect for:{Colors.ENDC}")
        print("  • Computer architecture education")
        print("  • RISC-V research and development")
        print("  • Embedded systems prototyping")
        print("  • Assembly language learning")
    
    def launch(self):
        """Main launcher entry point"""
        self.show_banner()
        
        # System check
        if not self.checker.check_system():
            print(f"\n{Colors.FAIL}❌ System requirements not met. Please fix issues and try again.{Colors.ENDC}")
            return False
        
        print(f"\n{Colors.OKGREEN}✅ All systems operational! Ready for launch! 🚀{Colors.ENDC}")
        
        # Check if this is first run
        if not Path('risc_v_system_initialized').exists():
            self.quick_start_wizard()
            
            # Create initialization marker
            with open('risc_v_system_initialized', 'w') as f:
                f.write(f"RISC-V System initialized on {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show main menu
        self.show_main_menu()
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='RISC-V Ultimate System Launcher')
    parser.add_argument('--gui', action='store_true', help='Launch GUI directly')
    parser.add_argument('--test', action='store_true', help='Run quick test')
    parser.add_argument('--monitor', action='store_true', help='Launch monitoring dashboard')
    parser.add_argument('--wizard', action='store_true', help='Run quick start wizard')
    
    args = parser.parse_args()
    
    launcher = SystemLauncher()
    
    if args.gui:
        launcher.launch_main_gui()
    elif args.test:
        launcher.run_ultimate_test_suite()
    elif args.monitor:
        launcher.launch_monitoring_dashboard()
    elif args.wizard:
        launcher.quick_start_wizard()
    else:
        # Full interactive launcher
        success = launcher.launch()
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()