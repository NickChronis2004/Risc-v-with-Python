
            # Fibonacci calculator
            main:
                addi x1, x0, 0      # fib(0) = 0
                addi x2, x0, 1      # fib(1) = 1
                addi x3, x0, 5      # calculate up to fib(5)
                addi x4, x0, 2      # index = 2
                
                sw x1, 0(x0)        # store fib(0)
                sw x2, 1(x0)        # store fib(1)
                
            fib_loop:
                beq x4, x3, done
                add x5, x1, x2      # fib(n) = fib(n-1) + fib(n-2)
                sw x5, 0(x4)        # store fib(n)
                
                add x1, x0, x2      # update fib(n-2)
                add x2, x0, x5      # update fib(n-1)
                addi x4, x4, 1      # index++
                
                bne x4, x3, fib_loop
                
            done:
                lw x6, 4(x0)        # load fib(4)
                halt
            