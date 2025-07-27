
            # Pipeline test
            main:
                addi x1, x0, 7
                addi x2, x0, 3
                
            loop:
                beq x1, x0, done
                add x3, x3, x2
                addi x1, x1, -1     # Using -1 as 15 in 4-bit
                bne x1, x0, loop
                
            done:
                sw x3, 5(x0)
                halt
            