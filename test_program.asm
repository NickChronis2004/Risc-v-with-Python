# Test program
main:
    addi x1, x0, 10    # x1 = 10
    addi x2, x0, 5     # x2 = 5
    add x3, x1, x2     # x3 = x1 + x2
    sub x4, x1, x2     # x4 = x1 - x2
    beq x3, x4, end    # if x3 == x4 goto end
    nop                # no operation
end:
    halt               # stop
