# File: src/examples/calculator.asm
# Απλό calculator με hardcoded values

main:
    # Βάλε τιμές
    addi x1, x0, 12     # x1 = 12
    addi x2, x0, 5      # x2 = 5
    
    # Υπολογισμοί
    add x3, x1, x2      # x3 = 12 + 5 = 17
    sub x4, x1, x2      # x4 = 12 - 5 = 7
    and x5, x1, x2      # x5 = 12 & 5 = 4
    or x6, x1, x2       # x6 = 12 | 5 = 13
    
    # Εκτύπωση αποτελεσμάτων
    sw x1, 0(x0)        # Print 12
    sw x2, 0(x0)        # Print 5
    sw x3, 0(x0)        # Print 17 (άθροισμα)
    sw x4, 0(x0)        # Print 7 (διαφορά)
    sw x5, 0(x0)        # Print 4 (AND)
    sw x6, 0(x0)        # Print 13 (OR)
    
    halt