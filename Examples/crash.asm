main:
    addi x1, x0, 15
    addi x2, x0, 15      # x2 = 15
    addi x3, x0, 15      # x3 = 15  
    add x4, x2, x3       # x4 = 30
    add x5, x4, x4       # x5 = 60
    add x6, x5, x5       # x6 = 120
    add x7, x6, x6       # x7 = 240
    add x8, x7, x3       # x8 = 255
    addi x9, x8, 1       # x9 = 256 (BEYOND BOUNDS!)
    sw x1, 0(x9)         # Address 256+0x1000 = 0x1100 (OUT!)
    halt
