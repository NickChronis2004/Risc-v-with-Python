# File: src/examples/print_test.asm
# Απλό print test με διεύθυνση 0x1000 (offset 0)

main:
    # Test 1: Print 5
    addi x1, x0, 5
    sw x1, 0(x0)          # Print 5 (0x1000 + 0 = 0x1000 = magic address!)
    
    # Test 2: Print 7
    addi x2, x0, 7
    sw x2, 0(x0)          # Print 7
    
    # Test 3: Print άθροισμα 5+7=12
    add x3, x1, x2          # x3 = 5 + 7 = 12
    sw x3, 0(x0)          # Print 12
    
    # Test 4: Print διαφορά 12-5=7
    sub x4, x3, x1          # x4 = 12 - 5 = 7
    sw x4, 0(x0)          # Print 7
    
    # Τέλος
    halt