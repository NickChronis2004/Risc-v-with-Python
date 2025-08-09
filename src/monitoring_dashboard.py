"""
RISC-V Processor Monitoring Dashboard

Lightweight Tkinter dashboard to visualize a running RiscVProcessor.
Shows live cycle/instruction rates, register values, and recent memory writes.
"""

import sys
import time


def _require_tk():
    try:
        import tkinter as tk  # noqa: F401
        from tkinter import ttk  # noqa: F401
        return True
    except Exception as e:
        print(f"❌ Tkinter not available: {e}")
        print("Install tkinter or run: python ultimate_launcher.py --test")
        return False


class ProcessorMonitor:
    def __init__(self, processor):
        self.processor = processor
        self._last_snapshot = None
        self._last_time = None

    def snapshot(self):
        return {
            "timestamp": time.time(),
            "pc": self.processor.pc,
            "cycles": self.processor.cycle_count,
            "instructions": self.processor.instruction_count,
            "halted": self.processor.halted,
            "registers": [self.processor.register_file.read(i) for i in range(16)],
            "mem_reads": self.processor.stats.get("memory_reads", 0),
            "mem_writes": self.processor.stats.get("memory_writes", 0),
        }

    def rates(self, snap_now):
        if self._last_snapshot is None:
            self._last_snapshot = snap_now
            self._last_time = snap_now["timestamp"]
            return {"cycle_rate": 0.0, "inst_rate": 0.0, "read_rate": 0.0, "write_rate": 0.0}

        dt = max(snap_now["timestamp"] - self._last_time, 1e-6)
        cr = (snap_now["cycles"] - self._last_snapshot["cycles"]) / dt
        ir = (snap_now["instructions"] - self._last_snapshot["instructions"]) / dt
        rr = (snap_now["mem_reads"] - self._last_snapshot["mem_reads"]) / dt
        wr = (snap_now["mem_writes"] - self._last_snapshot["mem_writes"]) / dt

        self._last_snapshot = snap_now
        self._last_time = snap_now["timestamp"]
        return {"cycle_rate": cr, "inst_rate": ir, "read_rate": rr, "write_rate": wr}


class MonitoringDashboard:
    REFRESH_MS = 100

    def __init__(self):
        import tkinter as tk
        from tkinter import ttk
        from MainCPU import RiscVProcessor

        self.tk = tk
        self.ttk = ttk

        self.root = tk.Tk()
        self.root.title("RISC-V Monitoring Dashboard")
        self.root.geometry("900x600")

        self.processor = RiscVProcessor(64, 64)
        self.monitor = ProcessorMonitor(self.processor)

        self._build_ui()
        self._load_sample()

    def _build_ui(self):
        tk = self.tk
        ttk = self.ttk

        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=8, pady=8)

        self.status_var = tk.StringVar(value="Status: READY")
        ttk.Label(top, textvariable=self.status_var).pack(side=tk.LEFT)

        ttk.Button(top, text="Start", command=self._start).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Step", command=self._step).pack(side=tk.LEFT)
        ttk.Button(top, text="Reset", command=self._reset).pack(side=tk.LEFT, padx=5)

        rate = ttk.LabelFrame(self.root, text="Rates (per second)")
        rate.pack(fill=tk.X, padx=8, pady=4)
        self.cycle_rate = tk.StringVar(value="0.0")
        self.inst_rate = tk.StringVar(value="0.0")
        self.read_rate = tk.StringVar(value="0.0")
        self.write_rate = tk.StringVar(value="0.0")

        row = ttk.Frame(rate)
        row.pack(fill=tk.X, padx=6, pady=4)
        for label, var in (
            ("Cycles", self.cycle_rate),
            ("Instructions", self.inst_rate),
            ("Mem Reads", self.read_rate),
            ("Mem Writes", self.write_rate),
        ):
            box = ttk.Frame(row)
            box.pack(side=tk.LEFT, padx=10)
            ttk.Label(box, text=label).pack()
            ttk.Label(box, textvariable=var, font=("Consolas", 12, "bold")).pack()

        mid = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        mid.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        reg_frame = ttk.Labelframe(mid, text="Registers (x0..x15)")
        mem_frame = ttk.Labelframe(mid, text="Recent Memory (non-zero)")
        mid.add(reg_frame, weight=3)
        mid.add(mem_frame, weight=2)

        self.reg_labels = []
        for i in range(16):
            r = i // 4
            c = i % 4
            cell = ttk.Frame(reg_frame)
            cell.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            ttk.Label(cell, text=f"x{i}").pack()
            var = self.tk.StringVar(value="0x0000")
            ttk.Label(cell, textvariable=var, font=("Consolas", 11)).pack()
            self.reg_labels.append(var)
        for c in range(4):
            reg_frame.columnconfigure(c, weight=1)

        self.mem_text = self.tk.Text(mem_frame, height=20, font=("Consolas", 10))
        self.mem_text.pack(fill=tk.BOTH, expand=True)

    def _load_sample(self):
        # Simple sample program; safe if memory empty
        program = [
            0x5107,  # addi x1, x0, 7
            0x5205,  # addi x2, x0, 5
            0x0312,  # add x3, x1, x2
            0x9320,  # sw x3, 0(x2)
            0x8420,  # lw x4, 0(x2)
            0xF000,  # halt
        ]
        self.processor.load_program_direct(program)

    def _start(self):
        self._tick()

    def _step(self):
        if not self.processor.halted:
            self.processor.step()
            self._refresh()

    def _reset(self):
        self.processor.reset()
        self._load_sample()
        self._refresh()

    def _tick(self):
        # Run one step to produce activity, then refresh UI and schedule next
        if not self.processor.halted:
            self.processor.step()
        self._refresh()
        self.root.after(self.REFRESH_MS, self._tick)

    def _refresh(self):
        snap = self.monitor.snapshot()
        rates = self.monitor.rates(snap)
        self.cycle_rate.set(f"{rates['cycle_rate']:.1f}")
        self.inst_rate.set(f"{rates['inst_rate']:.1f}")
        self.read_rate.set(f"{rates['read_rate']:.1f}")
        self.write_rate.set(f"{rates['write_rate']:.1f}")

        status = "HALTED" if snap["halted"] else "RUNNING"
        self.status_var.set(f"Status: {status} | PC: 0x{snap['pc']:04X} | Cycles: {snap['cycles']}")

        for i, val in enumerate(snap["registers"]):
            self.reg_labels[i].set(f"0x{val:04X}")

        self._refresh_memory()

    def _refresh_memory(self):
        non_zero = self.processor.data_memory.find_non_zero()
        self.mem_text.delete("1.0", self.tk.END)
        if not non_zero:
            self.mem_text.insert(self.tk.END, "(no data)\n")
            return
        self.mem_text.insert(self.tk.END, "Address    Value   Dec\n")
        self.mem_text.insert(self.tk.END, "-" * 24 + "\n")
        for addr, value in non_zero[:50]:
            self.mem_text.insert(self.tk.END, f"0x{addr:04X}   0x{value:04X}  {value}\n")

    def run(self):
        self.root.after(self.REFRESH_MS, self._refresh)
        self.root.mainloop()


def main():
    if not _require_tk():
        return 1
    try:
        app = MonitoringDashboard()
        app.run()
        return 0
    except Exception as e:
        print(f"❌ Error starting monitoring dashboard: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())



