.section .data
msg:    .asciz "Hello, World!\n"   # Μήνυμα που θα τυπωθεί

.section .text
.globl _start

_start:
    # a0 = pointer στο string που θα τυπωθεί
    la a0, msg

    # a1 = μήκος μηνύματος
    li a1, 14                # "Hello, World!\n" έχει 14 χαρακτήρες

    # a7 = κωδικός για write syscall (64)
    li a7, 64

    # a2 = αρχείο προορισμού: 1 (stdout)
    li a2, 1

    # syscall
    ecall

    # Exit syscall
    li a7, 93                # exit syscall
    li a0, 0                 # exit code 0
    ecall
