# Simple factorial calculation
main:
    addi x1, x0, 4     # n = 4
    addi x2, x0, 1     # result = 1
    
loop:
    beq x1, x0, done   # if n == 0, done
    # result = result * n (simulation με additions)
    add x3, x0, x0     # temp = 0
    add x4, x0, x2     # counter = result
    
multiply:
    beq x4, x0, mult_done
    add x3, x3, x1     # temp += n
    addi x4, x4, -1    # counter--
    bne x4, x0, multiply
    
mult_done:
    add x2, x0, x3     # result = temp
    addi x1, x1, -1    # n--
    bne x1, x0, loop
    
done:
    sw x2, 0(x0)       # Store result
    halt