
def step_execution_internal(self):
        """Internal step execution with enhanced exception handling"""
        if self.processor.halted:
            self.add_console_message("⏹️ Processor is halted", "warning")
            return
        
        old_pc = self.processor.pc
        old_cycles = self.processor.cycle_count
        
        # Capture register state before execution
        old_registers = {i: self.processor.register_file.read(i) for i in range(16)}
        
        try:
            # Execute one step with exception handling
            continuing = self.processor.step()
            
            # Capture register state after execution
            new_registers = {i: self.processor.register_file.read(i) for i in range(16)}
            
            # Find changed registers
            changed_registers = []
            for i in range(16):
                if old_registers[i] != new_registers[i]:
                    changed_registers.append(f"x{i}:0x{old_registers[i]:04X}→0x{new_registers[i]:04X}")
            
            # Add to execution trace if we executed an instruction
            if self.processor.cycle_count > old_cycles:
                if self.processor.execution_history:
                    last_execution = self.processor.execution_history[-1]
                    
                    # Determine memory access
                    memory_access = "None"
                    if "SW" in last_execution["assembly"].upper():
                        memory_access = "Write"
                    elif "LW" in last_execution["assembly"].upper():
                        memory_access = "Read"
                    
                    # Add to trace table
                    self.trace_tree.insert("", tk.END, values=(
                        last_execution["cycle"],
                        f"0x{last_execution['pc']:04X}",
                        f"0x{last_execution['instruction']:04X}",
                        last_execution["type"],
                        last_execution["assembly"],
                        ", ".join(changed_registers) if changed_registers else "None",
                        memory_access
                    ))
                    
                    # Auto-scroll to bottom if enabled
                    if self.auto_scroll_var.get():
                        items = self.trace_tree.get_children()
                        if items:
                            self.trace_tree.see(items[-1])
            
            if not continuing:
                self.add_execution_log(f"⏹️ Execution completed at cycle {self.processor.cycle_count}")
        
        except MemoryException as e:
            self.handle_processor_exception(
                "MemoryException", 
                str(e), 
                pc=e.pc, 
                instruction=e.instruction,
                recovery_action="Returned default value (0)"
            )
            
        except InvalidInstructionException as e:
            self.handle_processor_exception(
                "InvalidInstructionException", 
                str(e), 
                pc=e.pc, 
                instruction=e.instruction,
                recovery_action="Treated as NOP"
            )
            
        except RegisterException as e:
            self.handle_processor_exception(
                "RegisterException", 
                str(e), 
                pc=e.pc,
                recovery_action="Operation ignored"
            )
"""
Enhanced RISC-V 16-bit Processor GUI Application
Complete debugging interface with real-time visualization

Features:
- Real-time error messages and logs
- Program output console
- Complete memory visualization
- Detailed execution trace
- Enhanced debugging controls
- Assembly syntax highlighting
- Performance metrics

Requirements:
pip install tkinter customtkinter pillow
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import customtkinter as ctk
from threading import Thread
import time
import os
import sys
import re
from datetime import datetime

# Import your RISC-V components
try:
    from MainCPU import RiscVProcessor
    from Assembler import RiscVAssembler
    from RegisterFile import RegisterFile
    from Memory import InstructionMemory, DataMemory
    from ExceptionHandling import (
        ProcessorException, MemoryException, InvalidInstructionException,
        RegisterException, ExecutionException, ProcessorErrorHandler,
        EnhancedDataMemory, EnhancedInstructionMemory
    )
except ImportError as e:
    print(f"❌ Error importing RISC-V components: {e}")
    print("Make sure all RISC-V Python files are in the same directory")
    sys.exit(1)

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class EnhancedRiscVGUI:
    def __init__(self):
        """Initialize the Enhanced RISC-V GUI Application"""
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🖥️ RISC-V 16-bit Processor Simulator - Enhanced Edition")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 900)
        
        # Initialize error handling system
        self.error_handler = ProcessorErrorHandler(strict_mode=False)  # Graceful mode for GUI
        
        # Initialize processor and assembler with enhanced error handling
        self.processor = RiscVProcessor(instruction_memory_size=256, data_memory_size=256)
        self.assembler = RiscVAssembler()
        
        # Replace processor's memory with enhanced versions
        self.processor.data_memory = EnhancedDataMemory(
            size=256, 
            base_address=0x1000, 
            error_handler=self.error_handler
        )
        self.processor.instruction_memory = EnhancedInstructionMemory(
            size=256, 
            error_handler=self.error_handler
        )
        
        # GUI state
        self.is_running = False
        self.execution_thread = None
        self.auto_scroll = True
        self.show_zero_memory = False
        
        # Enhanced error handling mode
        self.strict_mode = False  # Can be toggled by user
        
        # Logs and messages
        self.console_logs = []
        self.error_logs = []
        self.execution_logs = []
        self.exception_logs = []  # New: track exceptions separately
        
        # Performance tracking
        self.start_time = None
        self.execution_start_time = None
        
        # Create GUI elements
        self.create_widgets()
        self.setup_layout()
        self.setup_syntax_highlighting()
        self.update_displays()
        
        # Welcome message
        self.add_console_message("🚀 Enhanced RISC-V Simulator Ready with Exception Handling!", "success")
        self.add_console_message("📝 Write assembly code and click 'Assemble & Load' to begin", "info")
        self.add_console_message("🔧 Advanced error handling enabled - graceful recovery mode", "info")
        self.add_console_message("⚙️ Exception handling: ProcessorException, MemoryException, ExecutionException", "debug")
    
    def create_widgets(self):
        """Create all GUI widgets with enhanced features"""
        
        # Main container with notebook for tabbed interface
        self.main_frame = ctk.CTkFrame(self.root)
        
        # Header with enhanced status
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="🖥️ RISC-V 16-bit Processor Simulator - Enhanced Edition",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Complete Debugging Environment with Real-time Visualization",
            font=ctk.CTkFont(size=14)
        )
        
        # Enhanced status bar with more information
        self.status_frame = ctk.CTkFrame(self.main_frame)
        
        # Status labels
        self.pc_label = ctk.CTkLabel(self.status_frame, text="PC: 0x0000", font=ctk.CTkFont(weight="bold"))
        self.cycles_label = ctk.CTkLabel(self.status_frame, text="Cycles: 0", font=ctk.CTkFont(weight="bold"))
        self.instructions_label = ctk.CTkLabel(self.status_frame, text="Instructions: 0", font=ctk.CTkFont(weight="bold"))
        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: READY", font=ctk.CTkFont(weight="bold"))
        self.performance_label = ctk.CTkLabel(self.status_frame, text="CPI: 0.00", font=ctk.CTkFont(weight="bold"))
        
        # Create notebook for main content
        self.notebook = ctk.CTkTabview(self.main_frame)
        
        # Tab 1: Code Editor & Controls
        self.editor_tab = self.notebook.add("📝 Editor & Controls")
        self.create_editor_tab()
        
        # Tab 2: Processor State
        self.state_tab = self.notebook.add("🖥️ Processor State")
        self.create_state_tab()
        
        # Tab 3: Memory Viewer
        self.memory_tab = self.notebook.add("💾 Memory Viewer")
        self.create_memory_tab()
        
        # Tab 4: Execution Trace
        self.trace_tab = self.notebook.add("🕒 Execution Trace")
        self.create_trace_tab()
        
        # Tab 5: Console & Logs
        self.console_tab = self.notebook.add("📺 Console & Logs")
        self.create_console_tab()
    
    def create_editor_tab(self):
        """Create the code editor and controls tab"""
        
        # Left side - Code editor
        self.editor_left = ctk.CTkFrame(self.editor_tab)
        self.code_label = ctk.CTkLabel(self.editor_left, text="📝 Assembly Code Editor", font=ctk.CTkFont(size=18, weight="bold"))
        
        # Code editor with line numbers
        self.code_container = ctk.CTkFrame(self.editor_left)
        
        # Line numbers
        self.line_numbers = tk.Text(
            self.code_container,
            width=4,
            height=25,
            font=("Consolas", 11),
            bg="#2b2b2b",
            fg="#666666",
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=0
        )
        
        # Code text area
        self.code_text = tk.Text(
            self.code_container,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#404040",
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10,
            undo=True,
            maxundo=50
        )
        
        # Bind events for line numbers and syntax highlighting
        self.code_text.bind('<KeyRelease>', self.on_text_change)
        self.code_text.bind('<Button-1>', self.on_text_change)
        self.code_text.bind('<MouseWheel>', self.on_text_scroll)
        
        # Scrollbars
        self.code_scrollbar_y = ctk.CTkScrollbar(self.code_container, command=self.code_text.yview)
        self.code_text.configure(yscrollcommand=self.code_scrollbar_y.set)
        
        # Right side - Controls and quick info
        self.editor_right = ctk.CTkFrame(self.editor_tab)
        
        # File operations
        self.file_frame = ctk.CTkFrame(self.editor_right)
        self.file_label = ctk.CTkLabel(self.file_frame, text="📁 File Operations", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.load_btn = ctk.CTkButton(self.file_frame, text="📁 Load File", command=self.load_file)
        self.save_btn = ctk.CTkButton(self.file_frame, text="💾 Save File", command=self.save_file)
        self.new_btn = ctk.CTkButton(self.file_frame, text="📄 New File", command=self.new_file)
        
        # Assembly operations
        self.assembly_frame = ctk.CTkFrame(self.editor_right)
        self.assembly_label = ctk.CTkLabel(self.assembly_frame, text="🔧 Assembly Operations", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.assemble_btn = ctk.CTkButton(self.assembly_frame, text="🔧 Assemble & Load", command=self.assemble_and_load, height=40)
        self.check_syntax_btn = ctk.CTkButton(self.assembly_frame, text="✅ Check Syntax", command=self.check_syntax)
        
        # Execution controls
        self.execution_frame = ctk.CTkFrame(self.editor_right)
        self.execution_label = ctk.CTkLabel(self.execution_frame, text="▶️ Execution Controls", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.run_btn = ctk.CTkButton(self.execution_frame, text="▶️ Run", command=self.run_program, height=40)
        self.step_btn = ctk.CTkButton(self.execution_frame, text="👆 Step", command=self.step_execution)
        self.pause_btn = ctk.CTkButton(self.execution_frame, text="⏸️ Pause", command=self.pause_execution)
        self.reset_btn = ctk.CTkButton(self.execution_frame, text="🔄 Reset", command=self.reset_processor)
        
        # Speed control
        self.speed_frame = ctk.CTkFrame(self.execution_frame)
        self.speed_label = ctk.CTkLabel(self.speed_frame, text="🏃 Speed Control:")
        self.speed_slider = ctk.CTkSlider(self.speed_frame, from_=1, to=10, number_of_steps=9)
        self.speed_slider.set(5)
        self.speed_value_label = ctk.CTkLabel(self.speed_frame, text="5")
        self.speed_slider.configure(command=self.update_speed_label)
        
        # Error handling controls
        self.error_handling_frame = ctk.CTkFrame(self.editor_right)
        self.error_handling_label = ctk.CTkLabel(self.error_handling_frame, text="🛡️ Error Handling", font=ctk.CTkFont(size=16, weight="bold"))
        
        # Error mode toggle
        self.strict_mode_var = tk.BooleanVar(value=False)
        self.strict_mode_check = ctk.CTkCheckBox(
            self.error_handling_frame,
            text="Strict Mode (Exceptions)",
            variable=self.strict_mode_var,
            command=self.toggle_error_mode
        )
        
        self.error_count_label = ctk.CTkLabel(self.error_handling_frame, text="Total Errors: 0")
        self.exception_count_label = ctk.CTkLabel(self.error_handling_frame, text="Exceptions: 0")
        self.recovery_count_label = ctk.CTkLabel(self.error_handling_frame, text="Recoveries: 0")
        
        # Error handler status
        self.error_status_label = ctk.CTkLabel(self.error_handling_frame, text="Mode: Graceful Recovery")
        
        # Error handling controls
        self.error_handling_frame = ctk.CTkFrame(self.editor_right)
        self.error_handling_label = ctk.CTkLabel(self.error_handling_frame, text="🛡️ Error Handling", font=ctk.CTkFont(size=16, weight="bold"))
        
        # Error mode toggle
        self.strict_mode_var = tk.BooleanVar(value=False)
        self.strict_mode_check = ctk.CTkCheckBox(
            self.error_handling_frame,
            text="Strict Mode (Exceptions)",
            variable=self.strict_mode_var,
            command=self.toggle_error_mode
        )
        
        self.error_count_label = ctk.CTkLabel(self.error_handling_frame, text="Total Errors: 0")
        self.exception_count_label = ctk.CTkLabel(self.error_handling_frame, text="Exceptions: 0")
        self.recovery_count_label = ctk.CTkLabel(self.error_handling_frame, text="Recoveries: 0")
        
        # Error handler status
        self.error_status_label = ctk.CTkLabel(self.error_handling_frame, text="Mode: Graceful Recovery")
        
        # Show error summary button
        self.show_errors_btn = ctk.CTkButton(self.error_handling_frame, text="📊 Error Summary", command=self.show_error_summary)
        
        # Program info
        self.info_frame = ctk.CTkFrame(self.editor_right)
        self.info_label = ctk.CTkLabel(self.info_frame, text="📊 Program Info", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.lines_label = ctk.CTkLabel(self.info_frame, text="Lines: 0")
        self.instructions_info_label = ctk.CTkLabel(self.info_frame, text="Instructions: 0")
        self.labels_label = ctk.CTkLabel(self.info_frame, text="Labels: 0")
        self.errors_label = ctk.CTkLabel(self.info_frame, text="Errors: 0")
        
        # Example code (enhanced)
        example_code = """# Enhanced RISC-V Assembly Example
# Calculate factorial and demonstrate features

main:
    # Initialize factorial calculation
    addi x1, x0, 5      # n = 5 (calculate 5!)
    addi x2, x0, 1      # result = 1
    addi x3, x0, 0      # counter = 0
    
factorial_loop:
    beq x1, x0, done    # if n == 0, we're done
    
    # Multiply result by current n (using repeated addition)
    add x4, x0, x0      # temp = 0
    add x5, x0, x2      # iteration counter = result
    
multiply_loop:
    beq x5, x0, mult_done   # if counter == 0, multiplication done
    add x4, x4, x1          # temp += n
    addi x5, x5, -1         # counter-- (using -1 as 15 in 4-bit)
    bne x5, x0, multiply_loop
    
mult_done:
    add x2, x0, x4      # result = temp
    addi x1, x1, -1     # n--
    addi x3, x3, 1      # increment counter
    bne x1, x0, factorial_loop
    
done:
    # Store results in memory
    sw x2, 0(x0)        # Store factorial result
    sw x3, 1(x0)        # Store iteration count
    
    # Load and verify
    lw x6, 0(x0)        # Load factorial result
    lw x7, 1(x0)        # Load iteration count
    
    # Final calculations for demo
    add x8, x6, x7      # Sum of result and iterations
    and x9, x6, x7      # Bitwise AND
    or x10, x6, x7      # Bitwise OR
    
    halt                # End program

# Additional test functions
test_branches:
    addi x11, x0, 10
    addi x12, x0, 10
    beq x11, x12, equal_test
    addi x13, x0, 1     # Should be skipped
    
equal_test:
    addi x14, x0, 100   # Mark that branch worked
    halt"""
        
        self.code_text.insert("1.0", example_code)
        self.update_line_numbers()
    
    def create_state_tab(self):
        """Create the processor state tab"""
        
        # Left side - Register file
        self.state_left = ctk.CTkFrame(self.state_tab)
        self.registers_label = ctk.CTkLabel(self.state_left, text="🗂️ Register File", font=ctk.CTkFont(size=18, weight="bold"))
        
        # Register display with color coding
        self.registers_container = ctk.CTkScrollableFrame(self.state_left, height=400)
        
        # Create register displays
        self.register_frames = []
        self.register_labels = []
        self.register_values = []
        
        register_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a7']
        
        for i in range(16):
            # Frame for each register
            reg_frame = ctk.CTkFrame(self.registers_container)
            reg_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            self.register_frames.append(reg_frame)
            
            # Register name and value
            name_label = ctk.CTkLabel(reg_frame, text=f"x{i} ({register_names[i]}):", font=ctk.CTkFont(family="Consolas", weight="bold"))
            name_label.pack(side=tk.LEFT, padx=5)
            
            value_label = ctk.CTkLabel(reg_frame, text="0x0000 (0)", font=ctk.CTkFont(family="Consolas"))
            value_label.pack(side=tk.RIGHT, padx=5)
            
            self.register_labels.append(name_label)
            self.register_values.append(value_label)
        
        # Right side - ALU and Control Unit status
        self.state_right = ctk.CTkFrame(self.state_tab)
        
        # ALU status
        self.alu_frame = ctk.CTkFrame(self.state_right)
        self.alu_label = ctk.CTkLabel(self.alu_frame, text="⚙️ ALU Status", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.alu_result_label = ctk.CTkLabel(self.alu_frame, text="Last Result: 0x0000", font=ctk.CTkFont(family="Consolas"))
        self.alu_zero_label = ctk.CTkLabel(self.alu_frame, text="Zero Flag: ❌", font=ctk.CTkFont(family="Consolas"))
        self.alu_overflow_label = ctk.CTkLabel(self.alu_frame, text="Overflow Flag: ❌", font=ctk.CTkFont(family="Consolas"))
        self.alu_negative_label = ctk.CTkLabel(self.alu_frame, text="Negative Flag: ❌", font=ctk.CTkFont(family="Consolas"))
        self.alu_operations_label = ctk.CTkLabel(self.alu_frame, text="Operations: 0", font=ctk.CTkFont(family="Consolas"))
        
        # Control Unit status
        self.control_frame = ctk.CTkFrame(self.state_right)
        self.control_label = ctk.CTkLabel(self.control_frame, text="🎛️ Control Unit", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.current_instruction_label = ctk.CTkLabel(self.control_frame, text="Current: None", font=ctk.CTkFont(family="Consolas"))
        self.instruction_type_label = ctk.CTkLabel(self.control_frame, text="Type: None", font=ctk.CTkFont(family="Consolas"))
        self.signals_generated_label = ctk.CTkLabel(self.control_frame, text="Signals Generated: 0", font=ctk.CTkFont(family="Consolas"))
        
        # Performance metrics
        self.performance_frame = ctk.CTkFrame(self.state_right)
        self.performance_title_label = ctk.CTkLabel(self.performance_frame, text="📈 Performance Metrics", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.cpi_label = ctk.CTkLabel(self.performance_frame, text="CPI: 0.00", font=ctk.CTkFont(family="Consolas"))
        self.frequency_label = ctk.CTkLabel(self.performance_frame, text="Frequency: 0 Hz", font=ctk.CTkFont(family="Consolas"))
        self.runtime_label = ctk.CTkLabel(self.performance_frame, text="Runtime: 0.00s", font=ctk.CTkFont(family="Consolas"))
        self.efficiency_label = ctk.CTkLabel(self.performance_frame, text="Efficiency: 0%", font=ctk.CTkFont(family="Consolas"))
    
    def create_memory_tab(self):
        """Create the memory viewer tab"""
        
        # Controls
        self.memory_controls = ctk.CTkFrame(self.memory_tab)
        self.memory_title = ctk.CTkLabel(self.memory_controls, text="💾 Memory Viewer", font=ctk.CTkFont(size=18, weight="bold"))
        
        # Memory type selection
        self.memory_type_var = tk.StringVar(value="Data Memory")
        self.memory_type_menu = ctk.CTkOptionMenu(
            self.memory_controls,
            variable=self.memory_type_var,
            values=["Data Memory", "Instruction Memory"],
            command=self.update_memory_view
        )
        
        # Show options
        self.show_zero_var = tk.BooleanVar(value=False)
        self.show_zero_check = ctk.CTkCheckBox(
            self.memory_controls,
            text="Show Zero Values",
            variable=self.show_zero_var,
            command=self.update_memory_view
        )
        
        # Address range
        self.address_frame = ctk.CTkFrame(self.memory_controls)
        self.start_addr_label = ctk.CTkLabel(self.address_frame, text="Start Address:")
        self.start_addr_entry = ctk.CTkEntry(self.address_frame, placeholder_text="0x1000")
        self.end_addr_label = ctk.CTkLabel(self.address_frame, text="End Address:")
        self.end_addr_entry = ctk.CTkEntry(self.address_frame, placeholder_text="0x1010")
        self.refresh_btn = ctk.CTkButton(self.address_frame, text="🔄 Refresh", command=self.update_memory_view)
        
        # Memory display
        self.memory_display_frame = ctk.CTkFrame(self.memory_tab)
        
        # Memory table
        columns = ("Address", "Hex Value", "Decimal", "Binary", "ASCII")
        self.memory_tree = ttk.Treeview(self.memory_display_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.memory_tree.heading(col, text=col)
            if col == "Address":
                self.memory_tree.column(col, width=80)
            elif col == "Binary":
                self.memory_tree.column(col, width=120)
            else:
                self.memory_tree.column(col, width=80)
        
        self.memory_scrollbar = ctk.CTkScrollbar(self.memory_display_frame, command=self.memory_tree.yview)
        self.memory_tree.configure(yscrollcommand=self.memory_scrollbar.set)
        
        # Memory statistics
        self.memory_stats_frame = ctk.CTkFrame(self.memory_tab)
        self.memory_stats_label = ctk.CTkLabel(self.memory_stats_frame, text="📊 Memory Statistics", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.total_memory_label = ctk.CTkLabel(self.memory_stats_frame, text="Total Memory: 0 bytes")
        self.used_memory_label = ctk.CTkLabel(self.memory_stats_frame, text="Used Memory: 0 bytes")
        self.free_memory_label = ctk.CTkLabel(self.memory_stats_frame, text="Free Memory: 0 bytes")
        self.memory_reads_label = ctk.CTkLabel(self.memory_stats_frame, text="Total Reads: 0")
        self.memory_writes_label = ctk.CTkLabel(self.memory_stats_frame, text="Total Writes: 0")
    
    def create_trace_tab(self):
        """Create the execution trace tab"""
        
        # Controls
        self.trace_controls = ctk.CTkFrame(self.trace_tab)
        self.trace_title = ctk.CTkLabel(self.trace_controls, text="🕒 Execution Trace", font=ctk.CTkFont(size=18, weight="bold"))
        
        # Trace options
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_check = ctk.CTkCheckBox(
            self.trace_controls,
            text="Auto Scroll",
            variable=self.auto_scroll_var
        )
        
        self.clear_trace_btn = ctk.CTkButton(self.trace_controls, text="🗑️ Clear Trace", command=self.clear_trace)
        self.export_trace_btn = ctk.CTkButton(self.trace_controls, text="📤 Export Trace", command=self.export_trace)
        
        # Filter options
        self.filter_frame = ctk.CTkFrame(self.trace_controls)
        self.filter_label = ctk.CTkLabel(self.filter_frame, text="Filter by Type:")
        self.filter_var = tk.StringVar(value="All")
        self.filter_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            variable=self.filter_var,
            values=["All", "R-Type", "I-Type", "S-Type", "B-Type", "J-Type", "Special"],
            command=self.update_trace_filter
        )
        
        # Trace display
        self.trace_display_frame = ctk.CTkFrame(self.trace_tab)
        
        # Enhanced trace table
        trace_columns = ("Cycle", "PC", "Instruction", "Type", "Assembly", "Registers Changed", "Memory Access")
        self.trace_tree = ttk.Treeview(self.trace_display_frame, columns=trace_columns, show="headings", height=25)
        
        for col in trace_columns:
            self.trace_tree.heading(col, text=col)
            if col == "Assembly":
                self.trace_tree.column(col, width=200)
            elif col == "Registers Changed":
                self.trace_tree.column(col, width=150)
            elif col == "Memory Access":
                self.trace_tree.column(col, width=120)
            else:
                self.trace_tree.column(col, width=80)
        
        self.trace_scrollbar = ctk.CTkScrollbar(self.trace_display_frame, command=self.trace_tree.yview)
        self.trace_tree.configure(yscrollcommand=self.trace_scrollbar.set)
    
    def create_console_tab(self):
        """Create the console and logs tab"""
        
        # Create sub-tabs for different log types
        self.log_notebook = ctk.CTkTabview(self.console_tab)
        
        # Console output tab
        self.console_output_tab = self.log_notebook.add("📺 Console Output")
        self.create_console_output()
        
        # Error logs tab
        self.error_logs_tab = self.log_notebook.add("❌ Error Logs")
        self.create_error_logs()
        
        # Assembly logs tab
        self.assembly_logs_tab = self.log_notebook.add("🔧 Assembly Logs")
        self.create_assembly_logs()
        
        # Exception logs tab - NEW
        self.exception_logs_tab = self.log_notebook.add("⚠️ Exception Logs")
        self.create_exception_logs()
        
        # Execution logs tab
        self.execution_logs_tab = self.log_notebook.add("▶️ Execution Logs")
        self.create_execution_logs()
    
    def create_console_output(self):
        """Create console output area"""
        
        # Console controls
        self.console_controls = ctk.CTkFrame(self.console_output_tab)
        self.console_label = ctk.CTkLabel(self.console_controls, text="📺 Console Output", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.clear_console_btn = ctk.CTkButton(self.console_controls, text="🗑️ Clear Console", command=self.clear_console)
        self.save_console_btn = ctk.CTkButton(self.console_controls, text="💾 Save Log", command=self.save_console_log)
        
        # Console text area
        self.console_frame = ctk.CTkFrame(self.console_output_tab)
        self.console_text = scrolledtext.ScrolledText(
            self.console_frame,
            font=("Consolas", 10),
            bg="#1a1a1a",
            fg="#ffffff",
            state=tk.DISABLED,
            wrap=tk.WORD,
            height=25
        )
        
        # Configure console text colors
        self.console_text.tag_configure("success", foreground="#4CAF50")
        self.console_text.tag_configure("error", foreground="#F44336")
        self.console_text.tag_configure("warning", foreground="#FF9800")
        self.console_text.tag_configure("info", foreground="#2196F3")
        self.console_text.tag_configure("debug", foreground="#9C27B0")
    
    def create_error_logs(self):
        """Create error logs area"""
        
        # Error controls
        self.error_controls = ctk.CTkFrame(self.error_logs_tab)
        self.error_label = ctk.CTkLabel(self.error_controls, text="❌ Error Logs", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.clear_errors_btn = ctk.CTkButton(self.error_controls, text="🗑️ Clear Errors", command=self.clear_error_logs)
        
        # Error display
        error_columns = ("Time", "Type", "Message", "Location")
        self.error_tree = ttk.Treeview(self.error_logs_tab, columns=error_columns, show="headings", height=20)
        
        for col in error_columns:
            self.error_tree.heading(col, text=col)
            if col == "Message":
                self.error_tree.column(col, width=400)
            else:
                self.error_tree.column(col, width=100)
    
    def create_assembly_logs(self):
        """Create assembly logs area"""
        
        self.assembly_log_text = scrolledtext.ScrolledText(
            self.assembly_logs_tab,
            font=("Consolas", 10),
            bg="#1a1a1a",
            fg="#ffffff",
            state=tk.DISABLED,
            wrap=tk.WORD,
            height=25
        )
    
    def create_exception_logs(self):
        """Create exception logs area"""
        
        # Exception controls
        self.exception_controls = ctk.CTkFrame(self.exception_logs_tab)
        self.exception_label = ctk.CTkLabel(self.exception_controls, text="⚠️ Exception Logs", font=ctk.CTkFont(size=16, weight="bold"))
        
        self.clear_exceptions_btn = ctk.CTkButton(self.exception_controls, text="🗑️ Clear Exceptions", command=self.clear_exception_logs)
        self.export_exceptions_btn = ctk.CTkButton(self.exception_controls, text="📤 Export Exceptions", command=self.export_exception_logs)
        
        # Exception display
        exception_columns = ("Time", "Exception Type", "Message", "PC", "Instruction", "Recovery Action")
        self.exception_tree = ttk.Treeview(self.exception_logs_tab, columns=exception_columns, show="headings", height=20)
        
        for col in exception_columns:
            self.exception_tree.heading(col, text=col)
            if col == "Message":
                self.exception_tree.column(col, width=300)
            elif col == "Recovery Action":
                self.exception_tree.column(col, width=200)
            else:
                self.exception_tree.column(col, width=100)
    
    def create_execution_logs(self):
        """Create execution logs area"""
        
        self.execution_log_text = scrolledtext.ScrolledText(
            self.execution_logs_tab,
            font=("Consolas", 10),
            bg="#1a1a1a",
            fg="#ffffff",
            state=tk.DISABLED,
            wrap=tk.WORD,
            height=25
        )
    
    def setup_layout(self):
        """Setup the layout of all widgets"""
        
        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        self.title_label.pack(pady=5)
        self.subtitle_label.pack(pady=(0, 5))
        
        # Status bar
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        self.pc_label.pack(side=tk.LEFT, padx=15)
        self.cycles_label.pack(side=tk.LEFT, padx=15)
        self.instructions_label.pack(side=tk.LEFT, padx=15)
        self.status_label.pack(side=tk.LEFT, padx=15)
        self.performance_label.pack(side=tk.LEFT, padx=15)
        
        # Notebook (main content)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Layout for each tab
        self.layout_editor_tab()
        self.layout_state_tab()
        self.layout_memory_tab()
        self.layout_trace_tab()
        self.layout_console_tab()
    
    def layout_editor_tab(self):
        """Layout the editor tab"""
        
        # Left side (70% width)
        self.editor_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.code_label.pack(pady=(10, 5))
        
        # Code container
        self.code_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.code_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right side (30% width)
        self.editor_right.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # File operations
        self.file_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        self.file_label.pack(pady=(5, 10))
        self.load_btn.pack(fill=tk.X, pady=2)
        self.save_btn.pack(fill=tk.X, pady=2)
        self.new_btn.pack(fill=tk.X, pady=2)
        
        # Assembly operations
        self.assembly_frame.pack(fill=tk.X, padx=10, pady=5)
        self.assembly_label.pack(pady=(5, 10))
        self.assemble_btn.pack(fill=tk.X, pady=2)
        self.check_syntax_btn.pack(fill=tk.X, pady=2)
        
        # Execution controls
        self.execution_frame.pack(fill=tk.X, padx=10, pady=5)
        self.execution_label.pack(pady=(5, 10))
        self.run_btn.pack(fill=tk.X, pady=2)
        self.step_btn.pack(fill=tk.X, pady=2)
        self.pause_btn.pack(fill=tk.X, pady=2)
        self.reset_btn.pack(fill=tk.X, pady=2)
        
        # Speed control
        self.speed_frame.pack(fill=tk.X, pady=5)
        self.speed_label.pack(pady=2)
        self.speed_slider.pack(fill=tk.X, pady=2)
        self.speed_value_label.pack(pady=2)
        
        # Error handling
        self.error_handling_frame.pack(fill=tk.X, padx=10, pady=5)
        self.error_handling_label.pack(pady=(5, 10))
        self.strict_mode_check.pack(anchor="w", padx=5, pady=2)
        self.error_status_label.pack(anchor="w", padx=5, pady=2)
        self.error_count_label.pack(anchor="w", padx=5, pady=1)
        self.exception_count_label.pack(anchor="w", padx=5, pady=1)
        self.recovery_count_label.pack(anchor="w", padx=5, pady=1)
        self.show_errors_btn.pack(fill=tk.X, pady=5)
        
        # Program info
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        self.info_label.pack(pady=(5, 10))
        self.lines_label.pack(anchor="w", padx=5, pady=1)
        self.instructions_info_label.pack(anchor="w", padx=5, pady=1)
        self.labels_label.pack(anchor="w", padx=5, pady=1)
        self.errors_label.pack(anchor="w", padx=5, pady=1)
    
    def layout_state_tab(self):
        """Layout the processor state tab"""
        
        # Left side - Registers
        self.state_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.registers_label.pack(pady=(10, 5))
        self.registers_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Right side - ALU, Control, Performance
        self.state_right.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # ALU status
        self.alu_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        self.alu_label.pack(pady=(5, 10))
        self.alu_result_label.pack(anchor="w", padx=5, pady=2)
        self.alu_zero_label.pack(anchor="w", padx=5, pady=2)
        self.alu_overflow_label.pack(anchor="w", padx=5, pady=2)
        self.alu_negative_label.pack(anchor="w", padx=5, pady=2)
        self.alu_operations_label.pack(anchor="w", padx=5, pady=2)
        
        # Control Unit status
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        self.control_label.pack(pady=(5, 10))
        self.current_instruction_label.pack(anchor="w", padx=5, pady=2)
        self.instruction_type_label.pack(anchor="w", padx=5, pady=2)
        self.signals_generated_label.pack(anchor="w", padx=5, pady=2)
        
        # Performance metrics
        self.performance_frame.pack(fill=tk.X, padx=10, pady=5)
        self.performance_title_label.pack(pady=(5, 10))
        self.cpi_label.pack(anchor="w", padx=5, pady=2)
        self.frequency_label.pack(anchor="w", padx=5, pady=2)
        self.runtime_label.pack(anchor="w", padx=5, pady=2)
        self.efficiency_label.pack(anchor="w", padx=5, pady=2)
    
    def layout_memory_tab(self):
        """Layout the memory tab"""
        
        # Controls at top
        self.memory_controls.pack(fill=tk.X, padx=10, pady=(10, 5))
        self.memory_title.pack(pady=5)
        
        # Memory type and options
        control_row1 = ctk.CTkFrame(self.memory_controls)
        control_row1.pack(fill=tk.X, pady=5)
        
        self.memory_type_menu.pack(side=tk.LEFT, padx=5)
        self.show_zero_check.pack(side=tk.LEFT, padx=20)
        
        # Address range
        self.address_frame.pack(fill=tk.X, pady=5)
        self.start_addr_label.pack(side=tk.LEFT, padx=5)
        self.start_addr_entry.pack(side=tk.LEFT, padx=5)
        self.end_addr_label.pack(side=tk.LEFT, padx=5)
        self.end_addr_entry.pack(side=tk.LEFT, padx=5)
        self.refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # Memory display (main area)
        self.memory_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.memory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.memory_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Statistics at bottom
        self.memory_stats_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        self.memory_stats_label.pack(pady=5)
        
        stats_row1 = ctk.CTkFrame(self.memory_stats_frame)
        stats_row1.pack(fill=tk.X, pady=2)
        self.total_memory_label.pack(in_=stats_row1, side=tk.LEFT, padx=10)
        self.used_memory_label.pack(in_=stats_row1, side=tk.LEFT, padx=10)
        self.free_memory_label.pack(in_=stats_row1, side=tk.LEFT, padx=10)
        
        stats_row2 = ctk.CTkFrame(self.memory_stats_frame)
        stats_row2.pack(fill=tk.X, pady=2)
        self.memory_reads_label.pack(in_=stats_row2, side=tk.LEFT, padx=10)
        self.memory_writes_label.pack(in_=stats_row2, side=tk.LEFT, padx=10)
    
    def layout_trace_tab(self):
        """Layout the trace tab"""
        
        # Controls at top
        self.trace_controls.pack(fill=tk.X, padx=10, pady=(10, 5))
        self.trace_title.pack(pady=5)
        
        # Control buttons
        control_row = ctk.CTkFrame(self.trace_controls)
        control_row.pack(fill=tk.X, pady=5)
        
        self.auto_scroll_check.pack(side=tk.LEFT, padx=5)
        self.clear_trace_btn.pack(side=tk.LEFT, padx=10)
        self.export_trace_btn.pack(side=tk.LEFT, padx=5)
        
        # Filter
        self.filter_frame.pack(fill=tk.X, pady=5)
        self.filter_label.pack(side=tk.LEFT, padx=5)
        self.filter_menu.pack(side=tk.LEFT, padx=5)
        
        # Trace display
        self.trace_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        self.trace_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.trace_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def layout_console_tab(self):
        """Layout the console tab"""
        
        # Log notebook takes full space
        self.log_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Console output layout
        self.console_controls.pack(in_=self.console_output_tab, fill=tk.X, pady=(0, 5))
        self.console_label.pack(side=tk.LEFT, pady=5)
        self.clear_console_btn.pack(side=tk.RIGHT, padx=5)
        self.save_console_btn.pack(side=tk.RIGHT, padx=5)
        
        self.console_frame.pack(in_=self.console_output_tab, fill=tk.BOTH, expand=True)
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Error logs layout
        self.error_controls.pack(in_=self.error_logs_tab, fill=tk.X, pady=(0, 5))
        self.error_label.pack(side=tk.LEFT, pady=5)
        self.clear_errors_btn.pack(side=tk.RIGHT, padx=5)
        
        self.error_tree.pack(in_=self.error_logs_tab, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Exception logs layout
        self.exception_controls.pack(in_=self.exception_logs_tab, fill=tk.X, pady=(0, 5))
        self.exception_label.pack(side=tk.LEFT, pady=5)
        self.clear_exceptions_btn.pack(side=tk.RIGHT, padx=5)
        self.export_exceptions_btn.pack(side=tk.RIGHT, padx=5)
        
        self.exception_tree.pack(in_=self.exception_logs_tab, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Assembly and execution logs
        self.assembly_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.execution_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_syntax_highlighting(self):
        """Setup syntax highlighting for assembly code"""
        
        # Define syntax highlighting patterns
        self.syntax_patterns = {
            'instruction': r'\b(add|sub|and|or|xor|addi|andi|ori|lw|sw|beq|bne|jal|nop|halt)\b',
            'register': r'\b(x[0-9]|x1[0-5]|zero|ra|sp|gp|tp|t[0-2]|s[01]|a[0-4]|a7)\b',
            'immediate': r'#.*$|[+-]?\d+|0x[0-9a-fA-F]+',
            'label': r'^\s*\w+:',
            'comment': r'#.*$'
        }
        
        # Configure text tags for syntax highlighting
        self.code_text.tag_configure('instruction', foreground='#569CD6')  # Blue
        self.code_text.tag_configure('register', foreground='#4EC9B0')     # Cyan
        self.code_text.tag_configure('immediate', foreground='#B5CEA8')    # Green
        self.code_text.tag_configure('label', foreground='#DCDCAA')        # Yellow
        self.code_text.tag_configure('comment', foreground='#6A9955')      # Dark Green
        self.code_text.tag_configure('error', foreground='#F44747', background='#2D1B1B')  # Red background
    
    def on_text_change(self, event=None):
        """Handle text changes for line numbers and syntax highlighting"""
        self.update_line_numbers()
        self.highlight_syntax()
        self.update_program_info()
    
    def on_text_scroll(self, event=None):
        """Sync line numbers with text scrolling"""
        self.line_numbers.yview_moveto(self.code_text.yview()[0])
    
    def update_line_numbers(self):
        """Update line numbers display"""
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        
        # Get total lines
        line_count = int(self.code_text.index('end-1c').split('.')[0])
        
        # Generate line numbers
        line_numbers = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert('1.0', line_numbers)
        
        self.line_numbers.config(state=tk.DISABLED)
    
    def highlight_syntax(self):
        """Apply syntax highlighting to code"""
        
        # Clear existing tags
        for tag in ['instruction', 'register', 'immediate', 'label', 'comment', 'error']:
            self.code_text.tag_remove(tag, '1.0', tk.END)
        
        # Get all text
        content = self.code_text.get('1.0', tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_start = f"{line_num}.0"
            
            # Apply syntax highlighting patterns
            for tag, pattern in self.syntax_patterns.items():
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    start_col = match.start()
                    end_col = match.end()
                    start_index = f"{line_num}.{start_col}"
                    end_index = f"{line_num}.{end_col}"
                    self.code_text.tag_add(tag, start_index, end_index)
    
    def update_program_info(self):
        """Update program information display"""
        content = self.code_text.get('1.0', tk.END)
        lines = content.split('\n')
        
        # Count lines (excluding empty)
        non_empty_lines = [line for line in lines if line.strip()]
        line_count = len(non_empty_lines)
        
        # Count instructions (rough estimate)
        instruction_count = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and ':' not in line:
                instruction_count += 1
        
        # Count labels
        label_count = len([line for line in lines if ':' in line and not line.strip().startswith('#')])
        
        # Update labels
        self.lines_label.configure(text=f"Lines: {line_count}")
        self.instructions_info_label.configure(text=f"Instructions: ~{instruction_count}")
        self.labels_label.configure(text=f"Labels: {label_count}")
    
    def update_speed_label(self, value):
        """Update speed control label"""
        self.speed_value_label.configure(text=f"{int(value)}")
    
    def add_console_message(self, message, msg_type="info"):
        """Add message to console with color coding and timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Millisecond precision
        
        self.console_text.config(state=tk.NORMAL)
        
        # Format message
        full_message = f"[{timestamp}] {message}\n"
        
        # Insert with appropriate tag
        self.console_text.insert(tk.END, full_message, msg_type)
        self.console_text.config(state=tk.DISABLED)
        self.console_text.see(tk.END)
        
        # Store in logs
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'type': msg_type
        }
        self.console_logs.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.console_logs) > 1000:
            self.console_logs.pop(0)
    
    def add_error_log(self, error_type, message, location=None):
        """Add error to error logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add to error tree
        self.error_tree.insert("", tk.END, values=(
            timestamp,
            error_type,
            message,
            location or "Unknown"
        ))
        
        # Auto scroll to bottom
        items = self.error_tree.get_children()
        if items:
            self.error_tree.see(items[-1])
        
        # Store in error logs
        error_entry = {
            'timestamp': timestamp,
            'type': error_type,
            'message': message,
            'location': location
        }
        self.error_logs.append(error_entry)
        
        # Also add to console
        self.add_console_message(f"ERROR [{error_type}]: {message}", "error")
        
        # Update error count
        self.errors_label.configure(text=f"Errors: {len(self.error_logs)}")
    
    def add_assembly_log(self, message):
        """Add message to assembly log"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        self.assembly_log_text.config(state=tk.NORMAL)
        self.assembly_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.assembly_log_text.config(state=tk.DISABLED)
        self.assembly_log_text.see(tk.END)
    
    def toggle_error_mode(self):
        """Toggle between strict and graceful error handling modes"""
        self.strict_mode = self.strict_mode_var.get()
        self.error_handler.strict_mode = self.strict_mode
        
        if self.strict_mode:
            mode_text = "Strict Mode (Exceptions)"
            self.add_console_message("⚠️ Switched to STRICT mode - exceptions will be thrown", "warning")
        else:
            mode_text = "Graceful Recovery"
            self.add_console_message("🛡️ Switched to GRACEFUL mode - errors will be recovered", "info")
        
        self.error_status_label.configure(text=f"Mode: {mode_text}")
        self.add_console_message(f"🔧 Error handling mode: {mode_text}", "debug")
    
    def handle_processor_exception(self, exception_type, message, pc=None, instruction=None, recovery_action="None"):
        """Handle processor exceptions with logging and recovery"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Add to exception tree
        self.exception_tree.insert("", tk.END, values=(
            timestamp,
            exception_type,
            message,
            f"0x{pc:04X}" if pc is not None else "N/A",
            f"0x{instruction:04X}" if instruction is not None else "N/A",
            recovery_action
        ))
        
        # Auto scroll to bottom
        items = self.exception_tree.get_children()
        if items:
            self.exception_tree.see(items[-1])
        
        # Store in exception logs
        exception_entry = {
            'timestamp': timestamp,
            'type': exception_type,
            'message': message,
            'pc': pc,
            'instruction': instruction,
            'recovery': recovery_action
        }
        self.exception_logs.append(exception_entry)
        
        # Add to console with appropriate severity
        if exception_type in ['MemoryException', 'InvalidInstructionException']:
            self.add_console_message(f"⚠️ {exception_type}: {message} - Recovery: {recovery_action}", "warning")
        else:
            self.add_console_message(f"❌ {exception_type}: {message} - Recovery: {recovery_action}", "error")
        
        # Update exception count
        self.update_error_counts()
    
    def show_error_summary(self):
        """Show detailed error summary in a popup window"""
        summary = self.error_handler.get_error_summary()
        
        # Create popup window
        popup = ctk.CTkToplevel(self.root)
        popup.title("🛡️ Error Handler Summary")
        popup.geometry("800x600")
        popup.grab_set()  # Make modal
        
        # Summary text
        summary_text = scrolledtext.ScrolledText(
            popup,
            font=("Consolas", 10),
            wrap=tk.WORD,
            height=30
        )
        summary_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Format summary
        full_summary = f"""🛡️ PROCESSOR ERROR HANDLER SUMMARY
{'='*60}

Mode: {'Strict (Exceptions)' if self.strict_mode else 'Graceful Recovery'}
Total Errors Handled: {self.error_handler.error_count}

{summary}

📊 GUI ERROR STATISTICS:
- Console Messages: {len(self.console_logs)}
- Error Log Entries: {len(self.error_logs)}
- Exception Log Entries: {len(self.exception_logs)}
- Assembly Errors: {len([log for log in self.error_logs if log.get('type') == 'ASSEMBLY'])}
- Execution Errors: {len([log for log in self.error_logs if log.get('type') == 'EXECUTION'])}

⚙️ ERROR HANDLER CONFIGURATION:
- Strict Mode: {self.error_handler.strict_mode}
- Error Count: {self.error_handler.error_count}
- Error Log Size: {len(self.error_handler.error_log)}

💡 RECOMMENDATIONS:
- Use Strict Mode for debugging specific issues
- Use Graceful Mode for continuous execution
- Check Exception Logs for detailed error traces
- Export logs for external analysis
"""
        
        summary_text.insert("1.0", full_summary)
        summary_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ctk.CTkButton(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=10)
    
    def update_error_counts(self):
        """Update error count displays"""
        total_errors = len(self.error_logs)
        exceptions = len(self.exception_logs)
        recoveries = len([log for log in self.exception_logs if log.get('recovery', 'None') != 'None'])
        
        self.error_count_label.configure(text=f"Total Errors: {total_errors}")
        self.exception_count_label.configure(text=f"Exceptions: {exceptions}")
        self.recovery_count_label.configure(text=f"Recoveries: {recoveries}")
        self.errors_label.configure(text=f"Errors: {total_errors}")
    
    def clear_exception_logs(self):
        """Clear exception logs"""
        for item in self.exception_tree.get_children():
            self.exception_tree.delete(item)
        self.exception_logs.clear()
        self.update_error_counts()
        self.add_console_message("🗑️ Exception logs cleared", "info")
    
    def export_exception_logs(self):
        """Export exception logs to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Exception Logs",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    import json
                    with open(filename, "w", encoding='utf-8') as f:
                        json.dump(self.exception_logs, f, indent=2)
                else:
                    with open(filename, "w", newline='', encoding='utf-8') as f:
                        if filename.endswith('.csv'):
                            f.write("Time,Exception Type,Message,PC,Instruction,Recovery Action\n")
                            for log in self.exception_logs:
                                f.write(f"{log['timestamp']},{log['type']},{log['message']},")
                                f.write(f"0x{log['pc']:04X} if log['pc'] else 'N/A',")
                                f.write(f"0x{log['instruction']:04X} if log['instruction'] else 'N/A',")
                                f.write(f"{log['recovery']}\n")
                        else:
                            for log in self.exception_logs:
                                f.write(f"[{log['timestamp']}] {log['type']}: {log['message']}\n")
                                if log['pc']:
                                    f.write(f"  PC: 0x{log['pc']:04X}\n")
                                if log['instruction']:
                                    f.write(f"  Instruction: 0x{log['instruction']:04X}\n")
                                f.write(f"  Recovery: {log['recovery']}\n\n")
                
                self.add_console_message(f"📤 Exception logs exported: {os.path.basename(filename)}", "success")
            except Exception as e:
                self.add_console_message(f"Error: {str(e)}", "error")


    def add_execution_log(self, message):
        """Add message to execution log"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        self.execution_log_text.config(state=tk.NORMAL)
        self.execution_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.execution_log_text.config(state=tk.DISABLED)
        self.execution_log_text.see(tk.END)
    
    # File operations
    def new_file(self):
        """Create new file"""
        if messagebox.askyesno("New File", "Clear current code and start new file?"):
            self.code_text.delete("1.0", tk.END)
            self.add_console_message("📄 New file created", "info")
            self.update_line_numbers()
    
    def load_file(self):
        """Load assembly file"""
        filename = filedialog.askopenfilename(
            title="Load Assembly File",
            filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "r", encoding='utf-8') as f:
                    content = f.read()
                
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert("1.0", content)
                
                self.add_console_message(f"📁 Loaded file: {os.path.basename(filename)}", "success")
                self.update_line_numbers()
                self.highlight_syntax()
                
            except Exception as e:
                self.add_error_log("FILE_IO", f"Error loading file: {str(e)}", filename)
    
    def save_file(self):
        """Save assembly file"""
        filename = filedialog.asksaveasfilename(
            title="Save Assembly File",
            defaultextension=".asm",
            filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                content = self.code_text.get("1.0", tk.END)
                with open(filename, "w", encoding='utf-8') as f:
                    f.write(content)
                
                self.add_console_message(f"💾 Saved file: {os.path.basename(filename)}", "success")
                
            except Exception as e:
                self.add_error_log("FILE_IO", f"Error saving file: {str(e)}", filename)
    
    # Assembly operations
    def check_syntax(self):
        """Check assembly syntax without assembling"""
        self.add_assembly_log("🔍 Starting syntax check...")
        
        try:
            code = self.code_text.get("1.0", tk.END)
            
            # Basic syntax checks
            lines = code.split('\n')
            errors = []
            warnings = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Check for common syntax errors
                if ':' in line and not re.match(r'^\w+:', line):
                    errors.append(f"Line {line_num}: Invalid label format")
                
                # Check instruction format
                if not ':' in line:
                    parts = line.split()
                    if parts and not parts[0] in ['add', 'sub', 'and', 'or', 'xor', 'addi', 'andi', 'ori', 'lw', 'sw', 'beq', 'bne', 'jal', 'nop', 'halt']:
                        warnings.append(f"Line {line_num}: Unknown instruction '{parts[0]}'")
            
            if errors:
                for error in errors:
                    self.add_error_log("SYNTAX", error, f"Line {line_num}")
                self.add_assembly_log(f"❌ Syntax check failed: {len(errors)} errors found")
            else:
                self.add_assembly_log(f"✅ Syntax check passed: No syntax errors found")
                if warnings:
                    for warning in warnings:
                        self.add_assembly_log(f"⚠️  Warning: {warning}")
            
        except Exception as e:
            self.add_error_log("SYNTAX_CHECK", f"Syntax check failed: {str(e)}")
    
    def assemble_and_load(self):
        """Assemble code and load into processor"""
        self.add_assembly_log("🔧 Starting assembly process...")
        
        try:
            code = self.code_text.get("1.0", tk.END)
            
            # Save to temporary file
            temp_filename = "temp_program.asm"
            with open(temp_filename, "w", encoding='utf-8') as f:
                f.write(code)
            
            self.add_assembly_log(f"📄 Temporary file created: {temp_filename}")
            
            # Assemble
            self.add_assembly_log("🔧 Assembling code...")
            machine_code = self.assembler.assemble_file(temp_filename)
            
            if machine_code:
                self.add_assembly_log(f"✅ Assembly successful: {len(machine_code)} instructions generated")
                
                # Show generated machine code
                self.add_assembly_log("📋 Generated machine code:")
                for i, instruction in enumerate(machine_code):
                    self.add_assembly_log(f"  {i:02d}: 0x{instruction:04X} ({instruction:016b})")
                
                # Load into processor
                success = self.processor.load_program_direct(machine_code)
                if success:
                    self.add_assembly_log("✅ Program loaded into processor successfully")
                    self.add_console_message(f"✅ Assembly complete: {len(machine_code)} instructions loaded", "success")
                    self.reset_processor()
                else:
                    self.add_error_log("ASSEMBLY", "Failed to load program into processor")
            else:
                self.add_error_log("ASSEMBLY", "Assembly failed - check your code for errors")
            
            # Cleanup
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                self.add_assembly_log(f"🗑️ Temporary file cleaned up")
                
        except Exception as e:
            self.add_error_log("ASSEMBLY", f"Assembly error: {str(e)}")
    
    # Execution control
    def run_program(self):
        """Run the program continuously"""
        if self.processor.instruction_memory.program_size == 0:
            self.add_error_log("EXECUTION", "No program loaded. Please assemble first.")
            return
        
        if self.is_running:
            self.stop_execution()
            return
        
        self.is_running = True
        self.run_btn.configure(text="⏹️ Stop")
        self.execution_start_time = time.time()
        
        self.add_console_message("▶️ Starting program execution...", "success")
        self.add_execution_log("▶️ Program execution started")
        
        def execution_loop():
            while self.is_running and not self.processor.halted:
                old_pc = self.processor.pc
                old_cycles = self.processor.cycle_count
                
                # Execute step
                self.step_execution()
                
                # Log execution details
                if self.processor.cycle_count > old_cycles:
                    self.add_execution_log(f"Cycle {self.processor.cycle_count}: PC=0x{old_pc:04X} -> 0x{self.processor.pc:04X}")
                
                # Speed control
                speed = self.speed_slider.get()
                delay = (11 - speed) * 0.05  # 0.05s to 0.5s delay
                time.sleep(delay)
            
            self.is_running = False
            self.run_btn.configure(text="▶️ Run")
            
            if self.processor.halted:
                runtime = time.time() - self.execution_start_time
                self.add_console_message(f"🏁 Program execution completed in {runtime:.3f}s", "success")
                self.add_execution_log(f"🏁 Program execution completed - Runtime: {runtime:.3f}s")
        
        self.execution_thread = Thread(target=execution_loop, daemon=True)
        self.execution_thread.start()
    
    def stop_execution(self):
        """Stop program execution"""
        self.is_running = False
        self.run_btn.configure(text="▶️ Run")
        
        if self.execution_start_time:
            runtime = time.time() - self.execution_start_time
            self.add_console_message(f"⏹️ Execution stopped after {runtime:.3f}s", "warning")
            self.add_execution_log(f"⏹️ Execution stopped - Runtime: {runtime:.3f}s")
    
    def pause_execution(self):
        """Pause/resume execution"""
        if self.is_running:
            self.stop_execution()
            self.pause_btn.configure(text="▶️ Resume")
        else:
            self.run_program()
            self.pause_btn.configure(text="⏸️ Pause")
    
    def step_execution(self):
        """Execute single instruction step"""
        if self.processor.instruction_memory.program_size == 0:
            self.add_error_log("EXECUTION", "No program loaded. Please assemble first.")
            return
        
        self.add_execution_log(f"👆 Single step execution - Cycle {self.processor.cycle_count + 1}")
        
        if self.processor.halted:
            self.add_console_message("⏹️ Processor is halted", "warning")
            return

        old_pc = self.processor.pc
        old_cycles = self.processor.cycle_count

        # Capture register state before execution
        old_registers = {i: self.processor.register_file.read(i) for i in range(16)}

        try:
            # Execute one step with exception handling
            continuing = self.processor.step()
            
            # Capture register state after execution
            new_registers = {i: self.processor.register_file.read(i) for i in range(16)}
            
            # Find changed registers
            changed_registers = []
            for i in range(16):
                if old_registers[i] != new_registers[i]:
                    changed_registers.append(f"x{i}:0x{old_registers[i]:04X}→0x{new_registers[i]:04X}")
            
            # Add to execution trace if we executed an instruction
            if self.processor.cycle_count > old_cycles:
                if self.processor.execution_history:
                    last_execution = self.processor.execution_history[-1]
                    
                    # Determine memory access
                    memory_access = "None"
                    if "SW" in last_execution["assembly"].upper():
                        memory_access = "Write"
                    elif "LW" in last_execution["assembly"].upper():
                        memory_access = "Read"
                    
                    # Add to trace table
                    self.trace_tree.insert("", tk.END, values=(
                        last_execution["cycle"],
                        f"0x{last_execution['pc']:04X}",
                        f"0x{last_execution['instruction']:04X}",
                        last_execution["type"],
                        last_execution["assembly"],
                        ", ".join(changed_registers) if changed_registers else "None",
                        memory_access
                    ))
                    
                    # Auto-scroll to bottom if enabled
                    if self.auto_scroll_var.get():
                        items = self.trace_tree.get_children()
                        if items:
                            self.trace_tree.see(items[-1])
            
            if not continuing:
                self.add_execution_log(f"⏹️ Execution completed at cycle {self.processor.cycle_count}")

        except MemoryException as e:
            self.handle_processor_exception(
                "MemoryException", 
                str(e), 
                pc=e.pc, 
                instruction=e.instruction,
                recovery_action="Returned default value (0)"
            )

        except RegisterException as e:
            self.handle_processor_exception(
                "RegisterException", 
                str(e), 
                pc=e.pc,
                recovery_action="Operation ignored"
            )
            
        except ExecutionException as e:
            self.handle_processor_exception(
                "ExecutionException", 
                str(e), 
                pc=e.pc, 
                instruction=e.instruction,
                recovery_action="Continued execution"
            )
            
        except ProcessorException as e:
            self.handle_processor_exception(
                "ProcessorException", 
                str(e), 
                pc=e.pc, 
                instruction=e.instruction,
                recovery_action="Generic recovery"
            )
            
        except Exception as e:
            # Catch any other unexpected exceptions
            self.handle_processor_exception(
                "UnexpectedException", 
                f"Unexpected error: {str(e)}", 
                pc=old_pc,
                recovery_action="Execution stopped"
            )
            self.add_console_message(f"💥 Unexpected exception during execution: {str(e)}", "error")
            self.stop_execution()
        
        # Update all displays
        self.root.after(0, self.update_displays)
    
    def update_memory_view(self, *args):
        """Update memory view with enhanced error handling"""
        
        # Clear existing items
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)
        
        # Determine memory type
        memory_type = self.memory_type_var.get()
        show_zeros = self.show_zero_var.get()
        
        try:
            # Get address range
            start_addr_str = self.start_addr_entry.get() or ("0x0000" if memory_type == "Instruction Memory" else "0x1000")
            end_addr_str = self.end_addr_entry.get() or ("0x0100" if memory_type == "Instruction Memory" else "0x1100")
            
            start_addr = int(start_addr_str, 16) if start_addr_str.startswith('0x') else int(start_addr_str)
            end_addr = int(end_addr_str, 16) if end_addr_str.startswith('0x') else int(end_addr_str)
            
        except ValueError:
            self.add_error_log("MEMORY_VIEW", "Invalid address format. Use hex (0x1000) or decimal.")
            return
        
        # Collect memory data with exception handling
        memory_data = []
        total_memory = 0
        used_memory = 0
        memory_errors = 0
        
        if memory_type == "Data Memory":
            # Data memory with enhanced error handling
            for addr in range(start_addr, min(end_addr + 1, 0x1000 + self.processor.data_memory.size)):
                if addr >= 0x1000:  # Valid data memory range
                    try:
                        value = self.processor.data_memory.read_word(addr, pc=self.processor.pc)
                        total_memory += 1
                        
                        if value != 0 or show_zeros:
                            if value != 0:
                                used_memory += 1
                            
                            # Convert to ASCII (printable characters only)
                            ascii_char = chr(value & 0xFF) if 32 <= (value & 0xFF) <= 126 else '.'
                            ascii_char2 = chr((value >> 8) & 0xFF) if 32 <= ((value >> 8) & 0xFF) <= 126 else '.'
                            ascii_repr = ascii_char2 + ascii_char
                            
                            memory_data.append((
                                f"0x{addr:04X}",
                                f"0x{value:04X}",
                                str(value),
                                f"{value:016b}",
                                ascii_repr
                            ))
                    
                    except MemoryException as e:
                        memory_errors += 1
                        self.handle_processor_exception(
                            "MemoryException", 
                            f"Memory read error at 0x{addr:04X}", 
                            pc=self.processor.pc,
                            recovery_action="Displayed as 0x0000"
                        )
                        
                        # Still show the entry with error indication
                        memory_data.append((
                            f"0x{addr:04X}",
                            "ERROR",
                            "ERROR",
                            "ERROR",
                            "ERR"
                        ))
            
            # Update data memory statistics
            try:
                stats = self.processor.data_memory.get_statistics()
                self.memory_reads_label.configure(text=f"Total Reads: {stats['reads']}")
                self.memory_writes_label.configure(text=f"Total Writes: {stats['writes']}")
            except Exception as e:
                self.add_console_message(f"⚠️ Error getting memory statistics: {str(e)}", "warning")
                self.memory_reads_label.configure(text="Total Reads: ERROR")
                self.memory_writes_label.configure(text="Total Writes: ERROR")
            
        else:
            # Instruction memory
            for addr in range(start_addr, min(end_addr + 1, self.processor.instruction_memory.size)):
                try:
                    value = self.processor.instruction_memory.read_instruction(addr)
                    total_memory += 1
                    
                    if value != 0 or show_zeros:
                        if value != 0:
                            used_memory += 1
                        
                        # Decode instruction for display
                        try:
                            decoded = self.processor.instruction_decoder.decode(value)
                            assembly = decoded.get('assembly', 'unknown')
                        except Exception:
                            assembly = 'decode_error'
                        
                        memory_data.append((
                            f"0x{addr:04X}",
                            f"0x{value:04X}",
                            str(value),
                            f"{value:016b}",
                            assembly
                        ))
                
                except Exception as e:
                    memory_errors += 1
                    self.handle_processor_exception(
                        "MemoryException", 
                        f"Instruction memory read error at 0x{addr:04X}", 
                        pc=addr,
                        recovery_action="Displayed as NOP"
                    )
                    
                    memory_data.append((
                        f"0x{addr:04X}",
                        "ERROR",
                        "ERROR",
                        "ERROR",
                        "nop"
                    ))
            
            # No read/write stats for instruction memory
            self.memory_reads_label.configure(text="Total Reads: N/A")
            self.memory_writes_label.configure(text="Total Writes: N/A")
        
        # Insert data into tree with error highlighting
        for data in memory_data:
            item = self.memory_tree.insert("", tk.END, values=data)
            
            # Color code based on value and errors
            if "ERROR" in data[1]:  # Error entries
                self.memory_tree.set(item, "Hex Value", data[1])
                # Could add red background if ttk supports it
            elif data[1] != "0x0000":  # Non-zero values
                self.memory_tree.set(item, "Hex Value", data[1])
        
        # Update memory statistics
        self.total_memory_label.configure(text=f"Total Memory: {total_memory * 2} bytes")
        self.used_memory_label.configure(text=f"Used Memory: {used_memory * 2} bytes")
        self.free_memory_label.configure(text=f"Free Memory: {(total_memory - used_memory) * 2} bytes")
        
        # Show memory errors if any
        if memory_errors > 0:
            self.add_console_message(f"⚠️ {memory_errors} memory access errors encountered during view update", "warning")
    
    def assemble_and_load(self):
        """Assemble code and load into processor with enhanced error handling"""
        self.add_assembly_log("🔧 Starting assembly process...")
        
        try:
            code = self.code_text.get("1.0", tk.END)
            
            # Save to temporary file
            temp_filename = "temp_program.asm"
            with open(temp_filename, "w", encoding='utf-8') as f:
                f.write(code)
            
            self.add_assembly_log(f"📄 Temporary file created: {temp_filename}")
            
            # Assemble with error handling
            self.add_assembly_log("🔧 Assembling code...")
            
            try:
                machine_code = self.assembler.assemble_file(temp_filename)
                
                if machine_code:
                    self.add_assembly_log(f"✅ Assembly successful: {len(machine_code)} instructions generated")
                    
                    # Show generated machine code
                    self.add_assembly_log("📋 Generated machine code:")
                    for i, instruction in enumerate(machine_code):
                        self.add_assembly_log(f"  {i:02d}: 0x{instruction:04X} ({instruction:016b})")
                    
                    # Load into processor with error handling
                    try:
                        success = self.processor.load_program_direct(machine_code)
                        if success:
                            self.add_assembly_log("✅ Program loaded into processor successfully")
                            self.add_console_message(f"✅ Assembly complete: {len(machine_code)} instructions loaded", "success")
                            self.reset_processor()
                        else:
                            self.add_error_log("ASSEMBLY", "Failed to load program into processor")
                            
                    except Exception as e:
                        self.handle_processor_exception(
                            "ProcessorException",
                            f"Program loading failed: {str(e)}",
                            recovery_action="Program not loaded"
                        )
                        
                else:
                    self.add_error_log("ASSEMBLY", "Assembly failed - check your code for errors")
                    self.add_assembly_log("❌ Assembly failed - no machine code generated")
                    
            except Exception as e:
                self.add_error_log("ASSEMBLY", f"Assembler error: {str(e)}")
                self.add_assembly_log(f"❌ Assembler exception: {str(e)}")
            
            # Cleanup
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                self.add_assembly_log(f"🗑️ Temporary file cleaned up")
                
        except Exception as e:
            self.add_error_log("ASSEMBLY", f"Assembly process error: {str(e)}")
            self.handle_processor_exception(
                "ExecutionException",
                f"Assembly process failed: {str(e)}",
                recovery_action="Assembly aborted"
            )
    
    def reset_processor(self):
        """Reset processor with enhanced error handling"""
        self.stop_execution()
        
        self.add_console_message("🔄 Resetting processor...", "info")
        self.add_execution_log("🔄 Processor reset initiated")
        
        try:
            self.processor.reset()
            
            # Clear execution trace
            for item in self.trace_tree.get_children():
                self.trace_tree.delete(item)
            
            # Reset error handler but keep logs for analysis
            old_error_count = self.error_handler.error_count
            self.error_handler.reset_errors()
            
            # Reset performance tracking
            self.start_time = None
            self.execution_start_time = None
            
            self.update_displays()
            self.update_memory_view()
            
            self.add_console_message("✅ Processor reset completed", "success")
            self.add_execution_log(f"✅ Processor reset completed - Previous errors: {old_error_count}")
            
        except Exception as e:
            self.handle_processor_exception(
                "ProcessorException",
                f"Reset failed: {str(e)}",
                recovery_action="Partial reset"
            )
            self.add_console_message(f"⚠️ Reset completed with warnings: {str(e)}", "warning")
    
    def update_displays(self):
        """Update all displays with enhanced error handling and exception info"""
        
        try:
            # Update status bar
            self.pc_label.configure(text=f"PC: 0x{self.processor.pc:04X}")
            self.cycles_label.configure(text=f"Cycles: {self.processor.cycle_count}")
            self.instructions_label.configure(text=f"Instructions: {self.processor.instruction_count}")
            
            status = "HALTED" if self.processor.halted else ("RUNNING" if self.is_running else "READY")
            self.status_label.configure(text=f"Status: {status}")
            
            # Calculate and display CPI
            if self.processor.instruction_count > 0:
                cpi = self.processor.cycle_count / self.processor.instruction_count
                self.performance_label.configure(text=f"CPI: {cpi:.2f}")
            else:
                self.performance_label.configure(text="CPI: 0.00")
            
            # Update registers with color coding and error handling
            register_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a7']
            
            for i in range(16):
                try:
                    value = self.processor.register_file.read(i)
                    self.register_values[i].configure(text=f"0x{value:04X} ({value})")
                    
                    # Color coding based on value
                    if value == 0:
                        self.register_frames[i].configure(fg_color=("gray75", "gray25"))
                    elif i == 0:  # x0 should always be zero
                        self.register_frames[i].configure(fg_color=("gray75", "gray25"))
                    else:
                        self.register_frames[i].configure(fg_color=("green", "dark green"))
                        
                except Exception as e:
                    self.register_values[i].configure(text="ERROR")
                    self.register_frames[i].configure(fg_color=("red", "dark red"))
                    self.add_console_message(f"⚠️ Error reading register x{i}: {str(e)}", "warning")
            
            # Update ALU status with error handling
            try:
                alu_flags = self.processor.alu.get_flags()
                self.alu_result_label.configure(text=f"Last Result: 0x{self.processor.alu.last_result:04X}")
                self.alu_zero_label.configure(text=f"Zero Flag: {'✅' if alu_flags['zero'] else '❌'}")
                self.alu_overflow_label.configure(text=f"Overflow Flag: {'✅' if alu_flags['overflow'] else '❌'}")
                self.alu_negative_label.configure(text=f"Negative Flag: {'✅' if alu_flags['negative'] else '❌'}")
                self.alu_operations_label.configure(text=f"Operations: {self.processor.alu.operations_count}")
            except Exception as e:
                self.add_console_message(f"⚠️ Error updating ALU status: {str(e)}", "warning")
            
            # Update Control Unit status
            try:
                if self.processor.execution_history:
                    last_exec = self.processor.execution_history[-1]
                    self.current_instruction_label.configure(text=f"Current: {last_exec['assembly']}")
                    self.instruction_type_label.configure(text=f"Type: {last_exec['type']}")
                else:
                    self.current_instruction_label.configure(text="Current: None")
                    self.instruction_type_label.configure(text="Type: None")
                
                control_stats = self.processor.control_unit.get_statistics()
                self.signals_generated_label.configure(text=f"Signals Generated: {control_stats['total_signals_generated']}")
            except Exception as e:
                self.add_console_message(f"⚠️ Error updating control unit status: {str(e)}", "warning")
            
            # Update performance metrics
            if self.processor.instruction_count > 0:
                cpi = self.processor.cycle_count / self.processor.instruction_count
                self.cpi_label.configure(text=f"CPI: {cpi:.2f}")
            else:
                self.cpi_label.configure(text="CPI: 0.00")
            
            # Calculate frequency (if running)
            if self.execution_start_time and self.is_running:
                runtime = time.time() - self.execution_start_time
                if runtime > 0:
                    frequency = self.processor.cycle_count / runtime
                    self.frequency_label.configure(text=f"Frequency: {frequency:.1f} Hz")
                else:
                    self.frequency_label.configure(text="Frequency: 0 Hz")
            else:
                self.frequency_label.configure(text="Frequency: 0 Hz")
            
            # Runtime
            if self.execution_start_time:
                runtime = time.time() - self.execution_start_time
                self.runtime_label.configure(text=f"Runtime: {runtime:.3f}s")
            else:
                self.runtime_label.configure(text="Runtime: 0.00s")
            
            # Efficiency (instructions per second)
            if self.execution_start_time and self.is_running:
                runtime = time.time() - self.execution_start_time
                if runtime > 0:
                    efficiency = (self.processor.instruction_count / runtime) * 100 / 1000  # Relative to 1kHz
                    self.efficiency_label.configure(text=f"Efficiency: {min(efficiency, 100):.1f}%")
                else:
                    self.efficiency_label.configure(text="Efficiency: 0%")
            else:
                self.efficiency_label.configure(text="Efficiency: 0%")
                
            # Update error counts
            self.update_error_counts()
            
        except Exception as e:
            self.add_console_message(f"💥 Critical error updating displays: {str(e)}", "error")
            self.handle_processor_exception(
                "ProcessorException",
                f"Display update failed: {str(e)}",
                recovery_action="Display partially updated"
            )
    
    def reset_processor(self):
        """Reset processor to initial state"""
        self.stop_execution()
        
        self.add_console_message("🔄 Resetting processor...", "info")
        self.add_execution_log("🔄 Processor reset initiated")
        
        self.processor.reset()
        
        # Clear execution trace
        for item in self.trace_tree.get_children():
            self.trace_tree.delete(item)
        
        # Clear error logs
        self.error_logs.clear()
        self.errors_label.configure(text="Errors: 0")
        
        # Reset performance tracking
        self.start_time = None
        self.execution_start_time = None
        
        self.update_displays()
        self.update_memory_view()
        
        self.add_console_message("✅ Processor reset completed", "success")
        self.add_execution_log("✅ Processor reset completed")
    
    def update_displays(self):
        """Update all display elements with enhanced information"""
        
        # Update status bar
        self.pc_label.configure(text=f"PC: 0x{self.processor.pc:04X}")
        self.cycles_label.configure(text=f"Cycles: {self.processor.cycle_count}")
        self.instructions_label.configure(text=f"Instructions: {self.processor.instruction_count}")
        
        status = "HALTED" if self.processor.halted else ("RUNNING" if self.is_running else "READY")
        self.status_label.configure(text=f"Status: {status}")
        
        # Calculate and display CPI
        if self.processor.instruction_count > 0:
            cpi = self.processor.cycle_count / self.processor.instruction_count
            self.performance_label.configure(text=f"CPI: {cpi:.2f}")
        else:
            self.performance_label.configure(text="CPI: 0.00")
        
        # Update registers with color coding for changes
        register_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a7']
        
        for i in range(16):
            value = self.processor.register_file.read(i)
            self.register_values[i].configure(text=f"0x{value:04X} ({value})")
            
            # Color coding based on value
            if value == 0:
                self.register_frames[i].configure(fg_color=("gray75", "gray25"))
            elif i == 0:  # x0 should always be zero
                self.register_frames[i].configure(fg_color=("gray75", "gray25"))
            else:
                self.register_frames[i].configure(fg_color=("green", "dark green"))
        
        # Update ALU status
        alu_flags = self.processor.alu.get_flags()
        self.alu_result_label.configure(text=f"Last Result: 0x{self.processor.alu.last_result:04X}")
        self.alu_zero_label.configure(text=f"Zero Flag: {'✅' if alu_flags['zero'] else '❌'}")
        self.alu_overflow_label.configure(text=f"Overflow Flag: {'✅' if alu_flags['overflow'] else '❌'}")
        self.alu_negative_label.configure(text=f"Negative Flag: {'✅' if alu_flags['negative'] else '❌'}")
        self.alu_operations_label.configure(text=f"Operations: {self.processor.alu.operations_count}")
        
        # Update Control Unit status
        if self.processor.execution_history:
            last_exec = self.processor.execution_history[-1]
            self.current_instruction_label.configure(text=f"Current: {last_exec['assembly']}")
            self.instruction_type_label.configure(text=f"Type: {last_exec['type']}")
        else:
            self.current_instruction_label.configure(text="Current: None")
            self.instruction_type_label.configure(text="Type: None")
        
        control_stats = self.processor.control_unit.get_statistics()
        self.signals_generated_label.configure(text=f"Signals Generated: {control_stats['total_signals_generated']}")
        
        # Update performance metrics
        if self.processor.instruction_count > 0:
            cpi = self.processor.cycle_count / self.processor.instruction_count
            self.cpi_label.configure(text=f"CPI: {cpi:.2f}")
        else:
            self.cpi_label.configure(text="CPI: 0.00")
        
        # Calculate frequency (if running)
        if self.execution_start_time and self.is_running:
            runtime = time.time() - self.execution_start_time
            if runtime > 0:
                frequency = self.processor.cycle_count / runtime
                self.frequency_label.configure(text=f"Frequency: {frequency:.1f} Hz")
            else:
                self.frequency_label.configure(text="Frequency: 0 Hz")
        else:
            self.frequency_label.configure(text="Frequency: 0 Hz")
        
        # Runtime
        if self.execution_start_time:
            runtime = time.time() - self.execution_start_time
            self.runtime_label.configure(text=f"Runtime: {runtime:.3f}s")
        else:
            self.runtime_label.configure(text="Runtime: 0.00s")
        
        # Efficiency (instructions per second)
        if self.execution_start_time and self.is_running:
            runtime = time.time() - self.execution_start_time
            if runtime > 0:
                efficiency = (self.processor.instruction_count / runtime) * 100 / 1000  # Relative to 1kHz
                self.efficiency_label.configure(text=f"Efficiency: {min(efficiency, 100):.1f}%")
            else:
                self.efficiency_label.configure(text="Efficiency: 0%")
        else:
            self.efficiency_label.configure(text="Efficiency: 0%")
    
    def update_memory_view(self, *args):
        """Update memory view based on current settings"""
        
        # Clear existing items
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)
        
        # Determine memory type
        memory_type = self.memory_type_var.get()
        show_zeros = self.show_zero_var.get()
        
        try:
            # Get address range
            start_addr_str = self.start_addr_entry.get() or ("0x0000" if memory_type == "Instruction Memory" else "0x1000")
            end_addr_str = self.end_addr_entry.get() or ("0x0100" if memory_type == "Instruction Memory" else "0x1100")
            
            start_addr = int(start_addr_str, 16) if start_addr_str.startswith('0x') else int(start_addr_str)
            end_addr = int(end_addr_str, 16) if end_addr_str.startswith('0x') else int(end_addr_str)
            
        except ValueError:
            self.add_error_log("MEMORY_VIEW", "Invalid address format. Use hex (0x1000) or decimal.")
            return
        
        # Collect memory data
        memory_data = []
        total_memory = 0
        used_memory = 0
        
        if memory_type == "Data Memory":
            # Data memory
            for addr in range(start_addr, min(end_addr + 1, 0x1000 + self.processor.data_memory.size)):
                if addr >= 0x1000:  # Valid data memory range
                    value = self.processor.data_memory.read_word(addr)
                    total_memory += 1
                    
                    if value != 0 or show_zeros:
                        if value != 0:
                            used_memory += 1
                        
                        # Convert to ASCII (printable characters only)
                        ascii_char = chr(value & 0xFF) if 32 <= (value & 0xFF) <= 126 else '.'
                        ascii_char2 = chr((value >> 8) & 0xFF) if 32 <= ((value >> 8) & 0xFF) <= 126 else '.'
                        ascii_repr = ascii_char2 + ascii_char
                        
                        memory_data.append((
                            f"0x{addr:04X}",
                            f"0x{value:04X}",
                            str(value),
                            f"{value:016b}",
                            ascii_repr
                        ))
            
            # Update data memory statistics
            stats = self.processor.data_memory.get_statistics()
            self.memory_reads_label.configure(text=f"Total Reads: {stats['reads']}")
            self.memory_writes_label.configure(text=f"Total Writes: {stats['writes']}")
            
        else:
            # Instruction memory
            for addr in range(start_addr, min(end_addr + 1, self.processor.instruction_memory.size)):
                value = self.processor.instruction_memory.read_instruction(addr)
                total_memory += 1
                
                if value != 0 or show_zeros:
                    if value != 0:
                        used_memory += 1
                    
                    # Decode instruction for display
                    decoded = self.processor.instruction_decoder.decode(value)
                    assembly = decoded.get('assembly', 'unknown')
                    
                    memory_data.append((
                        f"0x{addr:04X}",
                        f"0x{value:04X}",
                        str(value),
                        f"{value:016b}",
                        assembly
                    ))
            
            # No read/write stats for instruction memory
            self.memory_reads_label.configure(text="Total Reads: N/A")
            self.memory_writes_label.configure(text="Total Writes: N/A")
        
        # Insert data into tree
        for data in memory_data:
            item = self.memory_tree.insert("", tk.END, values=data)
            
            # Color code based on value
            if data[1] != "0x0000":  # Non-zero values
                self.memory_tree.set(item, "Hex Value", data[1])
        
        # Update memory statistics
        self.total_memory_label.configure(text=f"Total Memory: {total_memory * 2} bytes")
        self.used_memory_label.configure(text=f"Used Memory: {used_memory * 2} bytes")
        self.free_memory_label.configure(text=f"Free Memory: {(total_memory - used_memory) * 2} bytes")
    
    def update_trace_filter(self, *args):
        """Update trace display based on filter"""
        # This would filter the trace tree based on instruction type
        # For now, just refresh the display
        pass
    
    def clear_trace(self):
        """Clear execution trace"""
        for item in self.trace_tree.get_children():
            self.trace_tree.delete(item)
        self.add_console_message("🗑️ Execution trace cleared", "info")
    
    def export_trace(self):
        """Export execution trace to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Execution Trace",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "w", newline='', encoding='utf-8') as f:
                    # Write header
                    f.write("Cycle,PC,Instruction,Type,Assembly,Registers Changed,Memory Access\n")
                    
                    # Write trace data
                    for item in self.trace_tree.get_children():
                        values = self.trace_tree.item(item)['values']
                        f.write(",".join(str(v) for v in values) + "\n")
                
                self.add_console_message(f"📤 Trace exported to: {os.path.basename(filename)}", "success")
                
            except Exception as e:
                self.add_error_log("EXPORT", f"Error exporting trace: {str(e)}", filename)
    
    def clear_console(self):
        """Clear console output"""
        self.console_text.config(state=tk.NORMAL)
        self.console_text.delete("1.0", tk.END)
        self.console_text.config(state=tk.DISABLED)
        self.console_logs.clear()
        self.add_console_message("🗑️ Console cleared", "info")
    
    def save_console_log(self):
        """Save console log to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Console Log",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                content = self.console_text.get("1.0", tk.END)
                with open(filename, "w", encoding='utf-8') as f:
                    f.write(content)
                
                self.add_console_message(f"💾 Console log saved: {os.path.basename(filename)}", "success")
                
            except Exception as e:
                self.add_error_log("SAVE_LOG", f"Error saving console log: {str(e)}", filename)
    
    def clear_error_logs(self):
        """Clear error logs"""
        for item in self.error_tree.get_children():
            self.error_tree.delete(item)
        self.error_logs.clear()
        self.errors_label.configure(text="Errors: 0")
        self.add_console_message("🗑️ Error logs cleared", "info")
    
    def run(self):
        """Start the GUI application"""
        try:
            # Final setup
            self.update_displays()
            self.update_memory_view()
            
            # Start the main loop
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.add_console_message("⌨️ Application interrupted by user", "warning")
            self.root.quit()
        except Exception as e:
            self.add_error_log("APPLICATION", f"Unexpected error: {str(e)}")
            messagebox.showerror("Application Error", f"An unexpected error occurred:\n{str(e)}")


def main():
    """Main function to run the enhanced application"""
    print("🚀 Starting Enhanced RISC-V GUI Application...")
    
    # Check if required modules are available
    try:
        import customtkinter
        print("✅ CustomTkinter found")
    except ImportError:
        print("❌ CustomTkinter not found. Install with: pip install customtkinter")
        return
    
    try:
        from MainCPU import RiscVProcessor
        from Assembler import RiscVAssembler
        print("✅ RISC-V components found")
    except ImportError as e:
        print(f"❌ RISC-V components not found: {e}")
        print("Make sure all your RISC-V Python files are in the same directory")
        return
    
    # Create and run application
    try:
        app = EnhancedRiscVGUI()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()