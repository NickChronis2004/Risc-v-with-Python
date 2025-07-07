"""
Simple Real-time Logging System για RISC-V Processor

Απλό και εύκολο logging που:
- Καταγράφει εκτέλεση εντολών
- Παρακολουθεί register changes
- Εντοπίζει errors
- Δημιουργεί readable log file
- Real-time output στο terminal
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional


class SimpleLogger:
    """
    Απλό logging system για debugging
    """
    
    def __init__(self, log_file: str = None, console_output: bool = True):
        """
        Initialize simple logger
        
        Args:
            log_file: Αρχείο για αποθήκευση logs (optional)
            console_output: Εμφάνιση στο terminal
        """
        self.console_output = console_output
        self.log_file = log_file
        
        # Δημιουργία logs directory
        if log_file:
            log_dir = os.path.dirname(log_file) or "logs"
            os.makedirs(log_dir, exist_ok=True)
            
            # Άνοιγμα αρχείου
            self.file_handle = open(log_file, 'w', encoding='utf-8')
            self._write_header()
        else:
            self.file_handle = None
        
        # Στατιστικά
        self.instruction_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        self.log("🚀 Simple Logger Started", "INFO")
    
    def _write_header(self):
        """Γράφει header στο αρχείο"""
        if self.file_handle:
            header = f"""
RISC-V Processor Debug Log
==========================
Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Log File: {self.log_file}
==========================

"""
            self.file_handle.write(header)
            self.file_handle.flush()
    
    def log(self, message: str, level: str = "INFO", data: Dict = None):
        """
        Απλό logging message
        
        Args:
            message: Το μήνυμα
            level: INFO, WARNING, ERROR
            data: Extra data (optional)
        """
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # με milliseconds
        
        # Format message
        log_line = f"[{timestamp}] {level:<7} | {message}"
        
        if data:
            log_line += f" | {data}"
        
        # Console output
        if self.console_output:
            # Χρώματα για το terminal
            colors = {
                'INFO': '\033[94m',     # Blue
                'WARNING': '\033[93m',  # Yellow
                'ERROR': '\033[91m',    # Red
                'SUCCESS': '\033[92m'   # Green
            }
            reset_color = '\033[0m'
            
            color = colors.get(level, '')
            print(f"{color}{log_line}{reset_color}")
        
        # File output
        if self.file_handle:
            self.file_handle.write(log_line + '\n')
            self.file_handle.flush()
    
    def log_instruction(self, cycle: int, pc: int, instruction: int, assembly: str, 
                       registers_changed: Dict = None):
        """Log εκτέλεσης εντολής"""
        self.instruction_count += 1
        
        msg = f"Cycle {cycle:3d} | PC:0x{pc:04X} | 0x{instruction:04X} | {assembly}"
        
        # Προσθήκη register changes αν υπάρχουν
        extra_data = {}
        if registers_changed:
            extra_data['reg_changes'] = registers_changed
        
        self.log(msg, "INFO", extra_data if extra_data else None)
    
    def log_register_change(self, reg_num: int, old_value: int, new_value: int):
        """Log αλλαγής register"""
        msg = f"x{reg_num}: 0x{old_value:04X} → 0x{new_value:04X} ({old_value} → {new_value})"
        self.log(msg, "INFO")
    
    def log_memory_access(self, operation: str, address: int, value: int = None):
        """Log memory access"""
        if value is not None:
            msg = f"Memory {operation}: [0x{address:04X}] = 0x{value:04X} ({value})"
        else:
            msg = f"Memory {operation}: [0x{address:04X}]"
        
        self.log(msg, "INFO")
    
    def log_error(self, error_msg: str, context: Dict = None):
        """Log σφάλματος"""
        self.error_count += 1
        self.log(f"ERROR #{self.error_count}: {error_msg}", "ERROR", context)
    
    def log_warning(self, warning_msg: str, context: Dict = None):
        """Log προειδοποίησης"""
        self.log(f"WARNING: {warning_msg}", "WARNING", context)
    
    def log_success(self, success_msg: str):
        """Log επιτυχίας"""
        self.log(success_msg, "SUCCESS")
    
    def get_statistics(self) -> Dict:
        """Επιστρέφει στατιστικά"""
        runtime = time.time() - self.start_time
        
        return {
            'runtime_seconds': runtime,
            'instructions_logged': self.instruction_count,
            'errors': self.error_count,
            'instructions_per_second': self.instruction_count / runtime if runtime > 0 else 0
        }
    
    def print_summary(self):
        """Εκτυπώνει σύνοψη"""
        stats = self.get_statistics()
        
        print("\n" + "="*50)
        print("📊 LOGGING SESSION SUMMARY")
        print("="*50)
        print(f"⏱️  Runtime: {stats['runtime_seconds']:.2f} seconds")
        print(f"📝 Instructions logged: {stats['instructions_logged']}")
        print(f"🚨 Errors: {stats['errors']}")
        print(f"⚡ Instructions/second: {stats['instructions_per_second']:.2f}")
        
        if self.log_file:
            print(f"📄 Log saved to: {self.log_file}")
        
        print("="*50)
    
    def close(self):
        """Κλείσιμο logger"""
        # Log closure message before closing file
        if self.console_output:
            print("🏁 Simple Logger Closed")
        
        if self.file_handle:
            self.file_handle.write(f"\n\nSession ended: {datetime.now()}\n")
            self.file_handle.close()
            self.file_handle = None
        
        self.print_summary()


# Integration με τον υπάρχοντα MainCPU
def add_logging_to_processor(processor_class):
    """
    Decorator που προσθέτει logging σε υπάρχοντα processor
    """
    
    class LoggedProcessor(processor_class):
        
        def __init__(self, *args, **kwargs):
            # Extract logging parameters
            enable_logging = kwargs.pop('enable_logging', True)
            log_file = kwargs.pop('log_file', f"logs/risc_v_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            console_output = kwargs.pop('console_output', True)
            
            # Initialize parent
            super().__init__(*args, **kwargs)
            
            # Add logger
            if enable_logging:
                self.logger = SimpleLogger(log_file, console_output)
                self.logger.log("🖥️ Processor initialized with logging", "SUCCESS")
            else:
                self.logger = None
        
        def step(self):
            """Enhanced step με logging"""
            if not hasattr(self, 'logger') or not self.logger:
                return super().step()
            
            # Capture state before
            old_pc = self.pc
            old_registers = {}
            for i in range(16):
                old_registers[i] = self.register_file.read(i)
            
            # Execute original step
            result = super().step()
            
            # Log execution
            if hasattr(self, 'execution_history') and self.execution_history:
                last_execution = self.execution_history[-1]
                
                # Check for register changes
                register_changes = {}
                for i in range(16):
                    new_value = self.register_file.read(i)
                    if old_registers[i] != new_value:
                        register_changes[f'x{i}'] = f"{old_registers[i]}→{new_value}"
                
                # Log instruction
                self.logger.log_instruction(
                    cycle=last_execution["cycle"],
                    pc=last_execution["pc"],
                    instruction=last_execution["instruction"],
                    assembly=last_execution["assembly"],
                    registers_changed=register_changes if register_changes else None
                )
            
            # Log errors
            if self.halted and self.cycle_count > 0:
                self.logger.log_success(f"Program completed successfully in {self.cycle_count} cycles")
            
            return result
        
        def load_program_from_file(self, filename: str):
            """Enhanced load με logging"""
            if self.logger:
                self.logger.log(f"📂 Loading program from: {filename}", "INFO")
            
            result = super().load_program_from_file(filename)
            
            if self.logger:
                if result:
                    size = self.instruction_memory.get_program_size()
                    self.logger.log_success(f"Program loaded: {size} instructions")
                else:
                    self.logger.log_error(f"Failed to load program from {filename}")
            
            return result
        
        def run(self, max_cycles=1000):
            """Enhanced run με logging"""
            if self.logger:
                self.logger.log(f"▶️ Starting execution (max {max_cycles} cycles)", "INFO")
            
            result = super().run(max_cycles)
            
            if self.logger:
                if result:
                    self.logger.log_success(f"Execution completed in {self.cycle_count} cycles")
                else:
                    self.logger.log_warning(f"Execution stopped after {max_cycles} cycles")
            
            return result
        
        def reset(self):
            """Enhanced reset με logging"""
            if self.logger:
                self.logger.log("🔄 Resetting processor", "INFO")
            
            super().reset()
            
            if self.logger:
                self.logger.log_success("Processor reset completed")
        
        def save_debug_log(self):
            """Αποθήκευση debug log"""
            if self.logger:
                self.logger.close()
                return self.logger.log_file
            return None
    
    return LoggedProcessor


# Απλή χρήση
def demo_simple_logging():
    """Demo του simple logging"""
    print("🧪 Simple Logging Demo")
    print("="*30)
    
    # Import το υπάρχον MainCPU
    try:
        from MainCPU import RiscVProcessor
    except ImportError:
        print("❌ MainCPU.py not found!")
        return
    
    # Δημιουργία logged processor
    LoggedRiscVProcessor = add_logging_to_processor(RiscVProcessor)
    
    # Χρήση με logging
    processor = LoggedRiscVProcessor(
        instruction_memory_size=64,
        data_memory_size=64,
        enable_logging=True,
        console_output=True
    )
    
    # Test program
    test_program = [
        0x5107,  # ADDI x1, x0, 7
        0x5205,  # ADDI x2, x0, 5  
        0x0312,  # ADD x3, x1, x2
        0x9320,  # SW x3, 0(x2)
        0x8420,  # LW x4, 0(x2)
        0xF000   # HALT
    ]
    
    print("\n📝 Loading and running test program...")
    processor.load_program_direct(test_program)
    processor.run(max_cycles=50)
    
    print("\n💾 Saving debug log...")
    log_file = processor.save_debug_log()
    print(f"Log saved to: {log_file}")


if __name__ == "__main__":
    demo_simple_logging()