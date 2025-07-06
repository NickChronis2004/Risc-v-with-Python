# Simple Factorial Program
# Calculate 3! = 3 * 2 * 1 = 6

main:
    # Initialize
    addi x1, x0, 3      # n = 3
    addi x2, x0, 1      # result = 1
    
    # First multiplication: result = result * 3 = 1 * 3 = 3
    add x3, x0, x0      # temp = 0
    add x4, x0, x2      # counter = result (1)
    
loop1:
    beq x4, x0, done1   # if counter == 0, done
    add x3, x3, x1      # temp += n (3)
    addi x4, x4, -1     # counter--
    bne x4, x0, loop1   # continue
    
done1:
    add x2, x0, x3      # result = temp (3)
    addi x1, x1, -1     # n = 2
    
    # Second multiplication: result = result * 2 = 3 * 2 = 6  
    add x3, x0, x0      # temp = 0
    add x4, x0, x2      # counter = result (3)
    
loop2:
    beq x4, x0, done2   # if counter == 0, done
    add x3, x3, x1      # temp += n (2)
    addi x4, x4, -1     # counter--
    bne x4, x0, loop2   # continue
    
done2:
    add x2, x0, x3      # result = temp (6)
    addi x1, x1, -1     # n = 1
    
    # Store result in memory
    sw x2, 0(x0)        # Store 6 at memory[0]
    lw x5, 0(x0)        # Load back to x5
    
    # Final calculations
    add x6, x5, x5      # x6 = result * 2 = 12
    addi x7, x5, 1      # x7 = result + 1 = 7
    
    halt                # Done!
