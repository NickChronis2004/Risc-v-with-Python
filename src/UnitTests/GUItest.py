
"""
RISC-V Processor Monitoring Dashboard 📊
========================================

Real-time monitoring και debugging dashboard για το RISC-V simulator:
- Live performance metrics
- Memory usage tracking
- Instruction execution analysis
- Register state monitoring
- Exception και error tracking
- Visual performance graphs
"""

import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

import os
sys.path.append('..')

import time
import threading
from collections import deque
import tkinter as tk
from tkinter import ttk
import json
import datetime

# Add src to path
sys.path.append('src')


class ProcessorMonitor:
    """Real-time processor monitoring"""
    
    def __init__(self, processor):
        self.processor = processor
        self.monitoring = False
        
        # Data storage
        self.metrics_history = {
            'cycles': deque(maxlen=100),
            'instructions': deque(maxlen=100),
            'memory_reads': deque(maxlen=100),
            'memory_writes': deque(maxlen=100),
            'register_changes': deque(maxlen=100),
            'alu_operations': deque(maxlen=100),
            'branch_taken': deque(maxlen=100),
            'timestamps': deque(maxlen=100)
        }
        
        self.last_snapshot = None
        self.callbacks = []
    
    def add_callback(self, callback):
        """Add monitoring callback"""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring = True
        self.last_snapshot = self._take_snapshot()
        
        def monitor_loop():
            while self.monitoring:
                current_snapshot = self._take_snapshot()
                if self.last_snapshot:
                    metrics = self._calculate_metrics(self.last_snapshot, current_snapshot)
                    self._record_metrics(metrics)
                    
                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            callback(metrics, current_snapshot)
                        except Exception as e:
                            print(f"Callback error: {e}")
                
                self.last_snapshot = current_snapshot
                time.sleep(0.1)  # 10 FPS monitoring
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def _take_snapshot(self):
        """Take processor state snapshot"""
        return {
            'timestamp': time.time(),
            'pc': self.processor.pc,
            'cycles': self.processor.cycle_count,
            'instructions': self.processor.instruction_count,
            'halted': self.processor.halted,
            'registers': [self.processor.register_file.read(i) for i in range(16)],
            'alu_ops': self.processor.alu.operations_count,
            'memory_stats': self.processor.data_memory.get_statistics(),
            'processor_stats': dict(self.processor.stats)
        }
    
    def _calculate_metrics(self, last, current):
        """Calculate performance metrics"""
        time_delta = current['timestamp'] - last['timestamp']
        
        if time_delta == 0:
            time_delta = 0.001  # Avoid division by zero
        
        # Calculate rates
        cycle_rate = (current['cycles'] - last['cycles']) / time_delta
        instruction_rate = (current['instructions'] - last['instructions']) / time_delta
        
        # Memory operation deltas
        mem_reads = current['memory_stats']['reads'] - last['memory_stats']['reads']
        mem_writes = current['memory_stats']['writes'] - last['memory_stats']['writes']
        
        # Register changes
        reg_changes = sum(1 for i in range(16) 
                         if current['registers'][i] != last['registers'][i])
        
        # ALU operations
        alu_ops = current['alu_ops'] - last['alu_ops']
        
        # Branch statistics
        branches_taken = (current['processor_stats']['branches_taken'] - 
                         last['processor_stats']['branches_taken'])
        
        return {
            'cycle_rate': cycle_rate,
            'instruction_rate': instruction_rate,
            'memory_read_rate': mem_reads / time_delta,
            'memory_write_rate': mem_writes / time_delta,
            'register_changes': reg_changes,
            'alu_rate': alu_ops / time_delta,
            'branch_rate': branches_taken / time_delta,
            'time_delta': time_delta
        }
    
    def _record_metrics(self, metrics):
        """Record metrics in history"""
        timestamp = time.time()
        
        self.metrics_history['cycles'].append(metrics['cycle_rate'])
        self.metrics_history['instructions'].append(metrics['instruction_rate'])
        self.metrics_history['memory_reads'].append(metrics['memory_read_rate'])
        self.metrics_history['memory_writes'].append(metrics['memory_write_rate'])
        self.metrics_history['register_changes'].append(metrics['register_changes'])
        self.metrics_history['alu_operations'].append(metrics['alu_rate'])
        self.metrics_history['branch_taken'].append(metrics['branch_rate'])
        self.metrics_history['timestamps'].append(timestamp)
    
    def get_metrics_summary(self):
        """Get metrics summary"""
        if not self.metrics_history['timestamps']:
            return {}
        
        summary = {}
        for metric, values in self.metrics_history.items():
            if metric != 'timestamps' and values:
                summary[metric] = {
                    'current': values[-1] if values else 0,
                    'average': sum(values) / len(values) if values else 0,
                    'maximum': max(values) if values else 0,
                    'minimum': min(values) if values else 0
                }
        
        return summary


class MonitoringDashboard:
    """GUI Dashboard για monitoring"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📊 RISC-V Monitoring Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2E3440")
        
        self.processor = None
        self.monitor = None
        
        self.create_dashboard()
        self.load_test_processor()
    
    def create_dashboard(self):
        """Create dashboard interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#3B4252", height=80)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="📊 RISC-V Processor Monitoring Dashboard",
            font=("Arial", 18, "bold"),
            bg="#3B4252",
            fg="#ECEFF4"
        )
        title_label.pack(pady=20)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg="#2E3440")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Metrics
        left_panel = tk.Frame(main_frame, bg="#3B4252", width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Right panel - Details
        right_panel = tk.Frame(main_frame, bg="#3B4252")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_metrics_panel(left_panel)
        self.create_details_panel(right_panel)
        
        # Control panel
        control_frame = tk.Frame(self.root, bg="#434C5E", height=60)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        self.create_control_panel(control_frame)
    
    def create_metrics_panel(self, parent):
        """Create real-time metrics panel"""
        
        tk.Label(
            parent,
            text="⚡ Real-time Metrics",
            font=("Arial", 14, "bold"),
            bg="#3B4252",
            fg="#88C0D0"
        ).pack(pady=10)
        
        # Metrics display
        self.metrics_frame = tk.Frame(parent, bg="#3B4252")
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Initialize metric displays
        self.metric_labels = {}
        self.metric_values = {}
        
        metrics = [
            ("🔄 Cycle Rate", "cycles/sec"),
            ("📋 Instruction Rate", "inst/sec"),
            ("📖 Memory Reads", "reads/sec"),
            ("✏️ Memory Writes", "writes/sec"),
            ("🗂️ Register Changes", "changes"),
            ("⚙️ ALU Operations", "ops/sec"),
            ("🔀 Branch Rate", "branches/sec")
        ]
        
        for i, (name, unit) in enumerate(metrics):
            metric_frame = tk.Frame(self.metrics_frame, bg="#434C5E", relief=tk.RAISED, bd=1)
            metric_frame.pack(fill=tk.X, pady=5, padx=5)
            
            label = tk.Label(
                metric_frame,
                text=name,
                font=("Arial", 10, "bold"),
                bg="#434C5E",
                fg="#D8DEE9"
            )
            label.pack(anchor="w", padx=5, pady=2)
            
            value_label = tk.Label(
                metric_frame,
                text="0.0",
                font=("Consolas", 12, "bold"),
                bg="#434C5E",
                fg="#A3BE8C"
            )
            value_label.pack(anchor="w", padx=5)
            
            unit_label = tk.Label(
                metric_frame,
                text=unit,
                font=("Arial", 8),
                bg="#434C5E",
                fg="#88C0D0"
            )
            unit_label.pack(anchor="w", padx=5, pady=(0, 5))
            
            self.metric_values[name] = value_label
        
        # Performance graph area
        graph_frame = tk.Frame(parent, bg="#434C5E", height=200)
        graph_frame.pack(fill=tk.X, padx=10, pady=10)
        graph_frame.pack_propagate(False)
        
        tk.Label(
            graph_frame,
            text="📈 Performance Graph",
            font=("Arial", 12, "bold"),
            bg="#434C5E",
            fg="#88C0D0"
        ).pack(pady=5)
        
        self.graph_canvas = tk.Canvas(
            graph_frame,
            bg="#2E3440",
            height=150
        )
        self.graph_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_details_panel(self, parent):
        """Create detailed information panel"""
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Processor State Tab
        state_frame = tk.Frame(self.notebook, bg="#3B4252")
        self.notebook.add(state_frame, text="🖥️ Processor State")
        
        self.create_processor_state_tab(state_frame)
        
        # Memory Tab
        memory_frame = tk.Frame(self.notebook, bg="#3B4252")
        self.notebook.add(memory_frame, text="💾 Memory")
        
        self.create_memory_tab(memory_frame)
        
        # Execution Trace Tab
        trace_frame = tk.Frame(self.notebook, bg="#3B4252")
        self.notebook.add(trace_frame, text="🕒 Execution Trace")
        
        self.create_trace_tab(trace_frame)
        
        # Statistics Tab
        stats_frame = tk.Frame(self.notebook, bg="#3B4252")
        self.notebook.add(stats_frame, text="📊 Statistics")
        
        self.create_statistics_tab(stats_frame)
    
    def create_processor_state_tab(self, parent):
        """Create processor state display"""
        
        # PC and basic info
        info_frame = tk.Frame(parent, bg="#434C5E")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.pc_label = tk.Label(
            info_frame,
            text="PC: 0x0000",
            font=("Consolas", 14, "bold"),
            bg="#434C5E",
            fg="#88C0D0"
        )
        self.pc_label.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(
            info_frame,
            text="Status: READY",
            font=("Consolas", 14, "bold"),
            bg="#434C5E",
            fg="#A3BE8C"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.cycles_label = tk.Label(
            info_frame,
            text="Cycles: 0",
            font=("Consolas", 14, "bold"),
            bg="#434C5E",
            fg="#D8DEE9"
        )
        self.cycles_label.pack(side=tk.LEFT, padx=10)
        
        # Register display
        reg_frame = tk.Frame(parent, bg="#3B4252")
        reg_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(
            reg_frame,
            text="🗂️ Register File",
            font=("Arial", 12, "bold"),
            bg="#3B4252",
            fg="#88C0D0"
        ).pack(pady=5)
        
        # Register grid
        self.register_frame = tk.Frame(reg_frame, bg="#434C5E")
        self.register_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.register_labels = {}
        register_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a7']
        
        for i in range(16):
            row = i // 4
            col = i % 4
            
            reg_widget = tk.Frame(self.register_frame, bg="#4C566A", relief=tk.RAISED, bd=1)
            reg_widget.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
            name_label = tk.Label(
                reg_widget,
                text=f"x{i} ({register_names[i]})",
                font=("Consolas", 9, "bold"),
                bg="#4C566A",
                fg="#D8DEE9"
            )
            name_label.pack()
            
            value_label = tk.Label(
                reg_widget,
                text="0x0000",
                font=("Consolas", 10),
                bg="#4C566A",
                fg="#A3BE8C"
            )
            value_label.pack()
            
            self.register_labels[i] = value_label
        
        # Configure grid weights
        for i in range(4):
            self.register_frame.columnconfigure(i, weight=1)
    
    def create_memory_tab(self, parent):
        """Create memory monitoring tab"""
        
        # Memory statistics
        stats_frame = tk.Frame(parent, bg="#434C5E")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(
            stats_frame,
            text="📊 Memory Statistics",
            font=("Arial", 12, "bold"),
            bg="#434C5E",
            fg="#88C0D0"
        ).pack(pady=5)
        
        self.memory_stats_text = tk.Text(
            stats_frame,
            height=6,
            font=("Consolas", 10),
            bg="#2E3440",
            fg="#D8DEE9",
            state=tk.DISABLED
        )
        self.memory_stats_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Memory contents
        content_frame = tk.Frame(parent, bg="#3B4252")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(
            content_frame,
            text="💾 Memory Contents (Non-zero)",
            font=("Arial", 12, "bold"),
            bg="#3B4252",
            fg="#88C0D0"
        ).pack(pady=5)
        
        # Memory content display with scrollbar
        mem_scroll_frame = tk.Frame(content_frame, bg="#3B4252")
        mem_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.memory_text = tk.Text(
            mem_scroll_frame,
            font=("Consolas", 10),
            bg="#2E3440",
            fg="#A3BE8C",
            state=tk.DISABLED
        )
        
        mem_scrollbar = tk.Scrollbar(mem_scroll_frame, command=self.memory_text.yview)
        self.memory_text.configure(yscrollcommand=mem_scrollbar.set)
        
        self.memory_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mem_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_trace_tab(self, parent):
        """Create execution trace tab"""
        
        tk.Label(
            parent,
            text="🕒 Execution Trace",
            font=("Arial", 12, "bold"),
            bg="#3B4252",
            fg="#88C0D0"
        ).pack(pady=5)
        
        # Trace table
        trace_frame = tk.Frame(parent, bg="#3B4252")
        trace_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for trace
        self.trace_tree = ttk.Treeview(
            trace_frame,
            columns=("Cycle", "PC", "Instruction", "Assembly", "Changes"),
            show="headings",
            height=15
        )
        
        # Configure columns
        self.trace_tree.heading("Cycle", text="Cycle")
        self.trace_tree.heading("PC", text="PC")
        self.trace_tree.heading("Instruction", text="Instruction")
        self.trace_tree.heading("Assembly", text="Assembly")
        self.trace_tree.heading("Changes", text="Changes")
        
        self.trace_tree.column("Cycle", width=60)
        self.trace_tree.column("PC", width=80)
        self.trace_tree.column("Instruction", width=100)
        self.trace_tree.column("Assembly", width=200)
        self.trace_tree.column("Changes", width=150)
        
        # Scrollbar for trace
        trace_scrollbar = ttk.Scrollbar(trace_frame, command=self.trace_tree.yview)
        self.trace_tree.configure(yscrollcommand=trace_scrollbar.set)
        
        self.trace_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trace_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_statistics_tab(self, parent):
        """Create statistics tab"""
        
        tk.Label(
            parent,
            text="📊 Performance Statistics",
            font=("Arial", 12, "bold"),
            bg="#3B4252",
            fg="#88C0D0"
        ).pack(pady=5)
        
        self.stats_text = tk.Text(
            parent,
            font=("Consolas", 11),
            bg="#2E3440",
            fg="#D8DEE9",
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_control_panel(self, parent):
        """Create control panel"""
        
        # Load program button
        self.load_btn = tk.Button(
            parent,
            text="📁 Load Program",
            command=self.load_program,
            font=("Arial", 10, "bold"),
            bg="#5E81AC",
            fg="white",
            padx=15
        )
        self.load_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Start monitoring button
        self.monitor_btn = tk.Button(
            parent,
            text="▶️ Start Monitoring",
            command=self.toggle_monitoring,
            font=("Arial", 10, "bold"),
            bg="#A3BE8C",
            fg="white",
            padx=15
        )
        self.monitor_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Step execution button
        self.step_btn = tk.Button(
            parent,
            text="👆 Step",
            command=self.step_execution,
            font=("Arial", 10, "bold"),
            bg="#EBCB8B",
            fg="black",
            padx=15
        )
        self.step_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Reset button
        self.reset_btn = tk.Button(
            parent,
            text="🔄 Reset",
            command=self.reset_processor,
            font=("Arial", 10, "bold"),
            bg="#BF616A",
            fg="white",
            padx=15
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Export data button
        self.export_btn = tk.Button(
            parent,
            text="💾 Export Data",
            command=self.export_monitoring_data,
            font=("Arial", 10, "bold"),
            bg="#B48EAD",
            fg="white",
            padx=15
        )
        self.export_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Status indicator
        self.status_indicator = tk.Label(
            parent,
            text="● READY",
            font=("Arial", 12, "bold"),
            bg="#434C5E",
            fg="#A3BE8C"
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def load_test_processor(self):
        """Load test processor with sample program"""
        try:
            from MainCPU import RiscVProcessor
            from Assembler import RiscVAssembler
            
            self.processor = RiscVProcessor(64, 64)
            self.monitor = ProcessorMonitor(self.processor)
            
            # Add monitoring callback
            self.monitor.add_callback(self.update_display)
            
            # Load sample program
            sample_program = [
                0x510A,  # ADDI x1, x0, 10
                0x5205,  # ADDI x2, x0, 5
                0x0312,  # ADD x3, x1, x2
                0x9320,  # SW x3, 0(x2)
                0x8420,  # LW x4, 0(x2)
                0xF000   # HALT
            ]
            
            self.processor.load_program_direct(sample_program)
            self.update_static_display()
            
        except Exception as e:
            print(f"Error loading test processor: {e}")
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if not self.monitor:
            return
        
        if self.monitor.monitoring:
            self.monitor.stop_monitoring()
            self.monitor_btn.configure(text="▶️ Start Monitoring", bg="#A3BE8C")
            self.status_indicator.configure(text="● STOPPED", fg="#BF616A")
        else:
            self.monitor.start_monitoring()
            self.monitor_btn.configure(text="⏹️ Stop Monitoring", bg="#BF616A")
            self.status_indicator.configure(text="● MONITORING", fg="#A3BE8C")
    
    def step_execution(self):
        """Execute one step"""
        if self.processor and not self.processor.halted:
            self.processor.step()
            self.update_static_display()
    
    def reset_processor(self):
        """Reset processor"""
        if self.processor:
            self.processor.reset()
            self.update_static_display()
            
            # Clear trace
            for item in self.trace_tree.get_children():
                self.trace_tree.delete(item)
    
    def load_program(self):
        """Load new program"""
        # For demo, load a different sample program
        if self.processor:
            sample_programs = [
                [0x5107, 0x5203, 0x0312, 0xF000],  # Simple math
                [0x510F, 0x5200, 0x0312, 0x9320, 0x8420, 0xF000],  # Memory ops
                [0x5105, 0x5205, 0xA125, 0x5306, 0xF000]  # With branch
            ]
            
            import random
            program = random.choice(sample_programs)
            self.processor.reset()
            self.processor.load_program_direct(program)
            self.update_static_display()
    
    def update_display(self, metrics, snapshot):
        """Update display with new metrics"""
        # Update metrics
        metric_mapping = {
            "🔄 Cycle Rate": metrics.get('cycle_rate', 0),
            "📋 Instruction Rate": metrics.get('instruction_rate', 0),
            "📖 Memory Reads": metrics.get('memory_read_rate', 0),
            "✏️ Memory Writes": metrics.get('memory_write_rate', 0),
            "🗂️ Register Changes": metrics.get('register_changes', 0),
            "⚙️ ALU Operations": metrics.get('alu_rate', 0),
            "🔀 Branch Rate": metrics.get('branch_rate', 0)
        }
        
        for name, value in metric_mapping.items():
            if name in self.metric_values:
                self.metric_values[name].configure(text=f"{value:.2f}")
        
        # Update graph
        self.update_performance_graph()
        
        # Update static display
        self.root.after(0, self.update_static_display)
    
    def update_static_display(self):
        """Update static processor information"""
        if not self.processor:
            return
        
        # Update processor state
        self.pc_label.configure(text=f"PC: 0x{self.processor.pc:04X}")
        status = "HALTED" if self.processor.halted else "RUNNING"
        self.status_label.configure(text=f"Status: {status}")
        self.cycles_label.configure(text=f"Cycles: {self.processor.cycle_count}")
        
        # Update registers
        for i in range(16):
            value = self.processor.register_file.read(i)
            self.register_labels[i].configure(text=f"0x{value:04X}")
            
            # Highlight changed registers
            if hasattr(self, 'last_register_values'):
                if self.last_register_values[i] != value:
                    self.register_labels[i].configure(fg="#EBCB8B")  # Yellow for changes
                else:
                    self.register_labels[i].configure(fg="#A3BE8C")  # Green for normal
        
        self.last_register_values = [self.processor.register_file.read(i) for i in range(16)]
        
        # Update memory
        self.update_memory_display()
        
        # Update statistics
        self.update_statistics_display()
    
    def update_memory_display(self):
        """Update memory display"""
        if not self.processor:
            return
        
        # Memory statistics
        stats = self.processor.data_memory.get_statistics()
        self.memory_stats_text.configure(state=tk.NORMAL)
        self.memory_stats_text.delete(1.0, tk.END)
        
        stats_text = f"""Memory Statistics:
Total Accesses: {stats['total_accesses']}
Reads: {stats['reads']}
Writes: {stats['writes']}
Memory Size: {stats['size']} words
Base Address: 0x{stats['base_address']:04X}
"""
        self.memory_stats_text.insert(1.0, stats_text)
        self.memory_stats_text.configure(state=tk.DISABLED)
        
        # Memory contents
        non_zero = self.processor.data_memory.find_non_zero()
        self.memory_text.configure(state=tk.NORMAL)
        self.memory_text.delete(1.0, tk.END)
        
        if non_zero:
            self.memory_text.insert(tk.END, "Address  | Value  | Decimal\n")
            self.memory_text.insert(tk.END, "-" * 30 + "\n")
            
            for addr, value in non_zero[:20]:  # Show first 20
                self.memory_text.insert(tk.END, f"0x{addr:04X}   | 0x{value:04X} | {value:>5}\n")
        else:
            self.memory_text.insert(tk.END, "No data stored in memory")
        
        self.memory_text.configure(state=tk.DISABLED)
    
    def update_performance_graph(self):
        """Update performance graph"""
        if not self.monitor or not self.monitor.metrics_history['cycles']:
            return
        
        # Simple line graph
        self.graph_canvas.delete("all")
        width = self.graph_canvas.winfo_width()
        height = self.graph_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Get cycle rate data
        data = list(self.monitor.metrics_history['cycles'])
        if len(data) < 2:
            return
        
        # Scale data to canvas
        max_val = max(data) if data else 1
        min_val = min(data) if data else 0
        
        if max_val == min_val:
            max_val = min_val + 1
        
        points = []
        for i, value in enumerate(data):
            x = (i / (len(data) - 1)) * (width - 20) + 10
            y = height - 10 - ((value - min_val) / (max_val - min_val)) * (height - 20)
            points.extend([x, y])
        
        if len(points) >= 4:
            self.graph_canvas.create_line(points, fill="#88C0D0", width=2)
        
        # Draw axes
        self.graph_canvas.create_line(10, height-10, width-10, height-10, fill="#4C566A")  # X-axis
        self.graph_canvas.create_line(10, 10, 10, height-10, fill="#4C566A")  # Y-axis
        
        # Labels
        self.graph_canvas.create_text(width//2, height-5, text="Time", fill="#D8DEE9", font=("Arial", 8))
        self.graph_canvas.create_text(5, 15, text=f"{max_val:.1f}", fill="#D8DEE9", font=("Arial", 8))
        self.graph_canvas.create_text(5, height-15, text=f"{min_val:.1f}", fill="#D8DEE9", font=("Arial", 8))
    
    def update_statistics_display(self):
        """Update statistics display"""
        if not self.processor:
            return
        
        self.stats_text.configure(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        # Processor statistics
        stats_text = f"""📊 PROCESSOR STATISTICS
{'='*40}

Execution:
  Total Cycles: {self.processor.cycle_count}
  Instructions Executed: {self.processor.instruction_count}
  Program Counter: 0x{self.processor.pc:04X}
  Status: {'HALTED' if self.processor.halted else 'RUNNING'}

Instruction Mix:
  R-Type: {self.processor.stats['r_type_count']}
  I-Type: {self.processor.stats['i_type_count']}
  S-Type: {self.processor.stats['s_type_count']}
  B-Type: {self.processor.stats['b_type_count']}
  J-Type: {self.processor.stats['j_type_count']}
  Special: {self.processor.stats['special_count']}

Memory Operations:
  Reads: {self.processor.stats['memory_reads']}
  Writes: {self.processor.stats['memory_writes']}

Branch Statistics:
  Branches Taken: {self.processor.stats['branches_taken']}
  Branches Not Taken: {self.processor.stats['branches_not_taken']}

ALU Operations: {self.processor.alu.operations_count}
"""
        
        # Add monitoring statistics if available
        if self.monitor:
            summary = self.monitor.get_metrics_summary()
            if summary:
                stats_text += f"\n📈 MONITORING STATISTICS\n{'='*40}\n"
                for metric, data in summary.items():
                    stats_text += f"\n{metric.replace('_', ' ').title()}:\n"
                    stats_text += f"  Current: {data['current']:.2f}\n"
                    stats_text += f"  Average: {data['average']:.2f}\n"
                    stats_text += f"  Maximum: {data['maximum']:.2f}\n"
                    stats_text += f"  Minimum: {data['minimum']:.2f}\n"
        
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.configure(state=tk.DISABLED)
    
    def export_monitoring_data(self):
        """Export monitoring data to file"""
        if not self.monitor:
            return
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"risc_v_monitoring_{timestamp}.json"
            
            # Prepare data for export
            export_data = {
                'timestamp': timestamp,
                'processor_state': {
                    'pc': self.processor.pc,
                    'cycles': self.processor.cycle_count,
                    'instructions': self.processor.instruction_count,
                    'halted': self.processor.halted,
                    'registers': [self.processor.register_file.read(i) for i in range(16)]
                },
                'metrics_history': {
                    key: list(values) for key, values in self.monitor.metrics_history.items()
                },
                'statistics': dict(self.processor.stats),
                'memory_stats': self.processor.data_memory.get_statistics()
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Monitoring data exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
    
    def run(self):
        """Run the dashboard"""
        # Start with a small delay to ensure proper initialization
        self.root.after(100, self.update_static_display)
        self.root.mainloop()


def main():
    """Main function"""
    print("📊 Starting RISC-V Monitoring Dashboard...")
    
    try:
        dashboard = MonitoringDashboard()
        dashboard.run()
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()