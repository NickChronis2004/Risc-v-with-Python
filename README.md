![Python](https://img.shields.io/badge/Python-3.7+-blue)
![Lines of Code](https://img.shields.io/badge/Lines%20of%20Code-~3k-green)
![Tests](https://img.shields.io/badge/Tests-34%20passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

# RISC-V 16-bit Processor Simulator

An educational RISC-V processor simulator implemented in Python. Simulates a 16-bit Harvard-architecture CPU with a two-pass assembler, full instruction execution, and an interactive GUI.

## Features

### Core Components

- **Complete 16-bit CPU**: Fetch → Decode → Execute pipeline in software
- **Two-Pass Assembler**: Converts `.asm` source to 16-bit machine code, with binary (`.bin`) and hex (`.hex`) output
- **ALU**: 7 operations — ADD, SUB, AND, OR, XOR, EQ, NE — with zero/overflow/negative flags
- **Harvard Architecture**: Separate instruction memory (0x0000–0x03FF) and data memory (0x1000–0x13FF)
- **Register File**: 16 registers (x0–x15) with ABI name aliases; x0 is hardwired to 0
- **Control Unit**: Lookup-table-based control signal generation
- **Instruction Decoder**: Binary → structured decode for all instruction types
- **Exception Handling**: Configurable strict/graceful fault modes

### User Interfaces

- **GUI** (`src/interface.py`): Real-time register and memory visualization with step-by-step debugging
- **Monitoring Dashboard** (`src/monitoring_dashboard.py`): Live performance metrics
- **Ultimate Launcher** (`ultimate_launcher.py`): Menu-driven entry point for all features

### Testing

- **34 unit tests** across ALU, Memory, RegisterFile, and Assembler — all passing
- Integration tests, performance benchmarks, and real-world scenarios

## Project Structure

```
risc-v-with-python/
├── ultimate_launcher.py        # Main entry point
├── src/
│   ├── MainCPU.py              # Top-level RiscVProcessor (integrates all components)
│   ├── ALU.py                  # Arithmetic Logic Unit
│   ├── RegisterFile.py         # 16-register file
│   ├── Memory.py               # InstructionMemory + DataMemory
│   ├── InstructionDecoder.py   # Binary → structured decode
│   ├── ControlUnit.py          # Control signal generation
│   ├── Assembler.py            # Two-pass assembler + BinaryLoader
│   ├── LoggedMainCPU.py        # CPU with execution logging
│   ├── ExceptionHandling.py    # Fault tolerance modes
│   ├── SimpleLogging.py        # Logging utilities
│   ├── ExecutionScript.py      # Batch execution helper
│   ├── interface.py            # Tkinter/CustomTkinter GUI
│   ├── monitoring_dashboard.py # Performance dashboard
│   ├── gui_test_scenarios.py   # GUI test scenarios
│   ├── setup_script.py         # Optional dependency installer
│   └── UnitTests/
│       ├── ALU_tests.py        # 8 ALU tests
│       ├── Memory_tests.py     # 9 Memory tests
│       ├── RF_Tests.py         # 8 RegisterFile tests
│       ├── AssemblerTest.py    # 9 Assembler tests
│       ├── GUItest.py
│       ├── master_test_runner.py
│       ├── real_world_scenarios.py
│       ├── ultimate_test_suite.py
│       └── test_utils.py
├── Examples/                   # Sample .asm programs
└── Documentation/              # PDF module references
```

## Installation & Setup

**Prerequisites:** Python 3.7+, `tkinter` (bundled with most Python distributions)

```bash
git clone <repository-url>
cd risc-v-with-python

# Optional: install customtkinter for the modern GUI theme
python src/setup_script.py
```

## Running the System

Launch from the project root:

```bash
python ultimate_launcher.py
```

This opens an interactive menu with options for testing, GUI, assembler, component inspection, and data export.

### Common Options

| Option | Description                                       |
|--------|---------------------------------------------------|
| 1      | Unit tests (ALU, Memory, RegisterFile, Assembler) |
| 2      | Integration tests                                 |
| 3      | Performance benchmarks                            |
| 5      | Full test suite                                   |
| 6      | Main GUI                                          |
| 7      | Monitoring dashboard                              |
| 9      | Interactive assembler (REPL)                      |
| 10     | Component inspector                               |
| 14     | Export all data as ZIP                            |

### Command-Line Flags

```bash
python ultimate_launcher.py --gui     # Launch GUI directly
python ultimate_launcher.py --test    # Run quick tests
python ultimate_launcher.py --wizard  # Setup wizard
python ultimate_launcher.py --help    # Show help
```

## Interactive Assembler

Select option 9 from the launcher, then type assembly instructions line by line:

```
ASM> addi x1, x0, 10    # x1 = 10
ASM> addi x2, x0, 5     # x2 = 5
ASM> add x3, x1, x2     # x3 = 15
ASM> sw x3, 0(x0)       # store x3 to data memory
ASM> halt
ASM> run
ASM> quit
```

**Commands:** `help`, `example`, `run`, `load <file>`, `quit`

## Instruction Set

| Type | Mnemonic   | Format                | Operation                             |
|------|------------|-----------------------|---------------------------------------|
| R    | ADD        | `add rd, rs1, rs2`    | rd = rs1 + rs2                        |
| R    | SUB        | `sub rd, rs1, rs2`    | rd = rs1 − rs2                        |
| R    | AND        | `and rd, rs1, rs2`    | rd = rs1 & rs2                        |
| R    | OR         | `or rd, rs1, rs2`     | rd = rs1 \| rs2                       |
| R    | XOR        | `xor rd, rs1, rs2`    | rd = rs1 ^ rs2                        |
| I    | ADDI       | `addi rd, rs1, imm`   | rd = rs1 + imm (imm: 0–15)            |
| I    | ADDI (neg) | `addi rd, rs1, -imm`  | rd = rs1 − imm (assembler emits SUBI) |
| I    | ANDI       | `andi rd, rs1, imm`   | rd = rs1 & imm                        |
| I    | ORI        | `ori rd, rs1, imm`    | rd = rs1 \| imm                       |
| I    | LW         | `lw rd, offset(rs1)`  | rd = DataMem[rs1 + offset]            |
| S    | SW         | `sw rs2, offset(rs1)` | DataMem[rs1 + offset] = rs2           |
| B    | BEQ        | `beq rs1, rs2, label` | if rs1 == rs2: PC = label             |
| B    | BNE        | `bne rs1, rs2, label` | if rs1 != rs2: PC = label             |
| J    | JAL        | `jal rd, label`       | rd = PC+1; PC = label                 |
| —    | NOP        | `nop`                 | no operation                          |
| —    | HALT       | `halt`                | stop execution                        |

**Encoding:** all instructions are 16 bits — 4-bit opcode + 12-bit fields.

**Registers:** x0–x15; ABI aliases supported (`zero`, `ra`, `sp`, `gp`, `tp`, `t0`–`t2`, `s0`–`s1`, `a0`–`a3`, `a4`, `a7`).

**Memory:** data memory is mapped at base address `0x1000`. `sw x1, 0(x0)` writes to address `0x1000`.

### Negative ADDI

`addi x1, x1, -1` is valid syntax. The assembler converts it to the internal `SUBI` pseudo-instruction (opcode `0xD`), which the control unit executes as a subtraction. The magnitude must be 1–15.

## Example Programs

### Loop Counter (countdown from 3)

```assembly
    addi x1, x0, 3     # x1 = 3
loop:
    addi x1, x1, -1    # x1 = x1 - 1
    bne x1, x0, loop   # repeat while x1 != 0
    halt
```

### Store and Load

```assembly
    addi x1, x0, 42    # x1 = 42
    sw x1, 0(x0)       # DataMem[0x1000] = 42
    lw x2, 0(x0)       # x2 = DataMem[0x1000]
    halt
```

### Fibonacci (result in x2)

```assembly
main:
    addi x1, x0, 1      # x1 = 1 (fib n-1)
    addi x2, x0, 1      # x2 = 1 (fib n)
    addi x3, x0, 6      # x3 = 6 (iterations left)

loop:
    beq x3, x0, done
    add x4, x1, x2      # x4 = next fib
    add x1, x2, x0      # x1 = x2
    add x2, x4, x0      # x2 = x4
    addi x3, x3, -1     # x3--
    bne x3, x0, loop

done:
    sw x2, 0(x0)
    halt
```

## Running Tests

```bash
cd src/UnitTests
python ALU_tests.py
python Memory_tests.py
python RF_Tests.py
python AssemblerTest.py
```

Or run all suites from the launcher (option 5).

## Architecture Notes

### Instruction Encoding (16-bit)

```
R-type:  [opcode 4][rd 4][rs1 4][rs2 4]
I-type:  [opcode 4][rd 4][rs1 4][imm 4]
S-type:  [opcode 4][rs2 4][rs1 4][offset 4]
B-type:  [opcode 4][rs1 4][rs2 4][offset 4]
J-type:  [opcode 4][rd 4][offset 8]
Special: [opcode 4][000 12]
```

### Branch Offset

`beq/bne` encode `offset = target_addr − current_addr` as a signed 4-bit value (−8 to +7). The assembler calculates this automatically from labels.

### Memory Map

| Region      | Range                 | Description           |
|-------------|-----------------------|-----------------------|
| Instruction | `0x0000`–`0x03FF`     | Up to 1024 words      |
| Data        | `0x1000`–`0x13FF`     | 1024 data words       |

LW/SW addresses are computed as `rs1 + offset`, then mapped into data memory. Accessing outside `0x1000`–`0x13FF` logs a warning and returns 0.

## Performance

Running on CPython 3.x:

- ~225,000 simulated instructions/sec
- ~500,000 data memory operations/sec
- CPI = 1.0 (one clock cycle per instruction, no pipeline)

## Limitations

This is an educational simulator, not a production RISC-V implementation:

| Feature        | This simulator                         | Full RISC-V          |
|----------------|----------------------------------------|----------------------|
| Bit width      | 16-bit                                 | 32/64-bit            |
| Registers      | 16 (x0–x15)                            | 32 (x0–x31)          |
| Immediates     | 4-bit unsigned (ADDI: signed via SUBI) | 12-bit signed        |
| Floating point | No                                     | Yes (F/D extensions) |
| Virtual memory | No                                     | Yes                  |
| Interrupts     | No                                     | Yes                  |
| System calls   | No                                     | Yes                  |
| Pipeline       | No                                     | Yes (hardware)       |
| Compressed ISA | No                                     | Yes (C extension)    |

## Troubleshooting

**"Module not found" errors** — run the launcher from the project root, not from inside `src/`:

```bash
# Correct
python ultimate_launcher.py

# Wrong
cd src && python ../ultimate_launcher.py
```

**GUI won't start** — check tkinter is available:

```bash
python -c "import tkinter; print('ok')"
```

**Tests fail with import errors** — run tests from `src/UnitTests/`, not from `src/`:

```bash
cd src/UnitTests && python AssemblerTest.py
```

## Contributing

Bug reports, feature suggestions, and pull requests are welcome.

**Contact:** [nickchronis2004@gmail.com](mailto:nickchronis2004@gmail.com)

---

*Educational tool for computer architecture courses. For production RISC-V work, see [RARS](https://github.com/TheThirdOne/rars) or [Spike](https://github.com/riscv-software-src/riscv-isa-sim).*
