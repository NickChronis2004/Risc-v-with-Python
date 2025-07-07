# My first custom program  
main:
    addi x1, x0, 8      # x1 = 8
    addi x2, x0, 3      # x2 = 3
    
    # Calculate x1 * x2 manually (8 * 3 = 24)
    add x3, x3, x1      # x3 = 8
    add x3, x3, x1      # x3 = 16  
    add x3, x3, x1      # x3 = 24
    
    sw x3, 0(x0)        # store result (24) to memory
    lw x4, 0(x0)        # load back to verify
    halt                # stop execution