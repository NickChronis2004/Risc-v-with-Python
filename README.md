
# 🖥️ RISC-V 16-bit Processor GUI Simulator

Ένα πλήρες desktop GUI application για τον RISC-V 16-bit simulator σου με real-time visualization!

## ✨ Features

- **📝 Code Editor**: Syntax highlighting για assembly code
- **🗂️ Register File Viewer**: Real-time εμφάνιση όλων των registers
- **💾 Memory Viewer**: Visualisation του data memory  
- **⚙️ ALU Status**: Live εμφάνιση ALU flags και αποτελεσμάτων
- **🕒 Execution Trace**: Step-by-step ιστορικό εκτέλεσης
- **📺 Console Output**: Logging και error messages
- **🎮 Interactive Controls**: Assemble, Run, Step, Reset
- **💾 File Operations**: Load/Save assembly αρχείων
- **⚡ Speed Control**: Ρύθμιση ταχύτητας εκτέλεσης

## 🚀 Εγκατάσταση

### Βήμα 1: Προετοιμασία
Βεβαιώσου ότι έχεις όλα τα RISC-V αρχεία στον ίδιο φάκελο:
```
ALU.py
RegisterFile.py
Memory.py
InstructionDecoder.py
ControlUnit.py
Assembler.py
MainCPU.py
ExceptionHandling.py
```

### Βήμα 2: Εγκατάσταση Dependencies
```bash
# Αυτόματη εγκατάσταση
python setup_risc_v_gui.py

# Ή χειροκίνητα
pip install customtkinter pillow
```

### Βήμα 3: Εκτέλεση
```bash
python RiscV_GUI.py

# Ή χρησιμοποίησε το launcher script
./run_risc_v_gui.sh      # Linux/Mac
run_risc_v_gui.bat       # Windows
```

## 📖 Χρήση

### Βασική Χρήση
1. **Γράψε Assembly Code** στο αριστερό panel
2. **Click "🔧 Assemble"** για να μετατρέψεις σε machine code
3. **Click "▶️ Run"** για συνεχή εκτέλεση ή "👆 Step" για βήμα-προς-βήμα
4. **Παρακολούθησε** τα registers, memory, και ALU status σε real-time

### Παράδειγμα Κώδικα
```assembly
# Απλή αριθμητική και memory operations
addi x1, x0, 10    # x1 = 10
addi x2, x0, 5     # x2 = 5
add x3, x1, x2     # x3 = x1 + x2 = 15
sw x3, 0(x0)       # Store x3 to memory[0]
lw x4, 0(x0)       # Load memory[0] to x4
beq x3, x4, equal  # Branch if equal
addi x5, x0, 1     # Should be skipped
equal:
addi x6, x0, 100   # x6 = 100
halt               # Stop execution
```

### Controls

| Button | Λειτουργία |
|--------|------------|
| 🔧 Assemble | Μετατρέπει assembly σε machine code |
| ▶️ Run | Συνεχής εκτέλεση (γίνεται ⏹️ Stop όταν τρέχει) |
| 👆 Step | Εκτέλεση μίας εντολής |
| 🔄 Reset | Επαναφορά processor στην αρχική κατάσταση |
| 📁 Load | Φόρτωση assembly αρχείου |
| 💾 Save | Αποθήκευση assembly αρχείου |

### Speed Control
Χρησιμοποίησε το slider για να ρυθμίσεις την ταχύτητα εκτέλεσης (1 = αργό, 10 = γρήγορο)

## 🎨 Interface Περιοχές

### 📝 Code Editor (Αριστερά)
- Assembly code editor με syntax highlighting
- Line numbers και scrollbars
- Load/Save αρχείων
- Control buttons

### 🗂️ Register File (Πάνω δεξιά)
- Εμφάνιση όλων των 16 registers (x0-x15)
- ABI names (zero, ra, sp, etc.)
- Hex και decimal values
- Highlight όταν αλλάζουν

### 💾 Data Memory (Μέσα δεξιά)
- Εμφάνιση non-zero memory locations
- Address και value σε hex/decimal
- Auto-update κατά την εκτέλεση

### ⚙️ ALU Status (Κάτω δεξιά)
- Last result
- Zero Flag
- Overflow Flag  
- Negative Flag
- Real-time updates

### 📺 Console (Κάτω αριστερά)
- Success/Error/Warning messages
- Timestamp για κάθε message
- Auto-scroll
- Color-coded messages

### 🕒 Execution Trace (Κάτω δεξιά)
- Cycle-by-cycle execution history
- PC, Instruction, Assembly για κάθε step
- Auto-scroll
- Full execution path

## 🛠️ Troubleshooting

### CustomTkinter Issues
```bash
# Αν έχεις πρόβλημα με CustomTkinter
pip uninstall customtkinter
pip install customtkinter

# Ή χρησιμοποίησε specific version
pip install customtkinter==5.2.0
```

### Tkinter Missing (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tkinter

# CentOS/RHEL
sudo yum install tkinter
```

### Import Errors
Βεβαιώσου ότι όλα τα RISC-V αρχεία είναι στον ίδιο φάκελο με το `RiscV_GUI.py`

## 🔧 Customization

### Themes
Μπορείς να αλλάξεις το theme στην αρχή του `RiscV_GUI.py`:
```python
ctk.set_appearance_mode("dark")    # "dark" ή "light"
ctk.set_default_color_theme("blue") # "blue", "green", "dark-blue"
```

### Window Size
```python
self.root.geometry("1400x900")  # Αλλαξε το μέγεθος
```

### Colors
Μπορείς να customάρεις τα χρώματα στα color dictionaries μέσα στον κώδικα.

## 📚 Υποστηριζόμενες Εντολές

### R-Type (Register-Register)
- `ADD rd, rs1, rs2` - Πρόσθεση
- `SUB rd, rs1, rs2` - Αφαίρεση  
- `AND rd, rs1, rs2` - Λογικό AND
- `OR rd, rs1, rs2` - Λογικό OR
- `XOR rd, rs1, rs2` - Λογικό XOR

### I-Type (Immediate)
- `ADDI rd, rs1, imm` - Πρόσθεση με immediate
- `ANDI rd, rs1, imm` - AND με immediate
- `ORI rd, rs1, imm` - OR με immediate
- `LW rd, offset(rs1)` - Load word

### S-Type (Store)
- `SW rs2, offset(rs1)` - Store word

### B-Type (Branch)
- `BEQ rs1, rs2, offset` - Branch if equal
- `BNE rs1, rs2, offset` - Branch if not equal

### J-Type (Jump)
- `JAL rd, offset` - Jump and link

### Special
- `NOP` - No operation
- `HALT` - Stop execution

## 🎯 ABI Register Names

| Register | ABI Name | Purpose |
|----------|----------|---------|
| x0 | zero | Hard-wired zero |
| x1 | ra | Return address |
| x2 | sp | Stack pointer |
| x3 | gp | Global pointer |
| x4 | tp | Thread pointer |
| x5 | t0 | Temporary 0 |
| x6 | t1 | Temporary 1 |
| x7 | t2 | Temporary 2 |
| x8 | s0 | Saved 0 / Frame pointer |
| x9 | s1 | Saved 1 |
| x10 | a0 | Argument 0 / Return value 0 |
| x11 | a1 | Argument 1 / Return value 1 |
| x12 | a2 | Argument 2 |
| x13 | a3 | Argument 3 |
| x14 | a4 | Argument 4 |
| x15 | a7 | System call number |

## 🐛 Αναφορά Bugs

Αν βρεις κάποιο bug ή έχεις suggestions:
1. Έλεγξε το console output για error messages
2. Βεβαιώσου ότι ο assembly κώδικας είναι σωστός
3. Try reset και assemble ξανά

## 🎉 Features που έρχονται

- [ ] Syntax highlighting στον code editor
- [ ] Breakpoints support
- [ ] Memory editor
- [ ] Performance profiling
- [ ] Dark/Light theme toggle
- [ ] Export execution trace
- [ ] More example programs
- [ ] Tutorial mode

## 📄 License

Αυτό το project είναι για εκπαιδευτικούς σκοπούς.

---

**Enjoy coding in RISC-V assembly! 🚀**# Risc-v-with-Python