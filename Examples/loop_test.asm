# File: src/examples/loop_test.asm
# Απλούστατο loop χωρίς πολυπλοκότητα

main:
    addi x1, x0, 1      # x1 = 1
    sw x1, 0(x0)        # Print 1
    
    addi x1, x0, 2      # x1 = 2  
    sw x1, 0(x0)        # Print 2
    
    addi x1, x0, 3      # x1 = 3
    sw x1, 0(x0)        # Print 3
    
    addi x1, x0, 4      # x1 = 4
    sw x1, 0(x0)        # Print 4
    
    addi x1, x0, 5      # x1 = 5
    sw x1, 0(x0)        # Print 5
    
    addi x1, x0, 15     # x1 = sum (1+2+3+4+5 = 15)
    sw x1, 0(x0)        # Print sum
    
    halt