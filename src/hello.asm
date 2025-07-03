
# Simple RISC-V Assembly Program
# Calculates factorial of 4 and stores results

# Program: Calculate 4! = 4 * 3 * 2 * 1 = 24
# Uses loops, branches, memory operations

main:
    # Initialize variables
    addi x1, x0, 4      # n = 4 (number to calculate factorial)
    addi x2, x0, 1      # result = 1 (accumulator)
    addi x3, x0, 0      # counter for memory addresses
    
    # Store initial values in memory for debugging
    sw x1, 0(x3)        # Store n at memory[0]
    sw x2, 1(x3)        # Store initial result at memory[1]

factorial_loop:
    # Check if n == 0 (end condition)
    beq x1, x0, done    # if n == 0, goto done
    
    # Multiply result by n (simulate with repeated addition)
    add x4, x0, x0      # temp = 0 (for multiplication)
    add x5, x0, x2      # copy of result for inner loop
    
multiply_loop:
    beq x5, x0, multiply_done  # if counter == 0, multiplication done
    add x4, x4, x1             # temp += n
    addi x5, x5, -1            # counter--
    bne x5, x0, multiply_loop  # continue if counter != 0
    
multiply_done:
    add x2, x0, x4      # result = temp
    addi x1, x1, -1     # n--
    
    # Store intermediate result
    addi x3, x3, 2      # next memory address
    sw x2, 0(x3)        # store current result
    
    bne x1, x0, factorial_loop  # continue if n != 0

done:
    # Store final result at special location
    addi x6, x0, 15     # memory address 15 (0xF)
    sw x2, 0(x6)        # store final result at memory[15]
    
    # Load it back to verify
    lw x7, 0(x6)        # x7 = final result
    
    # Some final calculations for demonstration
    add x8, x7, x7      # x8 = result * 2
    addi x9, x7, 1      # x9 = result + 1
    
    halt                # End program