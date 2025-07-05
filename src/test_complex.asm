
# Complex test program  
main:
    addi x1, x0, 5      # x1 = 5
    addi x2, x0, -1     # x2 = -1 (should become 0xF)
    add x3, x1, x2      # x3 = 5 + (-1) = 4
    sw x3, 0(x0)        # Store x3 to memory[0]
    lw x4, 0(x0)        # Load from memory[0] to x4
    beq x3, x4, equal   # Branch if equal (should branch)
    nop                 # Should be skipped
equal:
    halt                # Stop execution