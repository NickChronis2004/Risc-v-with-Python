![Python](https://img.shields.io/badge/Python-3.7+-blue)
![Lines of Code](https://img.shields.io/badge/Lines%20of%20Code-11,679-green)
![Tests](https://img.shields.io/badge/Test%20Coverage-44.5%25-orange)
![License](https://img.shields.io/badge/License-MIT-blue)


# 🚀 RISC-V 16-bit Processor Simulator System

A comprehensive, educational RISC-V processor simulator with real-time monitoring, advanced debugging capabilities, and production-ready testing framework.

## 🌟 Features

### 🔧 Core Components
- **Complete RISC-V Implementation**: 16-bit processor with full instruction set
- **Advanced ALU**: 7 operations with flags and performance tracking
- **Harvard Architecture**: Separate instruction and data memory systems
- **Register File**: 16 registers (x0-x15) with ABI name support
- **Control Unit**: Comprehensive signal generation and flow control
- **Assembler**: Full-featured ASM → binary converter with debugging

### 🎨 User Interfaces
- **Modern GUI**: Real-time visualization with CustomTkinter
- **Monitoring Dashboard**: Live performance metrics and debugging
- **Interactive CLI**: Command-line tools for development
- **Ultimate Launcher**: Mission control center for all operations

### 🧪 Testing & Validation
- **Unit Tests**: Comprehensive component testing
- **Integration Tests**: Full system validation
- **Performance Benchmarks**: Speed and efficiency analysis
- **Real-World Scenarios**: Production readiness testing
- **Educational Test Suite**: Academic use case validation

### 📊 Data Export & Logging
- **Complete System Export**: ZIP files with all source, tests, and reports
- **JSON Reports**: Detailed test results and performance metrics
- **Log Files**: Execution traces and debugging information
- **Binary Export**: Assembly programs to executable format

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.7+** (Required)
- **tkinter** (usually included with Python)
- **Optional**: customtkinter for modern GUI

### Step 1: Initial Setup
**IMPORTANT**: Always run the setup script first!

```bash
# Clone the repository
git clone <repository-url>
cd risc-v-simulator

# Run setup script (MANDATORY)
python src/setup_script.py
```

The setup script will:
- ✅ Check Python version compatibility
- ✅ Install required dependencies
- ✅ Verify system requirements
- ✅ Create necessary directories
- ✅ Initialize configuration files

### Step 2: Launch the System

#### Option A: Ultimate Launcher (Recommended)
```bash
# Navigate to src directory
cd src

# Launch mission control
python ../ultimate_launcher.py
```

#### Option B: Direct Components
```bash
# GUI only
python ultimate_launcher.py --gui

# Testing only
python ultimate_launcher.py --test

# Quick start wizard
python ultimate_launcher.py --wizard
```

## 🎛️ System Features Guide

### 1. 🧪 Testing & Validation

#### Unit Tests (Option 1)
- Tests individual components (ALU, Memory, Registers)
- Validates basic functionality
- **Usage**: Select option 1 from launcher

#### Integration Tests (Option 2)
- Tests component interactions
- Full system validation
- **Usage**: Select option 2 from launcher

#### Performance Tests (Option 3)
- Benchmarks execution speed
- Memory efficiency analysis
- **Usage**: Select option 3 from launcher

#### Real-World Scenarios (Option 4)
- Embedded system simulation
- Educational platform testing
- Research capability assessment
- **Usage**: Select option 4 from launcher

#### Ultimate Test Suite (Option 5)
- **COMPLETE** system validation
- All tests combined
- **Duration**: Several minutes
- **Usage**: Select option 5 from launcher

### 2. 🖥️ User Interfaces

#### Main GUI (Option 6)
- Visual assembly editor
- Real-time execution monitoring
- Step-by-step debugging
- **Features**:
  - 📝 Syntax highlighting
  - ⚡ Live execution
  - 🗂️ Register visualization
  - 💾 Memory browser

#### Monitoring Dashboard (Option 7)
- Performance metrics
- System monitoring
- **Real-time data**:
  - CPU cycles
  - Memory usage
  - Instruction mix
  - Branch statistics

#### GUI Test Runner (Option 8)
- Visual test execution
- Interactive test results
- Progress monitoring

### 3. 🔧 Development Tools

#### Interactive Assembler (Option 9)
**Most Popular Feature!**
```bash
# From launcher, select option 9
ASM> addi x1, x0, 10    # Load immediate
ASM> add x2, x1, x1     # Add registers
ASM> sw x2, 0(x0)       # Store to memory
ASM> halt               # Stop execution
ASM> run                # Execute program
ASM> quit               # Exit
```

**Commands**:
- `help` - Show available commands
- `example` - Show example programs
- `run` - Execute assembled program
- `load <file>` - Load assembly file
- `quit` - Exit assembler

#### Component Inspector (Option 10)
**Deep System Analysis**
1. **Register File**: View all 16 registers with ABI names
2. **ALU**: Status, flags, operation history
3. **Memory System**: Data memory contents and statistics
4. **Instruction Decoder**: Supported instruction set
5. **Control Unit**: Complete control signal table

#### Performance Profiler (Option 11)
- Execution time analysis
- Instruction throughput metrics
- Performance bottleneck identification

### 4. 📊 Reports & Data Export

#### System Report Generation (Option 12)
- **Comprehensive** system status
- Test results summary
- Performance metrics
- **Output**: JSON format report

#### Test History (Option 13)
- Previous test runs
- Historical performance data
- **Files**: `risc_v_test_report_*.json`

#### Export All Data (Option 14)
**COMPLETE SYSTEM EXPORT**
- **Output**: `risc_v_complete_export_YYYYMMDD_HHMMSS.zip`
- **Contains**:
  - ✅ All source code (`src/`)
  - ✅ Test files (`UnitTests/`)
  - ✅ Generated reports (`.json`)
  - ✅ Documentation (`README.md`, `LICENSE`)
  - ✅ Configuration files

## 📁 Working Directory Structure

**IMPORTANT**: Always work from the correct directory!

```
risc-v-simulator/
├── src/                          # 📍 START HERE
│   ├── MainCPU.py               # Core processor
│   ├── ALU.py                   # Arithmetic unit
│   ├── Memory.py                # Memory system
│   ├── Assembler.py             # Assembly compiler
│   ├── interface.py             # Main GUI
│   ├── setup_script.py          # 🚨 RUN FIRST
│   └── UnitTests/               # Test suite
├── ultimate_launcher.py         # Mission control
├── Examples/                    # Sample programs
├── Documentation/              # Technical docs
└── logs/                       # Generated log files
```

### Proper Usage Pattern:
```bash
# 1. Setup (one time only)
python src/setup_script.py

# 2. Navigate to src
cd src

# 3. Launch system
python ../ultimate_launcher.py
```

## 📊 Log Files & Data Export

### Automatic Log Generation
The system automatically creates various log files:

#### Test Reports
- **Location**: Current directory and `src/UnitTests/`
- **Format**: `risc_v_test_report_YYYYMMDD_HHMMSS.json`
- **Contains**: Test results, timing, pass/fail status

#### Real-World Assessments
- **Format**: `risc_v_real_world_assessment_YYYYMMDD_HHMMSS.json`
- **Contains**: Production readiness metrics

#### Execution Logs
- **Location**: `logs/` directory
- **Contains**: Detailed execution traces, debug information

#### Complete System Export
- **Trigger**: Option 14 from launcher
- **Format**: `risc_v_complete_export_YYYYMMDD_HHMMSS.zip`
- **Size**: Complete project backup

### Manual Data Export
```bash
# From launcher
🚀 Select mission (1-15): 14

# System will create:
✅ Complete export saved: risc_v_complete_export_20250707_210000.zip
```

## 🎮 Quick Start Examples

### Example 1: First Program
```bash
# 1. Launch system
cd src
python ../ultimate_launcher.py

# 2. Select Interactive Assembler (option 9)
🚀 Select mission (1-15): 9

# 3. Write simple program
ASM> addi x1, x0, 10     # x1 = 10
ASM> addi x2, x0, 5      # x2 = 5
ASM> add x3, x1, x2      # x3 = 15
ASM> halt                # Stop
ASM> run                 # Execute

# 4. View results in registers
```

### Example 2: System Analysis
```bash
# 1. Launch Component Inspector (option 10)
🚀 Select mission (1-15): 10

# 2. Explore components
Select component (1-6): 1    # View registers
Select component (1-6): 2    # View ALU status
Select component (1-6): 3    # View memory
```

### Example 3: Performance Testing
```bash
# 1. Run Performance Tests (option 3)
🚀 Select mission (1-15): 3

# 2. View results
# System shows: Instructions/second, cycles/second

# 3. Export data for analysis (option 14)
🚀 Select mission (1-15): 14
```

## 🛠️ Advanced Usage

### Custom Assembly Programs
Create `.asm` files in the project directory:

```assembly
# fibonacci.asm
main:
    addi x1, x0, 1      # x1 = 1 (first fib)
    addi x2, x0, 1      # x2 = 1 (second fib)
    addi x3, x0, 8      # x3 = 8 (counter)
    
loop:
    beq x3, x0, done    # if counter == 0, exit
    add x4, x1, x2      # x4 = x1 + x2 (next fib)
    add x1, x2, x0      # x1 = x2
    add x2, x4, x0      # x2 = x4
    addi x3, x3, -1     # counter--
    bne x3, x0, loop    # continue loop
    
done:
    sw x2, 0(x0)        # store result
    halt
```

### Load and Run Custom Programs
```bash
# In Interactive Assembler
ASM> load fibonacci.asm
ASM> run
```

### Comprehensive Testing
```bash
# Run complete validation
🚀 Select mission (1-15): 5

# Duration: Several minutes
# Tests: Unit, Integration, Performance, Real-World
```

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. "Module not found" errors
```bash
# Solution: Run from correct directory
cd src
python ../ultimate_launcher.py
```

#### 2. Setup script not run
```bash
# Solution: Always run setup first
python src/setup_script.py
```

#### 3. GUI doesn't start
```bash
# Check tkinter installation
python -c "import tkinter"

# Install if missing (Ubuntu/Debian)
sudo apt-get install python3-tkinter
```

#### 4. Tests fail with path errors
```bash
# Ensure you're in src directory
pwd  # Should end with /src
```

#### 5. Permission errors
```bash
# Make launcher executable
chmod +x ultimate_launcher.py
```

### Debug Mode
```bash
# Enable verbose output
export RISC_V_DEBUG=1
python ultimate_launcher.py
```

## 📚 Educational Resources

### Learning Path
1. **Start with Component Inspector** (Option 10)
   - Understand system architecture
   - See instruction set
   - Explore register file

2. **Try Interactive Assembler** (Option 9)
   - Write simple programs
   - Learn RISC-V instructions
   - Debug step-by-step

3. **Run Performance Tests** (Option 3)
   - Understand system capabilities
   - See execution metrics

4. **Export and Analyze Data** (Option 14)
   - Study generated reports
   - Analyze performance logs

### Sample Assignments
```assembly
# Assignment 1: Basic Operations
addi x1, x0, 15
addi x2, x0, 7
add x3, x1, x2      # Addition
sub x4, x1, x2      # Subtraction
and x5, x1, x2      # Bitwise AND
halt

# Assignment 2: Memory Operations
addi x1, x0, 42
sw x1, 0(x0)        # Store to memory
lw x2, 0(x0)        # Load from memory
add x3, x1, x2      # Use loaded data
halt

# Assignment 3: Control Flow
addi x1, x0, 5      # Counter
addi x2, x0, 0      # Accumulator
loop:
    beq x1, x0, done
    add x2, x2, x1
    addi x1, x1, -1
    bne x1, x0, loop
done:
    halt
```

## 🎯 Supported Instructions

### Complete Instruction Set

| Type | Instruction | Format | Description |
|------|-------------|--------|-------------|
| **R-Type** | ADD | `add rd, rs1, rs2` | rd = rs1 + rs2 |
| | SUB | `sub rd, rs1, rs2` | rd = rs1 - rs2 |
| | AND | `and rd, rs1, rs2` | rd = rs1 & rs2 |
| | OR | `or rd, rs1, rs2` | rd = rs1 \| rs2 |
| | XOR | `xor rd, rs1, rs2` | rd = rs1 ^ rs2 |
| **I-Type** | ADDI | `addi rd, rs1, imm` | rd = rs1 + imm |
| | ANDI | `andi rd, rs1, imm` | rd = rs1 & imm |
| | ORI | `ori rd, rs1, imm` | rd = rs1 \| imm |
| | LW | `lw rd, offset(rs1)` | rd = memory[rs1 + offset] |
| **S-Type** | SW | `sw rs2, offset(rs1)` | memory[rs1 + offset] = rs2 |
| **B-Type** | BEQ | `beq rs1, rs2, offset` | if (rs1 == rs2) PC += offset |
| | BNE | `bne rs1, rs2, offset` | if (rs1 != rs2) PC += offset |
| **J-Type** | JAL | `jal rd, offset` | rd = PC + 1; PC += offset |
| **Special** | NOP | `nop` | No operation |
| | HALT | `halt` | Stop execution |

## 📊 Performance Metrics

### Benchmark Results (Typical System)
- **Execution Speed**: 225,000+ instructions/second
- **Memory Throughput**: 100,000+ operations/second  
- **Assembly Speed**: 20,000+ lines/second
- **Test Suite**: 4/5 test categories pass (>80%)

### System Capabilities
- **Max Program Size**: 1024 instructions
- **Data Memory**: 1024 words
- **Register File**: 16 × 16-bit registers
- **Address Space**: 16-bit (64KB)

## 🔐 Data Security & Export

### Exported Data Contents
When you select "Export All Data" (Option 14):

```
risc_v_complete_export_YYYYMMDD_HHMMSS.zip
├── source/                 # All .py source files
├── tests/                  # Complete test suite
├── reports/                # All .json reports
├── README.md              # This documentation
└── LICENSE                # License information
```

### Safe Data Handling
- ✅ No personal data collected
- ✅ All data stored locally
- ✅ Complete source code included
- ✅ Portable project format

## 🚀 Command Reference

### Ultimate Launcher Commands
```bash
python ultimate_launcher.py           # Full interactive mode
python ultimate_launcher.py --gui     # GUI only
python ultimate_launcher.py --test    # Quick test
python ultimate_launcher.py --wizard  # Setup wizard
python ultimate_launcher.py --help    # Show help
```

### Interactive Assembler Commands
```
help        # Show command help
example     # Show example programs  
run         # Execute current program
load <file> # Load assembly file
quit        # Exit assembler
```

## 📞 Support & Documentation

### Getting Help
1. **Interactive Help**: Use `help` commands in each tool
2. **System Check**: Run setup script for diagnostics
3. **Debug Mode**: Set `RISC_V_DEBUG=1` for verbose output
4. **Component Inspector**: Use Option 10 for system analysis

### Documentation Structure
- **README.md** (this file) - Complete user guide
- **Documentation/modules/** - Technical API reference
- **Examples/** - Sample programs and use cases

---

## 🎉 Quick Reference Card

### Essential Commands
```bash
# 1. First-time setup
python src/setup_script.py

# 2. Navigate to working directory  
cd src

# 3. Launch system
python ../ultimate_launcher.py

# 4. Most popular options:
#    Option 9: Interactive Assembler
#    Option 10: Component Inspector  
#    Option 14: Export All Data
```

### Key Features
- 🚀 **Complete RISC-V Simulation**
- 🔧 **Interactive Development Tools**  
- 📊 **Comprehensive Testing Framework**
- 💾 **Complete Data Export**
- 🎓 **Educational Resources**


## 🤝 Contributing and Communication

This project is open source and welcomes contributions from the community! 

### How to Contribute
- 🐛 **Report bugs** - Found an issue? Let us know!
- 💡 **Suggest features** - Have an idea? We'd love to hear it!
- 🛠️ **Submit pull requests** - Ready to contribute code?
- 📚 **Improve documentation** - Help make this project more accessible

### Get in Touch
For questions, suggestions, or collaboration opportunities:
**Contact:** nickchronis2004@example.com

**Happy Coding! Welcome to RISC-V simulation!** 🚀
