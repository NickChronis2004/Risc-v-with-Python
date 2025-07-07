"""
Flexible Logged MainCPU που μπορεί να φορτώνει .asm αρχεία
"""

from MainCPU import RiscVProcessor
from SimpleLogging import add_logging_to_processor
import time
import os
import sys

# Create logged processor class
LoggedRiscVProcessor = add_logging_to_processor(RiscVProcessor)

# 🖨️ PATCH: Επέκταση της store_word με print support
def enhanced_store_word(self, address, value):
    """Store a word in memory with print support"""
    # 🖨️ PRINT ZONE - Magic address for output
    if address == 0x1000:  # Απλούστερη διεύθυνση: αρχή της μνήμης!
        print(f"📺 OUTPUT: {value}")
        if hasattr(self, 'logger') and self.logger:
            self.logger.info(f"📺 Print: {value}")
        return
    
    # Original store_word logic from MainCPU
    if address < 0x1000:
        raise ValueError(f"Invalid memory address: 0x{address:04X}")
    
    # Write to data memory using the DataMemory method
    try:
        old_value = self.data_memory.read_word(address)
        self.data_memory.write_word(address, value)
        
        # Log the memory write
        if hasattr(self, 'logger') and self.logger:
            self.logger.info(f"✏️  Memory Write: [0x{address:04X}] 0x{old_value:04X} → 0x{value:04X}")
        print(f"✏️  Memory Write: [0x{address:04X}] 0x{old_value:04X} → 0x{value:04X}")
    except Exception as e:
        print(f"⚠️  Invalid write address: 0x{address:04X}")

# Apply the patch to LoggedRiscVProcessor
LoggedRiscVProcessor.store_word = enhanced_store_word

def load_asm_file_if_exists(filename):
    """
    Προσπαθεί να φορτώσει .asm αρχείο, αλλιώς επιστρέφει None
    """
    if os.path.exists(filename):
        print(f"📂 Found {filename}, loading...")
        return filename
    else:
        print(f"❌ File {filename} not found")
        return None

def main():
    """Flexible demo που μπορεί να φορτώνει από αρχείο ή να χρησιμοποιεί default program"""
    print("🖥️ RISC-V Processor με Flexible Loading & Print Support")
    print("="*50)
    
    processor = LoggedRiscVProcessor(
        instruction_memory_size=256,
        data_memory_size=256,
        enable_logging=True,
        console_output=True
    )
    
    # ========================================
    # ΕΠΙΛΟΓΗ 1: Προσπάθησε να φορτώσεις από αρχείο
    # ========================================
    
    possible_files = [ 
    "src/examples/loop_test.asm",         
    "src/examples/branch_test.asm",
    "src/examples/calculator.asm",
    "src/examples/print_test.asm",
    "src/examples/my_program.asm",
    "src/examples/factorial.asm"
    ]
    
    program_loaded = False
    
    print("🔍 Looking for .asm files...")
    for filename in possible_files:
        if os.path.exists(filename):
            print(f"✅ Found: {filename}")
            try:
                success = processor.load_program_from_file(filename)
                if success:
                    program_loaded = True
                    print(f"🎉 Successfully loaded program from: {filename}")
                    break
                else:
                    print(f"❌ Failed to assemble: {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
    
    # ========================================
    # ΕΠΙΛΟΓΗ 2: Αν δεν βρήκε αρχείο, χρησιμοποίησε default
    # ========================================
    
    if not program_loaded:
        print("\n📝 No .asm file found, using default test program with prints...")
        
        # Default test program με print στη διεύθυνση 0x1000
        test_program = [
            0x5105,  # ADDI x1, x0, 5      -> x1 = 5
            0x9100,  # SW x1, 0(x0)        -> Print 5! (0x1000 + 0 = 0x1000)
            0x5207,  # ADDI x2, x0, 7      -> x2 = 7  
            0x9200,  # SW x2, 0(x0)        -> Print 7!
            0x0312,  # ADD x3, x1, x2      -> x3 = 12
            0x9300,  # SW x3, 0(x0)        -> Print 12!
            0xF000   # HALT
        ]
        
        success = processor.load_program_direct(test_program)
        if success:
            program_loaded = True
            print("✅ Default program loaded successfully!")
            print("   Will print: 5, 7, 12")
    
    # ========================================
    # ΕΚΤΕΛΕΣΗ
    # ========================================
    
    if not program_loaded:
        print("❌ No program could be loaded!")
        return
    
    print("\n▶️ Starting execution with detailed logging...")
    print("-" * 60)
    
    # Run the program
    processor.run(max_cycles=100)
    
    print("-" * 60)
    print("🏁 Execution completed!")
    
    # Show results
    show_results(processor)
    
    # Save debug log
    log_file = processor.save_debug_log()
    print(f"\n📄 Debug log saved to: {log_file}")

def show_results(processor):
    """Εμφανίζει τα αποτελέσματα"""
    
    print("\n📊 Final Register States:")
    non_zero_registers = []
    for i in range(16):
        value = processor.register_file.read(i)
        if value != 0:
            non_zero_registers.append((i, value))
    
    if non_zero_registers:
        for reg_num, value in non_zero_registers:
            print(f"   x{reg_num}: {value} (0x{value:04X})")
    else:
        print("   (All registers are zero)")
    
    print("\n💾 Memory State:")
    non_zero_memory = processor.data_memory.find_non_zero()
    if non_zero_memory:
        for addr, value in non_zero_memory:
            print(f"   [0x{addr:04X}]: {value} (0x{value:04X})")
    else:
        print("   (No data in memory)")
    
    print(f"\n⚡ Performance:")
    print(f"   Cycles executed: {processor.cycle_count}")
    print(f"   Instructions executed: {processor.instruction_count}")
    if processor.halted:
        print("   ✅ Program completed successfully")
    else:
        print("   ⚠️  Program did not complete")

def interactive_mode():
    """Interactive mode για γρήγορο testing"""
    print("🎮 INTERACTIVE MODE")
    print("="*30)
    
    while True:
        print("\nOptions:")
        print("1. Load .asm file")
        print("2. Use default program") 
        print("3. Exit")
        
        choice = input("Choose (1-3): ").strip()
        
        if choice == "1":
            filename = input("Enter .asm filename: ").strip()
            if filename and os.path.exists(filename):
                run_with_file(filename)
            else:
                print(f"❌ File '{filename}' not found!")
        
        elif choice == "2":
            main()
        
        elif choice == "3":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice!")

def run_with_file(filename):
    """Τρέχει με συγκεκριμένο αρχείο"""
    print(f"\n🚀 Running with: {filename}")
    print("="*40)
    
    processor = LoggedRiscVProcessor(
        instruction_memory_size=256,
        data_memory_size=256, 
        enable_logging=True,
        console_output=True
    )
    
    success = processor.load_program_from_file(filename)
    if success:
        processor.run(max_cycles=200)
        show_results(processor)
        log_file = processor.save_debug_log()
        print(f"📄 Log saved to: {log_file}")
    else:
        print("❌ Failed to load program!")


   # 🖨️ PATCH: Επέκταση της _execute_store με print support
def enhanced_execute_store(self, decoded, control_signals):
    """Execute SW instruction with print support"""
    
    # Calculate memory address: rs1 + offset
    base_address = self.register_file.read(decoded["rs1"])
    offset = decoded["offset"]
    
    # Handle negative offset
    if offset < 0:
        offset = (1 << 16) + offset
    
    memory_address = (base_address + offset) & 0xFFFF
    
    # Convert to data memory address space
    data_address = 0x1000 + (memory_address & 0x3FF)
    
    # 🖨️ PRINT CHECK: Magic address για output
    if data_address == 0x1000:
        store_data = self.register_file.read(decoded["rs2"])
        print(f"📺 OUTPUT: {store_data}")
        return  # Δεν αποθηκεύεις στη μνήμη!
    
    # Get data to store
    store_data = self.register_file.read(decoded["rs2"])
    
    # Write to data memory (normal operation)
    self.data_memory.write_word(data_address, store_data)
    self.stats["memory_writes"] += 1

# Apply the patch
LoggedRiscVProcessor._execute_store = enhanced_execute_store

if __name__ == "__main__":
    # Check για command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_mode()
        else:
            # Προσπάθησε να φορτώσεις το αρχείο από command line
            filename = sys.argv[1]
            if os.path.exists(filename):
                run_with_file(filename)
            else:
                print(f"❌ File '{filename}' not found!")
                main()  # Fallback to default
    else:
        main()  # Default behavior