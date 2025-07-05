import Assembler
from Assembler import RiscVAssembler

assembler = RiscVAssembler()
machine_code = assembler.assemble_file('test_complex.asm')
assembler.display_results()