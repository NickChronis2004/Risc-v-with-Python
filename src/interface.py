"""
RISC-V 16-bit Processor GUI Application - FIXED VERSION
Desktop application with real-time visualization

Requirements:
pip install tkinter customtkinter pillow
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from threading import Thread
import time
import os
import sys

# Import your RISC-V components
from MainCPU import RiscVProcessor
from Assembler import RiscVAssembler

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RiscVGUI:
    def __init__(self):
        """Initialize the RISC-V GUI Application"""
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🖥️ RISC-V 16-bit Processor Simulator")
        self.root.geometry("1400x900")
        
        # Initialize processor and assembler
        self.processor = RiscVProcessor(instruction_memory_size=256, data_memory_size=256)
        self.assembler = RiscVAssembler()
        
        # GUI state
        self.is_running = False
        self.execution_thread = None
        
        # Create GUI elements
        self.create_widgets()
        self.setup_layout()
        self.update_displays()
        
        # Status
        self.add_console_message("🚀 RISC-V Simulator Ready!", "success")
        self.add_console_message("Write assembly code and click 'Assemble' to begin", "info")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="🖥️ RISC-V 16-bit Processor Simulator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Educational RISC-V Simulator with Real-time Visualization",
            font=ctk.CTkFont(size=14)
        )
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.pc_label = ctk.CTkLabel(self.status_frame, text="PC: 0x0000", font=ctk.CTkFont(weight="bold"))
        self.cycles_label = ctk.CTkLabel(self.status_frame, text="Cycles: 0", font=ctk.CTkFont(weight="bold"))
        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: READY", font=ctk.CTkFont(weight="bold"))
        
        # Left panel - Code editor
        self.left_panel = ctk.CTkFrame(self.main_frame)
        self.code_label = ctk.CTkLabel(self.left_panel, text="📝 Assembly Code", font=ctk.CTkFont(size=16, weight="bold"))
        
        # Code text area with scrollbar
        self.code_frame = ctk.CTkFrame(self.left_panel)
        self.code_text = tk.Text(
            self.code_frame,
            wrap=tk.NONE,
            font=("Consolas", 12),
            bg="#212121",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#404040",
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10
        )
        
        # Scrollbars for code editor
        self.code_scrollbar_y = ctk.CTkScrollbar(self.code_frame, command=self.code_text.yview)
        self.code_text.configure(yscrollcommand=self.code_scrollbar_y.set)
        
        self.code_scrollbar_x = ctk.CTkScrollbar(self.code_frame, orientation="horizontal", command=self.code_text.xview)
        self.code_text.configure(xscrollcommand=self.code_scrollbar_x.set)
        
        # Control buttons
        self.controls_frame = ctk.CTkFrame(self.left_panel)
        self.assemble_btn = ctk.CTkButton(self.controls_frame, text="🔧 Assemble", command=self.assemble_code)
        self.run_btn = ctk.CTkButton(self.controls_frame, text="▶️ Run", command=self.run_program)
        self.step_btn = ctk.CTkButton(self.controls_frame, text="👆 Step", command=self.step_execution)
        self.reset_btn = ctk.CTkButton(self.controls_frame, text="🔄 Reset", command=self.reset_processor)
        self.load_btn = ctk.CTkButton(self.controls_frame, text="📁 Load", command=self.load_file)
        self.save_btn = ctk.CTkButton(self.controls_frame, text="💾 Save", command=self.save_file)
        
        # Speed control
        self.speed_frame = ctk.CTkFrame(self.controls_frame)
        self.speed_label = ctk.CTkLabel(self.speed_frame, text="Speed:")
        self.speed_slider = ctk.CTkSlider(self.speed_frame, from_=1, to=10, number_of_steps=9)
        self.speed_slider.set(5)
        
        # Right panel - Processor state
        self.right_panel = ctk.CTkFrame(self.main_frame)
        
        # Register file
        self.registers_label = ctk.CTkLabel(self.right_panel, text="🗂️ Register File", font=ctk.CTkFont(size=16, weight="bold"))
        self.registers_frame = ctk.CTkScrollableFrame(self.right_panel, height=200)
        
        # Create register displays
        self.register_vars = []
        self.register_labels = []
        register_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a7']
        
        for i in range(16):
            var = tk.StringVar(value=f"x{i} ({register_names[i]}): 0x0000 (0)")
            self.register_vars.append(var)
            
            label = ctk.CTkLabel(self.registers_frame, textvariable=var, font=ctk.CTkFont(family="Consolas"))
            label.grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)
            self.register_labels.append(label)
        
        # Memory view
        self.memory_label = ctk.CTkLabel(self.right_panel, text="💾 Data Memory", font=ctk.CTkFont(size=16, weight="bold"))
        self.memory_frame = ctk.CTkScrollableFrame(self.right_panel, height=150)
        
        # ALU status
        self.alu_label = ctk.CTkLabel(self.right_panel, text="⚙️ ALU Status", font=ctk.CTkFont(size=16, weight="bold"))
        self.alu_frame = ctk.CTkFrame(self.right_panel)
        
        self.alu_result_var = tk.StringVar(value="Last Result: 0x0000")
        self.alu_zero_var = tk.StringVar(value="Zero Flag: ❌")
        self.alu_overflow_var = tk.StringVar(value="Overflow Flag: ❌")
        self.alu_negative_var = tk.StringVar(value="Negative Flag: ❌")
        
        ctk.CTkLabel(self.alu_frame, textvariable=self.alu_result_var, font=ctk.CTkFont(family="Consolas")).pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(self.alu_frame, textvariable=self.alu_zero_var, font=ctk.CTkFont(family="Consolas")).pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(self.alu_frame, textvariable=self.alu_overflow_var, font=ctk.CTkFont(family="Consolas")).pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(self.alu_frame, textvariable=self.alu_negative_var, font=ctk.CTkFont(family="Consolas")).pack(anchor="w", padx=10, pady=2)
        
        # Bottom panel - Console and execution trace
        self.bottom_panel = ctk.CTkFrame(self.main_frame)
        
        # Console
        self.console_label = ctk.CTkLabel(self.bottom_panel, text="📺 Console Output", font=ctk.CTkFont(size=16, weight="bold"))
        self.console_frame = ctk.CTkFrame(self.bottom_panel)
        self.console_text = tk.Text(
            self.console_frame,
            height=8,
            font=("Consolas", 10),
            bg="#1a1a1a",
            fg="#ffffff",
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=5
        )
        self.console_scrollbar = ctk.CTkScrollbar(self.console_frame, command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=self.console_scrollbar.set)
        
        # Execution trace
        self.trace_label = ctk.CTkLabel(self.bottom_panel, text="🕒 Execution Trace", font=ctk.CTkFont(size=16, weight="bold"))
        self.trace_frame = ctk.CTkFrame(self.bottom_panel)
        
        # Trace table
        self.trace_tree = ttk.Treeview(
            self.trace_frame,
            columns=("Cycle", "PC", "Instruction", "Assembly"),
            show="headings",
            height=8
        )
        
        self.trace_tree.heading("Cycle", text="Cycle")
        self.trace_tree.heading("PC", text="PC")
        self.trace_tree.heading("Instruction", text="Instruction")
        self.trace_tree.heading("Assembly", text="Assembly")
        
        self.trace_tree.column("Cycle", width=60)
        self.trace_tree.column("PC", width=80)
        self.trace_tree.column("Instruction", width=100)
        self.trace_tree.column("Assembly", width=200)
        
        self.trace_scrollbar = ctk.CTkScrollbar(self.trace_frame, command=self.trace_tree.yview)
        self.trace_tree.configure(yscrollcommand=self.trace_scrollbar.set)
        
        # Example code
        example_code = """# Example: Simple arithmetic and memory operations
addi x1, x0, 10    # x1 = 10
addi x2, x0, 5     # x2 = 5
add x3, x1, x2     # x3 = x1 + x2 = 15
sw x3, 0(x0)       # Store x3 to memory[0]
lw x4, 0(x0)       # Load memory[0] to x4
beq x3, x4, equal  # Branch if equal
addi x5, x0, 1     # Should be skipped
equal:
addi x6, x0, 100   # x6 = 100
halt               # Stop execution"""
        
        self.code_text.insert("1.0", example_code)
    
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
        self.pc_label.pack(side=tk.LEFT, padx=20)
        self.cycles_label.pack(side=tk.LEFT, padx=20)
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Main content area
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (code editor)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.code_label.pack(pady=(10, 5))
        
        self.code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.code_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Control buttons layout
        self.assemble_btn.pack(side=tk.LEFT, padx=5)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        self.step_btn.pack(side=tk.LEFT, padx=5)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Speed control
        self.speed_frame.pack(side=tk.RIGHT, padx=10)
        self.speed_label.pack(side=tk.LEFT, padx=5)
        self.speed_slider.pack(side=tk.LEFT, padx=5)
        
        # Right panel (processor state)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        self.registers_label.pack(pady=(10, 5))
        self.registers_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.memory_label.pack(pady=(0, 5))
        self.memory_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.alu_label.pack(pady=(0, 5))
        self.alu_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Bottom panel
        self.bottom_panel.pack(fill=tk.X, pady=(10, 0))
        
        # Split bottom panel
        bottom_left = ctk.CTkFrame(self.bottom_panel)
        bottom_right = ctk.CTkFrame(self.bottom_panel)
        
        bottom_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        bottom_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Console
        self.console_label.pack(in_=bottom_left, pady=(10, 5))
        self.console_frame.pack(in_=bottom_left, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.console_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Execution trace
        self.trace_label.pack(in_=bottom_right, pady=(10, 5))
        self.trace_frame.pack(in_=bottom_right, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.trace_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.trace_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def add_console_message(self, message, msg_type="info"):
        """Add message to console with color coding"""
        self.console_text.config(state=tk.NORMAL)
        
        # Color mapping
        colors = {
            "success": "#4CAF50",
            "error": "#F44336", 
            "warning": "#FF9800",
            "info": "#2196F3"
        }
        
        # Insert message with timestamp
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.console_text.insert(tk.END, full_message)
        self.console_text.config(state=tk.DISABLED)
        self.console_text.see(tk.END)
    
    def update_displays(self):
        """Update all display elements"""
        # Update status
        self.pc_label.configure(text=f"PC: 0x{self.processor.pc:04X}")
        self.cycles_label.configure(text=f"Cycles: {self.processor.cycle_count}")
        status = "HALTED" if self.processor.halted else ("RUNNING" if self.is_running else "READY")
        self.status_label.configure(text=f"Status: {status}")
        
        # Update registers
        register_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a7']
        for i in range(16):
            value = self.processor.register_file.read(i)
            self.register_vars[i].set(f"x{i} ({register_names[i]}): 0x{value:04X} ({value})")
        
        # Update memory
        for widget in self.memory_frame.winfo_children():
            widget.destroy()
        
        non_zero_memory = self.processor.data_memory.find_non_zero()
        if non_zero_memory:
            for addr, value in non_zero_memory[:10]:  # Show first 10
                mem_label = ctk.CTkLabel(
                    self.memory_frame,
                    text=f"0x{addr:04X}: 0x{value:04X} ({value})",
                    font=ctk.CTkFont(family="Consolas")
                )
                mem_label.pack(anchor="w", padx=5, pady=1)
        else:
            # FIXED: Remove the style="italic" parameter
            no_data_label = ctk.CTkLabel(self.memory_frame, text="(No data stored)", font=ctk.CTkFont(family="Consolas"))
            no_data_label.pack(anchor="w", padx=5, pady=1)
        
        # Update ALU
        alu_flags = self.processor.alu.get_flags()
        self.alu_result_var.set(f"Last Result: 0x{self.processor.alu.last_result:04X}")
        self.alu_zero_var.set(f"Zero Flag: {'✅' if alu_flags['zero'] else '❌'}")
        self.alu_overflow_var.set(f"Overflow Flag: {'✅' if alu_flags['overflow'] else '❌'}")
        self.alu_negative_var.set(f"Negative Flag: {'✅' if alu_flags['negative'] else '❌'}")
    
    def assemble_code(self):
        """Assemble the code in the text editor"""
        try:
            code = self.code_text.get("1.0", tk.END)
            
            # Save to temporary file
            with open("temp_program.asm", "w") as f:
                f.write(code)
            
            # Assemble
            machine_code = self.assembler.assemble_file("temp_program.asm")
            
            if machine_code:
                # Load into processor
                success = self.processor.load_program_direct(machine_code)
                if success:
                    self.add_console_message(f"✅ Successfully assembled {len(machine_code)} instructions", "success")
                    self.reset_processor()
                else:
                    self.add_console_message("❌ Failed to load program into processor", "error")
            else:
                self.add_console_message("❌ Assembly failed - check your code for errors", "error")
            
            # Cleanup
            if os.path.exists("temp_program.asm"):
                os.remove("temp_program.asm")
                
        except Exception as e:
            self.add_console_message(f"❌ Assembly error: {str(e)}", "error")
    
    def run_program(self):
        """Run the program continuously"""
        if self.processor.instruction_memory.program_size == 0:
            self.add_console_message("❌ No program loaded. Please assemble first.", "error")
            return
        
        if self.is_running:
            self.stop_execution()
            return
        
        self.is_running = True
        self.run_btn.configure(text="⏹️ Stop")
        self.add_console_message("▶️ Starting program execution...", "success")
        
        def execution_loop():
            while self.is_running and not self.processor.halted:
                self.step_execution_internal()
                
                # Speed control (1-10, where 10 is fastest)
                speed = self.speed_slider.get()
                delay = (11 - speed) * 0.1  # 0.1s to 1.0s delay
                time.sleep(delay)
            
            self.is_running = False
            self.run_btn.configure(text="▶️ Run")
            
            if self.processor.halted:
                self.add_console_message("🏁 Program execution completed", "success")
        
        self.execution_thread = Thread(target=execution_loop, daemon=True)
        self.execution_thread.start()
    
    def stop_execution(self):
        """Stop program execution"""
        self.is_running = False
        self.run_btn.configure(text="▶️ Run")
        self.add_console_message("⏹️ Execution stopped", "warning")
    
    def step_execution(self):
        """Execute single instruction step"""
        if self.processor.instruction_memory.program_size == 0:
            self.add_console_message("❌ No program loaded. Please assemble first.", "error")
            return
        
        self.step_execution_internal()
    
    def step_execution_internal(self):
        """Internal step execution without checks"""
        if self.processor.halted:
            self.add_console_message("⏹️ Processor is halted", "warning")
            return
        
        old_pc = self.processor.pc
        old_cycles = self.processor.cycle_count
        
        # Execute one step
        continuing = self.processor.step()
        
        # Add to execution trace if we executed an instruction
        if self.processor.cycle_count > old_cycles:
            if self.processor.execution_history:
                last_execution = self.processor.execution_history[-1]
                self.trace_tree.insert("", tk.END, values=(
                    last_execution["cycle"],
                    f"0x{last_execution['pc']:04X}",
                    f"0x{last_execution['instruction']:04X}",
                    last_execution["assembly"]
                ))
                
                # Auto-scroll to bottom
                items = self.trace_tree.get_children()
                if items:
                    self.trace_tree.see(items[-1])
        
        # Update displays
        self.root.after(0, self.update_displays)
        
        if not continuing:
            self.add_console_message(f"Step {self.processor.cycle_count}: Execution completed", "info")
    
    def reset_processor(self):
        """Reset processor to initial state"""
        self.stop_execution()
        self.processor.reset()
        
        # Clear execution trace
        for item in self.trace_tree.get_children():
            self.trace_tree.delete(item)
        
        self.update_displays()
        self.add_console_message("🔄 Processor reset to initial state", "success")
    
    def load_file(self):
        """Load assembly file"""
        filename = filedialog.askopenfilename(
            title="Load Assembly File",
            filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "r") as f:
                    content = f.read()
                
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert("1.0", content)
                
                self.add_console_message(f"📁 Loaded file: {os.path.basename(filename)}", "success")
                
            except Exception as e:
                self.add_console_message(f"❌ Error loading file: {str(e)}", "error")
    
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
                with open(filename, "w") as f:
                    f.write(content)
                
                self.add_console_message(f"💾 Saved file: {os.path.basename(filename)}", "success")
                
            except Exception as e:
                self.add_console_message(f"❌ Error saving file: {str(e)}", "error")
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()


def main():
    """Main function to run the application"""
    print("🚀 Starting RISC-V GUI Application...")
    
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
    app = RiscVGUI()
    app.run()


if __name__ == "__main__":
    main()