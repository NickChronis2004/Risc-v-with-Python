
# File: src/examples/branch_test.asm
# Απλό test για branches

main:
    addi x1, x0, 10     # x1 = 10
    addi x2, x0, 5      # x2 = 5
    
    # Test 1: BEQ (Branch if Equal)
    beq x1, x2, equal   # Won't branch (10 != 5)
    sw x1, 0(x0)        # Print 10 (this will execute)
    
    # Test 2: BNE (Branch if Not Equal)  
    bne x1, x2, not_equal # Will branch (10 != 5)
    sw x2, 0(x0)        # Print 5 (this will be SKIPPED)
    
equal:
    # This won't execute
    addi x3, x0, 99
    sw x3, 0(x0)        # Won't print 99
    
not_equal:
    # This will execute
    add x3, x1, x2      # x3 = 10 + 5 = 15
    sw x3, 0(x0)        # Print 15
    
    halt