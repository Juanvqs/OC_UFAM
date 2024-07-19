data r0, 0x05
data r1, 0x07
data r2, 0xff
data r3, 0x00

add r0, r3
add r2, r1 

jz  0x00 // vai entrar em loop quando for 0 

jmp  0x08 // vai para o endereco de 08 

