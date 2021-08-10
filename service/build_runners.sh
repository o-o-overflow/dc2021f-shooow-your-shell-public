#!/bin/bash -e

for ARCH in x86_64 riscv64 aarch64
do
	$ARCH-linux-gnu-gcc-9 -static -o runner-$ARCH runner.c
done
